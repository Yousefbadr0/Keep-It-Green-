"""
Keep It Green — Machine (single program, ATM kiosk on the laptop)
=================================================================
ONE program that runs on the recycling-machine laptop. It:
  - shows the ATM kiosk UI full-screen (the official design) in a built-in window,
  - runs the YOLO model + webcam + Arduino IN THIS SAME PYTHON PROCESS,
  - starts an ATM session on the backend  ->  shows a QR + 6-digit code,
  - the user SCANS the QR with the app, OR types a code from the app on the keypad,
  - on each accepted item: posts the transaction, opens the servo, animates the screen.

No separate "bridge" / web server — the UI is embedded and driven directly from Python.

Run:   python machine.py
Deps:  pip install pywebview ultralytics opencv-python pyserial requests "qrcode[pil]"
       (If ultralytics/opencv are missing it runs in SIMULATE mode so you can still demo.)
Needs: the backend running (it serves the kiosk page) and keep_it_green_best.pt next to this file.
"""

import base64
import io
import json
import threading
import time
from pathlib import Path

import requests

try:
    import webview
except Exception:
    webview = None

try:
    import cv2
    from ultralytics import YOLO
    HAS_CV = True
except Exception:
    HAS_CV = False
try:
    import serial
    HAS_SERIAL = True
except Exception:
    HAS_SERIAL = False
try:
    import qrcode
    HAS_QR = True
except Exception:
    HAS_QR = False

# ----------------------------- Configuration -----------------------------
# Secrets/deploy values live in machine_config.json NEXT TO THIS FILE (kept out of
# version control), overridable by environment variables. Nothing secret is in code.
#   machine_config.json: { "backend_base": "...", "machine_key": "...", "machine_id": 2, ... }
import os as _os

def _load_cfg():
    cfg = {}
    p = Path(__file__).resolve().parent / "machine_config.json"
    if p.exists():
        try:
            cfg = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print("[WARN] machine_config.json is invalid:", e)
    return cfg

_cfg = _load_cfg()
BACKEND_BASE = _os.environ.get("KIG_BACKEND", _cfg.get("backend_base", "http://localhost:5217"))
KIOSK_URL    = BACKEND_BASE + "/kiosk/"
MACHINE_KEY  = _os.environ.get("KIG_MACHINE_KEY", _cfg.get("machine_key", ""))
MACHINE_ID   = int(_os.environ.get("KIG_MACHINE_ID", _cfg.get("machine_id", 1)))
LOCATION     = _cfg.get("location", "Cairo")     # fallback; the backend supplies the real one
if not MACHINE_KEY:
    print("[ERROR] No machine key configured. Create AI/machine_config.json with")
    print('        {"backend_base": "https://...", "machine_key": "...", "machine_id": 2}')
    print("        or set the KIG_MACHINE_KEY environment variable.")

MODEL_PATH   = str(Path(__file__).resolve().parent / "keep_it_green_best_V4.pt")
CONF_THRESH  = 0.65

# ── Detection sanity guards + diagnostics ────────────────────────────────────
# Points are awarded from the detected CLASS (plastic/aluminium); the box is only
# used for the on-screen frame. If the model returns a box that fills (almost) the
# whole frame it has NOT localised the object — a known weakness of this model on
# the machine's webcam (full-frame training labels + domain gap; see NOTES below).
# We ALWAYS log that so a fault is never silent, and can optionally reject it.
MIN_BOX_AREA_FRAC  = 0.01   # a real box shouldn't be a tiny speck ...
MAX_BOX_AREA_FRAC  = 0.95   # ... nor fill ≥95% of the frame (that = a full-frame hallucination).
                            # Tuned for the retrained tight-box model: real close-up items may be
                            # large but a genuine detection won't fill the whole frame. Old model
                            # emitted 100%-area boxes, which this still rejects.
REJECT_UNLOCALIZED = True   # STRICT (default): drop non-localised (full-frame) reads so
                            # the machine does NOT hallucinate an item on an empty intake.
                            # With the current model this also rejects most REAL items
                            # (their boxes come back full-frame too) — that is the signal
                            # to retrain. Set False to count anyway (logs "[!]" per read).
DEBUG_DETECT       = True   # print each frame's top raw model output to the terminal
#
# NOTES — if detection misbehaves, it is the MODEL, not this file:
#   * Proof: run  python test_webcam.py  and watch the "area=" column. ~100% on a
#     real item (or a plastic read on an empty intake) = the model, full stop.
#   * Root cause: ~74% of training boxes were full-frame (classification datasets
#     converted to whole-image boxes) + a plastic/aluminium class imbalance, so the
#     model classifies well but localises poorly and over-predicts "plastic".
#   * Real fix: retrain with TIGHT boxes, add real machine-camera images (the
#     AI/captures/ frames are perfect labelling material) and some empty-intake
#     "background" images, and rebalance the two classes. Then boxes come out tight
#     and this guard can be switched to strict (REJECT_UNLOCALIZED = True).

STABLE_SECONDS = 1.2       # an item must stay detected this long before it counts (anti-misfire buffer)
FLICKER_GAP    = 0.4       # tolerate a dropout this long without resetting the buffer (jittery model)
COOLDOWN_SEC = 3
SESSION_IDLE_TIMEOUT = 60        # end the session after this many seconds with no item

ARDUINO_PORT = _cfg.get("arduino_port", None)   # e.g. "COM5" in machine_config.json; null disables servos
BAUD_RATE    = 9600

POINTS  = {"Plastic": 10, "Aluminum": 15}
DISPLAY = {"Plastic": "Plastic bottle", "Aluminum": "Aluminum can"}
SERIAL_CMD = {"Plastic": b"P", "Aluminum": b"A"}

SIMULATE = not HAS_CV            # no model/camera -> simulate items for the demo

# ----------------------------- shared state ------------------------------
_lock = threading.Lock()
_det = {"item": None, "conf": 0.0, "frame": None}
_entered = {"code": None}        # a code typed on the kiosk keypad
_choice = {"v": None}            # "another" / "finish" tapped on the choice screen
_ui_state = {"s": "idle"}        # the screen currently shown
_session = {"active": False}     # True only while a user session is live (gates camera+model)
window = None


class Api:
    """Exposed to the kiosk page as window.pywebview.api"""
    def submit_code(self, code):
        code = (str(code) if code is not None else "").strip()
        if code:
            with _lock:
                _entered["code"] = code
        return True

    def choose(self, what):
        with _lock:
            _choice["v"] = what
        return True


def ui(state):
    _ui_state["s"] = state.get("state", _ui_state["s"])
    try:
        window.evaluate_js("kioskApply(" + json.dumps(state) + ")")
    except Exception:
        pass


def push_frame(bgr):
    """Send one (annotated) webcam frame to the kiosk screen."""
    if not HAS_CV:
        return
    try:
        small = cv2.resize(bgr, (480, 360))
        ok, buf = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 55])
        if ok:
            uri = "data:image/jpeg;base64," + base64.b64encode(buf).decode()
            window.evaluate_js("kioskFrame(" + json.dumps(uri) + ")")
    except Exception:
        pass


def draw_object_box(img, box, item, conf, progress, done):
    """Draw a tight box + label that fits the detected object (not the whole screen).
    Amber while confirming (with a progress bar), spring-green once confirmed."""
    x1, y1, x2, y2 = box
    green = (100, 201, 24)     # Spring #18C964 (BGR)
    sun   = (61, 200, 255)     # Sun    #FFC83D (BGR)
    ink   = (42, 59, 12)       # Forest #0C3B2A (BGR)
    color = green if done else sun
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
    label = f"{DISPLAY.get(item, item)} {int(conf * 100)}%"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    ly = y1 - th - 12 if (y1 - th - 12) > 0 else y1 + 4
    cv2.rectangle(img, (x1, ly), (x1 + tw + 14, ly + th + 10), color, -1)
    cv2.putText(img, label, (x1 + 7, ly + th + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ink, 2)
    if not done:               # "confirming…" progress along the top edge of the box
        bw = int((x2 - x1) * progress)
        cv2.rectangle(img, (x1, max(0, y1 - 6)), (x1 + bw, max(2, y1 - 2)), green, -1)


def ui_error(msg):
    try:
        window.evaluate_js("kioskError(" + json.dumps(msg) + ")")
    except Exception:
        pass


def make_qr(text):
    if not HAS_QR:
        return None
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ----------------------------- backend calls -----------------------------
def start_session():
    r = requests.post(f"{BACKEND_BASE}/api/Detection/session/start",
                      params={"machineId": MACHINE_ID},
                      headers={"X-Machine-Key": MACHINE_KEY}, timeout=10)
    r.raise_for_status()
    return r.json()


def session_status(code):
    try:
        r = requests.get(f"{BACKEND_BASE}/api/Detection/session/{code}/status",
                         headers={"X-Machine-Key": MACHINE_KEY}, timeout=10)
        d = r.json()
        return d.get("Paired", False), d.get("UserName")
    except Exception:
        return False, None


_PENDING = Path(__file__).resolve().parent / "pending_transactions.jsonl"
CAPTURES_KEEP = 300              # newest capture images to keep (older auto-pruned)


def _save_capture(item, frame):
    """Save the accepted frame (labelling material for retraining) and prune old ones."""
    if frame is None or not HAS_CV:
        return ""
    cap_dir = Path("captures"); cap_dir.mkdir(exist_ok=True)
    img_path = f"captures/{int(time.time())}_{item}.jpg"
    cv2.imwrite(img_path, frame)
    try:
        files = sorted(cap_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime)
        for old in files[:-CAPTURES_KEEP]:
            old.unlink(missing_ok=True)
    except Exception:
        pass
    return img_path


def _post_detection(payload):
    r = requests.post(f"{BACKEND_BASE}/api/Detection", json=payload,
                      headers={"X-Machine-Key": MACHINE_KEY}, timeout=10)
    # 2xx = credited; 4xx = permanently rejected (bad session) — don't retry those.
    return r.status_code < 500


def flush_pending():
    """Re-send transactions that failed earlier (network blip) so no points are lost."""
    if not _PENDING.exists():
        return
    lines = [ln for ln in _PENDING.read_text(encoding="utf-8").splitlines() if ln.strip()]
    still = []
    for ln in lines:
        try:
            if not _post_detection(json.loads(ln)):
                pass                      # 4xx: session is gone; drop it
        except Exception:
            still.append(ln)              # network again -> keep for next time
    if still:
        _PENDING.write_text("\n".join(still) + "\n", encoding="utf-8")
        print(f"[queue] {len(still)} transaction(s) still pending")
    else:
        _PENDING.unlink(missing_ok=True)
        if lines:
            print(f"[queue] flushed {len(lines)} queued transaction(s)")


def submit(code, item, conf, frame):
    """Credit the item. Retries on transient failure; if the network is down, the
    transaction is queued to disk and re-sent at the next session start — the user's
    points are never silently lost."""
    img_path = _save_capture(item, frame)
    payload = {"Otp": code, "ItemType": item,
               "ConfidenceScore": round(conf, 3), "ImagePath": img_path}
    for attempt in range(3):
        try:
            _post_detection(payload)
            return
        except Exception as e:
            print(f"[WARN] submit attempt {attempt + 1}/3 failed: {e}")
            time.sleep(0.8 * (attempt + 1))
    with _PENDING.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
    print("[queue] transaction saved to pending_transactions.jsonl (will retry)")


# ----------------------------- detection ---------------------------------
def _item_from_class(name):
    """Map a model class name to a reward bucket, or None if it isn't rewarded."""
    n = str(name).lower()
    if "plastic" in n or "pet" in n or "bottle" in n:
        return "Plastic"
    if "alumin" in n or "can" in n or "metal" in n:
        return "Aluminum"
    return None


def detection_supervisor():
    """Keeps detection alive: if the loop ever dies (camera unplugged, driver hiccup,
    model error) it logs the cause and restarts instead of leaving the machine frozen."""
    while True:
        try:
            detection_thread()
        except Exception as e:
            print(f"[ERROR] detection loop crashed: {e!r} — restarting in 3s")
            with _lock:
                _det.update(item=None, conf=0.0, frame=None)
            time.sleep(3)


def detection_thread():
    model = YOLO(MODEL_PATH)
    names = model.names
    print(f"[model] loaded {MODEL_PATH}")
    print(f"[model] task={getattr(model, 'task', '?')}  classes={names}")
    print(f"[model] guards: conf>={CONF_THRESH}, box area "
          f"{int(MIN_BOX_AREA_FRAC * 100)}%..{int(MAX_BOX_AREA_FRAC * 100)}%, "
          f"reject_unlocalised={REJECT_UNLOCALIZED}")
    # Open the camera ONCE and keep it WARM in the background, so it opens instantly when
    # a session starts (no VideoCapture re-init lag). The MODEL, however, runs only on the
    # place-item screen -> a warm camera, but NO detecting/counting in the background.
    cam_index = int(_cfg.get("camera_index", 0))
    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print(f"[ERROR] camera {cam_index} could not be opened — check camera_index in machine_config.json")
    print("Detection thread started (camera warm; model runs only on the place-item screen).")
    last_push = 0.0
    last_log = 0.0
    cand_item = None            # the class we're currently building confidence on
    cand_since = 0.0            # when we first saw it continuously
    cand_last_seen = 0.0        # last frame the candidate was seen (flicker tolerance)
    cand_conf = 0.0             # last REAL confidence for the candidate (so it never shows 0%)
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue
        # Run the MODEL only on the place-item screen ("connected"). On idle / detected /
        # drop / choice / summary we keep grabbing frames (camera stays warm) but do NOT
        # infer -> no background detection and no false counts between items.
        if _ui_state["s"] != "connected":
            cand_item, cand_since = None, 0.0
            with _lock:
                _det.update(item=None, conf=0.0, frame=None)
            time.sleep(0.03)
            continue
        res = model(frame, conf=CONF_THRESH, verbose=False)[0]
        H, W = frame.shape[:2]
        frame_area = float(W * H) or 1.0

        # Take the single most-confident detection, then SANITY-CHECK it. The class
        # and box come straight from the model — we only accept it if it actually
        # localises an object (guards above). This keeps model faults visible (a
        # full-frame "whole image = plastic" read is rejected, not counted).
        raw_item, conf, box, reject, cls_name, area_frac = None, 0.0, None, None, None, 0.0
        if res.boxes is not None and len(res.boxes):
            i = int(res.boxes.conf.argmax().item())
            conf = float(res.boxes.conf[i].item())
            cls_name = str(names[int(res.boxes.cls[i].item())])
            box = [int(v) for v in res.boxes.xyxy[i].tolist()]
            area_frac = max(0.0, (box[2] - box[0]) * (box[3] - box[1]) / frame_area)
            mapped = _item_from_class(cls_name)
            if mapped is None:
                reject = f"unmapped class '{cls_name}'"
            elif area_frac < MIN_BOX_AREA_FRAC:
                reject = f"box too small ({area_frac * 100:.1f}%)"
            elif area_frac >= MAX_BOX_AREA_FRAC:
                reject = f"box fills {area_frac * 100:.0f}% of frame — model did not localise the object"
            raw_item = None if (reject and REJECT_UNLOCALIZED) else mapped

        now = time.time()

        # Throttled diagnostics — always show exactly what the model returned, so a
        # bad read is attributable to the MODEL rather than to this machine code.
        if DEBUG_DETECT and now - last_log > 0.5:
            last_log = now
            if cls_name is None:
                print("[detect] (no object)")
            else:
                if raw_item and reject:
                    verdict = f"COUNT {raw_item}  [!] {reject}"   # counted, but flagged
                elif raw_item:
                    verdict = f"COUNT {raw_item}"
                else:
                    verdict = f"REJECT - {reject}"
                print(f"[detect] {cls_name:14s} conf={conf:.2f} area={area_frac * 100:3.0f}%  ->  {verdict}")

        # stability buffer — the same class must persist ~STABLE_SECONDS before it
        # counts. A single flickered/dropped frame does NOT reset the timer (the model
        # is jittery on the webcam): the candidate survives gaps shorter than FLICKER_GAP.
        if raw_item and raw_item == cand_item:
            cand_last_seen, cand_conf = now, conf                              # still here
        elif raw_item and raw_item != cand_item:
            cand_item, cand_since, cand_last_seen, cand_conf = raw_item, now, now, conf  # new candidate
        elif cand_item and now - cand_last_seen > FLICKER_GAP:
            cand_item, cand_since, cand_conf = None, 0.0, 0.0                  # gone long enough
        held = (now - cand_since) if cand_item else 0.0
        confirmed = cand_item if (cand_item and held >= STABLE_SECONDS) else None
        progress = min(1.0, held / STABLE_SECONDS) if cand_item else 0.0

        # expose the confirmed item + its LAST REAL confidence. Using the current frame's
        # conf showed 0% whenever the item was confirmed on a flicker-gap frame (raw=None).
        with _lock:
            _det.update(item=confirmed, conf=cand_conf, frame=frame)

        # live preview with a box that fits the object (~8 fps, only on the "place item" screen)
        if _ui_state["s"] == "connected" and now - last_push > 0.12:
            view = frame.copy()
            if box is not None and cand_item:
                draw_object_box(view, box, cand_item, conf, progress, confirmed is not None)
            push_frame(view)
            last_push = now


def open_arduino():
    if not HAS_SERIAL or ARDUINO_PORT is None:
        return None
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print("Arduino connected on", ARDUINO_PORT)
        return ser
    except Exception as e:
        print("[WARN] Arduino not connected:", e)
        return None


def pop_entered():
    with _lock:
        c = _entered["code"]
        _entered["code"] = None
        return c


def wait_choice(timeout=13):
    """Wait for the user to tap Add-another / Finish; default to finish on timeout."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        with _lock:
            v = _choice["v"]
            _choice["v"] = None
        if v:
            return v
        time.sleep(0.2)
    return "finish"


def end_session(code):
    """Tell the backend to stop this session, so the paired phone auto-closes too."""
    try:
        requests.post(f"{BACKEND_BASE}/api/Detection/session/{code}/end",
                      headers={"X-Machine-Key": MACHINE_KEY}, timeout=10)
    except Exception as e:
        print("[WARN] end session failed:", e)


def fetch_total(code):
    try:
        r = requests.get(f"{BACKEND_BASE}/api/Detection/session/{code}/total",
                         headers={"X-Machine-Key": MACHINE_KEY}, timeout=10)
        return r.json().get("Points")
    except Exception:
        return None


def wait_ready():
    for _ in range(60):
        try:
            if window.evaluate_js("typeof window.kioskApply") == "function":
                return
        except Exception:
            pass
        time.sleep(0.25)


# ----------------------------- main loop ---------------------------------
def run():
    wait_ready()
    arduino = open_arduino()
    if HAS_CV and not SIMULATE:
        threading.Thread(target=detection_supervisor, daemon=True).start()
    else:
        print("Running in SIMULATE mode (no camera/model) — items auto-generated.")

    while True:
        flush_pending()                   # re-send any transactions queued while offline

        # 1) start a session and show the QR + code
        try:
            info = start_session()
            machine_code = info["PairingCode"]
            location = info.get("LocationName") or LOCATION
        except Exception as e:
            print("[WARN] cannot start session (backend down?):", e)
            ui({"state": "idle", "code": "------", "location": LOCATION})
            time.sleep(4)
            continue
        ui({"state": "idle", "code": machine_code, "qr": make_qr(machine_code), "location": location})

        # 2) wait for pairing — the app SCANS the QR, or the user TYPES a code on the keypad
        active_code, user = None, None
        t0 = time.time()
        while time.time() - t0 < 900:                # 15-minute window
            time.sleep(1.0)
            typed = pop_entered()
            if typed:
                paired, uname = session_status(typed)
                if paired:
                    active_code, user = typed, uname or "there"
                    break
                ui_error("Invalid or expired code")
            paired, uname = session_status(machine_code)
            if paired:
                active_code, user = machine_code, uname or "there"
                break
        if active_code is None:
            continue                                  # code expired -> start a fresh one
        _session["active"] = True                     # from here the camera + model run

        # 3) active session
        items, points = 0, 0
        last = time.time()
        cooldown = 0.0
        armed = True             # require the item to clear before the next one counts
        sim_next = time.time() + 8
        last_status_check = time.time()
        last_hold_log = 0.0      # throttle for the "have item but holding" diagnostic
        ended_checks = 0         # consecutive "not active" polls (debounce network blips)
        ui({"state": "connected", "userName": user, "sessionPts": 0})

        finished = False
        while not finished:
            time.sleep(0.2)
            now = time.time()

            # the user tapped "Finish session" on the phone -> the backend stops the
            # session, so this poll stops seeing it as active and we return to idle.
            if not SIMULATE and now - last_status_check > 1.5:
                last_status_check = now
                paired, _ = session_status(active_code)
                ended_checks = ended_checks + 1 if not paired else 0
                if ended_checks >= 2:
                    finished = True
                    continue
            if SIMULATE:
                item, conf, frame = (None, 0.0, None)
                if now >= sim_next:
                    item = "Plastic" if items % 2 == 0 else "Aluminum"
                    conf, sim_next = 0.93, now + 8
            else:
                with _lock:
                    item, conf, frame = _det["item"], _det["conf"], _det["frame"]

            if item and armed and now > cooldown:
                pts = POINTS[item]
                submit(active_code, item, conf, frame)
                if arduino:
                    try:
                        arduino.write(SERIAL_CMD[item])
                    except Exception:
                        pass
                items += 1
                points += pts
                cooldown = now + COOLDOWN_SEC
                armed = False               # don't re-count until the object is removed

                ui({"state": "detected", "item": DISPLAY[item], "confidence": round(conf * 100), "points": pts})
                time.sleep(2.4)
                ui({"state": "drop", "item": item})
                time.sleep(2.2)
                # ask: add another item, or finish?
                ui({"state": "choice", "item": DISPLAY[item], "points": pts, "seconds": 12})
                if wait_choice(13) == "finish":
                    finished = True
                else:
                    now2 = time.time()
                    last = now2
                    sim_next = now2 + 8
                    armed = True            # ready for the NEXT item — don't wait for a
                                            # "clear" frame the jittery model may never give
                    cooldown = now2 + 2     # short grace so a lingering read of the item we
                                            # just counted cannot immediately double-count
                    ui({"state": "connected", "userName": user, "sessionPts": points})

            else:
                # A confirmed item is present but NOT counted -> log WHY, so "it didn't
                # take my item" can be told apart from the model missing it entirely.
                if item and DEBUG_DETECT and now - last_hold_log > 1.5:
                    last_hold_log = now
                    why = "cooldown" if now <= cooldown else ("re-arming" if not armed else "")
                    if why:
                        print(f"[accept] have {item} but holding ({why})")
                if not item:
                    armed = True            # object cleared -> ready for the next one
                if now - last > SESSION_IDLE_TIMEOUT:
                    finished = True

        _session["active"] = False                    # session over -> stop the model
        end_session(active_code)                       # stop it on the backend -> phone auto-closes

        # 4) summary (this session + total points + thanks), then back to Idle for the next user
        ui({"state": "summary", "userName": user, "items": items,
            "points": points, "total": fetch_total(active_code)})
        time.sleep(7)


def main():
    global window
    if webview is None:
        print("pywebview is not installed.  pip install pywebview")
        return
    window = webview.create_window("Keep It Green", KIOSK_URL, js_api=Api(),
                                   fullscreen=True, background_color="#0C3B2A")
    webview.start(run)


if __name__ == "__main__":
    main()
