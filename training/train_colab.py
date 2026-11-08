"""Trainiert chess_yolov8n.pt für die Figurenerkennung (YOLOv8n, 12 Klassen).

Datensätze (beide CC-BY-4.0, von Hugging Face):
- dopaul/chess-pieces-merged, davon nur die Bilder aus "chess_pieces_dominique".
  Die Bilder aus "chess_pieces_roboflow" haben dort keine Labels (Stand
  2026-11-08: 693 Bilder, 0 Boxen) und würden Figuren als Hintergrund lehren.
  Bei den Formaten 960x1280 und 4032x3024 passen die Labels nicht zum Bild
  (gehören zur gedrehten Fassung, vermutlich EXIF), auch die fallen weg.
- Francesco/chess-pieces-mjzgj (Roboflow "Chess Pieces" aus RF100, COCO-Boxen).

Gedacht für eine Colab-GPU (siehe README, Abschnitt 5). Ergebnis:
<out>/chess_yolov8n.pt und <out>/metrics.json.

    python train_colab.py --epochs 100 --out /content/w/out
"""
import argparse
import io
import json
import os
import shutil

import pandas as pd
from huggingface_hub import hf_hub_download, list_repo_files
from PIL import Image

DOMINIQUE = "dopaul/chess-pieces-merged"
RF100 = "Francesco/chess-pieces-mjzgj"
BROKEN_SIZES = {(960, 1280), (4032, 3024)}
NAMES = ["black-bishop", "black-king", "black-knight", "black-pawn", "black-queen", "black-rook",
         "white-bishop", "white-king", "white-knight", "white-pawn", "white-queen", "white-rook"]


def _write(root, split, name, img_bytes, lines):
    img_dir = os.path.join(root, "images", split)
    lbl_dir = os.path.join(root, "labels", split)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)
    Image.open(io.BytesIO(img_bytes)).convert("RGB").save(os.path.join(img_dir, name + ".jpg"), quality=95)
    with open(os.path.join(lbl_dir, name + ".txt"), "w") as f:
        f.write("\n".join(lines))


def _parquet(repo, prefix):
    files = [f for f in list_repo_files(repo, repo_type="dataset")
             if f.startswith(f"data/{prefix}-") and f.endswith(".parquet")]
    return pd.concat([pd.read_parquet(hf_hub_download(repo, f, repo_type="dataset")) for f in files],
                     ignore_index=True)


def export_yolo(root):
    counts = {}
    # Dominique: bereits YOLO-normiert, Klassen-IDs wie NAMES
    for hf_split, split in {"train": "train", "valid": "val", "test": "test"}.items():
        df = _parquet(DOMINIQUE, hf_split)
        df = df[df["source_dataset"] == "chess_pieces_dominique"]
        sizes = list(zip(df["image_width"], df["image_height"]))
        df = df[[sz not in BROKEN_SIZES for sz in sizes]]
        for i, row in df.iterrows():
            a = row["annotations"]
            lines = [f"{int(c)} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
                     for c, x, y, w, h in zip(a["class_id"], a["x_center"], a["y_center"],
                                              a["width"], a["height"])]
            if lines:
                _write(root, split, f"dom_{hf_split}_{i:05d}", row["image"]["bytes"], lines)
                counts[("dominique", split)] = counts.get(("dominique", split), 0) + 1
    # RF100: COCO-Boxen in Pixeln [x, y, w, h]; Kategorie 2..13 -> 0..11,
    # 0 "chess-pieces" und 1 "bishop" (ohne Farbe) werden verworfen
    for hf_split, split in {"train": "train", "validation": "val", "test": "test"}.items():
        df = _parquet(RF100, hf_split)
        for i, row in df.iterrows():
            W, H = row["width"], row["height"]
            o = row["objects"]
            lines = []
            for cat, (x, y, w, h) in zip(o["category"], o["bbox"]):
                if cat < 2:
                    continue
                lines.append(f"{int(cat) - 2} {(x + w / 2) / W:.6f} {(y + h / 2) / H:.6f} {w / W:.6f} {h / H:.6f}")
            if lines:
                _write(root, split, f"rf_{hf_split}_{i:05d}", row["image"]["bytes"], lines)
                counts[("rf100", split)] = counts.get(("rf100", split), 0) + 1
    print("Bilder:", {f"{k[0]}/{k[1]}": v for k, v in counts.items()}, flush=True)
    yaml_path = os.path.join(root, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(f"path: {root}\ntrain: images/train\nval: images/val\ntest: images/test\n")
        f.write("names:\n" + "".join(f"  {i}: {n}\n" for i, n in enumerate(NAMES)))
    return yaml_path, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--data-dir", default="/content/w/dataset")
    ap.add_argument("--out", default="/content/w/out")
    args = ap.parse_args()

    from ultralytics import YOLO

    shutil.rmtree(args.data_dir, ignore_errors=True)
    yaml_path, counts = export_yolo(args.data_dir)
    model = YOLO("yolov8n.pt")
    model.train(data=yaml_path, epochs=args.epochs, imgsz=args.imgsz, batch=32,
                patience=25, project=args.out, name="run", exist_ok=True, plots=True)

    best = os.path.join(args.out, "run", "weights", "best.pt")
    final = YOLO(best)
    metrics = {}
    for split in ("val", "test"):
        m = final.val(data=yaml_path, split=split, imgsz=args.imgsz, project=args.out,
                      name=f"eval_{split}", exist_ok=True)
        metrics[split] = {"mAP50": float(m.box.map50), "mAP50-95": float(m.box.map),
                          "per_class_mAP50-95": dict(zip(NAMES, map(float, m.box.maps)))}
    shutil.copy(best, os.path.join(args.out, "chess_yolov8n.pt"))
    with open(os.path.join(args.out, "metrics.json"), "w") as f:
        json.dump({"datasets": [DOMINIQUE + " (nur chess_pieces_dominique)", RF100],
                   "images": {f"{k[0]}/{k[1]}": v for k, v in counts.items()}, "epochs": args.epochs, "imgsz": args.imgsz, **metrics}, f, indent=2)
    print("FERTIG", json.dumps(metrics), flush=True)


if __name__ == "__main__":
    main()
