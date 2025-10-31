"""
JPG Converter Module

This module converts TIFF files to JPG format for the alfalfa segmentation pipeline.
It creates compressed JPG images suitable for visualization, web display, or quick preview 
purposes while maintaining good image quality.

Key features:
- TIFF to JPG format conversion
- Automatic channel handling (RGB/RGBA/Grayscale)
- High-quality compression (95% quality)
- Batch processing of multiple TIFF files
"""

import os
from PIL import Image
import numpy as np
import argparse

def tiff_to_jpg(tiff_filepath, output_filepath):
    try:
        # Open TIFF image
        img = Image.open(tiff_filepath)
        
        # Convert to RGB if necessary (handles RGBA, L, etc.)
        if img.mode in ('RGBA', 'LA'):
            # Create white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as JPG with high quality
        img.save(output_filepath, 'JPEG', quality=95)
        print(f"Successfully converted '{tiff_filepath}' to '{output_filepath}'")
    except Exception as e:
        print(f"Error converting '{tiff_filepath}': {e}")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert TIFF files to JPG")
    p.add_argument("--file", type=str, help="Path to a single .tif/.tiff file (overrides directory scan)")
    p.add_argument("--num-shards", type=int, default=None, help="Total number of parallel shards (for SLURM arrays)")
    p.add_argument("--shard-index", type=int, default=None, help="Index of this shard [0..num-shards-1]")
    return p.parse_args()


def main():
    """Main function to convert TIFF files to JPG format"""
    # Convert all .tiff/.tif files in the folder (repo-relative)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(os.path.dirname(current_dir))  # .../src
    data_dir = os.path.join(src_dir, 'data')
    input_folder = os.path.join(data_dir, 'output_images', 'tiff_images')
    output_root = os.path.join(data_dir, 'output_images')
    jpg_output_folder = os.path.join(output_root, 'jpg_images')
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(jpg_output_folder, exist_ok=True)

    args = parse_args()

    # Build list of TIFF paths to process
    if args.file:
        if os.path.isabs(args.file):
            tiff_paths = [args.file]
        else:
            tiff_paths = [os.path.join(input_folder, args.file)]
    else:
        tiff_files = [f for f in sorted(os.listdir(input_folder)) if f.lower().endswith((".tif", ".tiff"))]
        if not tiff_files:
            print(f"No TIFF files found in {input_folder}")
            print("Make sure to run tiff_converter.py first to generate TIFF files.")
            return
        tiff_paths = [os.path.join(input_folder, f) for f in tiff_files]

        # Shard across array tasks if requested
        if args.num_shards is not None and args.shard_index is not None:
            if args.num_shards <= 0 or not (0 <= args.shard_index < args.num_shards):
                raise ValueError("Invalid shard params: require 0 <= shard_index < num_shards and num_shards > 0")
            tiff_paths = [p for i, p in enumerate(tiff_paths) if i % args.num_shards == args.shard_index]
            if not tiff_paths:
                print("No files assigned to this shard. Exiting.")
                return

    print(f"Found {len(tiff_paths)} TIFF files to convert in this shard...")

    for tiff_path in tiff_paths:
        filename = os.path.basename(tiff_path)
        jpg_name = os.path.splitext(filename)[0] + '.jpg'
        jpg_path = os.path.join(jpg_output_folder, jpg_name)
        tiff_to_jpg(tiff_path, jpg_path)
    
    print(f"Conversion complete! JPG files saved to: {jpg_output_folder}")


if __name__ == "__main__":
    main()