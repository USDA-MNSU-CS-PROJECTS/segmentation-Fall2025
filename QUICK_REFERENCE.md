# 🚀 Quick Reference Card - Pipeline Commands

## 📋 One-Line Commands for Each Stage

### **Setup**
```bash
pip install -r requirements.txt
```

### **Stage 1: ND2 Measurements**
```bash
python src/main/core/pixel_to_micron_measurement/process_nd2_measurements.py
```
📂 Input: `src/data/nd2_images/input_images/*.nd2`  
📤 Output: `src/data/detector_results/nd2_micron_measurements.csv`

---

### **Stage 2: ND2 → TIFF**
```bash
python src/main/core/tiff_converter.py
```
📂 Input: `src/data/nd2_images/input_images/*.nd2`  
📤 Output: `src/data/output_images/tiff_images/*.tiff`

---

### **Stage 3: TIFF → JPG**
```bash
python src/main/core/jpg_converter.py
```
📂 Input: `src/data/output_images/tiff_images/*.tiff`  
📤 Output: `src/data/output_images/jpg_images/*.jpg`

---

### **Stage 4: Manual Setup** ⚠️
**No command - Manual action required**

Create folder structure:
```
src/data/yolo_train/
├── images/       # Add training images here
├── labels/       # Add YOLO labels here
└── classes.txt   # Create with class names
```

---

### **Stage 5: Generate data.yaml**
```bash
python src/main/core/yolo/yolo_data_yaml_generator.py
```
📂 Input: `src/data/yolo_train/images/`, `labels/`, `classes.txt`  
📤 Output: `src/data/yolo_train/data.yaml`

---

### **Stage 6: Train YOLO**
```bash
# Default (150 epochs, batch 4)
python src/main/core/yolo/yolo_train.py

# Custom settings
python src/main/core/yolo/yolo_train.py --epochs 100 --batch 8 --imgsz 640
```
📂 Input: `data.yaml`, `yolo11n-seg.pt`  
📤 Output: `src/data/yolo_results/runs/segment/<run>/weights/best.pt`

---

### **Stage 7: YOLO Detection**
```bash
python src/main/core/yolo/yolo_detection.py
```
📂 Input: `jpg_images/*.jpg`, `best.pt`  
📤 Output: `src/data/yolo_results/final_yolo_jpg_images/*_seg.jpg`

---

### **Stage 8: Background Removal**
```bash
python src/main/core/yolo/yolo_background_removal.py
```
📂 Input: `jpg_images/*.jpg`, `best.pt`  
📤 Output: `src/data/yolo_results/final_yolo_jpg_images/*_nobg.jpg`

---

### **Stage 9: Lignin Detection**
```bash
python src/main/core/detectors/"Lignin(PG)_detector.py" --batch --debug
```
📂 Input: `final_yolo_jpg_images/*_nobg.jpg`  
📤 Output: `src/data/detector_results/lignin_detector_results/`

---

### **Stage 10: Pectin Detection**
```bash
python src/main/core/detectors/"Pectin(RR)_detector.py" --batch --debug
```
📂 Input: `final_yolo_jpg_images/*_nobg.jpg`  
📤 Output: `src/data/detector_results/pectin_detector_results/`

---

### **Bonus: Visualize Training**
```bash
# Comprehensive visualization
python scripts/visualize_comprehensive.py

# Basic 4-panel visualization
python scripts/visualize_results.py
```
📂 Input: `yolo_results/runs/segment/<run>/results.csv`  
📤 Output: `src/data/yolo_results/*.png`

---

## 🔄 Run Complete Pipeline

```bash
# All stages
python src/main/pipeline/pipeline.py

# Skip specific stages
python src/main/pipeline/pipeline.py --skip-tiff --skip-jpg --skip-yolo-training

# Custom YOLO settings
python src/main/pipeline/pipeline.py --yolo-epochs 100 --yolo-batch-size 8
```

---

## 🛠️ Common Parameters

### YOLO Training
- `--epochs N` - Number of training epochs (default: 150)
- `--batch N` - Batch size (default: 4)
- `--imgsz N` - Image size (default: 640)

### Detectors
- `--batch` - Process all configured folders
- `--debug` - Show detailed information
- `--conf N` - Confidence threshold (default: 0.25)
- `--mask-mode MODE` - Mask mode (auto/yolo/nonwhite)

### Pipeline
- `--skip-<stage>` - Skip specific stage
- `--yolo-epochs N` - Training epochs
- `--yolo-batch-size N` - Batch size
- `--config FILE` - Custom config file

---

## 📊 Expected Outputs

| Stage | Output Folder | Files |
|-------|--------------|-------|
| 1 | `detector_results/` | `nd2_micron_measurements.csv` |
| 2 | `output_images/tiff_images/` | `*.tiff` |
| 3 | `output_images/jpg_images/` | `*.jpg` |
| 5 | `yolo_train/` | `data.yaml` |
| 6 | `yolo_results/runs/segment/` | `best.pt`, `results.csv` |
| 7 | `yolo_results/final_yolo_jpg_images/` | `*_seg.jpg` |
| 8 | `yolo_results/final_yolo_jpg_images/` | `*_nobg.jpg` |
| 9 | `detector_results/lignin_detector_results/` | CSV + visualizations |
| 10 | `detector_results/pectin_detector_results/` | CSV + visualizations |

---

## ⚡ Quick Start (If You Have Pre-Trained Model)

If you already have trained weights from handover materials:

```bash
# 1. Place JPG images in jpg_images/
# 2. Place trained model in yolo_results/runs/segment/<run>/weights/best.pt
# 3. Run detection
python src/main/core/yolo/yolo_detection.py

# 4. Run background removal
python src/main/core/yolo/yolo_background_removal.py

# 5. Run detectors
python src/main/core/detectors/"Lignin(PG)_detector.py" --batch --debug
python src/main/core/detectors/"Pectin(RR)_detector.py" --batch --debug
```

---

## 🚨 Troubleshooting Quick Fixes

| Error | Solution |
|-------|----------|
| "No .nd2 files found" | Add files to `src/data/nd2_images/input_images/` |
| "No training data" | Set up `yolo_train/` folder structure |
| "CUDA out of memory" | Use `--batch 2` or `--batch 1` |
| "No trained model" | Complete training or use pre-trained weights |
| "Module not found" | Run `pip install -r requirements.txt` |

---

**For detailed explanations, see `STEP_BY_STEP_GUIDE.md`**

