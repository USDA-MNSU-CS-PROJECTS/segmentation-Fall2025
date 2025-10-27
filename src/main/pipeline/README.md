# Alfalfa Segmentation Pipeline - Complete Workflow Summary 🎯

## What We've Built

I've created a comprehensive YOLO-based segmentation pipeline for your alfalfa project that includes:

### 🏗️ **Core Pipeline Components**

1. **`pipeline.py`** - Main orchestrator that runs the complete workflow
2. **ND2 → TIFF Conversion** - Converts Nikon microscopy files to standard TIFF format
3. **TIFF → JPG Conversion** - Creates compressed images for visualization
4. **Manual YOLO Setup** - User-guided training data preparation
5. **YOLO Data.yaml Generation** - Automatic dataset configuration
6. **YOLO Training** - Custom segmentation model training
7. **YOLO Detection** - Inference on images using trained model
8. **YOLO Background Removal** - AI-powered object isolation
9. **Lignin Detection** - Automated lignin content analysis
10. **Pectin Detection** - Automated pectin content analysis

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

# Test your setup
python test_pipeline.py
```

### **Step 2: Add Your Data**

- Place your ND2 files in: `src/data/nd2_images/input_images/`

### **Step 3: Run the Pipeline**

```bash
# Run complete pipeline
python src/main/pipeline/pipeline.py

# Or run with custom options
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

## 🔧 **What the Pipeline Does**

### **Stage 1: ND2 → TIFF Conversion**

- Converts your microscopy ND2 files to standard TIFF format
- Handles 8-bit conversion and channel ordering
- Outputs to: `src/data/output_images/tiff_images/`

### **Stage 2: TIFF → JPG Conversion**

- Converts TIFF files to compressed JPG format
- Creates visualization-ready images
- Outputs to: `src/data/output_images/jpg_images/`

### **Stage 3: Manual YOLO Setup**

- **PAUSE**: Pipeline pauses for user to set up training data
- User creates `src/data/yolo_train/` structure with images and labels
- User defines classes in `classes.txt`

### **Stage 4: YOLO Data.yaml Generation**

- Automatically generates YOLO dataset configuration
- Creates `data.yaml` file pointing to training data
- Handles train/validation splits if available

### **Stage 5: YOLO Training**

- Trains custom YOLO segmentation model
- Uses configurable epochs, batch size, and image size
- Saves best model weights to: `src/data/yolo_results/runs/segment/`

### **Stage 6: YOLO Detection**

- Runs inference on images using trained model
- Creates segmentation visualizations
- Outputs to: `src/data/yolo_results/final_yolo_jpg_images/`

### **Stage 7: YOLO Background Removal**

- Removes background using trained segmentation model
- Keeps only detected objects
- Creates clean images on white canvas
- Outputs to: `src/data/yolo_results/final_yolo_jpg_images/`

### **Stage 8: Lignin Detection**

- Analyzes lignin content in processed images using HSV color analysis
- Detects red regions in PG-stained images
- Calculates lignin ratios within cell regions
- Outputs to: `src/data/detector_results/lignin_detector_results/`

### **Stage 9: Pectin Detection**

- Analyzes pectin content in processed images using Ruthenium Red staining
- Detects pectin regions with multiple HSV color ranges
- Calculates pectin ratios within cell regions
- Outputs to: `src/data/detector_results/pectin_detector_results/`

## ⚙️ **Configuration Options**

### **Pipeline Config** (`config/pipeline_config.json`)

```json
{
  "run_tiff_conversion": true,
  "run_jpg_conversion": true,
  "run_yolo_data_yaml": true,
  "run_yolo_training": true,
  "run_yolo_detection": true,
  "run_yolo_background_removal": true,
  "run_lignin_detection": true,
  "run_pectin_detection": true,
  "max_images": null,
  "yolo_epochs": 100,
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

**Critical**: The pipeline includes a manual pause step where you must set up your YOLO training data:

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
