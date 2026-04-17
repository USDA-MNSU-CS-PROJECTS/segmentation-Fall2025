#!/bin/bash

echo "🌱 Alfalfa Cell Segmentation Analysis - Gradio UI"
echo "=================================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if Gradio is installed
if ! python3 -c "import gradio" 2>/dev/null; then
    echo "⚠️  Gradio not installed. Installing now..."
    pip install gradio>=4.0.0
    echo ""
fi

echo "✅ Gradio installed"
echo ""

# Check for model
if [ -f "src/data/yolo_results/runs/segment/handover-model/weights/best.pt" ]; then
    echo "✅ Model found: best.pt"
else
    echo "⚠️  Warning: Model not found at expected location"
    echo "   Please place best.pt in:"
    echo "   src/data/yolo_results/runs/segment/handover-model/weights/"
    echo ""
fi

# Launch the app
echo "🚀 Launching Gradio UI..."
echo ""
echo "   The web interface will open at: http://localhost:7860"
echo "   Press Ctrl+C to stop the server"
echo ""
echo "=================================================="
echo ""

python3 gradio_app.py
