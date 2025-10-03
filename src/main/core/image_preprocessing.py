from rembg import remove
from PIL import Image
import os
import numpy as np
import cv2

# Simple knobs to adjust behavior
EXPANSION_PIXELS = 25  # how much to grow the mask with dilation
CROP_MARGIN = 100      # extra pixels around the grown mask when cropping

def main() -> None:
    # Resolve repo-relative paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(os.path.dirname(current_dir))  # .../src
    data_dir = os.path.join(src_dir, "data")
    input_dir = os.path.join(data_dir, "nd2_images", "input_images")
    output_root = os.path.join(data_dir, "main_images", "output_images")
    tiff_dir = os.path.join(output_root, "tiff_images")
    jpg_dir = os.path.join(output_root, "jpg_images")
    preprocessed_dir = os.path.join(output_root, "preprocessed_images")

    # Ensure input and output directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_root, exist_ok=True)
    os.makedirs(tiff_dir, exist_ok=True)
    os.makedirs(jpg_dir, exist_ok=True)
    os.makedirs(preprocessed_dir, exist_ok=True)

    # Collect all TIFFs to preprocess
    tiff_candidates = [f for f in os.listdir(tiff_dir) if f.lower().endswith((".tiff", ".tif"))]
    if not tiff_candidates:
        raise FileNotFoundError(
            f"No TIFF files found in '{tiff_dir}'. Run tiff_converter first or add a TIFF."
        )

    for filename in tiff_candidates:
        input_path = os.path.join(tiff_dir, filename)
        base_name, _ = os.path.splitext(filename)
        output_path = os.path.join(preprocessed_dir, f"{base_name}_removed.png")

        # Open input image
        try:
            input_image = Image.open(input_path).convert("RGB")  # convert to RGB
        except FileNotFoundError:
            print(f"Error: Input image '{input_path}' not found.")
            raise

        # Remove background
        print(f"Removing background for: {filename} ...")
        output_image = remove(input_image)

        # Make the cutout a bit bigger by growing the mask and cropping to it
        # We keep ORIGINAL image pixels inside that crop
        result_rgba = output_image.convert("RGBA")
        result_array = np.array(result_rgba)
        alpha = result_array[:, :, 3].astype(np.uint8)

        # 1) Binarize alpha so we have a clear foreground mask
        base_mask = (alpha > 0).astype(np.uint8) * 255

        # 2) Dilate to expand the foreground region outward
        kernel_size = (EXPANSION_PIXELS * 2 + 1, EXPANSION_PIXELS * 2 + 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
        expanded_mask = cv2.dilate(base_mask, kernel, iterations=1)

        # 3) Optional slight blur to soften edges (avoids blocky/pixely outline)
        expanded_alpha = cv2.GaussianBlur(expanded_mask, (5, 5), 0)

        # Find bounding box of the expanded subject
        ys, xs = np.where(expanded_alpha > 0)
        if ys.size == 0 or xs.size == 0:
            # Nothing detected; just save original removal result
            output_image.save(output_path)
            print(f"Background removed successfully. Output saved to: {output_path}")
            continue

        y_min, y_max = int(ys.min()), int(ys.max())
        x_min, x_max = int(xs.min()), int(xs.max())

        # Add a simple uniform margin around the box
        margin = CROP_MARGIN
        img_h, img_w = expanded_alpha.shape
        y_min = max(0, y_min - margin)
        y_max = min(img_h - 1, y_max + margin)
        x_min = max(0, x_min - margin)
        x_max = min(img_w - 1, x_max + margin)

        # Crop ORIGINAL RGB and expanded alpha to this box
        original_rgb = np.array(input_image.convert("RGB"))
        crop_rgb = original_rgb[y_min:y_max + 1, x_min:x_max + 1, :]
        crop_alpha = expanded_alpha[y_min:y_max + 1, x_min:x_max + 1]

        # Stack to RGBA and save
        crop_rgba = np.dstack([crop_rgb, crop_alpha])
        output_image = Image.fromarray(crop_rgba, mode="RGBA")

        # Save result
        output_image.save(output_path)

        print(f"Background removed successfully. Output saved to: {output_path}")

if __name__ == "__main__":
    main()
