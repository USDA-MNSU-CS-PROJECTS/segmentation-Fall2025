# Alfalfa Segmentation Pipeline 🌱

## Overview

This project develops a comprehensive image analysis pipeline for alfalfa stem cross-section segmentation using YOLO-based deep learning.  
The pipeline processes microscopy images (`.nd2` format) through a complete workflow from raw data to segmented results:

**Pipeline Workflow**:

1. **ND2 → TIFF Conversion** - Convert Nikon microscopy files to standard TIFF format
2. **TIFF → JPG Conversion** - Create compressed images for visualization
3. **Manual YOLO Setup** - User prepares training data (images + labels)
4. **YOLO Training** - Train custom segmentation model
5. **YOLO Detection** - Run inference on images
6. **YOLO Background Removal** - AI-powered object isolation
7. **Lignin Detection** - Analyze lignin content in processed images
8. **Pectin Detection** - Analyze pectin content in processed images

**Current Status**: Complete YOLO-based segmentation pipeline with detector analysis ✅  
**Key Features**: Automated training, detection, background removal, and chemical composition analysis

Results will inform USDA research on alfalfa improvement and provide insights into cell wall structure and composition analysis.

---

## Features

### **Current Pipeline Features**

- ✅ **ND2 → TIFF Conversion** (batch processing)
- ✅ **TIFF → JPG Conversion** (compressed visualization)
- ✅ **Manual YOLO Data Setup** (user-guided training data preparation)
- ✅ **YOLO Data.yaml Generation** (automatic dataset configuration)
- ✅ **YOLO Model Training** (custom segmentation model training)
- ✅ **YOLO Detection** (inference on images)
- ✅ **YOLO Background Removal** (AI-powered object isolation)
- ✅ **Lignin Detection** (automated lignin content analysis)
- ✅ **Pectin Detection** (automated pectin content analysis)
- ✅ **Supercomputer Ready** (SLURM/PBS job scripts)

### **Image Analysis Features**

- ✅ **Lignin Detection** (`Lignin(PG)_detector.py`) - HSV color thresholding for red regions in PG-stained images
- ✅ **Pectin Detection** (`Pectin(RR)_detector.py`) - Ruthenium Red staining analysis for pectin content
- ✅ **YOLO Segmentation Training** (`yolo_train.py`) - Train custom segmentation models
- ✅ **YOLO Detection** (`yolo_detection.py`) - Run inference with trained models
- ✅ **YOLO Background Removal** (`yolo_background_removal.py`) - AI-powered object isolation
- ✅ **YOLO Data Preparation** (`yolo_data_yaml_generator.py`) - Generate training datasets

### **Upcoming Features** (Advanced Analysis)

- 🔄 **Enhanced Detection Models** - Improved segmentation accuracy
- 🔄 **Batch Processing Optimization** - Faster processing for large datasets
- 🔄 **Advanced Visualization** - Better result visualization and analysis tools

---

## Repository Structure

```
alfalfa-segmentation/
├── README.md
├── SUPERCOMPUTER_GUIDE.md
├── requirements.txt             # Python dependencies
├── setup.sh                    # Setup script
├── test_pipeline.py            # Test script
├── config/
│   └── pipeline_config.json    # Pipeline configuration
├── scripts/
│   ├── slurm_job.sh           # SLURM job script
│   └── pbs_job.sh            # PBS job script
└── src/
    ├── data/
    │   ├── nd2_images/
    │   │   └── input_images/    # Place .nd2 files here
    │   ├── output_images/
    │   │   ├── jpg_images/          # Generated .jpg
    │   │   ├── tiff_images/         # Generated .tif/.tiff
    │   │   └── preprocessed_images/ # Background-removed .png outputs
    │   ├── yolo_train/                # YOLO training data
    │   │   ├── images/                # Training images
    │   │   ├── labels/                # YOLO format labels
    │   │   ├── classes.txt            # Class names
    │   │   └── data.yaml              # Dataset configuration
    │   ├── yolo_results/               # YOLO outputs
    │   │   ├── runs/segment/          # Training runs and weights
    │   │   └── final_yolo_jpg_images/  # Detection and background removal outputs
    │   └── detector_results/           # Detector analysis results
    │       ├── lignin_detector_results/    # Lignin detection results and visualizations
    │       └── pectin_detector_results/    # Pectin detection results and visualizations
    └── main/
        ├── core/
        │   ├── tiff_converter.py       # ND2 → 8-bit TIFF (batch)
        │   ├── jpg_converter.py       # 8-bit TIFF → jpg
        │   ├── image_preprocessing.py   # Background removal on TIFF (batch)
        │   ├── detectors/              # Image analysis detectors
        │   │   ├── Lignin(PG)_detector.py  # Lignin detection via HSV color analysis
        │   │   ├── Pectin(RR)_detector.py  # Pectin detection via Ruthenium Red staining
        │   │   └── README.md               # Detailed detector documentation
        │   └── yolo/                  # YOLO segmentation tools
        │       ├── yolo_background_removal.py  # AI-powered background removal
        │       ├── yolo_data_yaml_generator.py # Generate YOLO training datasets
        │       ├── yolo_detection.py       # YOLO segmentation inference
        │       ├── yolo_train.py          # YOLO segmentation model training
        │       └── YOLO_WORKFLOW_ANALYSIS.md # YOLO Workflow README
        └── pipeline/
            ├── pipeline.py             # Main pipeline orchestrator
            └── SUPERCOMPUTER_GUIDE.md  # Supercomputer usage guide
```

---

## ⚠️ **Important Setup Notes**

**For New Users**: Some folders in `src/data/` will be created automatically when you run the scripts, while others require manual setup:

### **📁 Automatic Folder Creation**

These folders will be created automatically when you run the corresponding scripts:

- `src/data/output_images/` - Created by conversion scripts
- `src/data/yolo_results/` - Created by YOLO training/detection scripts
- `src/data/detector_results/lignin_detector_results/` - Created by lignin detection scripts
- `src/data/detector_results/pectin_detector_results/` - Created by pectin detection scripts

### **📁 Manual Setup Required**

You need to manually create and populate these folders:

1. **For Image Processing** (Required before conversion):

   ```
   src/data/nd2_images/input_images/  # Place your .nd2 files here
   ```

2. **For YOLO Training** (Required before training):

   ```
   src/data/yolo_train/
   ├── images/          # Upload your annotated images here
   ├── labels/          # Upload your YOLO format labels here
   └── classes.txt     # Create this file with your class names
   ```

### **🔄 Workflow Order**

1. **Manual**: Create required folders and upload your `.nd2` files to `src/data/nd2_images/input_images/`
2. **Automatic**: Convert ND2 → TIFF using `tiff_converter.py`
3. **Automatic**: Convert TIFF → JPG using `jpg_converter.py`
4. **Manual**: Set up YOLO training data in `src/data/yolo_train/` (images + labels + classes.txt)
5. **Automatic**: Run YOLO training, detection, and background removal scripts
6. **Automatic**: Run lignin and pectin detection analysis on processed images

---

Clone the repo and install dependencies:

```bash
git clone https://github.com/<your-org>/alfalfa-segmentation.git
cd alfalfa-segmentation
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Recommended Python version: **3.10+** (tested with 3.12)

---

## Local Usage (Your Computer)

### Quick Start

1. **Setup**: Run the setup script

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

**⚠️ WARNING:** Try not to push up or commit any .nd2 or .tiff images, this may break the repository. Instead, just run things locally and use the pipeline in any future work (pipeline
work in progress)

2. **Add Images**: Place your `.nd2` files into: `src/data/nd2_images/input_images`

3. **Run Individual Steps**:

   **Convert ND2 → TIFF:**

   ```bash
   python src/main/core/tiff_converter.py
   ```

   **Convert TIFF → JPG:**

   ```bash
   python src/main/core/jpg_converter.py
   ```

   **Set up YOLO Training Data:**

   - Create `src/data/yolo_train/images/` and add your training images
   - Create `src/data/yolo_train/labels/` and add your YOLO format labels
   - Create `src/data/yolo_train/classes.txt` with your class names

   **Generate YOLO Data Configuration:**

   ```bash
   python src/main/core/yolo/yolo_data_yaml_generator.py
   ```

   **Train YOLO Model:**

   ```bash
   python src/main/core/yolo/yolo_train.py --epochs 100
   ```

   **Run YOLO Detection:**

   ```bash
   python src/main/core/yolo/yolo_detection.py
   ```

   **Run YOLO Background Removal:**

   ```bash
   python src/main/core/yolo/yolo_background_removal.py
   ```

   **Run Lignin Detection:**

   ```bash
   python src/main/core/detectors/"Lignin(PG)_detector.py" --batch
   ```

   **Run Pectin Detection:**

   ```bash
   python src/main/core/detectors/"Pectin(RR)_detector.py" --batch
   ```

   **Run Complete Pipeline:**

   ```bash
   python src/main/pipeline/pipeline.py
   ```

### Local Pipeline Options

- `--skip-tiff`: Skip ND2 to TIFF conversion
- `--skip-jpg`: Skip TIFF to JPG conversion
- `--skip-yolo-data-yaml`: Skip YOLO data.yaml generation
- `--skip-yolo-training`: Skip YOLO training
- `--skip-yolo-detection`: Skip YOLO detection
- `--skip-yolo-bg-removal`: Skip YOLO background removal
- `--skip-lignin-detection`: Skip lignin detection
- `--skip-pectin-detection`: Skip pectin detection
- `--yolo-epochs N`: Set number of training epochs
- `--yolo-batch-size N`: Set training batch size
- `--yolo-image-size N`: Set training image size
- `--detector-conf N`: Set detector confidence threshold
- `--detector-mask-mode MODE`: Set detector mask mode (auto/yolo/nonwhite)
- `--config FILE`: Use custom configuration file

---

## 🚀 YOLO Segmentation Quick Start

### **⚡ Usage**

**Run Detection/Inference:**

```bash
python src/main/core/yolo/yolo_detection.py
```

**Run Background Removal:**

```bash
python src/main/core/yolo/yolo_background_removal.py
```

**Detect Lignin Content:**

```bash
python src/main/core/detectors/"Lignin(PG)_detector.py" --batch --debug
```

**Detect Pectin Content:**

```bash
python src/main/core/detectors/"Pectin(RR)_detector.py" --batch --debug
```

**Train Models:**

```bash
python src/main/core/yolo/yolo_train.py --epochs 100
```

### **📁 Dataset Location**

- **Images**: `src/data/yolo_train/images/`
- **Labels**: `src/data/yolo_train/labels/`
- **Configuration**: `src/data/yolo_train/data.yaml`

For detailed YOLO workflow information, see: [`src/main/core/yolo/YOLO_WORKFLOW_ANALYSIS.md`](src/main/core/yolo/YOLO_WORKFLOW_ANALYSIS.md)

For detailed detector documentation, see: [`src/main/core/detectors/README.md`](src/main/core/detectors/README.md)

---

## Supercomputer Usage (Large-Scale Processing)

**⚠️ For processing thousands of images on supercomputers, see the [Supercomputer Guide](src/main/pipeline/SUPERCOMPUTER_GUIDE.md)**

### Quick Supercomputer Start

1. **Upload your project** to the supercomputer
2. **Add ND2 files** to `src/data/nd2_images/input_images/`
3. **Submit job**:
   ```bash
   sbatch scripts/slurm_job.sh    # SLURM systems
   qsub scripts/pbs_job.sh        # PBS systems
   ```

### What Supercomputer Processing Includes

- **ND2 → TIFF Conversion** (batch processing)
- **Background Removal** (AI-powered preprocessing)
- **ML Data Preparation** (train/val/test splits)
- **CNN Training** (cell wall classification model)
- **Results & Visualizations** (training curves, metrics)

---

## Filename Structure & Classification

### **Filename Pattern**

`YYYY0XXX[abcd]_T[timepoint]_10xstitch_PG_removed.png`

**Example**: `20240780a_T0_10xstitch_PG_removed.png`

- `20240` = Year + space
- `780` = Plant ID (same plant = same 3-digit ID - 785 and 790 would also be the same plant as example.)
- `a,b,c,d` = 4 cross regions of the same plant
- `T0` = Time point (T0=before digestion, future: T4,T8,T24,T48,T96)

### **Current Classification** (TEMPORARY - NEEDS UPDATING)

- `thin_non_lignified`
- `thick_non_lignified`
- `thin_lignified`
- `thick_lignified`

### **Image-Based Classification**

- ✅ **Lignin Detection** - HSV color analysis identifies high/low lignin regions in PG-stained images
- ✅ **Pectin Detection** - Ruthenium Red staining analysis for pectin content in RR-stained images
- ✅ **YOLO Segmentation** - AI-powered cell wall boundary detection and background removal
- ✅ **Automated Analysis** - Batch processing with metadata extraction and visualization
- 🔄 **Thickness Measurement** - Automated wall thickness quantification
- 🔄 **Integrated Classification** - Combine all metrics for final classification

## Deliverables

---

## Team

- **Student Developer:** Evan Darling, Dade Willms, JaeJun Lee, Aaron Hansen

---

## Acknowledgements

This project is supported by the **USDA Agricultural Research Service**.  
Student contributions may be acknowledged in a future crop science journal publication.
