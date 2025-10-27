# Detectors Directory 🔬

This directory contains specialized image analysis tools for detecting specific biological components in alfalfa microscopy images.

## 📋 **Overview**

The detectors analyze images that have already been processed through the YOLO background removal pipeline. They use HSV color space analysis to identify and quantify specific stained regions within detected cell boundaries.

## 🔧 **Available Detectors**

### **Lignin(PG)\_detector.py**

**Purpose**: Detects lignin content in PG-stained images

**What it detects**: Red regions indicating lignin presence in cell walls

**Color Analysis**:

- Uses HSV color space with two red ranges
- Range 1: Hue 0-10°, Saturation 80-255, Value 50-255
- Range 2: Hue 170-180°, Saturation 80-255, Value 50-255
- Applies morphological operations to clean up noise

**Input Requirements**:

- Images must be JPG format
- Images should come from YOLO background removal pipeline
- Folder structure: `src/data/yolo_results/[folder]_PG/`

**Output**:

- CSV file with lignin ratios and metadata
- Visualization images showing detected regions
- Results saved to: `src/data/detector_results/lignin_detector_results/`

### **Pectin(RR)\_detector.py**

**Purpose**: Detects pectin content in Ruthenium Red stained images

**What it detects**: Deep red/burgundy and reddish brown regions indicating pectin presence

**Color Analysis**:

- Uses HSV color space with multiple ranges for comprehensive detection
- Deep red range: Hue 0-15° and 165-180°, Saturation 100-255, Value 80-255
- Brown range: Hue 5-25° and 160-180°, Saturation 50-255, Value 40-200
- Applies morphological operations to clean up noise

**Input Requirements**:

- Images must be JPG format
- Images should come from YOLO background removal pipeline
- Folder structure: `src/data/yolo_results/[folder]_RR/`

**Output**:

- CSV file with pectin ratios and metadata
- Visualization images showing detected regions
- Results saved to: `src/data/detector_results/pectin_detector_results/`

## 🚀 **Usage Examples**

### **Batch Processing (Recommended)**

Process all configured folders automatically:

```bash
# Lignin detection
python detectors/"Lignin(PG)_detector.py" --batch --debug

# Pectin detection
python detectors/"Pectin(RR)_detector.py" --batch --debug
```

### **Single Folder Processing**

Process a specific folder:

```bash
# Lignin detection
python detectors/"Lignin(PG)_detector.py" --input src/data/yolo_results/20240630-20240644_10xstitch_PG --debug

# Pectin detection
python detectors/"Pectin(RR)_detector.py" --input src/data/yolo_results/20240630-20240644_10xstitch_RR --debug
```

### **Custom Parameters**

Override default settings:

```bash
# Custom confidence threshold
python detectors/"Lignin(PG)_detector.py" --batch --conf 0.3 --debug

# Custom YOLO weights
python detectors/"Pectin(RR)_detector.py" --batch --weights src/data/yolo_results/runs/segment/latest/weights/best.pt --debug

# Force specific mask mode
python detectors/"Lignin(PG)_detector.py" --batch --mask-mode yolo --debug
```

## 📊 **Output Format**

### **CSV Results**

Both detectors generate CSV files with the following columns:

**Metadata Columns**:

- `Project`: Always "DASS"
- `ImageSet`: Folder name (e.g., "20240630-20240644_10xstitch_PG")
- `Location`: "STP" for samples, "control" for standards
- `Maturity`: "EF" for samples, "control" for standards
- `AlfalfaLine`: Determined by 4-digit ID modulo 5 (Megatron, 4351, 54Q32, 4016, 55v12)
- `ImageID`: Full filename without extension
- `Year`: Extracted from filename
- `LabID`: 8-digit identifier
- `CrossSection`: Cross-section identifier (a, b, c, d)
- `IncubationTime_Hr`: Time point (T0, T24, etc.)
- `ImageType`: Image type (10xstitch, etc.)
- `Stain`: Stain type (PG or RR)

**Analysis Columns**:

- `filename`: Original image filename
- `[component]_pixel_count`: Number of detected pixels
- `cell_pixel_count`: Total pixels in detected cell region
- `total_pixel_count`: Total pixels in entire image
- `cells_detected`: Number of cells detected by YOLO
- `[component]_ratio_in_cell`: Ratio of component pixels to cell pixels
- `Percentage of [Component]`: Percentage format of the ratio

### **Visualization Images**

- Saved as `[original_name]_detected.jpg`
- Green contours show detected cell boundaries
- Blue overlay shows detected component regions
- Text overlay shows detection statistics

## ⚙️ **Configuration**

### **Input Folders**

Configure input folders by editing the script files:

**Lignin(PG)\_detector.py**:

```python
BATCH_INPUT_FOLDERS = [
    "src/data/yolo_results/20240630-20240644_10xstitch_PG",
    "src/data/yolo_results/20240705-20240719_10xstitch_PG",
    "src/data/yolo_results/20240780-20240794_10xstitch_PG",
    "src/data/yolo_results/20240855-20240869_10xstitch_PG",
]
```

**Pectin(RR)\_detector.py**:

```python
BATCH_INPUT_FOLDERS = [
    "src/data/yolo_results/20240630-20240644_10xstitch_RR",
    "src/data/yolo_results/20240705-20240719_10xstitch_RR",
    "src/data/yolo_results/20240780-20240794_10xstitch_RR",
    "src/data/yolo_results/20240855-20240869_10xstitch_RR",
]
```

### **Output Folders**

Results are automatically saved to:

- Lignin: `src/data/detector_results/lignin_detector_results/`
- Pectin: `src/data/detector_results/pectin_detector_results/`

## 🔍 **Cell Detection Methods**

Both detectors support multiple cell detection methods:

### **Auto Mode (Default)**

- Automatically chooses between YOLO and non-white heuristic
- Uses non-white heuristic for background-removed images
- Uses YOLO for images with complex backgrounds

### **YOLO Mode**

- Uses trained YOLO segmentation model
- Requires `best.pt` weights file
- More accurate but requires GPU/CPU resources

### **Non-white Mode**

- Uses white background heuristic
- Assumes images have white backgrounds
- Faster processing, good for pre-processed images

## 📁 **Directory Structure**

```
src/main/core/detectors/
├── README.md                    # This documentation
├── Lignin(PG)_detector.py       # Lignin detection tool
└── Pectin(RR)_detector.py       # Pectin detection tool
```

## ⚠️ **Important Notes**

1. **Prerequisites**: Images must be processed through YOLO background removal first
2. **File Formats**: Only JPG images are supported
3. **Folder Naming**: Input folders should end with `_PG` or `_RR` for proper metadata extraction
4. **Weights**: YOLO mode requires trained weights (`best.pt`) - auto-detects latest if not specified
5. **Memory**: Large images may require significant RAM
6. **GPU**: YOLO mode benefits from GPU acceleration

## 🐛 **Troubleshooting**

### **Common Issues**

- **"No images found"**: Check input folder paths and ensure JPG files exist
- **"No best.pt found"**: Train a YOLO model first or specify weights with `--weights`
- **"No cell detected"**: Try different `--mask-mode` or adjust `--conf` threshold
- **"Permission denied"**: Check file permissions and folder access

### **Debug Mode**

Use `--debug` flag for detailed processing information:

```bash
python detectors/"Lignin(PG)_detector.py" --batch --debug
```

### **Performance Tips**

- Use `--mask-mode nonwhite` for faster processing on background-removed images
- Adjust `--conf` threshold (0.1-0.5) based on detection quality
- Process smaller batches if memory is limited
