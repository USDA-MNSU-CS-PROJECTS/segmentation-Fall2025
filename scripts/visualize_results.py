"""
YOLO Training Results Basic Visualization Script

This script creates a 4-panel visualization of YOLO box detection metrics:
- Precision: Ratio of correct predictions among all predictions
- Recall: Ratio of detected objects among all ground truth objects  
- mAP50: Mean Average Precision at IoU threshold of 0.5
- mAP50-95: Mean Average Precision over IoU range 0.5 to 0.95

Each metric is displayed with area-filled line plots to show training progress.

Author: GitHub Copilot
Date: 2025-11-07
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Find repo root and latest YOLO training run
script_path = Path(__file__).resolve()
repo_root = script_path.parents[1]  # scripts/ -> repo root

# Find latest run folder in src/data/yolo_results/runs/segment/
runs_dir = repo_root / "src/data/yolo_results/runs/segment"
if not runs_dir.exists():
    raise FileNotFoundError(f"YOLO results directory not found: {runs_dir}")

# Find all run folders and get the most recent one
run_folders = [d for d in runs_dir.iterdir() if d.is_dir()]
if not run_folders:
    raise FileNotFoundError(f"No training runs found in {runs_dir}")

latest_run = max(run_folders, key=lambda p: p.stat().st_mtime)
results_csv = latest_run / "results.csv"

if not results_csv.exists():
    raise FileNotFoundError(f"results.csv not found in {latest_run}")

print(f"Using results from: {latest_run.name}")
print(f"Reading from: {results_csv}")

# Read CSV file containing training results
df = pd.read_csv(results_csv)

# Font configuration for cross-platform compatibility
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False  # Prevent minus sign rendering issues

# Graph style configuration
plt.style.use('default')
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('YOLO Training Performance Metrics (150 Epochs)', fontsize=16, fontweight='bold')

# Define color palette for different metrics
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# 1. Precision Graph (Box Detection)
ax1 = axes[0, 0]
ax1.plot(df['epoch'], df['metrics/precision(B)'], 
         color=colors[0], linewidth=2.5, alpha=0.8, label='Box Precision')
ax1.fill_between(df['epoch'], df['metrics/precision(B)'], 
                 alpha=0.3, color=colors[0])  # Area fill effect
ax1.set_title('Precision (Box Detection)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Precision')
ax1.grid(True, alpha=0.3)  # Show grid with transparency
ax1.set_ylim(0, 1.05)      # Set Y-axis range
ax1.legend()

# 2. Recall Graph (Box Detection)
ax2 = axes[0, 1]
ax2.plot(df['epoch'], df['metrics/recall(B)'], 
         color=colors[1], linewidth=2.5, alpha=0.8, label='Box Recall')
ax2.fill_between(df['epoch'], df['metrics/recall(B)'], 
                 alpha=0.3, color=colors[1])  # Area fill effect
ax2.set_title('Recall (Box Detection)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Recall')
ax2.grid(True, alpha=0.3)  # Show grid with transparency
ax2.set_ylim(0, 1.05)      # Set Y-axis range
ax2.legend()

# 3. mAP50 Graph (Box Detection)
ax3 = axes[1, 0]
ax3.plot(df['epoch'], df['metrics/mAP50(B)'], 
         color=colors[2], linewidth=2.5, alpha=0.8, label='Box mAP50')
ax3.fill_between(df['epoch'], df['metrics/mAP50(B)'], 
                 alpha=0.3, color=colors[2])  # Area fill effect
ax3.set_title('mAP50 (Box Detection)', fontsize=14, fontweight='bold')
ax3.set_xlabel('Epoch')
ax3.set_ylabel('mAP50')
ax3.grid(True, alpha=0.3)  # Show grid with transparency
ax3.set_ylim(0, 1.05)      # Set Y-axis range
ax3.legend()

# 4. mAP50-95 Graph (Box Detection)
ax4 = axes[1, 1]
ax4.plot(df['epoch'], df['metrics/mAP50-95(B)'], 
         color=colors[3], linewidth=2.5, alpha=0.8, label='Box mAP50-95')
ax4.fill_between(df['epoch'], df['metrics/mAP50-95(B)'], 
                 alpha=0.3, color=colors[3])  # Area fill effect
ax4.set_title('mAP50-95 (Box Detection)', fontsize=14, fontweight='bold')
ax4.set_xlabel('Epoch')
ax4.set_ylabel('mAP50-95')
ax4.grid(True, alpha=0.3)  # Show grid with transparency
ax4.set_ylim(0, 1.05)      # Set Y-axis range
ax4.legend()

# Adjust layout automatically
plt.tight_layout()
plt.subplots_adjust(top=0.93)  # Top margin for main title

# Save visualization to file in yolo_results directory
output_dir = repo_root / "src/data/yolo_results"
output_path = output_dir / 'yolo_metrics_visualization.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved visualization to: {output_path}")
plt.show()

# Print training statistics summary
print("=== Training Statistics Summary ===")
print(f"Total Epochs: {len(df)}")
print(f"Final Precision (Box): {df['metrics/precision(B)'].iloc[-1]:.4f}")
print(f"Final Recall (Box): {df['metrics/recall(B)'].iloc[-1]:.4f}")
print(f"Final mAP50 (Box): {df['metrics/mAP50(B)'].iloc[-1]:.4f}")
print(f"Final mAP50-95 (Box): {df['metrics/mAP50-95(B)'].iloc[-1]:.4f}")
print(f"Best mAP50 (Box): {df['metrics/mAP50(B)'].max():.4f} (Epoch {df.loc[df['metrics/mAP50(B)'].idxmax(), 'epoch']})")
print(f"Best mAP50-95 (Box): {df['metrics/mAP50-95(B)'].max():.4f} (Epoch {df.loc[df['metrics/mAP50-95(B)'].idxmax(), 'epoch']})")