#!/usr/bin/env python3
"""Test if all imports work for gradio_app.py"""

print("Testing imports...\n")

try:
    print("1. Testing gradio...")
    import gradio as gr
    print(f"   ✅ Gradio {gr.__version__}")
except Exception as e:
    print(f"   ❌ Gradio: {e}")
    exit(1)

try:
    print("2. Testing sys and pathlib...")
    import sys
    from pathlib import Path
    print("   ✅ sys and pathlib")
except Exception as e:
    print(f"   ❌ {e}")
    exit(1)

try:
    print("3. Testing backend imports...")
    repo_root = Path(__file__).parent
    sys.path.insert(0, str(repo_root))
    
    from src.gradio_ui.backend.image_processor import ImageProcessor
    print("   ✅ ImageProcessor")
    
    from src.gradio_ui.backend.segmentation import SegmentationEngine
    print("   ✅ SegmentationEngine")
    
    from src.gradio_ui.backend.chemical_analysis import ChemicalAnalyzer
    print("   ✅ ChemicalAnalyzer")
    
    from src.gradio_ui.backend.results_manager import ResultsManager
    print("   ✅ ResultsManager")
    
    from src.gradio_ui.config import UIConfig
    print("   ✅ UIConfig")
    
except Exception as e:
    print(f"   ❌ Backend import error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

try:
    print("\n4. Testing config initialization...")
    config = UIConfig()
    print(f"   ✅ Config initialized")
    print(f"   Model path: {config.model_path}")
    print(f"   Model exists: {config.model_path.exists()}")
except Exception as e:
    print(f"   ❌ Config error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

try:
    print("\n5. Testing backend initialization...")
    image_processor = ImageProcessor(config)
    segmentation_engine = SegmentationEngine(config)
    chemical_analyzer = ChemicalAnalyzer(config)
    results_manager = ResultsManager(config)
    print("   ✅ All backends initialized")
except Exception as e:
    print(f"   ❌ Backend initialization error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*50)
print("✅ ALL IMPORTS SUCCESSFUL!")
print("The app should be able to start.")
print("="*50)
