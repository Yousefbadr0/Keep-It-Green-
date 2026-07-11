"""
Keep It Green — package machine-camera captures for labelling.

The machine saves every ACCEPTED item's frame to captures/. Those images are the
single most valuable training data we have (they are exactly what the deployed
camera sees). This script packs them into a zip ready to upload to Roboflow
(https://roboflow.com — free tier) for labelling.

Workflow to fine-tune the model on the machine's own domain:
  1. python prepare_captures.py            -> captures_for_labeling.zip
  2. Roboflow: new project (Object Detection) -> Upload the zip
  3. Label each image with tight boxes: classes  plastic_bottle , aluminum_can
     (also add ~30-50 photos of the EMPTY intake, left unlabelled = background)
  4. Generate a version -> Download -> format "YOLOv8" -> get the code snippet
  5. In keep_it_green.ipynb (Kaggle), add the (workspace, project, version) to
     RF_PROJECTS in cell 2.1 and Run All -> new keep_it_green_best.pt
  6. Drop the new .pt into AI/ (replace keep_it_green_best.pt) - done.

Run:  python prepare_captures.py [--max 400]
"""
import argparse
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description="Zip machine captures for Roboflow labelling.")
    ap.add_argument("--max", type=int, default=400, help="newest N images to include (default 400)")
    args = ap.parse_args()

    cap_dir = HERE / "captures"
    imgs = sorted(cap_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)[: args.max]
    if not imgs:
        print(f"No captures found in {cap_dir} — run the machine first (accepted items are saved there).")
        return

    out = HERE / "captures_for_labeling.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in imgs:
            z.write(p, p.name)
    print(f"Packed {len(imgs)} images -> {out}")
    print("Next: upload this zip to a Roboflow Object Detection project and label with")
    print("classes 'plastic_bottle' / 'aluminum_can' (tight boxes). See the header of this file.")


if __name__ == "__main__":
    main()
