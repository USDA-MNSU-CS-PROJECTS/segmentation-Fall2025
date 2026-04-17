# 🚀 Step-by-Step Pipeline Execution Guide

This guide shows you how to run each stage of the pipeline individually, step by step.

---

## 📋 **Prerequisites**

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or use the setup script
chmod +x setup.sh
./setup.sh
```

### 2. Verify Python Version
- **Required**: Python 3.10+ (tested with 3.12)

---

## 🔄 **Stage-by-Stage Execution**

### **Stage 1: ND2 Measurements Extraction**

**Purpose**: Extract pixel-to-micron calibration data from ND2 files

**Prerequisites**:
- Place `.nd2` files in `src/data/nd2_images/input_images/`

**Command**:
```bash
python src/main/core/pixel_to_micron_measurement/process_nd2_measurements.py
```

**Output**:
- `src/data/detector_results/nd2_micron_measurements.csv`

**What it does**:
- Reads ND2 metadata
- Extracts pixel-to-micron conversion factors
- Saves calibration data for accurate measurements

---

### **Stage 2: ND2 → TIFF Conversion**

**Purpose**: Convert Nikon microscopy files to standard TIFF format

**Prerequisites**:
- `.nd2` files in `src/data/nd2_images/input_images/`

**Command**:
```bash
python src/main/core/tiff_converter.py
```

**Output**:
- `src/data/output_images/tiff_images/*.tiff`

**What it does**:
- Converts ND2 proprietary format to 8-bit TIFF
- Handles BGR → RGB channel conversion
- Normalizes data to 0-255 range

---

### **Stage 3: TIFF → JPG Conversion**

**Purpose**: Create compressed images for visualization and YOLO training

**Prerequisites**:
- TIFF files from Stage 2

**Command**:
```bash
python src/main/core/jpg_converter.py
```

**Output**:
- `src/data/output_images/jpg_images/*.jpg`

**What it does**:
- Converts TIFF to JPG format
- Reduces file size for easier handling
- Maintains image quality for analysis

---

### **Stage 4: Manual YOLO Setup** ⚠️

**Purpose**: Prepare training data for YOLO model

**This is a MANUAL step - you need to set up the training data yourself**

#### Option A: Use Existing Dataset (Recommended for Testing)
If you have the handover materials with pre-annotated data:

1. Copy training images to `src/data/yolo_train/images/`
2. Copy YOLO labels to `src/data/yolo_train/labels/`
3. Create `src/data/yolo_train/classes.txt` with class names (one per line)

Example `classes.txt`:
```
cell
```

#### Option B: Create Your Own Annotations
Use Label Studio or similar annotation tool:

1. **Install Label Studio**:
   ```bash
   pip install label-studio
   label-studio start
   ```

2. **Annotate images** at `http://localhost:8080`

3. **Export** in YOLO format to `src/data/yolo_train/`

**Required folder structure**:
```
src/data/yolo_train/
├── images/          # Training images (JPG)
├── labels/          # YOLO format labels (.txt)
└── classes.txt      # Class names (one per line)
```

---

### **Stage 5: YOLO Data YAML Generation**

**Purpose**: Create dataset configuration file for YOLO training

**Prerequisites**:
- Training images in `src/data/yolo_train/images/`
- Labels in `src/data/yolo_train/labels/`
- `classes.txt` file exists

**Command**:
```bash
python src/main/core/yolo/yolo_data_yaml_generator.py
```

**Output**:
- `src/data/yolo_train/data.yaml`

**What it does**:
- Scans training data
- Creates YOLO-compatible configuration
- Sets up paths for training

---

### **Stage 6: YOLO Training**

**Purpose**: Train YOLO11 segmentation model on your data

**Prerequisites**:
- `data.yaml` from Stage 5
- Pre-trained weights: `yolo11n-seg.pt` (should be in repo root)

**Command**:
```bash
# Default settings (150 epochs, batch size 4, image size 640)
python src/main/core/yolo/yolo_train.py

# Custom settings
python src/main/core/yolo/yolo_train.py --epochs 100 --batch 8 --imgsz 640
```

**Output**:
- `src/data/yolo_results/runs/segment/<run-name>/weights/best.pt` ⭐
- `src/data/yolo_results/runs/segment/<run-name>/weights/last.pt`
- `src/data/yolo_results/runs/segment/<run-name>/results.csv`

**Training parameters**:
- `--epochs`: Number of training epochs (default: 150)
- `--batch`: Batch size (default: 4, reduce if OOM errors)
- `--imgsz`: Image size (default: 640)

**What it does**:
- Trains YOLO11 segmentation model
- Saves checkpoints every 5 epochs
- Generates training metrics (precision, recall, mAP)

**Training time**: Varies based on hardware (GPU recommended)

---

### **Stage 7: YOLO Detection**

**Purpose**: Run inference on images using trained model

**Prerequisites**:
- Trained model from Stage 6 (`best.pt`)
- JPG images in `src/data/output_images/jpg_images/`

**Command**:
```bash
python src/main/core/yolo/yolo_detection.py
```

**Output**:
- `src/data/yolo_results/final_yolo_jpg_images/*_seg.jpg` (visualizations)
- Detection results with bounding boxes and segmentation masks

**What it does**:
- Loads trained model (automatically finds latest `best.pt`)
- Runs inference on all JPG images
- Saves visualizations with detected objects

---

### **Stage 8: YOLO Background Removal**

**Purpose**: Remove background using AI segmentation masks

**Prerequisites**:
- Trained model from Stage 6 (`best.pt`)
- JPG images in `src/data/output_images/jpg_images/`

**Command**:
```bash
python src/main/core/yolo/yolo_background_removal.py
```

**Output**:
- `src/data/yolo_results/final_yolo_jpg_images/*_nobg.jpg`

**What it does**:
- Uses YOLO segmentation masks
- Isolates detected objects
- Places objects on white canvas (5000x5000px)
- Removes all background pixels

---

### **Stage 9: Lignin Detection**

**Purpose**: Detect and quantify lignin content in PG-stained images

**Prerequisites**:
- Background-removed images from Stage 8

**Command**:
```bash
# Batch processing (recommended)
python src/main/core/detectors/"Lignin(PG)_detector.py" --batch --debug

# Single folder
python src/main/core/detectors/"Lignin(PG)_detector.py" --input src/data/yolo_results/folder_name_PG --debug
```

**Output**:
- `src/data/detector_results/lignin_detector_results/combined_lignin_results.csv`
- `src/data/detector_results/lignin_detector_results/visualizations/*_detected.jpg`

**What it does**:
- HSV color space analysis for red regions
- Detects lignin-stained areas (PG staining)
- Calculates lignin ratio (lignin pixels / total pixels)
- Generates visualization overlays

**Parameters**:
- `--batch`: Process all configured folders
- `--debug`: Show detailed processing information
- `--conf`: Confidence threshold (default: 0.25)
- `--mask-mode`: Mask mode (auto/yolo/nonwhite)

---

### **Stage 10: Pectin Detection**

**Purpose**: Detect and quantify pectin content in RR-stained images

**Prerequisites**:
- Background-removed images from Stage 8

**Command**:
```bash
# Batch processing (recommended)
python src/main/core/detectors/"Pectin(RR)_detector.py" --batch --debug

# Single folder
python src/main/core/detectors/"Pectin(RR)_detector.py" --input src/data/yolo_results/folder_name_RR --debug
```

**Output**:
- `src/data/detector_results/pectin_detector_results/combined_pectin_results.csv`
- `src/data/detector_results/pectin_detector_results/visualizations/*_detected.jpg`

**What it does**:
- HSV color space analysis for deep red/burgundy regions
- Detects pectin-stained areas (Ruthenium Red staining)
- Calculates pectin ratio (pectin pixels / total pixels)
- Generates visualization overlays

**Parameters**:
- `--batch`: Process all configured folders
- `--debug`: Show detailed processing information
- `--conf`: Confidence threshold (default: 0.25)
- `--mask-mode`: Mask mode (auto/yolo/nonwhite)

---

### **Bonus: Visualize YOLO Training Results**

**Purpose**: Generate graphs showing training metrics over epochs

**Prerequisites**:
- Training completed (Stage 6)
- `results.csv` exists in training run folder

**Commands**:
```bash
# Basic 4-panel box detection metrics
python scripts/visualize_results.py

# Comprehensive metrics + segmentation analysis
python scripts/visualize_comprehensive.py
```

**Output**:
- `src/data/yolo_results/yolo_metrics_combined.png`
- `src/data/yolo_results/yolo_segmentation_metrics.png`

**What it shows**:
- Precision, Recall, mAP50, mAP50-95 over epochs
- Box detection metrics
- Mask/segmentation metrics
- Best performance annotations

---

## 🎯 **Quick Reference: Command Summary**

```bash
# Stage 1: ND2 Measurements
python src/main/core/pixel_to_micron_measurement/process_nd2_measurements.py

# Stage 2: ND2 → TIFF
python src/main/core/tiff_converter.py

# Stage 3: TIFF → JPG
python src/main/core/jpg_converter.py

# Stage 4: Manual setup (no command)

# Stage 5: Generate data.yaml
python src/main/core/yolo/yolo_data_yaml_generator.py

# Stage 6: Train YOLO
python src/main/core/yolo/yolo_train.py --epochs 150

# Stage 7: YOLO Detection
python src/main/core/yolo/yolo_detection.py

# Stage 8: Background Removal
python src/main/core/yolo/yolo_background_removal.py

# Stage 9: Lignin Detection
python src/main/core/detectors/"Lignin(PG)_detector.py" --batch --debug

# Stage 10: Pectin Detection
python src/main/core/detectors/"Pectin(RR)_detector.py" --batch --debug

# Bonus: Visualize Results
python scripts/visualize_comprehensive.py
```

---

## 🔧 **Troubleshooting**

### Common Issues

**1. "No .nd2 files found"**
- Solution: Place `.nd2` files in `src/data/nd2_images/input_images/`

**2. "No training data found"**
- Solution: Set up `src/data/yolo_train/` with images, labels, and classes.txt

**3. "CUDA out of memory" during training**
- Solution: Reduce batch size: `--batch 2` or `--batch 1`

**4. "No trained model found"**
- Solution: Complete Stage 6 (training) first, or use pre-trained weights from handover materials

**5. "Module not found" errors**
- Solution: Run `pip install -r requirements.txt`

---

## 📊 **Expected Outputs Summary**

| Stage | Output Location | File Types |
|-------|----------------|------------|
| 1 | `detector_results/` | `.csv` |
| 2 | `output_images/tiff_images/` | `.tiff` |
| 3 | `output_images/jpg_images/` | `.jpg` |
| 4 | `yolo_train/` | Manual setup |
| 5 | `yolo_train/` | `data.yaml` |
| 6 | `yolo_results/runs/segment/` | `best.pt`, `results.csv` |
| 7 | `yolo_results/final_yolo_jpg_images/` | `*_seg.jpg` |
| 8 | `yolo_results/final_yolo_jpg_images/` | `*_nobg.jpg` |
| 9 | `detector_results/lignin_detector_results/` | `.csv`, `.jpg` |
| 10 | `detector_results/pectin_detector_results/` | `.csv`, `.jpg` |

---

## 🚀 **Alternative: Run Complete Pipeline**

Instead of running stages individually, you can run the entire pipeline:

```bash
# Run all stages
python src/main/pipeline/pipeline.py

# Skip specific stages
python src/main/pipeline/pipeline.py --skip-tiff --skip-jpg

# Custom YOLO settings
python src/main/pipeline/pipeline.py --yolo-epochs 100 --yolo-batch-size 8
```

**Available flags**:
- `--skip-nd2-measurements`
- `--skip-tiff`
- `--skip-jpg`
- `--skip-yolo-data-yaml`
- `--skip-yolo-training`
- `--skip-yolo-detection`
- `--skip-yolo-bg-removal`
- `--skip-lignin-detection`
- `--skip-pectin-detection`
- `--skip-yolo-visualization`

---

## 📚 **Additional Resources**

- **Main README**: `README.md` - Overview and quick start
- **Pipeline README**: `src/main/pipeline/README.md` - Detailed workflow
- **YOLO README**: `src/main/core/yolo/README.md` - YOLO-specific documentation
- **Detectors README**: `src/main/core/detectors/README.md` - Detector documentation
- **YouTube Tutorials**: Links in main README

---

**Happy analyzing! 🌱**

