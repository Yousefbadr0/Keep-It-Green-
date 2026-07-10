"""
Keep It Green — Standalone Model Tester
=======================================
Tests ONLY the trained YOLO model. No Arduino, no backend.
Prints every kept detection to the terminal and (optionally) shows a window.

All filtering is done HERE (not by YOLO's plotter) so you have full control:
  --conf      minimum confidence; anything below is dropped          (default 0.65)
  --max-area  drop boxes bigger than this fraction of the frame      (default 0.95)
              -> kills the "whole canvas detected as plastic" artifact.
                 set --max-area 1.0 to disable this filter.

Usage
-----
  python test_model.py                       # webcam 0, window
  python test_model.py --source 1            # webcam index 1
  python test_model.py --source photo.jpg    # one image
  python test_model.py --source ./pics       # a folder of images
  python test_model.py --conf 0.5            # show detections >= 50%
  python test_model.py --max-area 1.0        # allow full-frame boxes too

Install:  pip install ultralytics opencv-python
"""

import argparse
import os
import time
from collections import defaultdict
from pathlib import Path

import cv2
from ultralytics import YOLO

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VID_EXT = {".mp4", ".avi", ".mov", ".mkv"}
WINDOW  = "Keep It Green — Test"

# We query the model at a low floor and filter ourselves -> total control.
QUERY_CONF = 0.05

SCRIPT_DIR = Path(__file__).resolve().parent


# ─── Setup helpers ────────────────────────────────────────────────────────────
def parse_args():
    ap = argparse.ArgumentParser(description="Test the Keep It Green YOLO model.")
    ap.add_argument("--model",    default="keep_it_green_best.pt", help=".pt or .onnx weights")
    ap.add_argument("--source",   default="0", help="webcam index, image, folder, or video")
    ap.add_argument("--conf",     type=float, default=0.65,
                    help="min confidence; boxes below are NOT shown (default 0.65)")
    ap.add_argument("--max-area", type=float, default=0.95, dest="max_area",
                    help="drop boxes covering more than this fraction of the frame "
                         "(default 0.95; use 1.0 to disable)")
    ap.add_argument("--show",     action="store_true", help="show the annotated window")
    return ap.parse_args()


def resolve_model(model_arg: str):
    """Find the weights whether given as-is, relative to cwd, or next to this script."""
    for cand in [Path(model_arg), SCRIPT_DIR / model_arg]:
        if cand.exists():
            return cand
    return None


def open_capture(source):
    """Open a webcam (int) or video file. Uses DirectShow on Windows for reliable webcams."""
    if str(source).isdigit():
        idx = int(source)
        if os.name == "nt":                       # Windows: MSMF often drops frames
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                return cap
        return cv2.VideoCapture(idx)
    return cv2.VideoCapture(source)


# ─── Detection filtering / drawing (single source of truth) ────────────────────
def extract_detections(result, frame_shape, conf_thresh, max_area):
    """Return [(cid, conf, (x1,y1,x2,y2), area_frac)] passing BOTH filters, best first."""
    H, W = frame_shape[:2]
    frame_area = float(W * H)
    dets = []
    if result.boxes is None:
        return dets
    for i in range(len(result.boxes)):
        conf = float(result.boxes.conf[i].item())
        if conf < conf_thresh:                    # below confidence -> skip
            continue
        x1, y1, x2, y2 = (int(v) for v in result.boxes.xyxy[i].tolist())
        area_frac = ((x2 - x1) * (y2 - y1)) / frame_area
        if area_frac > max_area:                  # near full-frame artifact -> skip
            continue
        cid = int(result.boxes.cls[i].item())
        dets.append((cid, conf, (x1, y1, x2, y2), area_frac))
    dets.sort(key=lambda d: d[1], reverse=True)
    return dets


def draw_detections(frame, dets, names):
    out = frame.copy()
    for cid, conf, (x1, y1, x2, y2), _ in dets:
        color = (255, 80, 30) if cid == 0 else (30, 90, 255)   # BGR: plastic=blue, alu=orange
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        cv2.putText(out, f"{names[cid]} {conf:.2f}", (x1, max(18, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return out


def print_detections(dets, names):
    if not dets:
        print("    (nothing above threshold)")
        return
    for cid, conf, (x1, y1, x2, y2), area in dets:
        print(f"    {names[cid]:16s} {conf:5.2f}  area={area*100:3.0f}%  "
              f"box=({x1:4d},{y1:4d},{x2:4d},{y2:4d})")


# ─── Runners ──────────────────────────────────────────────────────────────────
def run_stream(model, names, source, args):
    """Webcam (int) or video file — loop frames and print detections."""
    cap = open_capture(source)
    if not cap.isOpened():
        print(f"[ERROR] Could not open source: {source}")
        if str(source).isdigit():
            print("        Try a different camera index, e.g. --source 1")
        return

    print("Press Q, or close the window, (or Ctrl+C in the terminal) to stop.\n")
    frame_no, fails, seen_visible = 0, 0, False
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                fails += 1
                if fails == 1:
                    print("[WARN] Waiting for camera frames...")
                if fails > 60:
                    print("[ERROR] Camera stopped delivering frames — try --source 1")
                    break
                cv2.waitKey(30)
                continue
            fails = 0
            frame_no += 1

            t0 = time.perf_counter()
            result = model(frame, conf=QUERY_CONF, verbose=False)[0]
            ms = (time.perf_counter() - t0) * 1000

            dets = extract_detections(result, frame.shape, args.conf, args.max_area)
            print(f"[frame {frame_no:04d} | {ms:5.1f} ms | {1000/ms:4.1f} FPS] "
                  f"{len(dets)} detection(s)")
            print_detections(dets, names)

            if args.show:
                annotated = draw_detections(frame, dets, names)
                cv2.putText(annotated,
                            f"conf>={args.conf:.2f}  area<={args.max_area:.2f}",
                            (10, frame.shape[0] - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
                cv2.imshow(WINDOW, annotated)
                key = cv2.waitKey(1) & 0xFF
                vis = cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE)
                if vis >= 1:
                    seen_visible = True
                if key == ord("q") or (seen_visible and vis < 1):
                    break
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        cap.release()
        cv2.destroyAllWindows()


def run_images(model, names, paths, args):
    """Single image or folder — predict each and print, then a summary."""
    total = defaultdict(int)
    conf_sum = defaultdict(float)
    times = []
    show = args.show

    for i, p in enumerate(paths, 1):
        img = cv2.imread(str(p))
        if img is None:
            print(f"[{i}/{len(paths)}] {p.name} — could not read, skipping")
            continue

        t0 = time.perf_counter()
        result = model(img, conf=QUERY_CONF, verbose=False)[0]
        times.append((time.perf_counter() - t0) * 1000)

        dets = extract_detections(result, img.shape, args.conf, args.max_area)
        print(f"[{i}/{len(paths)}] {p.name}  | {times[-1]:5.1f} ms")
        print_detections(dets, names)
        for cid, conf, _, _ in dets:
            total[cid] += 1
            conf_sum[cid] += conf

        if show:
            cv2.imshow(WINDOW, draw_detections(img, dets, names))
            if (cv2.waitKey(0) & 0xFF == ord("q")) or \
               cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                show = False
                cv2.destroyAllWindows()

    cv2.destroyAllWindows()

    print("\n" + "=" * 60)
    print(" SUMMARY")
    print("=" * 60)
    print(f"Images processed : {len(times)}")
    print(f"Total detections : {sum(total.values())}")
    for cid in sorted(total):
        print(f"  {names[cid]:16s}: {total[cid]:4d}   (avg conf {conf_sum[cid]/total[cid]:.2f})")
    if times:
        mean = sum(times) / len(times)
        print(f"Avg inference    : {mean:.1f} ms  ({1000/mean:.1f} FPS)")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()

    model_path = resolve_model(args.model)
    if model_path is None:
        print(f"[ERROR] Model not found: {args.model}")
        print(f"        Looked in : {Path(args.model).resolve()}")
        print(f"        and        : {SCRIPT_DIR / args.model}")
        print("        Put keep_it_green_best.pt next to test_model.py (in the AI folder).")
        return

    print("=" * 60)
    print(" Keep It Green — Model Test")
    print("=" * 60)
    model = YOLO(str(model_path))
    names = model.names
    print(f"Model      : {model_path}")
    print(f"Classes    : {names}")
    print(f"Filters    : conf >= {args.conf}   |   max area <= {args.max_area*100:.0f}% of frame")

    src = args.source
    src_path = Path(src)

    if str(src).isdigit():
        print(f"Source     : webcam ({src})")
        print("=" * 60 + "\n")
        run_stream(model, names, src, args)

    elif src_path.is_dir():
        imgs = sorted(p for p in src_path.iterdir() if p.suffix.lower() in IMG_EXT)
        print(f"Source     : folder '{src}'  ({len(imgs)} images)")
        print("=" * 60 + "\n")
        if imgs:
            run_images(model, names, imgs, args)
        else:
            print("No images found in that folder.")

    elif src_path.suffix.lower() in IMG_EXT:
        print(f"Source     : image '{src}'")
        print("=" * 60 + "\n")
        run_images(model, names, [src_path], args)

    elif src_path.suffix.lower() in VID_EXT:
        print(f"Source     : video '{src}'")
        print("=" * 60 + "\n")
        run_stream(model, names, src, args)

    else:
        print(f"[ERROR] Unrecognized source: {src}")


if __name__ == "__main__":
    main()
