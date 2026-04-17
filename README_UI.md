# 🌱 Gradio UI - Quick Reference

## 🚀 **UI is Running at**: http://localhost:7860

---

## 📚 **Complete Documentation**

For detailed step-by-step breakdown of every feature, see:
👉 **[UI_COMPLETE_BREAKDOWN.md](UI_COMPLETE_BREAKDOWN.md)** (1000+ lines, covers everything!)

---

## ⚡ Quick Start Guide

### **5-Tab Workflow**

```
Tab 1 → Tab 2 → Tab 3 → Tab 4 → Tab 5
Upload  Segment  Analyze  Export  Settings
```

---

## 📋 **Each Tab - Quick Summary**

### **Tab 1: 📤 Upload & Process**
- **Does**: Converts .nd2/.tiff to JPG
- **Input**: Microscopy images (any format)
- **Output**: JPGs in `temp/processed/`
- **Time**: ~5 seconds per image

### **Tab 2: 🔬 Segmentation**
- **Does**: AI detects cells using YOLO
- **Input**: JPGs from Tab 1
- **Output**: 3 images (original, segmented, background-removed)
- **Saves**: `temp/processed/*.jpg` and `*.png`
- **Time**: ~10-30 seconds per image

### **Tab 3: 🧪 Chemical Analysis**
- **Does**: Detects lignin (red) and pectin (purple)
- **Input**: Background-removed PNGs from Tab 2
- **Output**: Colored overlays + metrics table
- **Saves**: `temp/results/*_lignin.jpg`, `*_pectin.jpg`
- **Time**: ~5 seconds per analysis

### **Tab 4: 📊 Results & Export**
- **Does**: Packages all results for download
- **Output**: ZIP file with all images + data
- **Gets**: Complete analysis ready for publication
- **Time**: ~5 seconds to create ZIP

### **Tab 5: ⚙️ Settings**
- **Does**: Configure model, thresholds, sensitivity
- **When**: Adjust if results aren't right
- **Saves**: Settings persist across sessions

---

## 🗂️ **Where Files Are Saved**

```
src/gradio_ui/temp/
├── uploads/          # Temporary (auto-deleted)
├── processed/        # JPGs, segmented images, PNGs
├── results/          # Lignin/Pectin visualizations
└── cache/            # Settings (JSON)
```

---

## 🎯 **Typical Session (5 minutes)**

1. **Upload** 3 images → 30 seconds
2. **Segment** each image → 1.5 minutes
3. **Analyze** chemistry → 1 minute
4. **Export** ZIP → 10 seconds
5. **Done!** → Use in research

---

## 🔧 **Key Technologies**

| What | Technology |
|------|-----------|
| UI | Gradio 4.16.0 |
| AI Model | YOLO11 (Ultralytics) |
| Images | OpenCV (cv2) |
| ND2 Files | nd2 library |
| Data | Pandas |

---

## 📊 **What You Get**

### **Segmentation Output**:
- Original image
- Image with colored boxes + masks (shows detected cells)
- Background-removed (white background, only cells)

### **Chemical Analysis Output**:
- Red overlay (lignin detection)
- Purple overlay (pectin detection)
- Metrics table (pixels, ratio, area in μm²)

### **Export Package** (ZIP):
- All processed images
- All analysis visualizations
- Organized in folders
- Ready for publication

---

## ⚙️ **Important Settings**

### **Confidence Threshold** (Tab 2, Tab 5)
- Default: 0.25
- Lower → More detections (may include false positives)
- Higher → Fewer, more confident detections
- **Adjust if**: Missing cells or seeing too many false detections

### **Color Sensitivity** (Tab 5)
- Lignin: 1-10 (default 5)
- Pectin: 1-10 (default 5)
- Higher → Detects more shades
- **Adjust if**: Missing stained regions or over-detecting

### **Pixel-to-Micron** (Tab 5)
- Default: 0.9785
- **Critical**: Get from your microscope calibration!
- Affects area measurements (μm²)

---

## 🐛 **Common Issues & Fixes**

| Problem | Solution |
|---------|----------|
| No cells detected | Lower confidence threshold |
| Too many false detections | Raise confidence threshold |
| Lignin not detected | Increase lignin sensitivity |
| Pectin not detected | Increase pectin sensitivity |
| Wrong area measurements | Update pixel-to-micron conversion |
| Model not found | Check Settings tab, verify best.pt exists |

---

## 📁 **Files to Keep**

### **Important**:
- `best.pt` - Trained YOLO model (keep this!)
- Downloaded ZIP files - Your results

### **Can Delete**:
- `temp/` folder - Temporary processing files
- Clear between sessions to save disk space

---

## 🎓 **For Biologists**

### **What You DON'T Need to Know**:
- How the AI works
- Image processing algorithms
- Code or programming

### **What You DO Need to Know**:
- Click tabs in order (1→2→3→4)
- Check if results look right
- Download ZIP when done
- Adjust settings if needed

---

## 🔬 **Scientific Methods**

### **Segmentation**:
- Deep learning (YOLO11)
- Instance segmentation
- Detects cell boundaries

### **Chemical Analysis**:
- HSV color space detection
- Lignin: Red hue detection (PG staining)
- Pectin: Burgundy hue detection (RR staining)

### **Measurements**:
- Pixel counting
- Ratio calculation (detected / total)
- Area conversion (pixels → μm²)

---

## 📞 **Need More Help?**

- **Full Breakdown**: See `UI_COMPLETE_BREAKDOWN.md`
- **Implementation Details**: See `GRADIO_IMPLEMENTATION_GUIDE.md`
- **Architecture**: See `GRADIO_UI_ARCHITECTURE.md`

---

## ✅ **Success Checklist**

After running a complete analysis:

- [ ] Uploaded images converted to JPG
- [ ] Segmentation shows cells detected
- [ ] Background-removed images look clean
- [ ] Lignin overlay shows red regions
- [ ] Pectin overlay shows purple regions
- [ ] Metrics table has numbers
- [ ] Downloaded ZIP file
- [ ] ZIP contains all images
- [ ] Ready to use in publication!

---

**The UI is complete and ready to use! Enjoy analyzing your alfalfa samples! 🌱🎉**
