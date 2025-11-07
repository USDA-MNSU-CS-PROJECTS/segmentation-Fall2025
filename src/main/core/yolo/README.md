# YOLO Workflow Analysis 🔍

## 🎯 **Quick Reference: Input/Output for Each Script**

```
┌──────────────────────────────────────────────────────────────────┐
│                     YOLO SCRIPTS WORKFLOW                         │
└──────────────────────────────────────────────────────────────────┘

1️⃣  yolo_data_yaml_generator.py
    📂 Reads from: src/data/yolo_train/ (images/, labels/, classes.txt)
    📤 Outputs to: src/data/yolo_train/data.yaml

2️⃣  yolo_train.py
    📂 Reads from:
       - src/data/yolo_train/data.yaml (dataset config)
       - yolo11n-seg.pt (base model from repo root)
    📤 Outputs to: src/data/yolo_results/runs/segment/<run-name>/
                   └── weights/best.pt  ⭐ (Used by steps 3 & 4)

3️⃣  yolo_detection.py
    📂 Reads from:
       - src/data/output_images/jpg_images/*.jpg (input images)
       - src/data/yolo_results/runs/segment/<latest>/weights/best.pt
    📤 Outputs to: src/data/yolo_results/final_yolo_jpg_images/
                   ├── *_seg.jpg (segmentation visualizations)
                   └── results.csv

4️⃣  yolo_background_removal.py
    📂 Reads from:
       - src/data/output_images/jpg_images/*.jpg (same as detection)
       - src/data/yolo_results/runs/segment/<latest>/weights/best.pt
    📤 Outputs to: src/data/yolo_results/final_yolo_jpg_images/
                   └── *_nobg.jpg (background removed on white canvas)

5️⃣  Lignin & Pectin Detectors (separate files)
    📂 Reads from: src/data/yolo_results/final_yolo_jpg_images/*.jpg
    📤 Outputs to: src/data/detector_results/lignin_detector_results/
                   src/data/detector_results/pectin_detector_results/
```

## 📁 **Complete File Structure & Workflow**

Based on analysis of all 4 YOLO files, here's the complete folder structure and workflow:

---

## 🚀 **Quick Start - Use Our Pre-Prepared Dataset**

**Great news!** We've already prepared a complete dataset for you to get started immediately (FOUND IN HANDOVER DOCUMENTS):

### **✅ Ready-to-Use Dataset (found in handover materials)**

- **150 annotated images** in `src/data/yolo_train/images/`
- **150 corresponding labels** in `src/data/yolo_train/labels/`
- **Pre-trained model weights** in `src/data/yolo_results/runs/segment/alfalfa-minimal-20251022-042922/weights/`
- **Dataset configuration** in `src/data/yolo_train/data.yaml`

### **🎯 Dataset Details**

- **Class**: `cell` (single class for cell wall segmentation)
- **Format**: YOLO segmentation format
- **Images**: 150 JPG images of alfalfa stem cross-sections
- **Labels**: Corresponding .txt files with polygon annotations
- **Model**: Already trained for 100 epochs with good performance

### **⚡ Immediate Usage**

```bash
# Skip training and go straight to detection/inference
python yolo_detection.py

# Or run background removal
python yolo_background_removal.py
```

**The model is already trained and ready to use!** You can start detecting cells in your images immediately.

---

## 🏷️ **Creating Your Own Dataset (Optional)**

If you want to create your own dataset or add more annotations, here's how to set up Label Studio:

### **Installation**

```bash
# On Windows with py launcher
py -m pip install label-studio

# Start Label Studio (Windows) depending on where you installed label-studio
& "C:\Users\[USERNAME]\AppData\Local\Programs\Python\Python312\Scripts\label-studio.exe" start
```

### **Step-by-Step Annotation Process**

#### **1. Start Label Studio**

- Opens in browser at `http://localhost:8080`
- Create account or sign in

#### **2. Create New Project**

- **Project Name**: "Alfalfa Cell Wall Segmentation"
- **Template**: Choose "Computer Vision" → "Object Detection with Bounding Boxes"
- **Description**: "Annotate lignin and pectin regions in alfalfa stem cross-sections"

#### **3. Configure Labeling Interface CODE (Copy paste this code into the Labeling Interface).**

**For Object Detection (Polygon Labels):**

```xml
<View>
  <Header value="Select label and click the image to start"/>
  <Image name="image" value="$image" zoom="true"/>
  <PolygonLabels name="label" toName="image" strokeWidth="3" pointSize="small" opacity="0.9">
  <Label value="cell" background="#FFA39E"/></PolygonLabels>
</View>
```

#### **4. Configure Labels**

Based on your detector files, use these class labels:

- `cell`

#### **5. Import Images**

- **Source**: Upload JPG images from `src/data/output_images/jpg_images/`
- **Batch Upload**: Select multiple images at once
- **Organization**: Consider organizing by plant ID or time point

#### **6. Annotation Guidelines**

- **Cell**: Outline the cell using polygons
- **Be consistent** with annotation style
- **Include partial objects** at image edges
- **Quality over quantity** - better to have fewer, well-annotated images
- **After annotating images** make sure to click blue Submit button so each jpg image is annotated successfully

#### **7. Export Annotations**

- Go to **Data Manager** → **Export**
- Choose **"YOLO with images"** format (this includes both images and labels)
- Download the zip file
- **File structure** will be:
  ```
  export.zip
  ├── images/
  │   ├── image1.jpg
  │   └── image2.jpg
  ├── labels/
  │   ├── image1.txt
  │   └── image2.txt
  ├── classes.txt
  └── data.yaml
  ```

#### **8. Extract to Training Folder**

```bash
# Extract the downloaded zip to src/data/yolo_train/
unzip export.zip -d src/data/yolo_train/

# Verify structure
ls src/data/yolo_train/
# Should show: images/ labels/ classes.txt data.yaml
```

#### **9. Verify Classes File**

The exported `classes.txt` should contain:

```
cell
```

### **💡 Annotation Tips**

- **Start small**: Begin with 50-100 images to test the workflow
- **Consistent labeling**: Use the same criteria for all annotations
- **Review annotations**: Double-check your work before exporting
- **Split data**: Consider annotating some images for validation
- **Use zoom**: Label Studio's zoom feature helps with precise annotations
- **Keyboard shortcuts**: Learn Label Studio shortcuts for faster annotation

---

## 🔄 **Step-by-Step Workflow**

### **Step 1: Data Preparation** (`yolo_data_yaml_generator.py`)

**📂 Current Dataset Structure (Ready to Use):**

```
src/data/yolo_train/
├── images/                    # 150 annotated images (JPG)
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ... (150 total)
├── labels/                    # 150 YOLO format labels (.txt files)
│   ├── image1.txt
│   ├── image2.txt
│   └── ... (150 total)
├── classes.txt               # Class names (one per line)
│   └── cell
├── data.yaml                 # Dataset configuration (already generated)
├── labels.cache              # Label cache file
└── notes.json                # Dataset metadata

src/data/yolo_results/runs/segment/
└── alfalfa-minimal-20251022-042922/
    ├── weights/
    │   ├── best.pt                      # ✅ Pre-trained model ready!
    │   └── last.pt
    ├── results.png                      # Training curves
    ├── confusion_matrix.png            # Model performance
    └── ... (other training outputs)
```

**📂 Alternative Structure (If Creating New Dataset):**

**📤 Output:**

- Creates `src/data/yolo_train/data.yaml` with dataset configuration

**🔧 Usage:**

```bash
python yolo_data_yaml_generator.py --dataset-root src/data/yolo_train
```

---

### **Step 2: Model Training** (`yolo_train.py`)

**What it does:** Trains the YOLO segmentation model on your annotated dataset

📂 **Input Sources:**

- `src/data/yolo_train/data.yaml` (generated in Step 1)
- `yolo11n-seg.pt` (base model from repo root)

📤 **Output Location:**

- `src/data/yolo_results/runs/segment/<run-name>/weights/best.pt` ⭐
- All subsequent scripts (detection, background removal) use this trained model

**✅ Model Already Trained!**

The model has already been trained and is ready to use:

- **Training completed**: 100 epochs
- **Model location**: `src/data/yolo_results/runs/segment/alfalfa-minimal-20251022-042922/weights/best.pt`
- **Performance**: Good results with confusion matrix and training curves available

**📂 Training Output Structure (Already Generated):**

```
src/data/yolo_results/runs/segment/
└── alfalfa-minimal-20251022-042922/    # Completed training run
    ├── weights/
    │   ├── best.pt                      # ✅ Best model weights (ready to use!)
    │   ├── last.pt                      # Latest checkpoint
    │   └── ... (checkpoints every 5 epochs)
    ├── results.png                     # Training curves
    ├── confusion_matrix.png            # Confusion matrix
    ├── val_batch0_labels.jpg           # Validation samples
    ├── val_batch0_pred.jpg              # Predictions
    └── args.yaml                       # Training arguments
```

**🔧 Re-training (Optional):**

If you want to retrain with different parameters:

```bash
python yolo_train.py --epochs 100 --imgsz 640
```

**📊 Training Parameters Used:**

- Epochs: 100
- Image size: 640x640
- Auto-detects GPU/CPU
- Saves checkpoints every 5 epochs

---

### **Step 3: Detection/Inference** (`yolo_detection.py`)

**What it does:** Runs trained YOLO model on images to create segmentation visualizations

📂 **Input Sources:**

- **Images**: `src/data/output_images/jpg_images/` (searches all subdirectories)
- **Weights**: Auto-finds latest `best.pt` from `src/data/yolo_results/runs/segment/<latest-run>/weights/`

📂 **Default Input Structure:**

```
src/data/output_images/jpg_images/
├── 20240705-20240719_10xstitch/
│   ├── image1.jpg
│   └── image2.jpg
└── [other folders]/
```

📤 **Output Structure:**

```
src/data/yolo_results/
└── final_yolo_jpg_images/
    ├── image1_seg.jpg                # With segmentation overlay
    ├── image2_seg.jpg
    └── results.csv                   # Detection statistics (image, num, area)
```

**Key Points:**

- Reads from the same input as background removal (different stages can run independently)
- Creates `*_seg.jpg` files showing detected objects
- All outputs go to the same `final_yolo_jpg_images/` folder

**📊 CSV Output Format:**

```csv
image,num,area
image1.jpg,3,12500
image2.jpg,1,8500
```

**🔧 Usage:**

```bash
# Auto-detect weights and process default folders
python yolo_detection.py

# Specify custom weights and input
python yolo_detection.py --weights path/to/best.pt --input path/to/images
```

---

### **Step 4: Background Removal** (`yolo_background_removal.py`)

**What it does:** Removes background from images, keeping only detected objects on white canvas

📂 **Input Sources:**

- **Images**: `src/data/output_images/jpg_images/` (same as detection)
- **Weights**: Auto-finds latest `best.pt` from `src/data/yolo_results/runs/segment/<latest-run>/weights/`

📂 **Default Input:**

```
src/data/output_images/jpg_images/
├── image1.jpg
├── image2.jpg
└── ...
```

📤 **Output Structure:**

```
src/data/yolo_results/
└── final_yolo_jpg_images/
    ├── image1_nobg.jpg               # Background removed (5000x5000 white canvas)
    ├── image2_nobg.jpg
    └── ...
```

**Key Points:**

- Creates `*_nobg.jpg` files (background removed)
- Places objects on white square canvas (default 5000x5000)
- If multiple objects detected, keeps the one closest to center
- High-quality output (95% JPG quality)

**🎯 Processing Features:**

- **Object Detection**: Uses YOLO segmentation to find cells
- **Background Removal**: Makes background transparent/white
- **Canvas Sizing**: Centers object on configurable white canvas
- **Multi-Object Handling**: Keeps center-most object if multiple detected
- **Quality**: Saves as high-quality JPG (95% quality)

**🔧 Usage:**

```bash
# Default settings (5000x5000 canvas)
python yolo_background_removal.py

# Custom canvas size
python yolo_background_removal.py --canvas-size 3000

# Custom input folder
python yolo_background_removal.py --input path/to/images
```

---

## 🔍 **Key Technical Details**

### **Weight File Auto-Detection**

All YOLO scripts search for weights in this order:

1. `src/data/yolo_results/runs/segment/[latest-run]/weights/best.pt` ✅ **Primary** (Current location)
2. `src/data/yolo_train/runs/segment/[latest-run]/weights/best.pt` (legacy)
3. `src/train/runs/segment/[latest-run]/weights/best.pt` (legacy)
4. `runs/segment/[latest-run]/weights/best.pt` (legacy)

**Current Model Location**: `src/data/yolo_results/runs/segment/alfalfa-minimal-20251022-042922/weights/best.pt`

### **Image Format Support**

- **Input**: JPG, JPEG, PNG
- **Output**: JPG (high quality), PNG (with transparency)

### **Path Resolution**

- Scripts use relative paths from repository root
- Auto-resolve absolute vs relative paths
- Create output directories as needed

### **Error Handling**

- Graceful handling of missing files/folders
- Detailed error messages
- Progress reporting during processing

---

## 📋 **Complete Workflow Summary**

### **🚀 Quick Start (Using Pre-Prepared Dataset)**

```bash
# Everything is ready! Just run detection/inference:
python yolo_detection.py

# Or run background removal:
python yolo_background_removal.py
```

### **🔄 Full Workflow (If Creating New Dataset)**

```bash
# 1. Prepare dataset structure
mkdir -p src/data/yolo_train/{images,labels}
# [Upload your annotated images and labels]
echo "cell" > src/data/yolo_train/classes.txt

# 2. Generate dataset config
python yolo_data_yaml_generator.py

# 3. Train model
python yolo_train.py --epochs 100

# 4. Run detection
python yolo_detection.py

# 5. Remove backgrounds
python yolo_background_removal.py
```

---

## ⚠️ **Important Notes**

1. **✅ Ready to Use**: The model is already trained and ready for detection/inference
2. **Dataset Available**: 150 annotated images with corresponding labels are included in handover docs
3. **File Formats**: All scripts expect JPG/PNG images, not ND2/TIFF
4. **Memory Usage**: Large images (5000x5000) require significant RAM/VRAM
5. **GPU Recommended**: Detection/inference benefits from CUDA acceleration
6. **Auto-Detection**: Scripts automatically find the pre-trained weights
7. **Single Class**: Current model detects "cell" class (cell wall segmentation)

---

## 🎯 **Expected Results**

**With the pre-prepared dataset, you can immediately get:**

- ✅ **Pre-trained YOLO segmentation model** (already available)
- ✅ **Detection results with visualizations** (run `yolo_detection.py`)
- ✅ **Background-removed images on white canvas** (run `yolo_background_removal.py`)
- ✅ **CSV files with detection statistics** (generated automatically)
- ✅ **Training metrics and curves** (already available in `runs/` folder)

**What you get when running detection:**

- Segmentation visualizations showing detected cell boundaries
- CSV files with detection counts and areas
- Results organized by input folder structure

**What you get when running background removal:**

- Clean images with transparent backgrounds
- Objects centered on white canvas (5000x5000 default)
- High-quality JPG output (95% quality)

---

## 📋 **Complete Input/Output Summary**

| Script                          | 📂 Input                                                                 | 📤 Output                                                                                                  | Purpose                                     |
| ------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| **yolo_data_yaml_generator.py** | `src/data/yolo_train/`<br>(images/, labels/, classes.txt)                | `src/data/yolo_train/data.yaml`                                                                            | Creates dataset configuration               |
| **yolo_train.py**               | `src/data/yolo_train/data.yaml`<br>`yolo11n-seg.pt`                      | `src/data/yolo_results/runs/segment/<run>/weights/best.pt`                                                 | Trains segmentation model                   |
| **yolo_detection.py**           | `src/data/output_images/jpg_images/*.jpg`<br>`weights/best.pt`           | `src/data/yolo_results/final_yolo_jpg_images/*_seg.jpg`<br>`results.csv`                                   | Creates segmentation visualizations         |
| **yolo_background_removal.py**  | `src/data/output_images/jpg_images/*.jpg`<br>`weights/best.pt`           | `src/data/yolo_results/final_yolo_jpg_images/*_nobg.jpg`                                                   | Removes background, centers on white canvas |
| **Lignin Detector**             | `src/data/yolo_results/final_yolo_jpg_images/*.jpg`<br>`weights/best.pt` | `src/data/detector_results/lignin_detector_results/`<br>`combined_lignin_results.csv`<br>`visualizations/` | Detects lignin regions                      |
| **Pectin Detector**             | `src/data/yolo_results/final_yolo_jpg_images/*.jpg`<br>`weights/best.pt` | `src/data/detector_results/pectin_detector_results/`<br>`combined_pectin_results.csv`<br>`visualizations/` | Detects pectin regions                      |

**Important Notes:**

- Detection and background removal read from the **same input** (`jpg_images/`)
- Both output to the **same folder** (`final_yolo_jpg_images/`)
- Lignin/Pectin detectors read from the **output** of detection/background removal
- All scripts automatically find the latest trained weights
