"""
This script processes ND2 files and extracts micron measurements.

It may need some work yet to be fully functional, as I think it might not be working quite as expected
But it is at least a start to get measurements correct from the nd2 images.
"""

from pathlib import Path
import csv
from nd2reader import ND2Reader

# Configuration
IMAGE_DIR = Path("src/data/nd2_images/input_images")
OUTPUT_DIR = Path("src/data/detector_results")
OUTPUT_CSV = OUTPUT_DIR / "nd2_micron_measurements.csv"

# Fallback constant pixel-to-micron conversion (used if metadata is not available)
PIXEL_TO_MICRON_FALLBACK = 0.9785316641067333

# Old path to test specific images
#BASE_FOLDER = Path("src/main/core/pixel_to_micron_measurement")
#IMAGE_DIR = BASE_FOLDER / "images"


def process_nd2_files():
    """
    Process ND2 files and extract micron measurements.
    Uses pixel_microns from metadata if available, otherwise falls back to constant.
    """
    results = []
    
    # Check if the input directory exists
    if not IMAGE_DIR.exists() or not IMAGE_DIR.is_dir():
        print(f"Error: The directory '{IMAGE_DIR}' does not exist or is not a directory.")
        return
    
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process all ND2 files
    nd2_files = list(IMAGE_DIR.glob("*.nd2"))
    if not nd2_files:
        print(f"No ND2 files found in '{IMAGE_DIR}'")
        return
    
    print(f"Processing {len(nd2_files)} ND2 file(s)...")
    
    for nd2_file in nd2_files:
        try:
            with ND2Reader(str(nd2_file)) as images:
                # Get image dimensions in pixels
                width_pixels = images.metadata['width']
                height_pixels = images.metadata['height']
                
                # Try to get pixel_microns from metadata, fall back to constant if not available
                try:
                    pixel_micron = images.metadata['pixel_microns']
                    pixel_micron_source = 'metadata'
                except (KeyError, TypeError):
                    pixel_micron = PIXEL_TO_MICRON_FALLBACK
                    pixel_micron_source = 'fallback_constant'
                
                # Calculate dimensions in microns
                width_microns = width_pixels * pixel_micron
                height_microns = height_pixels * pixel_micron
                area_microns = width_microns * height_microns
                
                # Store results
                results.append({
                    'image_name': nd2_file.name,
                    'pixel_microns': pixel_micron,
                    'pixel_microns_source': pixel_micron_source,
                    'width_pixels': width_pixels,
                    'height_pixels': height_pixels,
                    'width_microns': width_microns,
                    'height_microns': height_microns,
                    'area_square_microns': area_microns
                })
                
                print(f"Processed: {nd2_file.name} - Source: {pixel_micron_source}, "
                      f"Pixel-to-micron: {pixel_micron:.10f}")
                
        except Exception as e:
            print(f"Error processing file {nd2_file.name}: {e}")
            # Still add entry with error info
            results.append({
                'image_name': nd2_file.name,
                'pixel_microns': None,
                'pixel_microns_source': 'error',
                'width_pixels': None,
                'height_pixels': None,
                'width_microns': None,
                'height_microns': None,
                'area_square_microns': None,
                'error': str(e)
            })
    
    # Write results to CSV
    if results:
        write_csv(results)
        print(f"\nResults saved to: {OUTPUT_CSV}")
    else:
        print("No results to save.")


def write_csv(results):
    """Write measurement results to CSV file."""
    fieldnames = [
        'image_name',
        'pixel_microns',
        'pixel_microns_source',
        'width_pixels',
        'height_pixels',
        'width_microns',
        'height_microns',
        'area_square_microns'
    ]
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    process_nd2_files()

