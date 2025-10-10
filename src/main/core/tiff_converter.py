"""
TIFF Converter Module

This module converts ND2 (Nikon Digital) microscopy files to TIFF format for the alfalfa segmentation pipeline.
It handles the conversion from ND2's proprietary format to standard TIFF, including proper channel ordering
(RGB conversion from BGR), data type normalization to 8-bit, and optional compression.

Key features:
- ND2 to TIFF format conversion
- Automatic channel reordering (BGR to RGB)
- Data normalization to 8-bit for compatibility
- Optional compression support
- Multi-frame handling (takes first frame)
"""

import nd2
import tifffile
import numpy as np
import os

def main() -> None:
    """Convert ND2 files to TIFF format"""
    # ---- SETTINGS (repo-relative paths) ----
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(os.path.dirname(current_dir))  # .../src
    data_dir = os.path.join(src_dir, "data")
    input_dir = os.path.join(data_dir, "nd2_images", "input_images")
    output_root = os.path.join(data_dir, "output_images")
    jpg_output_dir = os.path.join(output_root, "jpg_images")
    tiff_output_dir = os.path.join(output_root, "tiff_images")

    # Ensure input and output directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_root, exist_ok=True)
    os.makedirs(jpg_output_dir, exist_ok=True)
    os.makedirs(tiff_output_dir, exist_ok=True)

    # Gather all .nd2 files in the input directory
    nd2_candidates = [f for f in os.listdir(input_dir) if f.lower().endswith('.nd2')]
    if not nd2_candidates:
        raise FileNotFoundError(f"No .nd2 files found in '{input_dir}'. Please add ND2 files.")
    compression = None  # or "zlib" for smaller size

    for filename in nd2_candidates:
        nd2_path = os.path.join(input_dir, filename)
        base_name, _ = os.path.splitext(filename)
        tiff_path = os.path.join(tiff_output_dir, f"{base_name}.tiff")

        # ---- LOAD ND2 IMAGE ----
        data = nd2.imread(nd2_path)
        print(f"Original ND2 shape: {data.shape}, dtype: {data.dtype}")

        # ---- CONVERT TO 8-BIT FOR VIEWING ----
        # Scale all pixel values to 0-255
        data_8bit = (data / data.max() * 255).astype(np.uint8)

        # ---- HANDLE CHANNEL ORDER (Optional) ----
        # If the image has 3 channels, ensure it's RGB
        if data_8bit.ndim == 4:  # shape: (frames, height, width, channels)
            data_8bit = data_8bit[0]  # take first frame if multiple frames

        if data_8bit.shape[-1] == 3:
            # ND2 sometimes stores as BGR → convert to RGB
            data_8bit = data_8bit[..., ::-1]

        # ---- SAVE TIFF ----
        tifffile.imwrite(tiff_path, data_8bit, compression=compression)
        print(f"8-bit TIFF saved at {tiff_path}")
        print(f"File size: {os.path.getsize(tiff_path) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()