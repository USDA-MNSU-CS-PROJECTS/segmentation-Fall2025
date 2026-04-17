#!/usr/bin/env python3
"""Simple test to see what's failing"""

import sys
print("Python version:", sys.version)
print("\n1. Testing imports...")

try:
    import gradio as gr
    print("✅ Gradio imported")
except Exception as e:
    print(f"❌ Gradio: {e}")
    sys.exit(1)

try:
    import cv2
    print("✅ OpenCV imported")
except Exception as e:
    print(f"❌ OpenCV: {e}")
    sys.exit(1)

try:
    import numpy as np
    print(f"✅ NumPy {np.__version__} imported")
except Exception as e:
    print(f"❌ NumPy: {e}")
    sys.exit(1)

print("\n2. Testing backend imports...")
try:
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from src.gradio_ui.config import UIConfig
    print("✅ Config imported")
    
    config = UIConfig()
    print(f"✅ Config created - Model at: {config.model_path}")
    
except Exception as e:
    print(f"❌ Config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from src.gradio_ui.backend.image_processor import ImageProcessor
    print("✅ ImageProcessor imported")
except Exception as e:
    print(f"❌ ImageProcessor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from src.gradio_ui.backend.segmentation import SegmentationEngine
    from src.gradio_ui.backend.chemical_analysis import ChemicalAnalyzer
    from src.gradio_ui.backend.results_manager import ResultsManager
    print("✅ All backends imported")
except Exception as e:
    print(f"❌ Backends: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ ALL IMPORTS SUCCESSFUL!")
print("\nNow trying to create minimal Gradio app...")

try:
    with gr.Blocks() as demo:
        gr.Markdown("# 🌱 Test Gradio App")
        gr.Button("Test Button")
    
    print("✅ Gradio app created")
    print("\nLaunching on http://localhost:7860...")
    print("Press Ctrl+C to stop\n")
    
    demo.launch(server_port=7860, share=False, show_error=True, quiet=False)
    
except Exception as e:
    print(f"❌ Launch failed: {e}")
    import traceback
    traceback.print_exc()
