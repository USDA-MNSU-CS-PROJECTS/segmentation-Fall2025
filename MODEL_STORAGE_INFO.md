# 🤖 Model Storage and Hosting Information

## 📦 **Two Types of Models in This Project**

### **1. Base Pre-trained Model (YOLO11n-seg.pt)**

**What it is**: Ultralytics YOLO11 nano segmentation model pre-trained on COCO dataset

**Location**: Should be in repository root
- Path: `yolo11n-seg.pt`
- Referenced in: `src/main/core/yolo/yolo_train.py` (line 42)

**Hosting**: 
- ✅ **Hosted by Ultralytics** on HuggingFace
- Download link: https://huggingface.co/Ultralytics/YOLO11/blob/main/yolo11n-seg.pt
- **Automatically downloaded** by Ultralytics library when you run training

**Status in your repo**: 
- ❌ NOT currently in your repository (file not found)
- ✅ Will be auto-downloaded when you run training for the first time
- File size: ~6 MB (YOLO11n is the "nano" lightweight version)

**How to get it**:
```bash
# Option 1: Auto-download (recommended)
# Just run training - it will download automatically
python src/main/core/yolo/yolo_train.py --epochs 1

# Option 2: Manual download
# Download from HuggingFace and place in repo root
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n-seg.pt
```

---

### **2. Custom Trained Model (best.pt)**

**What it is**: Your custom YOLO11 model fine-tuned on alfalfa cell images

**Location**: Saved in training output directory
- Path: `src/data/yolo_results/runs/segment/<run-name>/weights/best.pt`
- Example: `src/data/yolo_results/runs/segment/alfalfa-minimal-20251022-042922/weights/best.pt`

**Hosting**: 
- ❌ **NOT currently in your repository** (folder doesn't exist locally)
- ✅ **Mentioned in README** as being uploaded to Box (line 179)
- ✅ **Available in "handover materials"** according to YOLO README (line 56)

**From the README**:
> "Place runs folder here (this is our trained model we uploaded to Box or from the client or handover materials)"

**Status**:
- ✅ Model was previously trained by the team
- ✅ Uploaded to **Box** cloud storage
- ✅ Available in handover/client materials
- ❌ Not committed to Git repository (too large for GitHub)

**Training Details** (from documentation):
- **Dataset**: 150 annotated alfalfa cell images
- **Training duration**: 100 epochs
- **Class**: Single class "cell" for cell wall segmentation
- **Performance**: "Good performance" according to team
- **Training date**: October 22, 2025 (based on run name)

---

## 🗂️ **Where Models Are Stored**

### **In Version Control (GitHub)**
- ❌ Neither model is stored in Git
- **Reason**: `.pt` files are large binary files (not suitable for Git)
- **Good practice**: Model weights should not be committed to version control

### **In Cloud Storage (Box)**
- ✅ Custom trained model (`best.pt`) uploaded to Box
- ✅ Complete training run folder uploaded
- ✅ Available for download from handover materials

### **Auto-Downloaded**
- ✅ Base model (`yolo11n-seg.pt`) auto-downloaded by Ultralytics library
- **Cached location**: Usually in `~/.cache/ultralytics/` or downloaded to repo root

### **Generated During Training**
- ✅ New models created when you run `yolo_train.py`
- **Output**: `src/data/yolo_results/runs/segment/<run-name>/weights/`
  - `best.pt` - Best performing model (highest mAP)
  - `last.pt` - Most recent checkpoint
  - Checkpoints saved every 5 epochs

---

## 📥 **How to Get the Pre-Trained Custom Model**

### **Option 1: Download from Handover Materials**

If you have access to the handover/client materials:

1. **Download the complete runs folder** from Box
2. **Place it in**: `src/data/yolo_results/runs/`
3. **Verify structure**:
   ```
   src/data/yolo_results/
   └── runs/
       └── segment/
           └── alfalfa-minimal-20251022-042922/
               └── weights/
                   ├── best.pt
                   └── last.pt
   ```

### **Option 2: Train Your Own Model**

If you don't have access to handover materials:

```bash
# 1. Set up training data (Stage 4)
# Add images to: src/data/yolo_train/images/
# Add labels to: src/data/yolo_train/labels/
# Create: src/data/yolo_train/classes.txt

# 2. Generate data.yaml (Stage 5)
python src/main/core/yolo/yolo_data_yaml_generator.py

# 3. Train model (Stage 6)
python src/main/core/yolo/yolo_train.py --epochs 150

# Model will be saved to:
# src/data/yolo_results/runs/segment/<new-run-name>/weights/best.pt
```

**Training time**: Varies by hardware
- **With GPU**: ~2-4 hours for 150 epochs
- **CPU only**: Much longer (not recommended)

---

## 🎯 **Model File Sizes**

| Model | Size | Purpose |
|-------|------|---------|
| `yolo11n-seg.pt` | ~6 MB | Base pre-trained model |
| `best.pt` | ~6-10 MB | Your custom trained model |
| `last.pt` | ~6-10 MB | Latest training checkpoint |

**Note**: These are relatively small because YOLO11n is the "nano" variant

---

## 🚀 **Using the Models**

### **If You Have Pre-Trained Model from Box**

```bash
# 1. Download and place runs folder in correct location
# 2. Skip training and go straight to detection

python src/main/core/yolo/yolo_detection.py
python src/main/core/yolo/yolo_background_removal.py
```

**The scripts automatically find the latest trained model** in:
`src/data/yolo_results/runs/segment/<latest>/weights/best.pt`

### **If You Need to Train from Scratch**

Follow the complete pipeline from Stage 1-10 (see STEP_BY_STEP_GUIDE.md)

---

## 📋 **Model Hosting Summary**

| Model | Hosted Where | Access Method |
|-------|-------------|---------------|
| **Base YOLO11n-seg** | Ultralytics HuggingFace | Auto-download or manual download |
| **Custom best.pt** | Box cloud storage | Download from handover materials |
| **Training runs** | Box cloud storage | Download from handover materials |
| **New trained models** | Local (generated) | Train yourself using pipeline |

---

## 💡 **Recommendations**

1. **For Quick Start**: 
   - Get pre-trained model from Box/handover materials
   - Skip training stage
   - Jump to detection/analysis

2. **For Custom Training**:
   - Prepare your own annotated dataset
   - Train new model with your data
   - Takes longer but gives you control

3. **Model Management**:
   - Keep trained models in Box or cloud storage
   - Don't commit `.pt` files to Git
   - Document which model version was used for results

---

## 🔍 **How Scripts Find Models**

The detection and background removal scripts automatically locate models:

```python
# From yolo_detection.py and yolo_background_removal.py
# They search for the LATEST training run
runs_dir = repo / "src/data/yolo_results/runs/segment"
run_folders = [d for d in runs_dir.iterdir() if d.is_dir()]
latest_run = max(run_folders, key=lambda p: p.stat().st_mtime)
weights_path = latest_run / "weights/best.pt"
```

**Translation**: Scripts find the most recently modified training run and use `best.pt` from it.

---

## ❓ **Common Questions**

**Q: Where is yolo11n-seg.pt?**
- A: Auto-downloaded by Ultralytics library when you train. Or download from HuggingFace.

**Q: Where is the custom trained model?**
- A: In Box cloud storage (handover materials) or you need to train it yourself.

**Q: Why aren't models in the GitHub repo?**
- A: Too large for Git. Best practice is to store in cloud storage (Box/S3/etc.)

**Q: Can I use the model without training?**
- A: Yes! Download pre-trained model from Box and use detection/background removal scripts.

**Q: How do I share my trained model?**
- A: Upload the entire `runs/segment/<run-name>/` folder to Box or cloud storage.

---

**Need help accessing handover materials? Contact the original development team or USDA project coordinator.**
