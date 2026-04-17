#!/bin/bash

# Create and switch to UI branch
git checkout -b gradio-ui 2>/dev/null || git checkout gradio-ui

# Stage all UI files
git add gradio_app.py
git add src/gradio_ui/
git add GRADIO_UI_ARCHITECTURE.md
git add GRADIO_IMPLEMENTATION_GUIDE.md
git add GRADIO_UI_RECOMMENDATIONS.md
git add GRADIO_UI_SUMMARY.md
git add requirements_gradio.txt
git add STEP_BY_STEP_GUIDE.md
git add QUICK_REFERENCE.md
git add MODEL_STORAGE_INFO.md

# Commit with brief messages
git commit -m "Add Gradio web interface"

echo "✅ Committed all UI changes to gradio-ui branch"
echo ""
echo "Branch: gradio-ui"
git log --oneline -3
