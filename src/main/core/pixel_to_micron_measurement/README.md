# Pixel-to-Micron Measurement Utilities

This folder contains utilities to extract pixel-to-micron calibration and compute image dimensions/areas in microns from ND2 images, with results exported to CSV.

This may need some work yet, we kinda ran out of time to work on this measurement, but we know it is pretty close. It is also in the main pipeline.py file as well, so it runs when that is run.

## Files

- `process_nd2_measurements.py`: Combined script that processes ND2 files and exports micron measurements to CSV. Uses `pixel_microns` from ND2 metadata when available, otherwise falls back to a constant conversion factor.

## Input Directory

The script looks for ND2 files in:

```
src/data/nd2_images/input_images
```

Only files with the `.nd2` extension are processed.

## Output

Results are saved to a CSV file:

```
src/data/detector_results/nd2_micron_measurements.csv
```

The CSV contains the following columns:

- `image_name`: Name of the ND2 file
- `pixel_microns`: Pixel-to-micron conversion factor used
- `pixel_microns_source`: Source of the conversion factor (`metadata` or `fallback_constant`)
- `width_pixels`: Image width in pixels
- `height_pixels`: Image height in pixels
- `width_microns`: Image width in microns
- `height_microns`: Image height in microns
- `area_square_microns`: Total image area in square microns

## Dependencies

- `nd2reader`
- `pathlib` (standard library)
- `csv` (standard library)

Install with:

```
pip install nd2reader
```

## Usage

From the repository root:

```
python src/main/core/pixel_to_micron_measurement/process_nd2_measurements.py
```

The script will:

1. Process all ND2 files in the input directory
2. Extract pixel-to-micron conversion from metadata when available
3. Fall back to a constant value (`PIXEL_TO_MICRON_FALLBACK = 0.9785316641067333`) if metadata is missing
4. Calculate width, height, and area in microns for each image
5. Export all results to the CSV file

## Notes

- The script automatically uses ND2 metadata (`pixel_microns`) when available, which provides image-specific calibration.
- If metadata is not available, it falls back to the constant `PIXEL_TO_MICRON_FALLBACK` defined in the script. Adjust this value if your calibration differs.
- The `area_square_microns` represents the total image field of view area, not necessarily the actual cross-section area (which would require segmentation to exclude background).
- The output directory (`src/data/detector_results`) will be created automatically if it doesn't exist.
