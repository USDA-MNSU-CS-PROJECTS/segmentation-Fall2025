from __future__ import annotations

"""Lignin (red-region) detector for JPG images.

This script detects red (lignin) regions in images and calculates their ratio.
Modify the settings below to analyze your desired folder of images.

=== User Configuration ============================================
"""

# === Input Settings =============================================
# Process mode: 'single' or 'batch'
# - 'single': Process one folder specified in SINGLE_INPUT_FOLDER
# - 'batch': Process all folders in BATCH_INPUT_FOLDERS list
PROCESS_MODE = 'batch'  # Change to 'single' to process only one folder

# Single folder input (used when PROCESS_MODE = 'single')
SINGLE_INPUT_FOLDER = "src/data/yolo_results/final_yolo_jpg_images"

# Batch folders input (used when PROCESS_MODE = 'batch')
BATCH_INPUT_FOLDERS = [
    "src/data/yolo_results/final_yolo_jpg_images",
]

# === Output Settings ============================================
# Base output directory for results and visualizations
OUTPUT_FOLDER = "src/data/detector_results/lignin_detector_results"

"""=== Code Start (do not modify below) ========================="""
import argparse
import csv
import os
from pathlib import Path
from typing import Iterable, List, Tuple

import cv2
import numpy as np
from ultralytics import YOLO

# HSV color range settings for lignin (red) detection
# More conservative ranges to reduce false positive detection
HSV_RANGES = {
    # Deep red / burgundy
    'deep_red_lower': [0, 135, 40],
    'deep_red_upper': [10, 255, 255],
    'deep_red_lower2': [170, 135, 40],
    'deep_red_upper2': [180, 255, 255],

    # Reddish-brown with slight red extension (for #c4716d)
    'brown_lower': [4, 90, 60],
    'brown_upper': [17, 255, 210],
    'brown_lower2': [160, 90, 60],
    'brown_upper2': [176, 255, 210]
}

# Fallback constant pixel-to-micron conversion (used if ND2 measurements not available)
PIXEL_TO_MICRON_FALLBACK = 0.9785316641067333

def load_nd2_measurements(repo_root: Path) -> dict:
    """Load ND2 measurements CSV and create lookup dictionary.
    
    Returns:
        Dictionary mapping base image names to pixel_microns values
    """
    measurements_csv = repo_root / "src/data/detector_results/nd2_micron_measurements.csv"
    lookup = {}
    
    if not measurements_csv.exists():
        return lookup
    
    try:
        with measurements_csv.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_name = row.get('image_name', '')
                pixel_microns = row.get('pixel_microns', '')
                
                if image_name and pixel_microns:
                    try:
                        # Extract base name (remove .nd2 and suffixes like _burned_recent)
                        base_name = image_name.replace('.nd2', '').split('_burned')[0].split('_recent')[0]
                        # Remove any remaining .nd2 extensions
                        base_name = base_name.replace('.nd2', '')
                        lookup[base_name] = float(pixel_microns)
                    except (ValueError, AttributeError):
                        continue
    except Exception as e:
        print(f"Warning: Could not load ND2 measurements: {e}")
    
    return lookup


def get_pixel_microns(filename: str, nd2_lookup: dict, repo_root: Path) -> float:
    """Get pixel-to-micron conversion factor for an image.
    
    Args:
        filename: Image filename (e.g., '20240780a_T0_10xstitch_PG_nobg.jpg')
        nd2_lookup: Dictionary from load_nd2_measurements()
        repo_root: Repository root path
        
    Returns:
        Pixel-to-micron conversion factor
    """
    # Extract base name from JPG filename
    # Remove extension and common suffixes
    base_name = filename.replace('.jpg', '').replace('.jpeg', '').replace('_nobg', '')
    
    # Try exact match first
    if base_name in nd2_lookup:
        return nd2_lookup[base_name]
    
    # Try matching without some suffixes that might differ
    # Remove _removed, _detected, etc.
    base_name_clean = base_name.split('_removed')[0].split('_detected')[0]
    if base_name_clean in nd2_lookup:
        return nd2_lookup[base_name_clean]
    
    # Try partial matching (match beginning of name)
    for nd2_name, pixel_microns in nd2_lookup.items():
        if base_name.startswith(nd2_name) or nd2_name.startswith(base_name):
            return pixel_microns
    
    # Fallback to constant
    return PIXEL_TO_MICRON_FALLBACK


def list_jpg_files(folder: Path) -> List[Path]:
    """Return list of PG-stained jpg/jpeg files in folder (non-recursive)."""
    if not folder.exists():
        raise FileNotFoundError(f"Input folder not found: {folder}")
    # Filter for PG-stained images only (lignin detection)
    files = [p for p in folder.iterdir() 
             if p.suffix.lower() in {'.jpg', '.jpeg'} and '_PG_' in p.name and '_nobg' in p.name]
    files.sort()
    return files


def find_best_weights(repo_root: Path) -> Path:
    """Find the latest best.pt from training runs."""
    candidates = []
    for runs in [repo_root / "src/data/yolo_results/runs/segment", repo_root / "src/train/runs/segment", repo_root / "runs/segment"]:
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


def detect_cell_mask(model: YOLO, image: np.ndarray, conf: float = 0.25) -> Tuple[np.ndarray, int]:
    """Detect cell using YOLO and return binary mask of cell region.
    
    Args:
        model: YOLO segmentation model
        image: Input image (BGR format)
        conf: Confidence threshold
        
    Returns:
        Tuple of:
        - Binary mask (0 or 255) where 255 indicates cell region
        - Number of detected objects
    """
    # Run YOLO inference
    results = model(image, conf=conf, verbose=False)
    
    # Create empty mask
    cell_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    num_objects = 0
    
    if results and results[0].masks:
        masks = results[0].masks.data.cpu().numpy()
        num_objects = len(masks)
        
        # Combine all detected cell masks
        for mask in masks:
            mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))
            mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255
            cell_mask = cv2.bitwise_or(cell_mask, mask_binary)
    
    return cell_mask, num_objects


def estimate_cell_mask_nonwhite(image: np.ndarray) -> Tuple[np.ndarray, int]:
    """Estimate cell mask assuming white background output from background-removal.

    Heuristic:
    - Treat near-white pixels as background (low saturation & high value in HSV)
    - Invert to get non-white regions
    - Keep the largest connected component near the center

    Returns a binary mask and a pseudo count (1 if a component found else 0).
    """
    h, w = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # White background threshold in HSV: low S, high V
    low_white = np.array([0, 0, 220], dtype=np.uint8)
    high_white = np.array([180, 50, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, low_white, high_white)

    # Non-white mask
    nonwhite = cv2.bitwise_not(white_mask)

    # Morphological cleanup
    k = max(3, min(h, w) // 200)  # scale kernel with image size
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k | 1, k | 1))
    nonwhite = cv2.morphologyEx(nonwhite, cv2.MORPH_OPEN, kernel)
    nonwhite = cv2.morphologyEx(nonwhite, cv2.MORPH_CLOSE, kernel)

    # Connected components to keep largest component near center
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(nonwhite, connectivity=8)
    if num_labels <= 1:
        return np.zeros((h, w), dtype=np.uint8), 0

    # Ignore label 0 (background)
    areas = stats[1:, cv2.CC_STAT_AREA]
    centers = centroids[1:]
    # Prefer largest area, but if multiple, bias to closest to image center
    img_center = np.array([w / 2.0, h / 2.0])
    dists = np.linalg.norm(centers - img_center, axis=1)

    # Score = area - lambda * distance; choose best
    # Use lambda proportional to image size to avoid dominating area
    lam = max(h, w)  # pixels
    scores = areas - 0.5 * lam * (dists / lam)  # simplified
    best_idx = int(np.argmax(scores)) + 1  # shift due to background index

    cell_mask = (labels == best_idx).astype(np.uint8) * 255
    return cell_mask, 1


def detect_red_ratio(image: np.ndarray, cell_mask: np.ndarray = None, pixel_microns: float = None, debug: bool = False) -> Tuple[int, int, int, np.ndarray, np.ndarray]:
    """Detect red pixels in BGR image within cell region and return statistics.

    Uses HSV color space with two ranges for red.
    
    Args:
        image: Input image (BGR format)
        cell_mask: Binary mask of cell region (optional). If None, uses entire image.
        pixel_microns: Pixel-to-micron conversion factor (optional). If None, uses fallback.
        debug: Enable debug prints
        
    Returns:
        Tuple containing:
        - red_count: Number of red pixels detected in cell region
        - cell_pixels: Total number of pixels in cell region
        - total_pixels: Total number of pixels in entire image
        - lignin_mask: Binary mask of detected lignin regions
        - visualization: Image with cell and lignin regions highlighted
    """
    if image is None:
        raise ValueError("image is None")
    
    # convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    deep_red_lower1 = np.array(HSV_RANGES['deep_red_lower'])
    deep_red_upper1 = np.array(HSV_RANGES['deep_red_upper'])
    deep_red_lower2 = np.array(HSV_RANGES['deep_red_lower2'])
    deep_red_upper2 = np.array(HSV_RANGES['deep_red_upper2'])
    
    # Reddish brown/orange-brown detection (cell wall structures)
    brown_lower1 = np.array(HSV_RANGES['brown_lower'])
    brown_upper1 = np.array(HSV_RANGES['brown_upper'])
    brown_lower2 = np.array(HSV_RANGES['brown_lower2'])
    brown_upper2 = np.array(HSV_RANGES['brown_upper2'])
    
    # Create masks for deep red ranges
    deep_red_mask1 = cv2.inRange(hsv, deep_red_lower1, deep_red_upper1)
    deep_red_mask2 = cv2.inRange(hsv, deep_red_lower2, deep_red_upper2)
    deep_red_mask = cv2.bitwise_or(deep_red_mask1, deep_red_mask2)
    
    # Create masks for brown ranges
    brown_mask1 = cv2.inRange(hsv, brown_lower1, brown_upper1)
    brown_mask2 = cv2.inRange(hsv, brown_lower2, brown_upper2)
    brown_mask = cv2.bitwise_or(brown_mask1, brown_mask2)
    
    # Combine all pectin-related regions
    lignin_mask = cv2.bitwise_or(deep_red_mask, brown_mask)

    # Optional morphological cleaning to remove small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    lignin_mask = cv2.morphologyEx(lignin_mask, cv2.MORPH_OPEN, kernel)
    lignin_mask = cv2.morphologyEx(lignin_mask, cv2.MORPH_CLOSE, kernel)

    # If cell mask is provided, only count lignin within cell region
    if cell_mask is not None:
        # Apply cell mask to lignin mask
        lignin_in_cell = cv2.bitwise_and(lignin_mask, cell_mask)
        red_count = int(np.count_nonzero(lignin_in_cell))
        cell_pixels = int(np.count_nonzero(cell_mask))
    else:
        # No cell mask - use entire image
        lignin_in_cell = lignin_mask
        red_count = int(np.count_nonzero(lignin_mask))
        cell_pixels = int(lignin_mask.shape[0] * lignin_mask.shape[1])
    
    total_pixels = int(lignin_mask.shape[0] * lignin_mask.shape[1])

    # Convert pixels to square microns if conversion factor is provided
    if pixel_microns is None:
        pixel_microns = PIXEL_TO_MICRON_FALLBACK
    
    # Convert pixel counts to square microns (area conversion: pixels * (microns/pixel)^2)
    red_square_microns = red_count * (pixel_microns ** 2)
    cell_square_microns = cell_pixels * (pixel_microns ** 2)
    total_square_microns = total_pixels * (pixel_microns ** 2)
    
    # Convert square microns to square millimeters (1 micron = 0.001 mm, so 1 um^2 = 0.000001 mm^2)
    red_square_mm = red_square_microns * 0.000001
    cell_square_mm = cell_square_microns * 0.000001
    total_square_mm = total_square_microns * 0.000001

    # Create visualization
    vis_img = image.copy()
    
    # Show cell boundary in green if mask exists
    if cell_mask is not None:
        cell_contours, _ = cv2.findContours(cell_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(vis_img, cell_contours, -1, (0, 255, 0), 3)  # Green boundary
    
    # Create blue overlay for detected lignin regions
    overlay = np.zeros_like(image)
    overlay[lignin_in_cell > 0] = [255, 0, 0]  # BGR format - pure blue
    
    # Blend original image with blue overlay
    alpha = 0.5  # Transparency factor
    vis_img = cv2.addWeighted(vis_img, 1, overlay, alpha, 0)
    
    # Add text with detection results (show pixels, microns, and millimeters)
    if cell_pixels > 0:
        ratio = red_count / cell_pixels
        text1 = f"Lignin in cross section: {ratio:.2%}"
        text3 = f"Cross section area: {cell_square_microns:,.0f} um^2 ({cell_square_mm:.6f} mm^2) ({cell_pixels:,} px)"
        text4 = f"Lignin area in cross section: {red_square_microns:,.0f} um^2 ({red_square_mm:.6f} mm^2) ({red_count:,} px)"
    else:
        ratio = 0.0
        text1 = "No cross section detected"
        text3 = ""
        text4 = ""
    
    # Make text smaller and positioned higher with white outline for better visibility
    # Dynamically scale font based on image size (works well for 5000x5000 canvas)
    h, w = vis_img.shape[:2]
    base_scale = max(2.5, min(h, w) / 2000.0)  # ~2.5 for 5000px (smaller than before)
    font_scale_main = base_scale
    font_scale_sub = base_scale * 0.75  # Slightly smaller sub text
    thickness = max(4, int(base_scale * 1.5))  # Thinner for smaller text

    # Helper function to draw text with outline (bold)
    def draw_text_with_outline(img, text, pos, scale, color, thick):
        if not text:
            return
        # White outline (thicker for bold effect)
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), thick + 3, cv2.LINE_AA)
        # Black text (bold)
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)

    # Compute dynamic positions (moved up and left)
    x = int(30 * base_scale)  # Moved left (was 50)
    y = int(60 * base_scale)  # Moved up significantly (was 120)
    step = int(65 * base_scale)  # Tighter spacing (was 90)

    draw_text_with_outline(vis_img, text1, (x, y), font_scale_main, (0, 0, 0), thickness)
    y += step
    draw_text_with_outline(vis_img, text3, (x, y), font_scale_sub, (0, 0, 0), thickness)
    y += step
    draw_text_with_outline(vis_img, text4, (x, y), font_scale_sub, (0, 0, 0), thickness)

    if debug:
        print(f"red_count={red_count}, cell_pixels={cell_pixels}, total_pixels={total_pixels}, ratio={ratio:.6f}")
        print(f"red_square_microns={red_square_microns:.2f}, cell_square_microns={cell_square_microns:.2f}, pixel_microns={pixel_microns}")

    return red_count, cell_pixels, total_pixels, lignin_in_cell, vis_img


def extract_metadata_from_filename(filename: str, imageset: str) -> dict:
    """Extract metadata from image filename following the naming convention.
    
    Args:
        filename: Image filename (e.g., '20240780a_T0_10xstitch_PG.jpg')
        imageset: ImageSet name (e.g., '20240630-20240644_10xstitch_PG')
    
    Returns:
        Dictionary with metadata fields
    """
    import re
    
    # Remove file extension
    name = filename.rsplit('.', 1)[0]
    
    # Initialize metadata
    metadata = {
        'Project': 'DASS',
        'ImageSet': imageset,
        'Location': '',
        'Maturity': '',
        'AlfalfaLine': '',
        'ImageID': name,  # Full filename without extension
        'Year': '',
        'LabID': '',
        'CrossSection': '',
        'IncubationTime_Hr': '',
        'ImageType': '',
        'Stain': ''
    }
    
    # Extract Stain (last 2 characters before extension)
    if len(name) >= 2:
        metadata['Stain'] = name[-2:]
    
    # Check if STANDARD or numeric
    if name.startswith('STANDARD'):
        metadata['Location'] = 'control'
        metadata['Maturity'] = 'control'
        metadata['AlfalfaLine'] = 'control'
        metadata['LabID'] = 'STANDARD'
        
        # Extract from STANDARD pattern: STANDARD_20240780-20240794d_T0_10xstitch_PG
        # or: STANDARD20240780a_T0_10xstitch_PG
        match = re.search(r'STANDARD[_-]?(\d{4})(\d{4})([a-z]?).*?_T(\d+)_([^_]+)_', name + '_')
        if match:
            metadata['Year'] = match.group(1)
            metadata['CrossSection'] = match.group(3) if match.group(3) else ''
            metadata['IncubationTime_Hr'] = match.group(4)
            metadata['ImageType'] = match.group(5)
    
    elif name[0].isdigit():
        # Numeric pattern: 20240780a_T0_10xstitch_PG
        metadata['Location'] = 'STP'
        metadata['Maturity'] = 'EF'
        
        # Extract: YEAR(4) + 4-digit-ID + CrossSection(1) + _T + Time + _ + ImageType + _ + Stain
        match = re.match(r'(\d{4})(\d{4})([a-z]?).*?_T(\d+)_([^_]+)_', name + '_')
        if match:
            year = match.group(1)
            four_digit = match.group(2)
            cross_section = match.group(3)
            incubation_time = match.group(4)
            image_type = match.group(5)
            
            metadata['Year'] = year
            metadata['LabID'] = year + four_digit  # 8 digits
            metadata['CrossSection'] = cross_section if cross_section else ''
            metadata['IncubationTime_Hr'] = incubation_time
            metadata['ImageType'] = image_type
            
            # AlfalfaLine based on 4-digit modulo 5
            four_digit_int = int(four_digit)
            remainder = four_digit_int % 5
            if remainder == 0:
                metadata['AlfalfaLine'] = 'Megatron'
            elif remainder == 1:
                metadata['AlfalfaLine'] = '4351'
            elif remainder == 2:
                metadata['AlfalfaLine'] = '54Q32'
            elif remainder == 3:
                metadata['AlfalfaLine'] = '4016'
            elif remainder == 4:
                metadata['AlfalfaLine'] = '55v12'
    
    return metadata


def process_folder_with_vis(input_folder: Path, yolo_model: YOLO, vis_dir: Path, conf: float = 0.25, mask_mode: str = 'auto', debug: bool = False, repo_root: Path = None) -> list:
    """Process folder with custom visualization directory.
    
    This is a wrapper that sets up vis_dir and calls the main process_folder logic.
    """
    files = list_jpg_files(input_folder)
    if not files:
        print(f"No jpg files found in {input_folder}")
        return []

    # Create output directory for visualizations
    vis_dir.mkdir(parents=True, exist_ok=True)

    # Load ND2 measurements for pixel-to-micron conversion
    if repo_root is None:
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent.parent.parent.parent
    nd2_lookup = load_nd2_measurements(repo_root)
    
    # Inform user if using fallback conversion
    if not nd2_lookup:
        print(f"Note: ND2 measurements CSV not found. Using fallback pixel-to-micron conversion: {PIXEL_TO_MICRON_FALLBACK} µm/pixel")
    else:
        print(f"Loaded {len(nd2_lookup)} ND2 measurement(s) for pixel-to-micron conversion")

    results = []
    no_cell_count = 0
    total_files = len(files)
    
    print(f"\nProcessing {total_files} images...")
    print("-" * 80)
    
    for idx, p in enumerate(files, 1):
        if debug:
            print(f"[{idx}/{total_files}] Processing {p.name}")
        else:
            # Show progress every 10 images or at the end
            if idx % 10 == 0 or idx == total_files:
                print(f"Progress: {idx}/{total_files} ({idx/total_files*100:.1f}%)")
        
        try:
            img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                print(f"  Warning: failed to read image {p}")
                continue
            
            # Step 1: Build cell region mask (YOLO or non-white heuristic)
            chosen_mode = mask_mode
            if mask_mode == 'auto':
                # Heuristic: if folder looks like background-removed or white bg dominates, use nonwhite
                folder_str = str(input_folder).replace('\\', '/').lower()
                if 'background_removed' in folder_str:
                    chosen_mode = 'nonwhite'
                else:
                    # Quick white background ratio check
                    hsv_tmp = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    low_white = np.array([0, 0, 220], dtype=np.uint8)
                    high_white = np.array([180, 50, 255], dtype=np.uint8)
                    white_mask_tmp = cv2.inRange(hsv_tmp, low_white, high_white)
                    white_ratio = np.count_nonzero(white_mask_tmp) / white_mask_tmp.size
                    chosen_mode = 'nonwhite' if white_ratio > 0.6 else 'yolo'

            if chosen_mode == 'nonwhite':
                cell_mask, _ = estimate_cell_mask_nonwhite(img)
            else:
                cell_mask, _ = detect_cell_mask(yolo_model, img, conf=conf)
            
            # Track images with no cell detected
            if np.count_nonzero(cell_mask) == 0:
                no_cell_count += 1
                if debug:
                    print(f"  Warning: No cell detected in {p.name}")
            
            # Get pixel-to-micron conversion factor for this image
            pixel_microns = get_pixel_microns(p.name, nd2_lookup, repo_root)
            
            # Step 2: Detect lignin within cell region
            red_count, cell_pixels, total_pixels, lignin_mask, vis_img = detect_red_ratio(
                img, cell_mask, pixel_microns=pixel_microns, debug=debug
            )
            
            # Calculate ratio based on cell area (not entire image)
            ratio = red_count / cell_pixels if cell_pixels > 0 else 0.0
            
            # Convert to square microns
            red_square_microns = red_count * (pixel_microns ** 2)
            cell_square_microns = cell_pixels * (pixel_microns ** 2)
            total_square_microns = total_pixels * (pixel_microns ** 2)
            
            # Convert square microns to square millimeters (1 micron = 0.001 mm, so 1 um^2 = 0.000001 mm^2)
            red_square_mm = red_square_microns * 0.000001
            cell_square_mm = cell_square_microns * 0.000001
            total_square_mm = total_square_microns * 0.000001
            
            # Extract metadata from filename
            imageset = input_folder.name  # e.g., '20240630-20240644_10xstitch_PG'
            metadata = extract_metadata_from_filename(p.name, imageset)
            
            results.append((p.name, red_count, cell_pixels, total_pixels, ratio, metadata, 
                          red_square_microns, cell_square_microns, total_square_microns, pixel_microns,
                          red_square_mm, cell_square_mm, total_square_mm))

            # Save visualization
            vis_path = vis_dir / f"{p.stem}_detected.jpg"
            cv2.imwrite(str(vis_path), vis_img)
            if debug:
                print(f"  Saved visualization to {vis_path}")
                
        except Exception as e:
            print(f"  Error processing {p.name}: {e}")
            if debug:
                import traceback
                traceback.print_exc()

    print("-" * 80)
    
    # Calculate statistics
    if results:
        ratios = [r[4] for r in results if r[2] > 0]  # Only include images with detected cells
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            min_ratio = min(ratios)
            max_ratio = max(ratios)
            
            print(f"\n=== Statistics ===")
            print(f"Total images processed: {len(results)}")
            print(f"Images with cells: {len(ratios)}")
            print(f"Images without cells: {no_cell_count}")
            print(f"Average Lignin ratio: {avg_ratio:.2%}")
            print(f"Min Lignin ratio: {min_ratio:.2%}")
            print(f"Max Lignin ratio: {max_ratio:.2%}")
            print()

    # Return results for aggregation
    return results


def write_combined_csv(all_results: list, output_csv: Path) -> None:
    """Write combined results from multiple folders to a single CSV file."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Header row with all metadata fields
        writer.writerow([
            'Project', 'ImageSet', 'Location', 'Maturity', 'AlfalfaLine', 'ImageID', 'Year', 
            'LabID', 'CrossSection', 'IncubationTime_Hr', 'ImageType', 'Stain',
            'filename', 'lignin_pixel_count', 'cell_pixel_count', 'total_pixel_count', 
            'lignin_ratio_in_cell', 'Percentage of Lignin',
            'lignin_area_square_microns', 'cell_area_square_microns', 'total_area_square_microns',
            'lignin_area_square_mm', 'cell_area_square_mm', 'total_area_square_mm',
            'pixel_to_micron_conversion'
        ])
        
        # Data rows
        for row in all_results:
            if len(row) == 13:
                # New format with micron and millimeter measurements
                filename, red_count, cell_pixels, total_pixels, ratio, metadata, red_square_microns, cell_square_microns, total_square_microns, pixel_microns, red_square_mm, cell_square_mm, total_square_mm = row
            elif len(row) == 10:
                # Format with micron measurements only (convert to mm)
                filename, red_count, cell_pixels, total_pixels, ratio, metadata, red_square_microns, cell_square_microns, total_square_microns, pixel_microns = row
                red_square_mm = red_square_microns * 0.000001
                cell_square_mm = cell_square_microns * 0.000001
                total_square_mm = total_square_microns * 0.000001
            else:
                # Legacy format (for backward compatibility)
                filename, red_count, cell_pixels, total_pixels, ratio, metadata = row
                pixel_microns = PIXEL_TO_MICRON_FALLBACK
                red_square_microns = red_count * (pixel_microns ** 2)
                cell_square_microns = cell_pixels * (pixel_microns ** 2)
                total_square_microns = total_pixels * (pixel_microns ** 2)
                red_square_mm = red_square_microns * 0.000001
                cell_square_mm = cell_square_microns * 0.000001
                total_square_mm = total_square_microns * 0.000001
            
            writer.writerow([
                metadata['Project'],
                metadata['ImageSet'],
                metadata['Location'],
                metadata['Maturity'],
                metadata['AlfalfaLine'],
                metadata['ImageID'],
                metadata['Year'],
                metadata['LabID'],
                metadata['CrossSection'],
                metadata['IncubationTime_Hr'],
                metadata['ImageType'],
                metadata['Stain'],
                filename,
                red_count,
                cell_pixels,
                total_pixels,
                f"{ratio:.6f}",
                f"{ratio:.2%}",
                f"{red_square_microns:.2f}",
                f"{cell_square_microns:.2f}",
                f"{total_square_microns:.2f}",
                f"{red_square_mm:.6f}",
                f"{cell_square_mm:.6f}",
                f"{total_square_mm:.6f}",
                f"{pixel_microns:.10f}"
            ])

    print(f"\n✓ Wrote combined results for {len(all_results)} images to {output_csv}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Detect red (lignin) area in cell regions using YOLO + color detection')
    p.add_argument('--input', '-i', help='Input folder with JPG files (only for single folder mode)')
    p.add_argument('--output', '-o', help='Output CSV file path (optional, default: OUTPUT_FOLDER/combined_lignin_results.csv)')
    p.add_argument('--weights', '-w', help='Path to YOLO weights (optional, auto-detects best.pt if not specified)')
    p.add_argument('--conf', type=float, default=0.25, help='YOLO confidence threshold (default: 0.25)')
    p.add_argument('--mask-mode', choices=['auto', 'yolo', 'nonwhite'], default='auto',
                   help='How to build cell mask: yolo (model), nonwhite (white-background heuristic), or auto (default)')
    p.add_argument('--batch', action='store_true', help='Process multiple folders in batch mode and combine into single CSV')
    p.add_argument('--debug', action='store_true', help='Enable debug prints')
    return p.parse_args()


def main():
    """Main function to run lignin detection"""
    try:
        # Handle command line arguments
        args = parse_args()
        
        # Find repository root (4 levels up from this script)
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent.parent.parent.parent
        
        # Determine mode: CLI arguments override code settings
        if args.batch:
            mode = 'batch'
        elif args.input:
            mode = 'single'
        else:
            # Use code configuration
            mode = PROCESS_MODE
        
        # Load YOLO model
        if args.weights:
            weights_path = Path(args.weights)
            if not weights_path.is_absolute():
                weights_path = repo_root / weights_path
        else:
            weights_path = find_best_weights(repo_root)
            if weights_path is None:
                print("Error: No best.pt found in training runs.")
                print("Please specify weights with --weights or train a model first.")
                exit(1)
        
        print(f"Loading YOLO model from: {weights_path}")
        yolo_model = YOLO(str(weights_path))
        
        # Batch mode: process multiple folders and combine results
        if mode == 'batch':
            # Get folder list from CLI arg or code configuration
            if args.input:
                # If --input is provided with --batch, treat it as single folder in batch mode
                batch_folders = [Path(args.input)]
            else:
                # Use configured batch folders
                batch_folders = [Path(folder) for folder in BATCH_INPUT_FOLDERS]
            
            # Output paths
            output_folder = Path(OUTPUT_FOLDER) if not args.output else Path(args.output).parent
            output_csv = Path(args.output) if args.output else (output_folder / "combined_lignin_results.csv")
            vis_base_dir = output_folder / "visualizations"
            
            print(f"\n{'#'*80}")
            print(f"# BATCH MODE: Processing {len(batch_folders)} folder(s)")
            print(f"# Combined output will be saved to: {output_csv}")
            print(f"{'#'*80}")
            
            all_results = []
            for idx, folder in enumerate(batch_folders, 1):
                if not folder.exists():
                    print(f"\n[{idx}/{len(batch_folders)}] Warning: Folder not found, skipping: {folder}")
                    continue
                
                print(f"\n[{idx}/{len(batch_folders)}] Processing folder: {folder.name}")
                
                # Create visualization directory for this folder
                vis_dir = vis_base_dir / folder.name
                
                # Process folder and collect results
                folder_results = process_folder_with_vis(
                    folder, yolo_model, vis_dir, 
                    conf=args.conf, mask_mode=args.mask_mode, debug=args.debug, repo_root=repo_root
                )
                all_results.extend(folder_results)
            
            # Write combined CSV
            write_combined_csv(all_results, output_csv)
            
            print(f"\n{'#'*80}")
            print(f"# BATCH PROCESSING COMPLETE")
            print(f"# Total images processed: {len(all_results)}")
            print(f"{'#'*80}\n")
        
        # Single folder mode
        else:
            # Get input folder from CLI arg or code configuration
            if args.input:
                input_folder = Path(args.input)
            else:
                input_folder = Path(SINGLE_INPUT_FOLDER)
            
            if not input_folder.exists():
                print(f"Error: Input folder not found: {input_folder}")
                exit(1)
            output_csv = Path(args.output) if args.output else (Path(OUTPUT_FOLDER) / input_folder.name / "lignin_results.csv")
            vis_dir = output_csv.parent / "visualizations"
            
            print(f"Processing single folder: {input_folder}")
            print(f"Output CSV: {output_csv}")
            
            # Process folder
            results = process_folder_with_vis(
                input_folder, yolo_model, vis_dir,
                conf=args.conf, mask_mode=args.mask_mode, debug=args.debug, repo_root=repo_root
            )
            
            # Write CSV
            write_combined_csv(results, output_csv)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
