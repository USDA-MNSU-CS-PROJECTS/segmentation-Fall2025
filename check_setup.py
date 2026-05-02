#!/usr/bin/env python3
"""
Quick diagnostic script to check environment setup
Run this and share the output!
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("GRADIO UI - ENVIRONMENT CHECK")
print("=" * 60)

# 1. Python version
print("\n1. PYTHON VERSION:")
print(f"   {sys.version}")
print(f"   Executable: {sys.executable}")

# 2. Current directory
print("\n2. CURRENT DIRECTORY:")
cwd = Path.cwd()
print(f"   {cwd}")
print(f"   Is repo root: {(cwd / 'app.py').exists()}")

# 3. Git branch
print("\n3. GIT BRANCH:")
try:
    import subprocess
    branch = subprocess.run(['git', 'branch', '--show-current'], 
                          capture_output=True, text=True, cwd=cwd)
    print(f"   {branch.stdout.strip() or 'Unknown'}")
except:
    print("   Could not determine (git not available)")

# 4. Check for model
print("\n4. YOLO MODEL CHECK:")
model_search_paths = [
    cwd / "src/data/yolo_results/runs/segment",
    cwd / "best.pt",
    cwd / "weights/best.pt"
]

model_found = False
for path in model_search_paths:
    if path.exists():
        if path.is_dir():
            # Search for best.pt in subdirectories
            for run_dir in path.iterdir():
                if run_dir.is_dir():
                    weights = run_dir / "weights/best.pt"
                    if weights.exists():
                        print(f"   ✅ Found: {weights}")
                        print(f"      Size: {weights.stat().st_size / (1024*1024):.2f} MB")
                        model_found = True
                        break
        else:
            print(f"   ✅ Found: {path}")
            print(f"      Size: {path.stat().st_size / (1024*1024):.2f} MB")
            model_found = True
            
if not model_found:
    print("   ❌ No trained model found")
    print("   Need to download best.pt or train new model")

# 5. Check for test data
print("\n5. TEST DATA CHECK:")
nd2_path = cwd / "src/data/nd2_images/input_images"
if nd2_path.exists():
    nd2_files = list(nd2_path.glob("*.nd2"))
    if nd2_files:
        print(f"   ✅ Found {len(nd2_files)} .nd2 files")
        for f in nd2_files[:3]:
            print(f"      - {f.name}")
    else:
        print("   ⚠️  Folder exists but no .nd2 files")
else:
    print("   ❌ No input_images folder")
    print("   Need sample .nd2 files for testing")

# 6. Check installed packages
print("\n6. REQUIRED PACKAGES:")
required = {
    'gradio': 'Gradio UI framework',
    'ultralytics': 'YOLO model',
    'cv2': 'OpenCV (opencv-python)',
    'numpy': 'NumPy',
    'pandas': 'Pandas',
    'PIL': 'Pillow'
}

for package, description in required.items():
    try:
        if package == 'cv2':
            import cv2
        elif package == 'PIL':
            from PIL import Image
        else:
            __import__(package)
        print(f"   ✅ {package:15} - {description}")
    except ImportError:
        print(f"   ❌ {package:15} - {description} (NOT INSTALLED)")

# 7. Check Gradio UI structure
print("\n7. GRADIO UI FILES:")
ui_files = [
    "app.py",
    "src/gradio_ui/config.py",
    "src/gradio_ui/backend/segmentation.py"
]

for f in ui_files:
    path = cwd / f
    if path.exists():
        lines = len(path.read_text().splitlines())
        print(f"   ✅ {f:40} ({lines} lines)")
    else:
        print(f"   ❌ {f:40} (MISSING)")

# 8. What needs to be implemented
print("\n8. TO IMPLEMENT:")
to_implement = [
    "src/gradio_ui/backend/image_processor.py",
    "src/gradio_ui/backend/chemical_analysis.py",
    "src/gradio_ui/backend/results_manager.py",
    "src/gradio_ui/backend/utils.py"
]

for f in to_implement:
    path = cwd / f
    if path.exists():
        print(f"   ✅ {f}")
    else:
        print(f"   ⏳ {f} (NEEDS IMPLEMENTATION)")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

# Calculate readiness
checks = {
    'model': model_found,
    'test_data': (nd2_path.exists() and len(list(nd2_path.glob("*.nd2"))) > 0),
}

try:
    import gradio
    checks['gradio'] = True
except:
    checks['gradio'] = False

ready = all(checks.values())

if ready:
    print("✅ Environment is ready for implementation!")
else:
    print("⚠️  Some setup needed:")
    if not checks['model']:
        print("   - Get trained model (best.pt)")
    if not checks['test_data']:
        print("   - Get test .nd2 files")
    if not checks['gradio']:
        print("   - Install Gradio: pip install gradio")

print("\n" + "=" * 60)
print("\nShare this output to continue implementation!")
