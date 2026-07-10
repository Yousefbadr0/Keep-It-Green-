"""
Keep It Green — Live Webcam Test (simple)
=========================================
Tests ONLY the model on the webcam. No Arduino, no backend.

- Draws a box ONLY when confidence >= CONF_THRESHOLD (default 0.65).
- Prints detections to the terminal.
- Quits when you press Q  OR  close the window (the X button).

Run:
  python test_webcam.py
  python test_webcam.py --conf 0.5 --source 1
Install:  pip install ultralytics opencv-python
"""

import argparse
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

# Folder this script lives in — so the model is found no matter where you run from.
SCRIPT_DIR = Path(__file__).resolve().parent
WINDOW = "Keep It Green - Live Test"


def parse_args():
    ap = argparse.ArgumentParser(description="Live webcam test for the Keep It Green model.")
    ap.add_argument("--model",  default="keep_it_green_best.pt", help="path to .pt or .onnx weights")
    ap.add_argument("--source", default="0", help="webcam index (0, 1, ...)")
    ap.add_argument("--conf",   type=float, default=0.65, help="confidence threshold (default 0.65)")
    return ap.parse_args()


def resolve_model(model_arg: str):
    """Find the weights whether given as-is, relative to cwd, or next to this script."""
    for cand in [Path(model_arg), SCRIPT_DIR / model_arg]:
        if cand.exists():
            return cand
    return None


def main():
    args = parse_args()

    model_path = resolve_model(args.model)
    if model_path is None:
        print(f"[ERROR] Model not found: {args.model}")
        print(f"        Put keep_it_green_best.pt next to test_webcam.py (in the AI folder).")
        return

    print("=" * 60)
    print(" Keep It Green - Live Webcam Test")
    print("=" * 60)
    model = YOLO(str(model_path))
    names = model.names
    print(f"Model      : {model_path}")
    print(f"Classes    : {names}")
    print(f"Threshold  : {args.conf}  (boxes below this are not shown)")
    print("=" * 60)

    cap = cv2.VideoCapture(int(args.source) if args.source.isdigit() else args.source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print(f"[ERROR] Could not open webcam {args.source}. Try --source 1")
        return

    print("Press Q or close the window to stop.\n")
    frame_no = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame_no += 1

            # conf=args.conf -> the model only returns (and plot only draws)
            # detections at or above the threshold.
            t0 = time.perf_counter()
            result = model(frame, conf=args.conf, verbose=False)[0]
            ms = (time.perf_counter() - t0) * 1000

            boxes = result.boxes
            n = 0 if boxes is None else len(boxes)
            print(f"[frame {frame_no:04d} | {ms:5.1f} ms] {n} detection(s)")
            if n:
                fh, fw = frame.shape[:2]
                order = boxes.conf.argsort(descending=True)
                for i in order:
                    cid = int(boxes.cls[i].item())
                    conf = float(boxes.conf[i].item())
                    x1, y1, x2, y2 = [float(v) for v in boxes.xyxy[i].tolist()]
                    area = (x2 - x1) * (y2 - y1) / (fw * fh) * 100
                    # A real item fills PART of the frame. ~100% means the model
                    # only classified the whole image and did not localise anything.
                    flag = "  <-- FULL-FRAME box (model did NOT localise)" if area >= 92 else ""
                    print(f"    {names[cid]:16s} {conf:5.2f}  box=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}) "
                          f"area={area:3.0f}%{flag}")

            cv2.imshow(WINDOW, result.plot())

            # --- exit conditions ---
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            # window closed via the X button -> property drops below 1
            if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                break

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Closed.")


if __name__ == "__main__":
    main()
