"""
JPG Converter Module (OPTIONAL)

This module converts ND2 (Nikon Digital) microscopy files to JPG format for the alfalfa segmentation pipeline.
It provides a lightweight alternative to TIFF conversion, creating compressed JPG images suitable for
visualization, web display, or quick preview purposes while maintaining good image quality.

Key features:
- ND2 to JPG format conversion
- Automatic channel handling (RGB/RGBA/Grayscale)
- High-quality compression (95% quality)
- Multi-dimensional data handling
- Batch processing of multiple ND2 files
"""

import os
from nd2reader import ND2Reader
from PIL import Image
import numpy as np

def nd2_to_jpg(nd2_filepath, output_filepath):
    try:
        with ND2Reader(nd2_filepath) as images:
            image_data = images[0]
            if image_data.ndim == 3 and image_data.shape[0] in (3, 4):
                image_data = np.transpose(image_data, (1, 2, 0))
                mode = 'RGB' if image_data.shape[2] == 3 else 'RGBA'
            else:
                mode = 'L'
            img = Image.fromarray(image_data.astype(np.uint8), mode=mode)
            img.save(output_filepath, quality=95)
            print(f"Successfully converted '{nd2_filepath}' to '{output_filepath}'")
    except Exception as e:
        print(f"Error converting '{nd2_filepath}': {e}")

# Convert all .nd2 files in the folder (repo-relative)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))  # .../src
data_dir = os.path.join(src_dir, 'data')
input_folder = os.path.join(data_dir, 'nd2_images', 'input_images')
output_root = os.path.join(data_dir, 'output_images')
jpg_output_folder = os.path.join(output_root, 'jpg_images')
os.makedirs(input_folder, exist_ok=True)
os.makedirs(jpg_output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith('.nd2'):
        nd2_path = os.path.join(input_folder, filename)
        jpg_name = os.path.splitext(filename)[0] + '.jpg'
        jpg_path = os.path.join(jpg_output_folder, jpg_name)
        nd2_to_jpg(nd2_path, jpg_path)