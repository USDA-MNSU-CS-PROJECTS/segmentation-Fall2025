# 🔧 Fix and Start the UI

## ❌ Problem: "localhost refused to connect"

This means the app didn't start. Most likely **Gradio is not installed**.

---

## ✅ Solution: Install Gradio and Start

### **Step 1: Install Gradio**

Run this in your terminal:

```bash
pip install gradio>=4.0.0
```

Wait for it to install. You should see:
```
Successfully installed gradio-4.x.x
```

### **Step 2: Install Other Dependencies (just in case)**

```bash
pip install ultralytics opencv-python pandas numpy pillow openpyxl
```

### **Step 3: Start the UI**

```bash
python gradio_app.py
```

You should see output like:
```
Running on local URL:  http://127.0.0.1:7860
```

### **Step 4: Open Browser**

Go to: **http://localhost:7860**

---

## 🧪 Test If Gradio is Installed

Run this to check:

```bash
python -c "import gradio; print('Gradio installed:', gradio.__version__)"
```

**Expected output**: `Gradio installed: 4.x.x`

**If error**: Gradio not installed → Go to Step 1 above

---

## 🐛 Other Possible Issues

### **Issue: "ModuleNotFoundError: No module named 'gradio'"**

**Fix:**
```bash
pip install gradio
```

### **Issue: "ModuleNotFoundError: No module named 'ultralytics'"**

**Fix:**
```bash
pip install ultralytics
```

### **Issue: "Port 7860 already in use"**

**Fix:**
```bash
# Kill process on that port
lsof -ti:7860 | xargs kill -9

# Then try again
python gradio_app.py
```

### **Issue: Import errors from backend modules**

**Fix:**
```bash
# Make sure you're in the repo root
cd /Users/emmanuelkiprotich/USDA-Segmentation-S2

# Try again
python gradio_app.py
```

---

## 📋 Quick Diagnostic

Run these commands to check everything:

```bash
# 1. Check Python version (should be 3.10+)
python --version

# 2. Check if gradio is installed
python -c "import gradio; print('OK')"

# 3. Check if in correct directory
pwd
# Should show: /Users/emmanuelkiprotich/USDA-Segmentation-S2

# 4. Check if gradio_app.py exists
ls gradio_app.py
# Should show: gradio_app.py

# 5. Try to start
python gradio_app.py
```

---

## ✅ What Success Looks Like

When it works, you'll see:

```
Running on local URL:  http://127.0.0.1:7860

To create a public link, set `share=True` in `launch()`.
```

And your browser will automatically open to the UI!

---

## 💬 What to Do Next

1. **Install Gradio**: `pip install gradio`
2. **Start the app**: `python gradio_app.py`
3. **Tell me**: 
   - "It's running!" ✅
   - OR copy any error message you see ❌

---

## 🚀 Most Likely Fix

**Just run these two commands:**

```bash
pip install gradio
python gradio_app.py
```

**That should fix it!** 🎉

---

## 📞 If Still Not Working

Share with me:

1. **Output from**: `pip install gradio`
2. **Output from**: `python gradio_app.py`
3. **Any error messages**

I'll help you fix it immediately!
