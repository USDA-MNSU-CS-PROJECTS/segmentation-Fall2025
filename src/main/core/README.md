# Core Image Analysis Tools 🌱

This directory contains the core image analysis tools for the alfalfa segmentation pipeline. Each script performs a specific function in the image processing workflow.

## 📋 **Complete Workflow Order**

Follow these steps **in exact order** for the full image analysis pipeline:

### **Step 0: Extract ND2 Measurements**

```bash
python pixel_to_micron_measurement/process_nd2_measurements.py
```

**Purpose**: Extracts pixel-to-micron conversion measurements from ND2 files before conversion. Uses metadata when available, falls back to constant value if not.

### **Step 1: Convert ND2 to TIFF**

```bash
python tiff_converter.py
```

**Purpose**: Converts ND2 microscopy files to 8-bit TIFF format for processing.

### **Step 2: Convert TIFF to JPG**

```bash
python jpg_converter.py
```

**Purpose**: Converts TIFF files to JPG format for Label Studio annotation.

### **Step 3: Manual Annotation (Label Studio)**

**Manual Step**: Upload JPG images to Label Studio online for annotation.

- Export annotations as **"YOLO with images"** format
- Download the annotated dataset

### **Step 4: Upload to Train Folder**

**Manual Step**: Upload the Label Studio export to:

```
src/data/yolo_train/
├── images/          # Place your annotated images here
├── labels/          # Place your YOLO format labels here
└── classes.txt     # Create this file with your class names (generated)
```

### **Step 5: Generate YOLO Dataset Configuration**

```bash
python yolo/yolo_data_yaml_generator.py --dataset-root src/data/yolo_train
```

You can also run this file on its own.

**Purpose**: Creates `data.yaml` file for YOLO training from your dataset structure.

### **Step 6: Train YOLO Model**

```bash
python yolo/yolo_train.py --epochs 100 --imgsz 640
```

You can also run this file on its own.

**Purpose**: Trains a YOLO segmentation model on your annotated data.

### **Step 7: Run Detection**

```bash
python yolo/yolo_detection.py --weights src/data/yolo_results/runs/segment/[latest-run]/weights/best.pt
```

You can also run this file on its own.

**Purpose**: Runs inference with your trained model on new images.

### **Step 8: Background Removal**

```bash
python yolo/yolo_background_removal.py --input path/to/images --canvas-size 5000
```

You can also run this file on its own.

**Purpose**: Removes backgrounds and isolates detected objects using trained YOLO model.

### **Step 9: Lignin Detection (PG-stained images)**

```bash
python detectors/"Lignin(PG)_detector.py" --batch --debug
```

**Purpose**: Detects lignin content in PG-stained images using HSV color analysis.

### **Step 10: Pectin Detection (RR-stained images)**

```bash
python detectors/"Pectin(RR)_detector.py" --batch --debug
```

**Purpose**: Detects pectin content in Ruthenium Red stained images using HSV color analysis.

---

## 🔧 **Individual Tool Descriptions**

### **process_nd2_measurements.py**

Extracts pixel-to-micron measurements from ND2 files.

- **Input**: ND2 files in `src/data/nd2_images/input_images/`
- **Output**: CSV file `src/data/detector_results/nd2_micron_measurements.csv`
- **Purpose**: Extracts pixel-to-micron conversion ratios, image dimensions, and calculated measurements in microns
- **Usage**:
  ```bash
  python pixel_to_micron_measurement/process_nd2_measurements.py
  ```
- **Note**: This step runs automatically in the pipeline before TIFF conversion

### **tiff_converter.py**

Converts ND2 microscopy files to 8-bit TIFF format.

- **Input**: ND2 files in `src/data/nd2_images/input_images/`
- **Output**: TIFF files in `src/data/output_images/tiff_images/`
- **Usage**: `python tiff_converter.py`

### **jpg_converter.py**

Converts TIFF files to high-quality JPG format.

- **Input**: TIFF files from previous step
- **Output**: JPG files in `src/data/output_images/jpg_images/`
- **Usage**: `python jpg_converter.py`

### **image_preprocessing.py** (DEPRECATED)

Performs background removal on TIFF images using AI.

- **Input**: TIFF files
- **Output**: Preprocessed PNG files in `src/data/output_images/preprocessed_images/`
- **Usage**: `python image_preprocessing.py`

### **Lignin(PG)\_detector.py**

Detects lignin content in PG-stained images using HSV color analysis.

- **Purpose**: Identifies red regions (lignin) in PG-stained images using color thresholding
- **Input**: JPG images from YOLO background removal (`src/data/yolo_results/[folder]_PG/`)
- **Output**:
  - CSV results with lignin ratios and metadata (`src/data/detector_results/lignin_detector_results/`)
  - Visualization images showing detected regions
- **Features**:
  - Automatic cell detection using YOLO or white-background heuristic
  - HSV color space analysis for red/lignin detection
  - Batch processing of multiple folders
  - Metadata extraction from filename patterns
- **Usage**:

  ```bash
  # Batch mode (processes all configured folders)
  python detectors/"Lignin(PG)_detector.py" --batch --debug

  # Single folder mode
  python detectors/"Lignin(PG)_detector.py" --input src/data/yolo_results/folder_PG --debug

  # Custom weights and confidence
  python detectors/"Lignin(PG)_detector.py" --weights path/to/best.pt --conf 0.3 --batch
  ```

### **Pectin(RR)\_detector.py**

Detects pectin content in Ruthenium Red stained images using HSV color analysis.

- **Purpose**: Identifies pink/red regions (pectin) in RR-stained images using color thresholding
- **Input**: JPG images from YOLO background removal (`src/data/yolo_results/[folder]_RR/`)
- **Output**:
  - CSV results with pectin ratios and metadata (`src/data/detector_results/pectin_detector_results/`)
  - Visualization images showing detected regions
- **Features**:
  - Automatic cell detection using YOLO or white-background heuristic
  - HSV color space analysis for deep red/brown pectin detection
  - Batch processing of multiple folders
  - Metadata extraction from filename patterns
- **Usage**:

  ```bash
  # Batch mode (processes all configured folders)
  python detectors/"Pectin(RR)_detector.py" --batch --debug

  # Single folder mode
  python detectors/"Pectin(RR)_detector.py" --input src/data/yolo_results/folder_RR --debug

  # Custom weights and confidence
  python detectors/"Pectin(RR)_detector.py" --weights path/to/best.pt --conf 0.3 --batch
  ```

### **yolo_data_yaml_generator.py**

Generates YOLO dataset configuration file.

- **Purpose**: Creates `data.yaml` for YOLO training
- **Input**: Dataset structure in `src/data/yolo_train/`
- **Output**: `src/data/yolo_train/data.yaml`
- **Usage**:
  ```bash
  python yolo/yolo_data_yaml_generator.py --dataset-root src/data/yolo_train
  ```

### **yolo_train.py**

Trains YOLO segmentation models.

- **Purpose**: Trains custom segmentation model on annotated data
- **Input**: `src/data/yolo_train/data.yaml` + annotated images
- **Output**: Trained weights in `src/data/yolo_results/runs/segment/[run-name]/weights/`
- **Usage**:
  ```bash
  python yolo/yolo_train.py --epochs 100 --imgsz 640
  ```

### **yolo_detection.py**

Runs YOLO inference on images.

- **Purpose**: Detects and segments objects using trained model
- **Input**: Images + trained weights
- **Output**: Segmentation results + visualizations
- **Usage**:
  ```bash
  python yolo/yolo_detection.py --weights path/to/best.pt --input path/to/images
  ```

### **yolo_background_removal.py**

Removes backgrounds using YOLO segmentation.

- **Purpose**: Isolates detected objects and removes backgrounds
- **Input**: Images + trained YOLO model
- **Output**: Cropped objects on white square canvas
- **Usage**:
  ```bash
  python yolo/yolo_background_removal.py --input path/to/images --canvas-size 5000
  ```

---

## 📁 **Directory Structure**

```
src/main/core/
├── README.md                           # This file
├── tiff_converter.py                  # ND2 → TIFF conversion
├── jpg_converter.py                   # TIFF → JPG conversion
├── image_preprocessing.py             # Background removal (deprecated)
├── pixel_to_micron_measurement/       # Pixel-to-micron measurement utilities
│   ├── process_nd2_measurements.py    # Extract measurements from ND2 files
│   └── README.md                       # Measurement utilities documentation
├── detectors/                         # Image analysis detectors
│   ├── Lignin(PG)_detector.py         # Lignin detection
│   ├── Pectin(RR)_detector.py         # Pectin detection
│   └── README.md                       # Detector documentation
└── yolo/                              # YOLO segmentation tools
    ├── yolo_data_yaml_generator.py    # YOLO dataset config
    ├── yolo_train.py                  # YOLO model training
    ├── yolo_detection.py              # YOLO inference
    ├── yolo_background_removal.py     # YOLO background removal
    └── README.md                       # YOLO workflow documentation
```

---

## 🎯 **Quick Start Examples**

### **Basic Workflow**

```bash
# 0. Extract ND2 measurements (optional but recommended)
python pixel_to_micron_measurement/process_nd2_measurements.py

# 1. Convert ND2 files
python tiff_converter.py

# 2. Convert to JPG for annotation
python jpg_converter.py

# 3. [Manual: Annotate in Label Studio]

# 4. [Manual: Upload to src/data/yolo_train/]

# 5. Generate dataset config
python yolo/yolo_data_yaml_generator.py

# 6. Train model
python yolo/yolo_train.py --epochs 50

# 7. Run detection
python yolo/yolo_detection.py

# 8. Remove backgrounds
python yolo/yolo_background_removal.py --input src/data/jpg_images/sample_folder

# 9. Analyze lignin content (PG-stained images)
python detectors/"Lignin(PG)_detector.py" --batch --debug

# 10. Analyze pectin content (RR-stained images)
python detectors/"Pectin(RR)_detector.py" --batch --debug
```

### **Analysis Only (Skip Training)**

```bash
# Analyze lignin content (requires background-removed PG images)
python detectors/"Lignin(PG)_detector.py" --input src/data/yolo_results/folder_PG --debug

# Analyze pectin content (requires background-removed RR images)
python detectors/"Pectin(RR)_detector.py" --input src/data/yolo_results/folder_RR --debug
```

---

## ⚠️ **Important Notes**

1. **File Paths**: Most scripts use relative paths from the repository root
2. **Dependencies**: Ensure all requirements are installed (`pip install -r requirements.txt`)
3. **GPU**: YOLO training benefits from GPU acceleration (CUDA)
4. **Memory**: Large images may require significant RAM/VRAM
5. **File Formats**: Scripts expect specific input formats (ND2, TIFF, JPG)
6. **Do not upload mass images to GitHub**: This may break the repository, this is all for testing locally.

---

## 🔍 **Troubleshooting**

### **Common Issues**

- **"No images found"**: Check input folder paths and file extensions
- **"Weights not found"**: Ensure YOLO training completed successfully
- **"CUDA out of memory"**: Reduce batch size or image size
- **"Permission denied"**: Check file permissions and folder access
