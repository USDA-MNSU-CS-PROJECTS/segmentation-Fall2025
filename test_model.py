#!/usr/bin/env python3
"""Quick test to verify the YOLO model loads correctly"""

from pathlib import Path

model_path = Path("src/data/yolo_results/runs/segment/handover-model/weights/best.pt")

print("=" * 60)
print("TESTING YOLO MODEL")
print("=" * 60)

# Check if file exists
print(f"\n1. File exists: {model_path.exists()}")
if model_path.exists():
    size_mb = model_path.stat().st_size / (1024 * 1024)
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Path: {model_path}")

# Try to load with YOLO
print("\n2. Loading model with Ultralytics YOLO...")
try:
    from ultralytics import YOLO
    model = YOLO(str(model_path))
    print("   ✅ Model loaded successfully!")
    print(f"   Model type: {type(model).__name__}")
    print(f"   Task: {model.task}")
    
    # Check model info
    if hasattr(model, 'names'):
        print(f"   Classes: {model.names}")
    
    print("\n✅ ALL CHECKS PASSED!")
    print("The model is ready to use in the Gradio UI!")
    
except Exception as e:
    print(f"   ❌ Error loading model: {e}")
    print("\nTroubleshooting:")
    print("- Make sure ultralytics is installed: pip install ultralytics")
    print("- Make sure the best.pt file is not corrupted")

print("\n" + "=" * 60)
