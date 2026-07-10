# Keep It Green — AI / Machine module

Object detection (YOLOv8) **and** the recycling-machine program that runs on the laptop.

## Files

| File | What it is |
|---|---|
| **`machine.py`** | 🖥️ **The machine.** ONE program that runs on the laptop: shows the full-screen ATM kiosk UI (the official design, in a built-in WebView), **and** runs the YOLO model + webcam + Arduino in the same process. |
| `recycling_machine.ino` | Arduino sketch — opens the Plastic/Aluminum compartment on the `P`/`A` serial command. |
| `test_model.py` | Quick model tester (image / folder / video / webcam) — prints detections. No backend. |
| `test_webcam.py` | Minimal live-webcam test. No backend. |
| `keep_it_green_training.ipynb` | Clean training notebook (Kaggle). |
| `keep-it-green.ipynb` | The notebook **after running** (EDA charts, training curves, metrics) — for the presentation. |
| `keep_it_green_best.pt` | Trained YOLOv8 weights (used by `machine.py` + the testers). |
| `best.onnx` | ONNX export (optional). |

## The machine (ATM flow)

`machine.py` is a single program. The UI is the kiosk page the backend serves at `/kiosk/`,
embedded in a borderless full-screen window and **driven directly from Python** (no separate
"bridge" server). The YOLO model runs in Python in the same process.

```
Idle  →  Connected  →  Detected (+pts)  →  Drop it in  →  Summary
(QR + keypad)   (user paired)        (item type, %)     (servo opens)
```

**Starting a session — two ways, both on the idle screen:**
1. **Scan the QR** — the machine creates a session and shows a QR; the user scans it in the app.
2. **Enter a code** — the user taps "Get a code to type" in the app, gets a 6-digit code, and types it on the machine's **on-screen keypad**.

Once paired → the screen shows **Connected — {name}**; each detected item posts a transaction
(awards points), fires the Arduino servo, and animates **Detected → Drop → Connected**.

## Run it

1. **Backend** (serves the kiosk page + API):
   ```bash
   cd ..\Recycle
   dotnet run
   ```
2. **The machine** (this folder):
   ```bash
   pip install pywebview ultralytics opencv-python pyserial requests "qrcode[pil]"
   python machine.py
   ```
   It opens full-screen. Configure the top of `machine.py` if needed:
   - `BACKEND_BASE` (default `http://localhost:5217`)
   - `MACHINE_KEY` (must match `appsettings.json` → `Machine:ApiKey`)
   - `MACHINE_ID`, `ARDUINO_PORT` (`"COM3"` to drive servos, or `None`)
   - `MODEL_PATH`, `CONF_THRESH`, `COOLDOWN_SEC`, `SESSION_IDLE_TIMEOUT`, `POINTS`

> **No camera/model installed?** `machine.py` runs in **SIMULATE** mode and auto-generates items,
> so you can demo the whole QR → pair → items → summary flow without hardware.
> (Uses Windows WebView2, which ships with Windows 10/11.)

## Just testing the model (no backend)

```bash
python test_model.py --source 0        # webcam
python test_model.py --source ./pics   # a folder of images
```
