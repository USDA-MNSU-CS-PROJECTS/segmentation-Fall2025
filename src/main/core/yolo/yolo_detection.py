"""YOLO segmentation detection for trained weights.

This module loads a trained YOLO segmentation model and runs inference on image folders.
It performs cell/cross-section detection and creates visualization overlays showing
detected regions with bounding boxes and segmentation masks.

Usage:
    python yolo_detection.py --weights path/to/best.pt
    python yolo_detection.py --input path/to/images --conf 0.3
"""
from pathlib import Path
import argparse
import csv
import cv2
import numpy as np
from ultralytics import YOLO


def resolve_paths():
    """Resolve repository paths relative to this script's location.
    
    Calculates paths based on the script's location in the repository structure.
    The script is located at: <repo>/src/main/core/yolo/yolo_detection.py
    
    Returns:
        tuple: (repo_root, data_root, result_root)
            - repo_root: Repository root directory
            - data_root: Directory containing input images (src/data/output_images)
            - result_root: Directory for output results (src/data/yolo_results)
    """
    # File is at: <repo>/src/main/core/yolo/yolo_detection.py
    # Repo root = parents[4] (one extra level due to yolo/ subfolder)
    here = Path(__file__).resolve()
    repo = here.parents[4]
    return repo, repo / "src/data/output_images", repo / "src/data/yolo_results"

def find_weights(repo: Path) -> Path | None:
    """Automatically find the most recent trained model weights.
    
    Searches common training output directories for best.pt files and returns
    the most recently modified one. This allows the script to work without
    explicitly specifying weights if training has been run.
    
    Args:
        repo: Repository root directory
        
    Returns:
        Path to the most recent best.pt file, or None if no weights found
    """
    # Search both common locations: new training script default and legacy location
    candidates = []
    # Check multiple possible locations where training runs might be stored
    for runs in [repo / "src/data/yolo_results/runs/segment", 
                 repo / "src/train/runs/segment", 
                 repo / "runs/segment"]:
        if runs.exists():
            # Iterate through all training run directories
            for r in runs.iterdir():
                if r.is_dir():
                    best = r / "weights/best.pt"
                    if best.exists():
                        candidates.append(best)
    # Return the most recently modified weights file (most recent training run)
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None

def load_model(w: Path):
    """Load YOLO model from weights file.
    
    Args:
        w: Path to the model weights file (.pt)
        
    Returns:
        YOLO model instance, or None if weights file doesn't exist
    """
    if not w.exists():
        print(f"Error: {w} not found")
        return None
    return YOLO(str(w))

def list_images(folder: Path) -> list[Path]:
    """Recursively find all image files in a folder and its subdirectories.
    
    Searches for common image formats (JPG, JPEG, PNG) both in the specified
    folder and one level deep in subdirectories. This allows processing images
    organized in subfolders.
    
    Args:
        folder: Directory path to search for images
        
    Returns:
        Sorted list of image file paths (empty list if folder doesn't exist)
    """
    if not folder.exists():
        return []
    imgs = []
    # Check for images directly in folder
    imgs.extend(folder.glob("*.jpg"))
    imgs.extend(folder.glob("*.jpeg"))
    imgs.extend(folder.glob("*.png"))
    # Also check subdirectories (one level deep)
    for sub in folder.iterdir():
        if sub.is_dir():
            imgs.extend(sub.glob("*.jpg"))
            imgs.extend(sub.glob("*.jpeg"))
            imgs.extend(sub.glob("*.png"))
    return sorted(imgs)

def segment_image(model, img_path: Path, conf: float = 0.25, iou: float = 0.45):
    """Run YOLO segmentation inference on a single image.
    
    Performs object detection and segmentation, returning bounding boxes,
    confidence scores, and binary masks for each detected object.
    
    Args:
        model: YOLO model instance
        img_path: Path to input image file
        conf: Confidence threshold (0.0-1.0). Detections below this are filtered out.
        iou: Intersection over Union threshold for Non-Maximum Suppression (NMS).
             Higher values allow more overlapping detections.
    
    Returns:
        tuple: (image, detections, combined_mask)
            - image: Original image as numpy array (BGR format)
            - detections: List of dicts, each containing:
                - bbox: [x1, y1, x2, y2] bounding box coordinates
                - conf: Confidence score
                - class: Class ID
                - mask: Binary mask for this detection
                - area: Pixel area of the mask
            - combined_mask: Combined binary mask of all detections
    
    Raises:
        ValueError: If image file cannot be loaded
    """
    # Load image using OpenCV (BGR format)
    img = cv2.imread(str(img_path))
    if img is None:
        raise ValueError(f"Failed to load {img_path}")
    
    # Run YOLO inference
    results = model(img, conf=conf, iou=iou, verbose=False)
    
    # Initialize empty detection list and combined mask
    dets = []
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    # Process results if detections were found
    if results and results[0].masks and results[0].boxes:
        # Extract masks and boxes from GPU to CPU as numpy arrays
        masks = results[0].masks.data.cpu().numpy()
        boxes = results[0].boxes.data.cpu().numpy()
        
        # Process each detection
        for m, b in zip(masks, boxes):
            # Unpack bounding box: [x1, y1, x2, y2, confidence, class]
            x1, y1, x2, y2, c, cls = b
            
            # Resize mask to match image dimensions (YOLO returns masks at model input size)
            mr = cv2.resize(m, (img.shape[1], img.shape[0]))
            
            # Binarize mask: threshold at 0.5, convert to 0/255
            mb = (mr > 0.5).astype(np.uint8) * 255
            
            # Combine this mask with the overall mask (union of all detections)
            mask = cv2.bitwise_or(mask, mb)
            
            # Store detection information
            dets.append({
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                "conf": float(c),
                "class": int(cls),
                "mask": mb,
                "area": int(mb.sum() // 255)  # Count non-zero pixels
            })
    
    return img, dets, mask

def visualize(img: np.ndarray, dets: list[dict]) -> np.ndarray:
    """Create visualization overlay showing detections on the image.
    
    Draws colored segmentation masks, bounding boxes, and labels for each
    detected object. Uses different colors for different detections to
    distinguish multiple objects.
    
    Args:
        img: Input image (BGR format)
        dets: List of detection dictionaries from segment_image()
    
    Returns:
        Visualization image with overlays (BGR format)
    """
    # Create a copy to avoid modifying the original
    vis = img.copy()
    
    # Color palette for different detections (BGR format for OpenCV)
    # Colors cycle if more than 6 detections
    cols = [(0,0,255), (0,255,0), (255,0,0), (0,255,255), (255,0,255), (255,255,0)]
    
    # Draw each detection
    for i, d in enumerate(dets):
        # Select color (cycles through palette)
        col = cols[i % len(cols)]
        
        # Create colored overlay for the segmentation mask
        overlay = np.zeros_like(img)
        overlay[d["mask"] > 0] = col
        
        # Blend overlay with original image (70% original, 30% overlay)
        vis = cv2.addWeighted(vis, 0.7, overlay, 0.3, 0)
        
        # Draw bounding box
        x1, y1, x2, y2 = map(int, d["bbox"])
        cv2.rectangle(vis, (x1, y1), (x2, y2), col, 2)
        
        # Draw confidence label above bounding box
        lbl = f"cell: {d['conf']:.2f}"
        cv2.putText(vis, lbl, (x1+2, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    
    # Draw total detection count in top-left corner
    cv2.putText(vis, f"Detected: {len(dets)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)
    
    return vis

def process_folder(model, folder: Path, out_dir: Path, conf: float, iou: float) -> list[dict]:
    """Process all images in a folder with YOLO segmentation.
    
    Runs detection on all images in the specified folder, creates visualization
    overlays, and saves results to CSV. Each processed image gets a corresponding
    visualization file with _seg.jpg suffix.
    
    Args:
        model: YOLO model instance
        folder: Input folder containing images
        out_dir: Output directory for results
        conf: Confidence threshold for detection
        iou: IoU threshold for NMS
    
    Returns:
        List of detection result dictionaries, each containing:
            - image: Filename
            - num: Number of objects detected
            - area: Total pixel area of all detections
    """
    # Find all images in folder and subdirectories
    imgs = list_images(folder)
    if not imgs:
        print(f"No images in {folder.name}")
        return []
    
    print(f"Processing {len(imgs)} from {folder.name}...")
    
    # Create output subdirectory for visualization images
    out_sub = out_dir / "final_yolo_jpg_images"
    out_sub.mkdir(parents=True, exist_ok=True)
    
    # Process each image
    results = []
    for p in imgs:
        try:
            # Run segmentation inference
            img, dets, mask = segment_image(model, p, conf, iou)
            
            # Create visualization overlay
            vis = visualize(img, dets)
            
            # Save visualization with _seg suffix
            cv2.imwrite(str(out_sub / f"{p.stem}_seg.jpg"), vis)
            
            # Record statistics
            results.append({
                "image": p.name,
                "num": len(dets),
                "area": sum(d["area"] for d in dets)  # Total area across all detections
            })
            print(f"   {p.name}: {len(dets)} objects")
        except Exception as e:
            # Continue processing other images if one fails
            print(f"   {p.name}: {e}")
    
    # Write summary CSV with detection statistics
    with open(out_sub / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "num", "area"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Saved to: {out_sub}")
    return results

def main():
    """Main entry point for YOLO detection script.
    
    Parses command-line arguments, loads model weights, and processes
    image folders for object detection and segmentation.
    """
    # Parse command-line arguments
    p = argparse.ArgumentParser(description="YOLO segmentation detection with trained weights")
    p.add_argument("--weights", type=Path, 
                   help="Path to model weights (.pt file). Auto-detects latest best.pt if not specified.")
    p.add_argument("--input", type=Path, 
                   help="Direct path to input folder (absolute or relative). Overrides --folders.")
    p.add_argument("--folders", nargs="+", default=["jpg_images"],
                   help="Folder paths relative to src/data/output_images/")
    p.add_argument("--conf", type=float, default=0.25, 
                   help="Confidence threshold (0.0-1.0). Lower = more detections, higher = fewer but more confident.")
    p.add_argument("--iou", type=float, default=0.45, 
                   help="IoU threshold for NMS (0.0-1.0). Higher = allows more overlapping boxes.")
    p.add_argument("--output", type=Path, 
                   help="Output directory for results. Defaults to src/data/yolo_results/")
    args = p.parse_args()
    
    # Resolve repository paths
    repo, data_root, result_root = resolve_paths()
    
    # Find or use specified weights
    weights = args.weights or find_weights(repo)
    if not weights:
        print("No weights found. Use --weights")
        return
    
    print(f"Using: {weights}")
    
    # Load YOLO model
    model = load_model(weights)
    if not model:
        return
    
    # Set up output directory
    out = args.output or result_root
    out.mkdir(parents=True, exist_ok=True)
    print(f"Output: {out}")
    
    # Process input folders
    if args.input:
        # Direct path provided (absolute or relative)
        fp = Path(args.input)
        if fp.exists():
            print(f"Processing: {fp}")
            process_folder(model, fp, out, args.conf, args.iou)
        else:
            print(f"Input folder not found: {fp}")
    else:
        # Use relative folder paths from data_root
        for fn in args.folders:
            fp = data_root / fn
            if fp.exists():
                process_folder(model, fp, out, args.conf, args.iou)
            else:
                print(f"Not found: {fn}")
    
    print("\n Complete!")

if __name__ == "__main__":
    main()
