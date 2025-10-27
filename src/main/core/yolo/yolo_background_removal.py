"""YOLO-based background removal for segmented images.

Uses trained YOLO segmentation model to remove background and keep only detected objects.
Background is replaced with transparency (PNG) or white/black (JPG).
"""
from pathlib import Path
import argparse
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO


def resolve_paths():
    """Get repository root and default paths."""
    # File is at: <repo>/src/main/core/yolo/yolo_background_removal.py
    # Repo root = parents[4] (one extra level due to yolo/ subfolder)
    here = Path(__file__).resolve()
    repo = here.parents[4]
    return repo, repo / "src/data/output_images", repo / "src/data/yolo_results"


def find_best_weights(repo):
    """Find the latest best.pt from training runs."""
    candidates = []
    for runs in [repo / "src/data/yolo_results/runs/segment", repo / "src/train/runs/segment", repo / "runs/segment"]:
        if runs.exists():
            for run_dir in runs.iterdir():
                if run_dir.is_dir():
                    best = run_dir / "weights/best.pt"
                    if best.exists():
                        candidates.append(best)
    
    if not candidates:
        return None
    
    # Return the most recent best.pt
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_model(weights_path):
    """Load YOLO model from weights file."""
    if not weights_path.exists():
        raise FileNotFoundError(f"Weights not found: {weights_path}")
    
    print(f"Loading model from: {weights_path}")
    return YOLO(str(weights_path))


def list_images(folder):
    """Get all images from folder and subdirectories."""
    if not folder.exists():
        return []
    
    imgs = []
    # Direct images in folder
    imgs.extend(folder.glob("*.jpg"))
    imgs.extend(folder.glob("*.jpeg"))
    imgs.extend(folder.glob("*.png"))
    
    # Images in subdirectories
    for sub in folder.iterdir():
        if sub.is_dir():
            imgs.extend(sub.glob("*.jpg"))
            imgs.extend(sub.glob("*.jpeg"))
            imgs.extend(sub.glob("*.png"))
    
    return sorted(imgs)


def remove_background(model, img_path, conf=0.25, iou=0.45, keep_center_only=True):
    """
    Remove background from image using YOLO segmentation.
    Crops to just the detected object (not the full original image).
    
    Args:
        model: YOLO model
        img_path: Path to input image
        conf: Confidence threshold
        iou: IoU threshold for NMS
        keep_center_only: If True and multiple objects detected, keep only the one closest to center
    
    Returns:
        result_img_pil: PIL Image with background removed, CROPPED to object bounds (RGBA with transparency)
        num_objects: Number of detected objects
        kept_objects: Number of objects kept after filtering
    """
    img = cv2.imread(str(img_path))
    if img is None:
        raise ValueError(f"Failed to load {img_path}")
    
    # Run inference
    results = model(img, conf=conf, iou=iou, verbose=False)
    
    # Create combined mask for all detections
    combined_mask = np.zeros(img.shape[:2], dtype=np.uint8)
    num_objects = 0
    kept_objects = 0
    
    # Image center
    img_center_x = img.shape[1] / 2
    img_center_y = img.shape[0] / 2
    
    if results and results[0].masks and results[0].boxes:
        masks = results[0].masks.data.cpu().numpy()
        num_objects = len(masks)
        
        # If multiple objects and keep_center_only is True, select the one closest to center
        if keep_center_only and num_objects > 1:
            # Calculate distance from center for each mask
            mask_distances = []
            for mask in masks:
                mask_resized = cv2.resize(mask, (img.shape[1], img.shape[0]))
                mask_binary = (mask_resized > 0.5).astype(np.uint8)
                
                # Find centroid of mask
                moments = cv2.moments(mask_binary)
                if moments['m00'] != 0:
                    centroid_x = moments['m10'] / moments['m00']
                    centroid_y = moments['m01'] / moments['m00']
                else:
                    # Fallback to center of bounding box
                    coords = np.argwhere(mask_binary > 0)
                    if len(coords) > 0:
                        centroid_y = coords[:, 0].mean()
                        centroid_x = coords[:, 1].mean()
                    else:
                        centroid_x = img_center_x
                        centroid_y = img_center_y
                
                # Calculate Euclidean distance from image center
                distance = np.sqrt((centroid_x - img_center_x)**2 + (centroid_y - img_center_y)**2)
                mask_distances.append((distance, mask))
            
            # Sort by distance (closest first) and keep only the closest
            mask_distances.sort(key=lambda x: x[0])
            closest_mask = mask_distances[0][1]
            
            # Use only the closest mask
            mask_resized = cv2.resize(closest_mask, (img.shape[1], img.shape[0]))
            combined_mask = (mask_resized > 0.5).astype(np.uint8) * 255
            kept_objects = 1
        else:
            # Keep all masks
            for mask in masks:
                mask_resized = cv2.resize(mask, (img.shape[1], img.shape[0]))
                mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255
                combined_mask = cv2.bitwise_or(combined_mask, mask_binary)
            kept_objects = num_objects
    
    # Find bounding box of the mask to crop to just the object
    ys, xs = np.where(combined_mask > 0)
    
    if ys.size == 0 or xs.size == 0:
        # No object detected - return full image with transparency
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).convert("RGBA")
        return img_pil, num_objects, kept_objects
    
    # Get bounding box coordinates
    y_min, y_max = int(ys.min()), int(ys.max())
    x_min, x_max = int(xs.min()), int(xs.max())
    
    # Crop the original image and mask to this bounding box
    cropped_img = img[y_min:y_max+1, x_min:x_max+1]
    cropped_mask = combined_mask[y_min:y_max+1, x_min:x_max+1]
    
    # Convert to PIL Image with alpha channel (transparency)
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
    
    # Create RGBA image
    img_pil = Image.fromarray(img_rgb).convert("RGBA")
    
    # Apply mask as alpha channel
    alpha = Image.fromarray(cropped_mask)
    img_pil.putalpha(alpha)
    
    return img_pil, num_objects, kept_objects


def apply_square_white_background(img_pil, canvas_size=5000):
    """
    Centers image on a white square canvas.
    This is the EXACT logic from squareframe_batch.py.
    
    Args:
        img_pil: PIL Image in RGBA format
        canvas_size: Size of square canvas (default: 5000)
    
    Returns:
        PIL Image (RGB) with image centered on white square canvas
    """
    # Convert to RGBA if it's not already
    img = img_pil.convert("RGBA")
    
    # Determine the size for the square canvas
    max_dim = canvas_size
    
    # 1. Create a new white square image in 'RGB' mode
    # This will be used as the ultimate background.
    white_bg = Image.new('RGB', (max_dim, max_dim), (255, 255, 255))
    
    # 2. Create a temporary 'RGBA' canvas for pasting
    # We use 'RGBA' here to support the alpha channel of the input image
    # during the paste operation.
    canvas = Image.new('RGBA', (max_dim, max_dim), (255, 255, 255, 0))  # Fully transparent white
    
    # Calculate the offset to center the original image
    offset = ((max_dim - img.width) // 2, (max_dim - img.height) // 2)
    
    # 3. Paste the original image onto the transparent canvas
    # The 'img' parameter here is the mask, which tells paste()
    # how to handle transparency.
    canvas.paste(img, offset, img)
    
    # 4. Composite the transparent canvas over the solid white background
    # This step replaces the transparent areas of the canvas (which holds the centered image)
    # with the solid white color of white_bg.
    white_bg.paste(canvas, (0, 0), canvas)
    
    return white_bg


def process_folder(model, input_folder, output_dir, conf, iou, canvas_size, keep_center_only):
    """Process all images in folder with background removal and square canvas."""
    imgs = list_images(input_folder)
    
    if not imgs:
        print(f"No images found in {input_folder}")
        return
    
    print(f"\nProcessing {len(imgs)} images from {input_folder.name}...")
    print(f"Output canvas size: {canvas_size}x{canvas_size}")
    if keep_center_only:
        print("Mode: If multiple objects detected, keep only the one closest to center")
    
    # Create output directory
    out_sub = output_dir / "final_yolo_jpg_images"
    out_sub.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    total_objects_detected = 0
    total_objects_kept = 0
    multi_object_count = 0
    
    for img_path in imgs:
        try:
            # Step 1: Remove background using YOLO (returns PIL Image with transparency)
            img_no_bg, num_objects, kept_objects = remove_background(
                model, img_path, conf, iou, keep_center_only
            )
            
            # Step 2: Apply square white background (EXACT logic from squareframe_batch.py)
            final_img = apply_square_white_background(img_no_bg, canvas_size)
            
            # Save as JPG
            out_path = out_sub / f"{img_path.stem}_nobg.jpg"
            final_img.save(str(out_path), quality=95)
            
            # Print status
            if num_objects > 1 and keep_center_only:
                multi_object_count += 1
                print(f"  ✓ {img_path.name}: {num_objects} objects detected → kept center object")
            else:
                print(f"  ✓ {img_path.name}: {num_objects} object(s) detected")
            
            success_count += 1
            total_objects_detected += num_objects
            total_objects_kept += kept_objects
            
        except Exception as e:
            print(f"  ✗ {img_path.name}: Error - {e}")
    
    print(f"\nCompleted: {success_count}/{len(imgs)} images")
    print(f"Total objects detected: {total_objects_detected}")
    if keep_center_only and multi_object_count > 0:
        print(f"Images with multiple objects: {multi_object_count}")
        print(f"Objects kept after filtering: {total_objects_kept}")
    print(f"Output directory: {out_sub}")
    print(f"All images saved as {canvas_size}x{canvas_size} JPG")


def main():
    # ========== basic settings (input) ==========
    DEFAULT_INPUT = "jpg_images"  # input folder
    DEFAULT_CANVAS_SIZE = 5000  # output canvas size (all images will be 5000x5000)
    # ================================================
    
    parser = argparse.ArgumentParser(
        description="Remove background from images using YOLO segmentation"
    )
    
    # Model weights
    parser.add_argument(
        "--weights",
        type=Path,
        help="Path to model weights (.pt file). Auto-detects latest best.pt if not specified."
    )
    
    # Input/Output
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input folder path (absolute or relative to src/data/output_images/). Default: {DEFAULT_INPUT}"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory. Defaults to src/data/yolo_results/"
    )
    
    # Detection parameters
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold (default: 0.25)"
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.45,
        help="IoU threshold for NMS (default: 0.45)"
    )
    
    # Object selection option
    parser.add_argument(
        "--keep-center-only",
        action="store_true",
        default=True,
        help="If multiple objects detected, keep only the one closest to center (default: True)"
    )
    
    # Canvas size option
    parser.add_argument(
        "--canvas-size",
        type=int,
        default=DEFAULT_CANVAS_SIZE,
        help=f"Output canvas size in pixels (all images will be resized to this, default: {DEFAULT_CANVAS_SIZE}x{DEFAULT_CANVAS_SIZE})"
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    repo, data_root, result_root = resolve_paths()
    
    # Find or load weights
    if args.weights:
        weights_path = args.weights
        if not weights_path.is_absolute():
            weights_path = repo / weights_path
    else:
        weights_path = find_best_weights(repo)
        if weights_path is None:
            print("Error: No best.pt found in training runs.")
            print("Please specify weights with --weights or train a model first.")
            return
    
    # Load model
    try:
        model = load_model(weights_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Resolve input folder
    input_folder = args.input
    if not input_folder.is_absolute():
        # Try relative to data_root first
        candidate = data_root / input_folder
        if candidate.exists():
            input_folder = candidate
        else:
            # Try relative to current directory
            input_folder = Path.cwd() / input_folder
    
    if not input_folder.exists():
        print(f"Error: Input folder not found: {input_folder}")
        return
    
    # Resolve output directory
    output_dir = args.output if args.output else result_root
    if not output_dir.is_absolute():
        output_dir = repo / output_dir
    
    # Process images
    process_folder(
        model,
        input_folder,
        output_dir,
        args.conf,
        args.iou,
        args.canvas_size,
        args.keep_center_only
    )
    
    print("\n✓ Background removal complete!")


if __name__ == "__main__":
    main()
