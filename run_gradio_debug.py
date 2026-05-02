#!/usr/bin/env python3
"""Debug script to find what's wrong with app.py"""

print("="*60)
print("DEBUGGING GRADIO APP STARTUP")
print("="*60)

import sys
from pathlib import Path

# Ensure we're in the right place
repo_root = Path(__file__).parent
print(f"\nRepo root: {repo_root}")
print(f"Working dir: {Path.cwd()}")

# Try importing gradio
print("\n1. Testing Gradio import...")
try:
    import gradio as gr
    print(f"   ✅ Gradio {gr.__version__} imported")
except Exception as e:
    print(f"   ❌ Gradio import failed: {e}")
    sys.exit(1)

# Try importing our config
print("\n2. Testing config import...")
try:
    sys.path.insert(0, str(repo_root))
    from src.gradio_ui.config import UIConfig
    print("   ✅ Config imported")
except Exception as e:
    print(f"   ❌ Config import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try creating config
print("\n3. Testing config initialization...")
try:
    config = UIConfig()
    print(f"   ✅ Config created")
    print(f"   Model path: {config.model_path}")
    print(f"   Model exists: {config.model_path.exists()}")
except Exception as e:
    print(f"   ❌ Config creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try importing backends
print("\n4. Testing backend imports...")
try:
    from src.gradio_ui.backend.image_processor import ImageProcessor
    from src.gradio_ui.backend.segmentation import SegmentationEngine
    from src.gradio_ui.backend.chemical_analysis import ChemicalAnalyzer
    from src.gradio_ui.backend.results_manager import ResultsManager
    print("   ✅ All backends imported")
except Exception as e:
    print(f"   ❌ Backend import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try creating backend instances
print("\n5. Testing backend initialization...")
try:
    image_processor = ImageProcessor(config)
    segmentation_engine = SegmentationEngine(config)
    chemical_analyzer = ChemicalAnalyzer(config)
    results_manager = ResultsManager(config)
    print("   ✅ All backends initialized")
except Exception as e:
    print(f"   ❌ Backend initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL CHECKS PASSED - App should be able to start!")
print("="*60)

print("\nNow trying to create a minimal Gradio app...")

try:
    with gr.Blocks() as demo:
        gr.Markdown("# Test App")
        gr.Button("Test Button")
    
    print("✅ Gradio app created successfully")
    print("\nStarting server on http://localhost:7860...")
    print("Press Ctrl+C to stop")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
except Exception as e:
    print(f"❌ Failed to launch: {e}")
    import traceback
    traceback.print_exc()
