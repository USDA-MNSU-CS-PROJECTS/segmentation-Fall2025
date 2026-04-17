# 🚀 How to Start the Gradio UI

## Quick Start

### **Step 1: Install Gradio (if not already installed)**

```bash
pip install gradio
```

### **Step 2: Start the UI**

Open a terminal in the repository root and run:

```bash
python gradio_app.py
```

**OR use the launch script:**

```bash
./launch_ui.sh
```

---

## 🌐 Where It Will Run

Once started, the UI will be available at:

```
http://localhost:7860
```

**Or**

```
http://127.0.0.1:7860
```

The terminal will show a message like:

```
Running on local URL:  http://127.0.0.1:7860
```

Your browser should automatically open to that URL.

---

## ✅ What You Should See

1. **Terminal Output**:
   ```
   * Running on local URL:  http://127.0.0.1:7860
   
   To create a public link, set `share=True` in `launch()`.
   ```

2. **Browser**:
   - Opens automatically to http://localhost:7860
   - Shows: "🌱 Alfalfa Cell Segmentation Analysis Platform"
   - 5 tabs visible: Upload & Process, Segmentation, Chemical Analysis, Results & Export, Settings

---

## 🐛 If It Doesn't Start

### **Error: Module 'gradio' not found**

```bash
pip install gradio
```

### **Error: Port 7860 already in use**

```bash
# Kill existing process
lsof -ti:7860 | xargs kill -9

# Or use a different port
python gradio_app.py --port 8080
```

### **Error: Other import errors**

```bash
# Install all dependencies
pip install ultralytics opencv-python pandas numpy pillow
```

---

## 📋 Testing Checklist

Once the UI is running:

1. **Tab 1 (Upload & Process)**
   - Try uploading a JPG image
   - Click "Convert Images"
   - See if it appears in gallery

2. **Tab 2 (Segmentation)**
   - Select an image
   - Click "Run Segmentation"
   - See if 3 images appear

3. **Tab 3 (Chemical Analysis)**
   - Select analysis types
   - Pick a background-removed image
   - Click "Run Analysis"
   - Check results table

4. **Tab 4 (Results & Export)**
   - Click "Refresh Results"
   - Try downloading as ZIP

5. **Tab 5 (Settings)**
   - Click "Check Model"
   - Should show: ✅ Model is valid!

---

## 🛑 To Stop the UI

Press **Ctrl+C** in the terminal where it's running.

---

## 📞 What to Report Back

After starting and testing:

✅ **It's running at**: http://localhost:7860 (or whatever port it shows)

Then tell me:
- Did it start? ✅/❌
- Which tabs work? 
- Any errors? (screenshot or copy error message)
- What needs fixing?

---

**Go ahead and start it now!** 🚀
