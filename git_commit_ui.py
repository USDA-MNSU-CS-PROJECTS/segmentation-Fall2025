#!/usr/bin/env python3
"""Git commit script for UI changes"""

import subprocess
import os

os.chdir('/Users/emmanuelkiprotich/USDA-Segmentation-S2')

def run(cmd):
    """Run git command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr

# Create/checkout branch
print("Creating gradio-ui branch...")
output = run("git checkout -b gradio-ui 2>&1 || git checkout gradio-ui 2>&1")
print(output)

# Add files
print("\nAdding UI files...")
files = [
    "gradio_app.py",
    "src/gradio_ui/",
    "GRADIO_UI_ARCHITECTURE.md",
    "GRADIO_IMPLEMENTATION_GUIDE.md", 
    "GRADIO_UI_RECOMMENDATIONS.md",
    "GRADIO_UI_SUMMARY.md",
    "requirements_gradio.txt",
    "STEP_BY_STEP_GUIDE.md",
    "QUICK_REFERENCE.md",
    "MODEL_STORAGE_INFO.md"
]

for f in files:
    output = run(f"git add {f} 2>&1")
    if output.strip():
        print(f"  {f}: {output.strip()}")

# Commit
print("\nCommitting...")
output = run('git commit -m "Add Gradio UI" 2>&1')
print(output)

# Show status
print("\nCurrent branch:")
output = run("git branch --show-current 2>&1")
print(output)

print("\nRecent commits:")
output = run("git log --oneline -3 2>&1")
print(output)

print("\n✅ Done!")
