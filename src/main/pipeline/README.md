# Alfalfa Segmentation Pipeline - Complete Workflow Summary 🎯

## What We've Built

I've created a comprehensive YOLO-based segmentation pipeline for your alfalfa project that includes:

### 🏗️ **Core Pipeline Components**

1. **`pipeline.py`** - Main orchestrator that runs the complete workflow
2. **ND2 Measurements Extraction** - Extracts pixel-to-micron measurements from ND2 files
3. **ND2 → TIFF Conversion** - Converts Nikon microscopy files to standard TIFF format
4. **TIFF → JPG Conversion** - Creates compressed images for visualization
5. **Manual YOLO Setup** - User-guided training data preparation
6. **YOLO Data.yaml Generation** - Automatic dataset configuration
7. **YOLO Training** - Custom segmentation model training
8. **YOLO Detection** - Inference on images using trained model
9. **YOLO Background Removal** - AI-powered object isolation
10. **Lignin Detection** - Automated lignin content analysis
11. **Pectin Detection** - Automated pectin content analysis
12. **YOLO Training Results Visualization** - Generates visualization graphs from training metrics

### 🖥️ **Supercomputer Infrastructure**

1. **SLURM Job Script** (`scripts/slurm_job.sh`) - For SLURM-based systems
2. **PBS Job Script** (`scripts/pbs_job.sh`) - For PBS-based systems
3. **Configuration Files** - Easy parameter adjustment
4. **Setup Script** (`setup.sh`) - Automated environment setup

### 📚 **Documentation & Guides**

1. **Pipeline Summary** (`PIPELINE_SUMMARY.md`) - This comprehensive usage guide
2. **Updated README** - Quick start and usage options
3. **Supercomputer Guide** (`SUPERCOMPUTER_GUIDE.md`) - Comprehensive usage instructions

## 🚀 **How to Use This**

### **Step 1: Setup**

```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

### **Step 2: Add Your Data**

- Place your ND2 files in: `src/data/nd2_images/input_images/`

### **Step 3: Run the Pipeline**

```bash
# Run complete pipeline
python src/main/pipeline/pipeline.py

# Or run with custom options (just an example)
python src/main/pipeline/pipeline.py --yolo-epochs 50 --yolo-batch-size 8
```

### **Step 4: Manual YOLO Setup (When Prompted)**

When the pipeline reaches the manual pause step, you'll need to:

1. **Set up your yolo_train folder structure:**

   ```
   src/data/yolo_train/
   ├── images/           # Put your training images here
   ├── labels/           # Put your YOLO format labels here
   └── classes.txt      # Define your classes (one per line)
   ```

2. **Ensure your images and labels are properly formatted for YOLO**

3. **Press Enter to continue when ready**

### **Step 5: Monitor Progress**

The pipeline will automatically:

- Generate YOLO data.yaml configuration
- Train your segmentation model
- Run detection on your images
- Remove backgrounds using the trained model
- Analyze lignin content in processed images
- Analyze pectin content in processed images
- Generate visualization graphs from YOLO training metrics

## 📊 **Complete Workflow Diagram**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              ALFALFA PIPELINE                           │
└─────────────────────────────────────────────────────────────────────────┘

Stage 0: ND2 Measurements Extraction
  📂 src/data/nd2_images/input_images/*.nd2
  │
  └─→ 📤 src/data/detector_results/nd2_micron_measurements.csv

Stage 1: ND2 → TIFF
  📂 src/data/nd2_images/input_images/*.nd2
  │
  └─→ 📤 src/data/output_images/tiff_images/*.tiff

Stage 2: TIFF → JPG
  📂 src/data/output_images/tiff_images/*.tiff
  │
  └─→ 📤 src/data/output_images/jpg_images/*.jpg

      ↓ (Manual Setup)

Stage 3: User sets up yolo_train/ (with images/ and labels/)

  ┌──→ 📂 Training Data
  │      src/data/yolo_train/images/
  │      src/data/yolo_train/labels/
  │
Stage 4: Generate data.yaml
  └─→ 📤 src/data/yolo_train/data.yaml

Stage 5: Train Model
  📂 data.yaml + yolo11n-seg.pt
  │
  └─→ 📤 src/data/yolo_results/runs/segment/<run>/weights/best.pt

      ↓ (Uses trained weights from Stage 5)

Stage 6: YOLO Detection
  📂 src/data/output_images/jpg_images/*.jpg + best.pt
  │
  └─→ 📤 src/data/yolo_results/final_yolo_jpg_images/*_seg.jpg

Stage 7: Background Removal
  📂 src/data/output_images/jpg_images/*.jpg + best.pt
  │
  └─→ 📤 src/data/yolo_results/final_yolo_jpg_images/*_nobg.jpg

      ↓ (Reads from Stage 6 & 7 output)

Stage 8: Lignin Detection
  📂 src/data/yolo_results/final_yolo_jpg_images/*.jpg + best.pt
  │
  └─→ 📤 src/data/detector_results/lignin_detector_results/
      ├── combined_lignin_results.csv
      └── visualizations/*_detected.jpg

Stage 9: Pectin Detection
  📂 src/data/yolo_results/final_yolo_jpg_images/*.jpg + best.pt
  │
  └─→ 📤 src/data/detector_results/pectin_detector_results/
      ├── combined_pectin_results.csv
      └── visualizations/*_detected.jpg

Stage 10: YOLO Training Results Visualization
  📂 src/data/yolo_results/runs/segment/<latest-run>/results.csv
  │
  └─→ 📤 src/data/yolo_results/
      ├── yolo_metrics_visualization.png (from visualize_results.py)
      ├── yolo_metrics_combined.png (from visualize_comprehensive.py)
      └── yolo_segmentation_metrics.png (from visualize_comprehensive.py)
```

## 🔧 **What Each Stage Does**

### **Stage 0: ND2 Measurements Extraction**

📂 **Input**: `src/data/nd2_images/input_images/*.nd2`

- Reads ND2 microscopy files and extracts pixel-to-micron conversion measurements
- Uses metadata from ND2 files when available, falls back to constant value if not
- Extracts image dimensions and calculates measurements in microns

📤 **Output**: `src/data/detector_results/nd2_micron_measurements.csv`

- CSV file containing pixel-to-micron conversion ratios, image dimensions, and calculated measurements
- This data is used to ensure accurate measurements throughout the pipeline

### **Stage 1: ND2 → TIFF Conversion**

📂 **Input**: `src/data/nd2_images/input_images/*.nd2`

- Reads your microscopy ND2 files

📤 **Output**: `src/data/output_images/tiff_images/`

- Converts to standard TIFF format with 8-bit conversion

### **Stage 2: TIFF → JPG Conversion**

📂 **Input**: `src/data/output_images/tiff_images/*.tiff`

- Reads the TIFF files from Stage 1

📤 **Output**: `src/data/output_images/jpg_images/`

- Converts to compressed JPG format for visualization

### **Stage 3: Manual YOLO Setup** ⏸️

**PAUSE**: Pipeline waits for you to set up training data

- Create: `src/data/yolo_train/images/` (put training images here)
- Create: `src/data/yolo_train/labels/` (put YOLO labels here)
- Create: `src/data/yolo_train/classes.txt` (define classes)
- Press Enter when ready to continue

### **Stage 4: YOLO Data.yaml Generation**

📂 **Input**: `src/data/yolo_train/` (images, labels, classes.txt)

- Reads your training data structure

📤 **Output**: `src/data/yolo_train/data.yaml`

- Creates YOLO dataset configuration file

### **Stage 5: YOLO Training**

📂 **Input**:

- `src/data/yolo_train/data.yaml` (dataset config from Stage 4)
- `yolo11n-seg.pt` (base model from repo root)

📤 **Output**: `src/data/yolo_results/runs/segment/<run-name>/`

- `weights/best.pt` - Best model weights (used by all subsequent stages)
- `weights/last.pt` - Latest checkpoint
- Training metrics and visualizations

### **Stage 6: YOLO Detection**

📂 **Input**: `src/data/output_images/jpg_images/*.jpg`

- Reads JPG images from Stage 2
- Loads trained weights from Stage 5

📤 **Output**: `src/data/yolo_results/final_yolo_jpg_images/`

- Creates segmentation visualizations (`*_seg.jpg`)
- Generates `results.csv` with detection statistics

### **Stage 7: YOLO Background Removal**

📂 **Input**: `src/data/output_images/jpg_images/*.jpg`

- Reads same JPG images as Stage 6
- Loads trained weights from Stage 5

📤 **Output**: `src/data/yolo_results/final_yolo_jpg_images/`

- Creates background-removed images (`*_nobg.jpg`)
- Images placed on white canvas (5000x5000 default)

### **Stage 8: Lignin Detection**

📂 **Input**: `src/data/yolo_results/final_yolo_jpg_images/*.jpg`

- Reads output from Stages 6 & 7
- Uses trained YOLO model for cell detection

📤 **Output**: `src/data/detector_results/lignin_detector_results/`

- `combined_lignin_results.csv` - Analysis results
- `visualizations/` - Images with lignin regions highlighted

### **Stage 9: Pectin Detection**

📂 **Input**: `src/data/yolo_results/final_yolo_jpg_images/*.jpg`

- Reads output from Stages 6 & 7
- Uses trained YOLO model for cell detection

📤 **Output**: `src/data/detector_results/pectin_detector_results/`

- `combined_pectin_results.csv` - Analysis results
- `visualizations/` - Images with pectin regions highlighted

### **Stage 10: YOLO Training Results Visualization**

📂 **Input**: `src/data/yolo_results/runs/segment/<latest-run>/results.csv`

- Automatically finds the most recent training run folder
- Reads training metrics from results.csv

📤 **Output**: `src/data/yolo_results/`

- `yolo_metrics_visualization.png` - Basic 4-panel box detection metrics visualization
- `yolo_metrics_combined.png` - Combined metrics overview graph
- `yolo_segmentation_metrics.png` - Detailed segmentation metrics analysis (4 subplots)

**What it does:**

- Creates visualizations of YOLO training performance metrics
- Shows precision, recall, mAP50, and mAP50-95 for both box and mask detection
- Generates statistical summaries of training performance

## ⚙️ **Configuration Options** (IMPORTANT!!!)

### **Pipeline Config** (`config/pipeline_config.json`)

```json
{
  "run_nd2_measurements": true,
  "run_tiff_conversion": true,
  "run_jpg_conversion": true,
  "run_yolo_data_yaml": true,
  "run_yolo_training": true,
  "run_yolo_detection": true,
  "run_yolo_background_removal": true,
  "run_lignin_detection": true,
  "run_pectin_detection": true,
  "run_yolo_visualization": true,
  "max_images": null,
  "yolo_epochs": 150,
  "yolo_batch_size": 4,
  "yolo_image_size": 640,
  "yolo_conf_threshold": 0.25,
  "yolo_iou_threshold": 0.45,
  "yolo_canvas_size": 5000,
  "detector_conf_threshold": 0.25,
  "detector_mask_mode": "auto"
}
```

## 🎯 **Key Features**

### **YOLO-Based Segmentation**

- ✅ Complete YOLO workflow from training to inference
- ✅ Custom segmentation model training
- ✅ Automated background removal
- ✅ Configurable training parameters

### **Chemical Composition Analysis**

- ✅ Lignin detection using HSV color analysis
- ✅ Pectin detection using Ruthenium Red staining
- ✅ Automated ratio calculations within cell regions
- ✅ Batch processing with visualization outputs

### **Supercomputer Ready**

- ✅ SLURM and PBS job scripts
- ✅ Resource allocation (CPU, memory, GPU)
- ✅ Module loading and environment setup
- ✅ Comprehensive logging and error handling

### **Flexible & Configurable**

- ✅ JSON configuration files
- ✅ Command-line options
- ✅ Skip individual stages
- ✅ Process subset of images

### **Production Quality**

- ✅ Comprehensive error handling
- ✅ Detailed logging
- ✅ Progress monitoring
- ✅ Clean output organization

## 🔍 **What You'll Get**

After running the pipeline, you'll have:

1. **Processed Images**: TIFF and JPG files ready for analysis
2. **Trained Model**: YOLO segmentation model saved as weights
3. **Detection Results**: Segmentation visualizations with detected objects
4. **Clean Images**: Background-removed images with objects isolated
5. **Training Metrics**: Training curves and performance metrics
6. **Lignin Analysis**: CSV results with lignin ratios and visualizations
7. **Pectin Analysis**: CSV results with pectin ratios and visualizations

## 🚨 **Important Notes**

### **Manual Setup Step**

**Critical (can be downloaded from Handover Materials, but may need more manual annotations. This is explained more in the handover documentation)**: The pipeline includes a manual pause step where you must set up your YOLO training data:

1. **Create folder structure** in `src/data/yolo_train/`
2. **Add training images** to `images/` folder
3. **Add YOLO format labels** to `labels/` folder
4. **Define classes** in `classes.txt` file
5. **Press Enter** to continue when ready

### **YOLO Training Data Format**

- **Images**: Standard image formats (JPG, PNG, etc.)
- **Labels**: YOLO format text files with same name as images
- **Classes**: One class name per line in `classes.txt`

### **Supercomputer Resources**

- Default: 8 CPUs, 32GB RAM, 1 GPU, 4-hour runtime
- Adjust in job scripts based on your dataset size
- Monitor resource usage and adjust accordingly

### **Next Steps**

1. **Test locally first** with a small subset
2. **Set up YOLO training data** when prompted
3. **Run on supercomputer** with your full dataset
4. **Evaluate results** and adjust parameters
5. **Scale up** for larger datasets

## 🎉 **You're All Set!**

This pipeline gives you everything you need to:

- Process large-scale microscopy images on supercomputers
- Train custom YOLO segmentation models
- Run inference and background removal
- Analyze chemical composition (lignin and pectin content)
- Scale your research to handle thousands of images

The setup is designed to be simple but powerful - perfect for comprehensive alfalfa cell wall analysis! 🌱
