# 🌱 Gradio UI - Complete Step-by-Step Breakdown

## 📋 Overview

The UI has **5 tabs** that guide the biologist through a complete analysis workflow:
1. Upload & Process
2. Segmentation
3. Chemical Analysis  
4. Results & Export
5. Settings

---

## 🗂️ Data Storage Structure

All processing happens in `src/gradio_ui/temp/`:

```
src/gradio_ui/temp/
├── uploads/          # Original uploaded files (temporary)
├── processed/        # Converted JPGs, segmented images, bg-removed PNGs
├── results/          # Lignin/Pectin detection visualizations
└── cache/            # Settings and session metadata (JSON)
```

---

# TAB 1: 📤 Upload & Process

## What It Does
Converts microscopy images from various formats into standard JPG files ready for analysis.

## User Interface Components
1. **File Upload Area** (Drag & Drop)
   - Accepts: `.nd2`, `.tiff`, `.tif`, `.jpg`, `.jpeg`, `.png`
   - Can upload multiple files at once
   
2. **"Convert Images" Button**
   - Starts the conversion process
   
3. **Status Text Box**
   - Shows real-time progress messages
   - Lists each file being processed
   
4. **Gallery**
   - Displays all converted JPG images
   - 4 columns layout

## What Happens (Backend)

### Function: `ImageProcessor.process_uploads()`
**Location**: `src/gradio_ui/backend/image_processor.py`

### Processing Steps:

#### For `.nd2` Files:
1. Opens ND2 file using `nd2` library
2. Reads microscopy image data
3. Normalizes to 8-bit (0-255 range)
4. Converts RGB → BGR (OpenCV format)
5. Saves directly as JPG

**Code Used**:
- `nd2.ND2File()` - Opens Nikon microscopy files
- `cv2.imwrite()` - Saves as JPG with 95% quality

#### For `.tiff`/`.tif` Files:
1. Reads TIFF using OpenCV
2. Saves as JPG

**Code Used**:
- `cv2.imread()` - Reads TIFF
- `cv2.imwrite()` - Converts to JPG

#### For `.jpg`/`.png` Files:
1. Simply copies to processed folder
2. No conversion needed

**Code Used**:
- `shutil.copy2()` - File copy

## Outputs

### Saved To: `src/gradio_ui/temp/processed/`

**Files Created**:
- `{original_name}.jpg` - Converted JPG image

**Example**:
- Input: `alfalfa_sample_001.nd2`
- Output: `src/gradio_ui/temp/processed/alfalfa_sample_001.jpg`

## Status Messages

User sees messages like:
```
📤 Processing uploaded files...

🔄 Converting: alfalfa_001.nd2 (ND2 → JPG)
   ✅ alfalfa_001.nd2 → alfalfa_001.jpg

🔄 Converting: sample_002.tiff (TIFF → JPG)
   ✅ sample_002.tiff → sample_002.jpg

✅ Processed 2 image(s) successfully!
📁 Saved to: processed/
```

## What Can Go Wrong

- **Error**: "Could not read image"
  - Cause: Corrupted file or unsupported format
  
- **Error**: "ND2 conversion failed"
  - Cause: Malformed ND2 file

## Next Step
Converted images appear in the gallery and are ready for Tab 2 (Segmentation)

---

# TAB 2: 🔬 Segmentation

## What It Does
Uses AI (YOLO model) to detect and segment individual cells in the images.

## User Interface Components

1. **Image Selector Dropdown**
   - Lists all processed images from Tab 1
   - Select one image to analyze
   
2. **Confidence Threshold Slider**
   - Range: 0.1 to 0.9 (default: 0.25)
   - Lower = more detections (may include false positives)
   - Higher = fewer, more confident detections
   
3. **"Run Segmentation" Button**
   - Starts AI analysis
   
4. **Status Text Box**
   - Shows detection results
   
5. **Three Image Displays**:
   - **Original Image** - Your uploaded image
   - **Segmented Result** - With colored boxes and masks
   - **Background Removed** - Isolated cells on white background

## What Happens (Backend)

### Function: `SegmentationEngine.run_segmentation()`
**Location**: `src/gradio_ui/backend/segmentation.py`

### Processing Steps:

1. **Load YOLO Model** (first time only)
   - Loads: `src/data/yolo_results/runs/segment/handover-model/weights/best.pt`
   - Cached in memory for subsequent runs
   
2. **Read Input Image**
   - Uses: `cv2.imread()`
   
3. **Run AI Inference**
   ```python
   results = model.predict(
       source=img,
       conf=0.25,           # Confidence threshold
       iou=0.45,            # Overlap threshold
       max_det=300          # Max detections per image
   )
   ```
   
4. **Create Visualization Overlay**
   - Draws bounding boxes around detected cells
   - Overlays segmentation masks (colored regions)
   - Uses: `results[0].plot()`
   
5. **Remove Background**
   - Extracts segmentation masks
   - Creates white canvas (255, 255, 255)
   - Copies only detected cell pixels
   - Makes background pure white

### AI Model Details

**Model**: YOLO11 (Ultralytics)
**Type**: Instance Segmentation
**Trained On**: Alfalfa cell images (from handover materials)
**Task**: Detect and segment individual cell walls

**What It Detects**:
- Cell boundaries
- Individual cell regions
- Returns both bounding boxes AND pixel-level masks

## Outputs

### Saved To: `src/gradio_ui/temp/processed/`

**Files Created** (3 per analysis):

1. `{name}_original.jpg`
   - Copy of input image
   
2. `{name}_segmented_{timestamp}.jpg`
   - Image with colored boxes and masks overlay
   - Example: `alfalfa_001_segmented_20240115_143022.jpg`
   
3. `{name}_nobg_{timestamp}.png`
   - Background-removed version (PNG for transparency)
   - White background (255, 255, 255)
   - Example: `alfalfa_001_nobg_20240115_143022.png`

## Status Messages

User sees:
```
✅ Segmentation complete!

Detections: 12 cell(s) found
Confidence: 0.25
Model: best.pt

Outputs saved to: processed/
```

## Technical Details

### HSV Color Detection (Chemical Analysis Prep)
The background-removed image is created by:
1. Getting pixel-level masks from YOLO
2. Resizing masks to match image dimensions
3. Creating binary mask (0 or 1)
4. Copying pixels where mask = 1
5. Setting pixels where mask = 0 to white (255)

### Parameters You Can Adjust

In Settings Tab:
- **Confidence Threshold**: How sure the model must be (0.1-0.9)
- **IOU Threshold**: Overlap tolerance (default: 0.45)

## What Can Go Wrong

- **"Model not found"**
  - best.pt is missing or in wrong location
  
- **"No cells detected"**
  - Try lowering confidence threshold
  - Image may not contain cells
  
- **"CUDA out of memory"** (if using GPU)
  - Image too large
  - Reduce batch size (not exposed in UI currently)

## Next Step
Background-removed images are ready for Tab 3 (Chemical Analysis)

---

# TAB 3: 🧪 Chemical Analysis

## What It Does
Detects and quantifies chemical composition (lignin and pectin) using color-based detection.

## User Interface Components

1. **Analysis Type Checkboxes**
   - [ ] Lignin (PG) - Red staining detection
   - [ ] Pectin (RR) - Burgundy/purple staining detection
   - Can select one or both

2. **Image Selector Dropdown**
   - Lists all background-removed images from Tab 2
   - Shows files ending in `_nobg_*.png`

3. **"Run Chemical Analysis" Button**
   - Starts color detection analysis

4. **Status Text Box**
   - Shows analysis progress and results

5. **Two Visualization Images**:
   - **Lignin Detection Overlay** - Red highlights
   - **Pectin Detection Overlay** - Purple highlights

6. **Results Table**
   - Quantitative metrics in tabular format

## What Happens (Backend)

### Function: `ChemicalAnalyzer.run_analysis()`
**Location**: `src/gradio_ui/backend/chemical_analysis.py`

### How It Works

#### COLOR-BASED DETECTION METHOD

Both lignin and pectin are detected using **HSV color space analysis**:

**Why HSV?**
- HSV = Hue, Saturation, Value
- Better for color detection than RGB
- Separates color (hue) from intensity (value)

### Lignin Detection (PG Staining)

**What We're Looking For**: Red-stained regions (Phloroglucinol staining)

#### Processing Steps:

1. **Convert to HSV**
   ```python
   hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
   ```

2. **Define Red Color Range**
   - Red wraps around in HSV (0-10 and 170-180 degrees)
   - Lower red: H=0-10, S=50-255, V=50-255
   - Upper red: H=170-180, S=50-255, V=50-255

3. **Create Mask**
   - `cv2.inRange()` finds pixels matching red color
   - Results in binary mask (0 or 255)

4. **Remove Background**
   - Excludes white pixels (background)
   - Only analyzes cell regions

5. **Calculate Metrics**
   - Count lignin pixels (red regions)
   - Count total cell pixels (non-white)
   - Calculate ratio: lignin_pixels / total_pixels
   - Calculate area: pixels × (pixel_to_micron)²

6. **Create Visualization**
   - Make detected pixels pure red (0, 0, 255)
   - Blend 60% original + 40% overlay
   - Save as image

**Code**:
```python
# Define color range
lower_red1 = np.array([0, 50, 50])
upper_red1 = np.array([10, 255, 255])
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

# Calculate ratio
lignin_pixels = np.sum(mask > 0)
total_pixels = np.sum(non_white_mask)
ratio = lignin_pixels / total_pixels
```

### Pectin Detection (Ruthenium Red Staining)

**What We're Looking For**: Burgundy/deep red-purple regions

#### Processing Steps:

Same as lignin, but different color range:

**Burgundy Color Range**:
- Hue: 160-180 (red-purple end of spectrum)
- Saturation: 40-255
- Value: 40-200 (darker than bright red)

**Visualization Color**: Purple (128, 0, 128)

### Metrics Calculated

For Each Analysis:

1. **Pixel Count** (integer)
   - Number of pixels detected as lignin/pectin

2. **Ratio** (float, 0-1)
   - Formula: `detected_pixels / total_non_white_pixels`
   - Example: 0.234 = 23.4% of cell is lignin

3. **Area in Microns²** (float)
   - Formula: `pixels × (pixel_to_micron_conversion)²`
   - Uses fallback: 0.9785 pixels/micron (from ND2 metadata)
   - Example: 45678 pixels × 0.9785² = 43,700 μm²

## Outputs

### Saved To: `src/gradio_ui/temp/results/`

**Files Created**:

1. `{name}_lignin_detected.jpg`
   - Visualization with red overlay
   - Example: `alfalfa_001_nobg_20240115_143022_lignin_detected.jpg`

2. `{name}_pectin_detected.jpg`
   - Visualization with purple overlay
   - Example: `alfalfa_001_nobg_20240115_143022_pectin_detected.jpg`

### Results Table Format

| Metric | Lignin | Pectin |
|--------|--------|--------|
| Pixels | 45,678 | 23,456 |
| Ratio | 0.2340 | 0.1200 |
| Area (μm²) | 43,700.25 | 22,450.78 |

## Status Messages

User sees:
```
🧪 Running chemical analysis...

🔴 Analyzing lignin (PG staining)...
   ✅ Lignin ratio: 0.234

🟣 Analyzing pectin (Ruthenium Red)...
   ✅ Pectin ratio: 0.120

✅ Analysis complete!
📁 Saved to: results/
```

## Adjustable Parameters (Settings Tab)

1. **Lignin Sensitivity** (1-10 scale)
   - Adjusts color range tolerance
   - Higher = detects more shades of red

2. **Pectin Sensitivity** (1-10 scale)
   - Adjusts burgundy detection range
   - Higher = detects lighter shades

3. **Pixel-to-Micron Conversion**
   - Default: 0.9785316641067333
   - Can be updated if you know your microscope's calibration

## Scientific Background

### PG (Phloroglucinol) Staining
- Stains **lignin** red/pink
- Detects lignified cell walls
- Used to measure cell wall thickness/composition

### RR (Ruthenium Red) Staining
- Stains **pectin** burgundy/red-purple
- Detects pectic polysaccharides
- Used to measure cell wall composition

## What Can Go Wrong

- **No detection (ratio = 0.000)**
  - Image may not be stained
  - Try adjusting sensitivity in Settings
  - Check if image is background-removed (should be)

- **Everything detected (ratio ≈ 1.000)**
  - Sensitivity too high
  - Color range too broad
  - May need to adjust HSV ranges

## Next Step
Results are saved and ready to view/download in Tab 4

---

# TAB 4: 📊 Results & Export

## What It Does
Aggregates all session results and creates downloadable packages.

## User Interface Components

1. **Session Summary Text Box**
   - Shows statistics about current session
   - Auto-updates when you click "Refresh Results"

2. **"Refresh Results" Button**
   - Scans all temp folders
   - Counts processed images and analyses

3. **Export Format Selector**
   - Radio buttons:
     - CSV (tables only)
     - Excel (formatted workbook)
     - ZIP (All Files) ← Most useful!

4. **"Download Results" Button**
   - Creates downloadable file

5. **Download File Component**
   - Shows download link when ready

6. **Results Gallery**
   - Shows all generated visualizations
   - 3 columns layout

## What Happens (Backend)

### Function: `ResultsManager.get_session_summary()`
**Location**: `src/gradio_ui/backend/results_manager.py`

### Session Summary Process:

1. **Scans Folders**:
   ```python
   processed/ → Counts JPG files
   processed/ → Counts PNG files (background-removed)
   processed/ → Counts *_segmented_*.jpg
   results/   → Counts *_lignin_*.jpg
   results/   → Counts *_pectin_*.jpg
   ```

2. **Generates Summary**:
   ```
   📊 SESSION SUMMARY
   ========================================

   📁 Processed Images: 5
   📁 Background-Removed: 5
   🔬 Segmented Images: 5
   🧪 Lignin Analyses: 3
   🧪 Pectin Analyses: 3

   ✅ Total Analyses: 6

   📂 Results Location:
      /path/to/temp/results/
   ```

3. **Collects Gallery Images**:
   - All segmented images
   - All lignin overlays
   - All pectin overlays

### Export Functions

#### CSV Export: `_export_csv()`

Creates: `results_{timestamp}.csv`

**Contains**:
- Session metadata
- Timestamp
- (Could be enhanced to include actual metrics)

**Current Implementation**: Basic metadata only

#### Excel Export: `_export_excel()`

Creates: `results_{timestamp}.xlsx`

**Sheets**:
- Summary sheet with export date and session info
- (Could be enhanced with detailed data sheets)

**Uses**: `pandas.ExcelWriter` with `openpyxl` engine

#### ZIP Export: `_export_zip()` ← **RECOMMENDED**

Creates: `results_{timestamp}.zip`

**Contents**:
```
results_20240115_143022.zip
├── README.txt              # Info about the export
├── processed/
│   ├── image1.jpg
│   ├── image1_segmented_*.jpg
│   ├── image1_nobg_*.png
│   └── ... (all processed images)
└── results/
    ├── image1_lignin_detected.jpg
    ├── image1_pectin_detected.jpg
    └── ... (all analysis visualizations)
```

**README.txt contains**:
```
Alfalfa Cell Segmentation Analysis Results
==========================================

Export Date: 2024-01-15 14:30:22

Contents:
- processed/ : Segmented and background-removed images
- results/   : Chemical analysis visualizations (lignin, pectin)

For questions, contact your research coordinator.
```

## Outputs

### Saved To: `src/gradio_ui/temp/`

**Files Created**:
- `results_{timestamp}.csv` (CSV export)
- `results_{timestamp}.xlsx` (Excel export)
- `results_{timestamp}.zip` (ZIP export) ← **Best option**

**Example**:
- `results_20240115_143522.zip` (4.5 MB)

## What the Biologist Gets

When downloading ZIP file:

1. **Unzip the file**
2. **See organized folders**:
   - `processed/` - All images ready for presentation
   - `results/` - All analysis overlays
   - `README.txt` - Explains contents

3. **Use in Publications**:
   - Segmented images show cell boundaries
   - Lignin/Pectin overlays show chemical distribution
   - Can copy directly into papers/slides

## What Can Go Wrong

- **Empty ZIP or CSV**
  - No analyses have been run yet
  - Process some images first

- **Download button does nothing**
  - Browser blocked download
  - Check browser download permissions

## Next Step
Open ZIP file, use images in research, prepare publication!

---

# TAB 5: ⚙️ Settings

## What It Does
Configure model paths, detection parameters, and analysis sensitivity.

## User Interface Components

### YOLO Model Settings

1. **Model Path Text Box**
   - Shows current model location
   - Default: Auto-detected from `yolo_results/runs/segment/*/weights/best.pt`
   - Can be manually changed if needed

2. **Model Status Text Box**
   - Shows if model can be loaded
   - Displays model info

3. **"Check Model" Button**
   - Validates model file exists
   - Attempts to load it
   - Shows status

### Detection Parameters

1. **Default Confidence Threshold Slider**
   - Range: 0.1 - 0.9
   - Default: 0.25
   - Sets default for Tab 2 segmentation

2. **IOU Threshold Slider**
   - Range: 0.1 - 0.9
   - Default: 0.45
   - Controls how overlapping detections are handled
   - Higher = less overlap allowed

### Chemical Analysis Settings

1. **Pixel to Micron Conversion**
   - Number input
   - Default: 0.9785316641067333
   - Used when ND2 metadata not available
   - **Important**: Get this from your microscope calibration!

2. **Lignin Detection Sensitivity**
   - Scale: 1-10
   - Default: 5
   - 1 = Very strict (only bright red)
   - 10 = Very permissive (includes pink/orange)

3. **Pectin Detection Sensitivity**
   - Scale: 1-10
   - Default: 5
   - 1 = Only deep burgundy
   - 10 = Includes lighter purple/pink

### Save Settings

1. **"Save Settings" Button**
   - Saves all current values
   - Persists across sessions

2. **Settings Status Text**
   - Shows "✅ Settings saved successfully!"
   - Or error message

## What Happens (Backend)

### Function: `UIConfig.save_settings()`
**Location**: `src/gradio_ui/config.py`

### Settings Storage:

**File**: `src/gradio_ui/temp/cache/settings.json`

**Contents**:
```json
{
  "model_path": "src/data/yolo_results/.../best.pt",
  "confidence_default": 0.25,
  "iou_threshold": 0.45,
  "pixel_to_micron_fallback": 0.9785316641067333,
  "lignin_sensitivity": 5,
  "pectin_sensitivity": 5
}
```

### Model Check Process:

```python
def check_model_status(model_path):
    # 1. Check if file exists
    if not Path(model_path).exists():
        return "❌ Model not found"

    # 2. Check file size
    size_mb = file.size / (1024 * 1024)

    # 3. Try loading with Ultralytics
    try:
        model = YOLO(model_path)
        return f"✅ Model is valid!\n\nPath: {path}\nSize: {size_mb:.2f} MB"
    except:
        return "❌ Model file corrupted"
```

## Technical Details

### Confidence Threshold
**What It Does**: Filters YOLO detections

- Model outputs confidence score for each detection (0-1)
- Threshold = minimum confidence to keep detection
- Example: 0.25 means "keep if model is >25% sure"

**Effect**:
- Too low (0.1): Many false positives
- Too high (0.9): May miss real cells
- Sweet spot: Usually 0.2-0.4

### IOU Threshold (Intersection Over Union)
**What It Does**: Removes duplicate overlapping boxes

- When two boxes overlap, keep only one
- IOU = (overlap area) / (total area covered)
- Example: 0.45 means "merge boxes if >45% overlap"

**Effect**:
- Low (0.2): More aggressive merging
- High (0.7): Allows more overlaps
- Default 0.45 works well for cells

### Pixel-to-Micron Conversion
**What It Does**: Converts pixel measurements to real-world size

- Depends on microscope magnification
- Usually extracted from ND2 file metadata
- Fallback used when metadata unavailable

**How to Find Your Value**:
1. Take image of known-size object (calibration slide)
2. Measure object in pixels
3. Divide: real_size_microns / size_pixels
4. Example: 100 μm scale bar = 102 pixels → 100/102 = 0.98

**Impact**:
- Used in area calculations (μm²)
- Affects final scientific measurements
- **Critical for accurate results!**

### Color Sensitivity (1-10 Scale)

**How It Works**:
```python
# Sensitivity affects color range
sensitivity = 5  # User setting

# Lignin red range
lower = [0, 50, 50]
upper = [10 + sensitivity, 255, 255]  # Widens hue range

# Higher sensitivity = wider color range = more detections
```

**Effect**:
- Sensitivity 1: Very narrow color range
- Sensitivity 5: Moderate (default)
- Sensitivity 10: Wide range (may over-detect)

## Default Values

These are the built-in defaults:

```python
class UIConfig:
    confidence_default = 0.25
    iou_threshold = 0.45
    pixel_to_micron_fallback = 0.9785316641067333
    lignin_sensitivity = 5
    pectin_sensitivity = 5
    max_det = 300  # Max detections per image
```

## When to Adjust Settings

### Adjust Confidence If:
- ✅ **Too many false positives** → Increase to 0.3-0.4
- ✅ **Missing obvious cells** → Decrease to 0.15-0.2

### Adjust Lignin Sensitivity If:
- ✅ **Missing light red regions** → Increase to 7-8
- ✅ **Detecting non-lignin areas** → Decrease to 3-4

### Adjust Pectin Sensitivity If:
- ✅ **Missing light purple areas** → Increase to 7-8
- ✅ **Too much detected** → Decrease to 3-4

### Update Pixel-to-Micron If:
- ✅ **Working with different microscope** → Use new calibration
- ✅ **Different magnification** → Recalibrate

## Saved Settings Persist

Settings saved in this tab are:
- ✅ Loaded automatically on next launch
- ✅ Shared across all tabs
- ✅ Stored in JSON file
- ✅ Can be reset by deleting `cache/settings.json`

## What Can Go Wrong

- **Settings won't save**
  - Check folder permissions
  - Ensure `temp/cache/` exists

- **Model check fails**
  - Model file corrupted
  - Wrong file format (needs .pt PyTorch file)
  - Incompatible YOLO version

## Next Step
Settings are applied to all analyses. Go back to other tabs to use them!

---

# 🎯 COMPLETE WORKFLOW EXAMPLE

## Scenario: Analyze 3 Alfalfa Samples

### Step 1: Upload (Tab 1)
1. Drag 3 ND2 files: `sample_A.nd2`, `sample_B.nd2`, `sample_C.nd2`
2. Click "Convert Images"
3. See 3 JPGs in gallery

**Files Created**:
- `temp/processed/sample_A.jpg`
- `temp/processed/sample_B.jpg`
- `temp/processed/sample_C.jpg`

### Step 2: Segment (Tab 2)
1. Select "sample_A.jpg"
2. Keep confidence at 0.25
3. Click "Run Segmentation"
4. See: original, segmented (12 cells), background-removed
5. Repeat for B and C

**Files Created** (9 total):
- `sample_A_original.jpg`, `sample_A_segmented_143022.jpg`, `sample_A_nobg_143022.png`
- `sample_B_original.jpg`, `sample_B_segmented_143045.jpg`, `sample_B_nobg_143045.png`
- `sample_C_original.jpg`, `sample_C_segmented_143109.jpg`, `sample_C_nobg_143109.png`

### Step 3: Analyze Chemistry (Tab 3)
1. Select both Lignin and Pectin
2. Select "sample_A_nobg_143022.png"
3. Click "Run Analysis"
4. See red and purple overlays + metrics table:
   - Lignin: 45,678 pixels, ratio 0.234
   - Pectin: 23,456 pixels, ratio 0.120
5. Repeat for B and C

**Files Created** (6 total):
- `sample_A_nobg_143022_lignin_detected.jpg`
- `sample_A_nobg_143022_pectin_detected.jpg`
- `sample_B_nobg_143045_lignin_detected.jpg`
- `sample_B_nobg_143045_pectin_detected.jpg`
- `sample_C_nobg_143109_lignin_detected.jpg`
- `sample_C_nobg_143109_pectin_detected.jpg`

### Step 4: Export (Tab 4)
1. Click "Refresh Results"
2. See summary:
   - 3 processed images
   - 3 segmentations
   - 6 chemical analyses
3. Select "ZIP (All Files)"
4. Click "Download Results"
5. Download `results_20240115_143522.zip`

**ZIP Contains**:
- `processed/` folder: 9 files (JPGs + PNGs)
- `results/` folder: 6 files (lignin + pectin overlays)
- `README.txt`: Export info

### Step 5: Use in Research
1. Unzip file
2. Open in publication software
3. Use segmented images in Figure 1
4. Use lignin/pectin overlays in Figure 2
5. Copy metrics to Table 1
6. Publish paper! 🎉

---

# 📊 TECHNICAL SUMMARY

## Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **UI Framework** | Gradio 4.16.0 | Web interface |
| **AI Model** | YOLO11n (Ultralytics) | Cell segmentation |
| **Image Processing** | OpenCV (cv2) | Image manipulation |
| **ND2 Reading** | nd2 library | Microscopy format |
| **Data Handling** | Pandas | Tables and export |
| **Arrays** | NumPy | Numerical operations |

## File Formats

| Extension | Purpose | Where Used |
|-----------|---------|------------|
| `.nd2` | Nikon microscopy | Input (Tab 1) |
| `.tiff` | TIFF images | Input (Tab 1) |
| `.jpg` | Processed images | Throughout |
| `.png` | Background-removed | Tab 2 output |
| `.pt` | PyTorch model | YOLO weights |
| `.json` | Settings | Config storage |
| `.csv` | Data export | Tab 4 |
| `.xlsx` | Excel export | Tab 4 |
| `.zip` | Results package | Tab 4 |

## Disk Usage

Typical session (5 images):
- Uploads: ~50 MB (ND2 files)
- Processed JPGs: ~10 MB
- Segmented images: ~15 MB
- Background-removed: ~20 MB
- Analysis overlays: ~10 MB
- **Total**: ~105 MB per session

Cleanup: Delete `temp/` folder to free space

---

# 🎓 FOR THE BIOLOGIST

## What You Need to Know

1. **You don't need to understand the code**
   - Just click buttons in order: Tab 1 → 2 → 3 → 4

2. **The AI does the hard work**
   - Detects cells automatically
   - You just verify results look good

3. **Results are publication-ready**
   - Images have overlays and scale
   - Metrics are in standard units (μm²)
   - Download ZIP and you're done!

## Best Practices

1. **Start with 1-2 test images**
   - Make sure workflow works
   - Adjust settings if needed

2. **Check segmentation quality** (Tab 2)
   - Are all cells detected?
   - Any false positives?
   - Adjust confidence if needed

3. **Verify chemical detection** (Tab 3)
   - Do red overlays match staining?
   - Try adjusting sensitivity if wrong

4. **Always download ZIP** (Tab 4)
   - Contains everything
   - Organized folders
   - Ready to archive

## Common Questions

**Q: How long does analysis take?**
A: ~10-30 seconds per image (depending on size)

**Q: Can I analyze different stains?**
A: Currently only PG (lignin) and RR (pectin). Code can be modified for others.

**Q: What microscope magnification?**
A: Any! Just update pixel-to-micron in Settings.

**Q: Can I batch process 100 images?**
A: Yes! Upload all in Tab 1, then process each in Tabs 2-3.

**Q: Where are results saved?**
A: `src/gradio_ui/temp/` - Download ZIP before closing!

---

**You now have a complete understanding of every part of the UI!** 🌱🎉
