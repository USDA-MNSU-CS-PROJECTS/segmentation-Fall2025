# 🎨 Gradio UI Architecture for Alfalfa Segmentation

## 📋 Overview

A complete web-based interface for biologists to analyze alfalfa stem cross-sections without touching code. Built with Gradio for easy deployment and beautiful UX.

---

## 🏗️ System Architecture

### **3-Tier Architecture**

```
┌─────────────────────────────────────┐
│     Frontend (Gradio Web UI)        │  ← Biologist interacts here
├─────────────────────────────────────┤
│     Backend (Processing Logic)      │  ← Wraps existing pipeline
├─────────────────────────────────────┤
│     Storage (File System + Cache)   │  ← Temp data and results
└─────────────────────────────────────┘
```

---

## 📂 File Structure

```
USDA-Segmentation-S2/
├── gradio_app.py                    # Main Gradio application (entry point)
│
├── src/gradio_ui/
│   ├── __init__.py
│   ├── config.py                    # Configuration management
│   │
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── image_processor.py       # Handles ND2/TIFF/JPG conversion
│   │   ├── segmentation.py          # YOLO model wrapper
│   │   ├── chemical_analysis.py     # Lignin & Pectin detectors
│   │   ├── results_manager.py       # Results aggregation & export
│   │   └── utils.py                 # Helper functions
│   │
│   └── temp/                        # Session temporary files
│       ├── uploads/                 # Uploaded images
│       ├── processed/               # Converted & segmented images
│       ├── results/                 # Analysis results (CSV, images)
│       └── cache/                   # Session metadata (JSON)
│
├── src/main/core/                   # Existing pipeline (reused)
│   ├── yolo/
│   ├── detectors/
│   └── ...
│
└── src/data/                        # Existing data structure (untouched)
```

---

## 🎯 5-Tab Interface Design

### **Tab 1: 📤 Upload & Process**

**Purpose**: Upload and convert microscopy images

**UI Components**:
- Multi-file uploader (drag & drop)
- Format filter: `.nd2`, `.tiff`, `.jpg`, `.png`
- Process button
- Status log (real-time)
- Gallery of converted images

**Backend Functions**:
- `process_uploads()` - Converts ND2 → TIFF → JPG
- Extracts pixel-to-micron metadata
- Stores in `temp/processed/`

**User Flow**:
1. Drag & drop images
2. Click "Convert Images"
3. View converted images in gallery
4. Proceed to Tab 2

---

### **Tab 2: 🔬 Segmentation**

**Purpose**: Run AI model to detect and segment cells

**UI Components**:
- Image selector (dropdown)
- Confidence threshold slider (0.1-0.9)
- "Run Segmentation" button
- Side-by-side image comparison:
  - Original image
  - Segmented overlay
  - Background-removed version

**Backend Functions**:
- `run_segmentation()` - Loads YOLO model, runs inference
- Creates visualization overlays
- Generates background-removed images
- Saves to `temp/processed/`

**User Flow**:
1. Select image from dropdown
2. Adjust confidence if needed
3. Click "Run Segmentation"
4. View results (3 images)
5. Download or proceed to Tab 3

---

### **Tab 3: 🧪 Chemical Analysis**

**Purpose**: Detect lignin and pectin composition

**UI Components**:
- Checkbox group: Select analysis types
  - [ ] Lignin (PG staining)
  - [ ] Pectin (Ruthenium Red)
- Image selector (background-removed images)
- "Run Analysis" button
- Side-by-side detection overlays
- Results table (metrics)

**Backend Functions**:
- `run_lignin_analysis()` - HSV color detection for red regions
- `run_pectin_analysis()` - HSV detection for burgundy regions
- Calculates:
  - Pixel counts
  - Ratios (chemical pixels / total pixels)
  - Area in microns² (using pixel-to-micron conversion)

**User Flow**:
1. Select which analyses to run
2. Choose background-removed image
3. Click "Run Analysis"
4. View colored overlays
5. Review quantitative table

---

### **Tab 4: 📊 Results & Export**

**Purpose**: View all results and download data

**UI Components**:
- Session summary (text box):
  - # images processed
  - # segmentations completed
  - # chemical analyses done
- Results gallery (all visualizations)
- Export format selector:
  - CSV (tables only)
  - Excel (formatted workbook)
  - ZIP (all files: images + CSVs)
- Download button
- File download link

**Backend Functions**:
- `get_session_summary()` - Aggregates all results
- `export_results()` - Creates downloadable package
- Generates comprehensive CSV with all metrics

**User Flow**:
1. Review session summary
2. Browse all generated images
3. Choose export format
4. Click "Download Results"
5. Save to local machine

---

### **Tab 5: ⚙️ Settings**

**Purpose**: Configure model and analysis parameters

**UI Components**:
- **Model Settings**:
  - Model path input
  - "Check Model" button
  - Model status display
  
- **Detection Parameters**:
  - Default confidence slider
  - IOU threshold slider
  
- **Chemical Analysis**:
  - Pixel-to-micron fallback value
  - Lignin sensitivity slider
  - Pectin sensitivity slider
  
- "Save Settings" button

**Backend Functions**:
- `check_model_status()` - Verifies model exists
- `save_settings()` - Updates config file
- Persists settings across sessions

**User Flow**:
1. (Optional) Adjust default parameters
2. Check model status
3. Save settings
4. Return to analysis tabs

---

## 🔧 Backend Module Details

### **`config.py` - Configuration Management**

```python
class UIConfig:
    - model_path: Path to YOLO best.pt
    - temp_dir: Path to temp/
    - confidence_default: 0.25
    - iou_threshold: 0.45
    - pixel_to_micron_fallback: 0.9785
    
    Methods:
    - load_settings()
    - save_settings()
    - get_model_path()
```

### **`image_processor.py` - Image Conversion**

Wraps existing pipeline components:
```python
class ImageProcessor:
    - process_uploads(files) → (status, gallery)
    - convert_nd2_to_tiff()
    - convert_tiff_to_jpg()
    - extract_metadata()
```

Uses: `src/main/core/tiff_converter.py`, `jpg_converter.py`

### **`segmentation.py` - YOLO Wrapper**

```python
class SegmentationEngine:
    - run_segmentation(image, conf) → (status, orig, seg, nobg)
    - load_model()
    - detect_cells()
    - create_visualization()
    - remove_background()
```

Uses: `src/main/core/yolo/yolo_detection.py`, `yolo_background_removal.py`

### **`chemical_analysis.py` - Detector Wrapper**

```python
class ChemicalAnalyzer:
    - run_analysis(image, types) → (status, lig_viz, pec_viz, table)
    - analyze_lignin()
    - analyze_pectin()
    - create_overlay()
    - calculate_metrics()
```

Uses: `src/main/core/detectors/Lignin(PG)_detector.py`, `Pectin(RR)_detector.py`

### **`results_manager.py` - Results Aggregation**

```python
class ResultsManager:
    - get_session_summary() → (summary_text, gallery)
    - export_results(format) → file_path
    - aggregate_csv()
    - create_zip_package()
```

---

## 💾 Data Flow

### **Upload → Process Flow**

```
User uploads .nd2 file
    ↓
ImageProcessor.process_uploads()
    ↓
Converts: .nd2 → .tiff → .jpg
    ↓
Saves to: temp/processed/image_name.jpg
    ↓
Updates gallery in UI
```

### **Segmentation Flow**

```
User selects image + confidence
    ↓
SegmentationEngine.run_segmentation()
    ↓
Loads YOLO model (cached)
    ↓
Runs inference
    ↓
Generates 3 outputs:
  - Original (input)
  - Segmented overlay (boxes + masks)
  - Background removed (for chemistry)
    ↓
Saves to temp/processed/
    ↓
Updates UI images
```

### **Chemical Analysis Flow**

```
User selects analysis types + image
    ↓
ChemicalAnalyzer.run_analysis()
    ↓
For each selected type:
  - Run HSV color detection
  - Create colored overlay
  - Calculate metrics
    ↓
Saves overlays to temp/results/
    ↓
Updates UI with visualizations + table
```

---

## 🚀 Deployment Options

### **Option 1: Local Deployment** (Recommended for biologist)

```bash
# Install dependencies
pip install gradio pandas matplotlib opencv-python ultralytics

# Run app
python gradio_app.py

# Access at: http://localhost:7860
```

### **Option 2: Remote Access (Gradio Share)**

```python
# In gradio_app.py
app.launch(share=True)  # Creates public URL for 72 hours
```

### **Option 3: Server Deployment** (For lab use)

```bash
# Run on server
nohup python gradio_app.py &

# Access from lab computers: http://server-ip:7860
```

### **Option 4: Docker Container** (Advanced)

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "gradio_app.py"]
```

---

## 🎓 User Documentation (for Biologist)

Create a simple PDF guide:

1. **Getting Started** - How to launch the app
2. **Upload Images** - Drag & drop tutorial
3. **Run Analysis** - Click-by-click workflow
4. **Interpret Results** - What the metrics mean
5. **Export Data** - Download for publications
6. **Troubleshooting** - Common issues

---

## ✨ Key Features for Biologist

✅ **No coding required** - Point and click interface  
✅ **Visual feedback** - See results immediately  
✅ **Batch processing** - Analyze multiple images  
✅ **Download everything** - Get all data + images  
✅ **Adjustable parameters** - Control sensitivity  
✅ **Session persistence** - Don't lose work  
✅ **Professional outputs** - Publication-ready images  

---

**Next Steps**: Implement the backend modules!
