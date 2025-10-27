"""YOLO segmentation detection for trained weights.

Loads trained model and runs segmentation on image folders.
Usage: python yolo_detection.py --weights path/to/best.pt
"""
from pathlib import Path
import argparse
import csv
import cv2
import numpy as np
from ultralytics import YOLO

def resolve_paths():
    # File is at: <repo>/src/main/core/yolo/yolo_detection.py
    # Repo root = parents[4] (one extra level due to yolo/ subfolder)
    here = Path(__file__).resolve()
    repo = here.parents[4]
    return repo, repo / "src/data/output_images", repo / "src/data/yolo_results"

def find_weights(repo):
    # Search both common locations: new training script default and legacy location
    candidates = []
    for runs in [repo / "src/data/yolo_results/runs/segment", repo / "src/train/runs/segment", repo / "runs/segment"]:
        if runs.exists():
            for r in runs.iterdir():
                if r.is_dir():
                    best = r / "weights/best.pt"
                    if best.exists():
                        candidates.append(best)
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None

def load_model(w):
    if not w.exists():
        print(f"Error: {w} not found")
        return None
    return YOLO(str(w))

def list_images(folder):
    if not folder.exists():
        return []
    imgs = []
    # Check for images directly in folder
    imgs.extend(folder.glob("*.jpg"))
    imgs.extend(folder.glob("*.jpeg"))
    imgs.extend(folder.glob("*.png"))
    # Also check subdirectories
    for sub in folder.iterdir():
        if sub.is_dir():
            imgs.extend(sub.glob("*.jpg"))
            imgs.extend(sub.glob("*.jpeg"))
            imgs.extend(sub.glob("*.png"))
    return sorted(imgs)

def segment_image(model, img_path, conf=0.25, iou=0.45):
    img = cv2.imread(str(img_path))
    if img is None:
        raise ValueError(f"Failed to load {img_path}")
    results = model(img, conf=conf, iou=iou, verbose=False)
    dets = []
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    if results and results[0].masks and results[0].boxes:
        masks = results[0].masks.data.cpu().numpy()
        boxes = results[0].boxes.data.cpu().numpy()
        for m, b in zip(masks, boxes):
            x1, y1, x2, y2, c, cls = b
            mr = cv2.resize(m, (img.shape[1], img.shape[0]))
            mb = (mr > 0.5).astype(np.uint8) * 255
            mask = cv2.bitwise_or(mask, mb)
            dets.append({"bbox": [float(x1), float(y1), float(x2), float(y2)], "conf": float(c), "class": int(cls), "mask": mb, "area": int(mb.sum()//255)})
    return img, dets, mask

def visualize(img, dets):
    vis = img.copy()
    cols = [(0,0,255), (0,255,0), (255,0,0), (0,255,255), (255,0,255), (255,255,0)]
    for i, d in enumerate(dets):
        col = cols[i % len(cols)]
        overlay = np.zeros_like(img)
        overlay[d["mask"] > 0] = col
        vis = cv2.addWeighted(vis, 0.7, overlay, 0.3, 0)
        x1, y1, x2, y2 = map(int, d["bbox"])
        cv2.rectangle(vis, (x1, y1), (x2, y2), col, 2)
        lbl = f"cell: {d['conf']:.2f}"
        cv2.putText(vis, lbl, (x1+2, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(vis, f"Detected: {len(dets)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)
    return vis

def process_folder(model, folder, out_dir, conf, iou):
    imgs = list_images(folder)
    if not imgs:
        print(f"No images in {folder.name}")
        return []
    print(f"Processing {len(imgs)} from {folder.name}...")
    out_sub = out_dir / "final_yolo_jpg_images"
    out_sub.mkdir(parents=True, exist_ok=True)
    results = []
    for p in imgs:
        try:
            img, dets, mask = segment_image(model, p, conf, iou)
            vis = visualize(img, dets)
            cv2.imwrite(str(out_sub / f"{p.stem}_seg.jpg"), vis)
            results.append({"image": p.name, "num": len(dets), "area": sum(d["area"] for d in dets)})
            print(f"   {p.name}: {len(dets)} objects")
        except Exception as e:
            print(f"   {p.name}: {e}")
    with open(out_sub / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "num", "area"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved to: {out_sub}")
    return results

def main():
    p = argparse.ArgumentParser(description="YOLO segmentation detection with trained weights")
    p.add_argument("--weights", type=Path, help="Path to model weights (.pt file). Auto-detects latest best.pt if not specified.")
    p.add_argument("--input", type=Path, help="Direct path to input folder (absolute or relative). Overrides --folders.")
    p.add_argument("--folders", nargs="+", default=["jpg_images"],
                   help="Folder paths relative to src/data/output_images/")
    p.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    p.add_argument("--iou", type=float, default=0.45, help="IoU threshold for NMS")
    p.add_argument("--output", type=Path, help="Output directory for results. Defaults to src/data/yolo_results/")
    args = p.parse_args()
    repo, data_root, result_root = resolve_paths()
    weights = args.weights or find_weights(repo)
    if not weights:
        print("No weights found. Use --weights")
        return
    print(f"Using: {weights}")
    model = load_model(weights)
    if not model:
        return
    out = args.output or result_root
    out.mkdir(parents=True, exist_ok=True)
    print(f"Output: {out}")
    
    # Process input folders
    if args.input:
        # Direct path provided
        fp = Path(args.input)
        if fp.exists():
            print(f"Processing: {fp}")
            process_folder(model, fp, out, args.conf, args.iou)
        else:
            print(f"Input folder not found: {fp}")
    else:
        # Use relative folder paths
        for fn in args.folders:
            fp = data_root / fn
            if fp.exists():
                process_folder(model, fp, out, args.conf, args.iou)
            else:
                print(f"Not found: {fn}")
    print("\n Complete!")

if __name__ == "__main__":
    main()
