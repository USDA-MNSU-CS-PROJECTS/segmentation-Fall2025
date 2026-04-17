#!/bin/bash
cd /Users/emmanuelkiprotich/USDA-Segmentation-S2

# Checkout or create branch
git checkout -b gradio-ui 2>/dev/null || git checkout gradio-ui

# Add all new files
git add -A

# Commit
git commit -m "Add Gradio UI" || echo "Already committed or no changes"

# Show status
echo "Current branch:"
git branch --show-current
echo ""
echo "Recent commits:"
git log --oneline -3
