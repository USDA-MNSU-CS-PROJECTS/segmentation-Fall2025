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

def main():
    """Main function to convert all TIFF files to JPG format"""
    # Convert all .tiff/.tif files in the folder (repo-relative)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(os.path.dirname(current_dir))  # .../src
    data_dir = os.path.join(src_dir, 'data')
    input_folder = os.path.join(data_dir, 'output_images', 'tiff_images')
    output_root = os.path.join(data_dir, 'output_images')
    jpg_output_folder = os.path.join(output_root, 'jpg_images')
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(jpg_output_folder, exist_ok=True)

    # Process all TIFF files
    tiff_files = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.tiff', '.tif')):
            tiff_files.append(filename)

    if not tiff_files:
        print(f"No TIFF files found in {input_folder}")
        print("Make sure to run tiff_converter.py first to generate TIFF files.")
        return
    
    print(f"Found {len(tiff_files)} TIFF files to convert...")
    
    for filename in tiff_files:
        tiff_path = os.path.join(input_folder, filename)
        jpg_name = os.path.splitext(filename)[0] + '.jpg'
        jpg_path = os.path.join(jpg_output_folder, jpg_name)
        tiff_to_jpg(tiff_path, jpg_path)
    
    print(f"Conversion complete! JPG files saved to: {jpg_output_folder}")


if __name__ == "__main__":
    main()