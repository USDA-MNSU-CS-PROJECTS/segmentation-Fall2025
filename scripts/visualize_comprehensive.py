"""
YOLO Training Results Comprehensive Visualization Script

This script visualizes YOLO model training results in various ways:
1. Compare all key metrics in a single graph
2. Detailed analysis of segmentation metrics (4 subplots)
3. Print statistical summary information
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

# Read CSV file (YOLO training results data)
df = pd.read_csv(results_csv)

# Configure graph style (font settings for cross-platform compatibility)
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False  # Prevent minus sign rendering issues

# === 1. Display all key metrics in a single graph ===
fig, ax = plt.subplots(1, 1, figsize=(14, 8))

# Define color palette (distinct colors for each metric)
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# Plot all Box Detection metrics in a single graph
# Precision: Ratio of correct predictions among all predictions
ax.plot(df['epoch'], df['metrics/precision(B)'], 
        color=colors[0], linewidth=2.5, alpha=0.8, label='Precision (Box)', marker='o', markersize=2)
# Recall: Ratio of detected objects among all ground truth objects
ax.plot(df['epoch'], df['metrics/recall(B)'], 
        color=colors[1], linewidth=2.5, alpha=0.8, label='Recall (Box)', marker='s', markersize=2)
# mAP50: Mean Average Precision at IoU threshold of 0.5
ax.plot(df['epoch'], df['metrics/mAP50(B)'], 
        color=colors[2], linewidth=2.5, alpha=0.8, label='mAP50 (Box)', marker='^', markersize=2)
# mAP50-95: Mean Average Precision over IoU range 0.5 to 0.95
ax.plot(df['epoch'], df['metrics/mAP50-95(B)'], 
        color=colors[3], linewidth=2.5, alpha=0.8, label='mAP50-95 (Box)', marker='d', markersize=2)

# Configure graph settings and styling
ax.set_title('YOLO Training Performance Overview (All Metrics)', fontsize=16, fontweight='bold')
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.grid(True, alpha=0.3)  # Show grid with 30% transparency
ax.set_ylim(0, 1.05)      # Set Y-axis range
ax.legend(loc='lower right', fontsize=11)  # Set legend position

# Find and mark best performance points
best_map50_epoch = df.loc[df['metrics/mAP50(B)'].idxmax(), 'epoch']
best_map50_95_epoch = df.loc[df['metrics/mAP50-95(B)'].idxmax(), 'epoch']
best_map50_value = df['metrics/mAP50(B)'].max()
best_map50_95_value = df['metrics/mAP50-95(B)'].max()

# Annotate best performance points with arrows and text
ax.annotate(f'Best mAP50: {best_map50_value:.4f}', 
            xy=(best_map50_epoch, best_map50_value), 
            xytext=(best_map50_epoch + 10, best_map50_value - 0.05),
            arrowprops=dict(arrowstyle='->', color=colors[2], alpha=0.7),
            fontsize=10, color=colors[2])

ax.annotate(f'Best mAP50-95: {best_map50_95_value:.4f}', 
            xy=(best_map50_95_epoch, best_map50_95_value), 
            xytext=(best_map50_95_epoch + 10, best_map50_95_value + 0.02),
            arrowprops=dict(arrowstyle='->', color=colors[3], alpha=0.7),
            fontsize=10, color=colors[3])

# Auto-adjust layout
plt.tight_layout()

# Save first graph (combined metrics version) in yolo_results directory
output_dir = repo_root / "src/data/yolo_results"
output_path1 = output_dir / 'yolo_metrics_combined.png'
plt.savefig(output_path1, dpi=300, bbox_inches='tight')
print(f"Saved combined metrics visualization to: {output_path1}")
plt.show()

# === 2. Detailed segmentation metrics analysis (4 subplots) ===
fig2, axes2 = plt.subplots(2, 2, figsize=(15, 12))
fig2.suptitle('YOLO Segmentation Performance Metrics (150 Epochs)', fontsize=16, fontweight='bold')

# 1. Precision (Mask) - Mask precision
ax1 = axes2[0, 0]
ax1.plot(df['epoch'], df['metrics/precision(M)'], 
         color=colors[0], linewidth=2.5, alpha=0.8, label='Mask Precision')
ax1.fill_between(df['epoch'], df['metrics/precision(M)'], 
                 alpha=0.3, color=colors[0])  # Area fill effect
ax1.set_title('Precision (Mask/Segmentation)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Precision')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 1.05)
ax1.legend()

# 2. Recall (Mask) - Mask recall
ax2 = axes2[0, 1]
ax2.plot(df['epoch'], df['metrics/recall(M)'], 
         color=colors[1], linewidth=2.5, alpha=0.8, label='Mask Recall')
ax2.fill_between(df['epoch'], df['metrics/recall(M)'], 
                 alpha=0.3, color=colors[1])  # Area fill effect
ax2.set_title('Recall (Mask/Segmentation)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Recall')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 1.05)
ax2.legend()

# 3. mAP50 (Mask) - Mask mean average precision (IoU 0.5)
ax3 = axes2[1, 0]
ax3.plot(df['epoch'], df['metrics/mAP50(M)'], 
         color=colors[2], linewidth=2.5, alpha=0.8, label='Mask mAP50')
ax3.fill_between(df['epoch'], df['metrics/mAP50(M)'], 
                 alpha=0.3, color=colors[2])  # Area fill effect
ax3.set_title('mAP50 (Mask/Segmentation)', fontsize=14, fontweight='bold')
ax3.set_xlabel('Epoch')
ax3.set_ylabel('mAP50')
ax3.grid(True, alpha=0.3)
ax3.set_ylim(0, 1.05)
ax3.legend()

# 4. mAP50-95 (Mask) - Mask mean average precision (IoU 0.5~0.95)
ax4 = axes2[1, 1]
ax4.plot(df['epoch'], df['metrics/mAP50-95(M)'], 
         color=colors[3], linewidth=2.5, alpha=0.8, label='Mask mAP50-95')
ax4.fill_between(df['epoch'], df['metrics/mAP50-95(M)'], 
                 alpha=0.3, color=colors[3])  # Area fill effect
ax4.set_title('mAP50-95 (Mask/Segmentation)', fontsize=14, fontweight='bold')
ax4.set_xlabel('Epoch')
ax4.set_ylabel('mAP50-95')
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0, 1.05)
ax4.legend()

# Auto-adjust layout and set top margin
plt.tight_layout()
plt.subplots_adjust(top=0.93)  # Top margin for title

# Save second graph (detailed segmentation analysis version) in yolo_results directory
output_path2 = output_dir / 'yolo_segmentation_metrics.png'
plt.savefig(output_path2, dpi=300, bbox_inches='tight')
print(f"Saved segmentation metrics visualization to: {output_path2}")
plt.show()

# === 3. Print statistical summary information ===

# Print final and best performance for segmentation
print("\n=== Segmentation Statistics Summary ===")
print(f"Final Precision (Mask): {df['metrics/precision(M)'].iloc[-1]:.4f}")
print(f"Final Recall (Mask): {df['metrics/recall(M)'].iloc[-1]:.4f}")
print(f"Final mAP50 (Mask): {df['metrics/mAP50(M)'].iloc[-1]:.4f}")
print(f"Final mAP50-95 (Mask): {df['metrics/mAP50-95(M)'].iloc[-1]:.4f}")
print(f"Best mAP50 (Mask): {df['metrics/mAP50(M)'].max():.4f} (Epoch {df.loc[df['metrics/mAP50(M)'].idxmax(), 'epoch']})")
print(f"Best mAP50-95 (Mask): {df['metrics/mAP50-95(M)'].max():.4f} (Epoch {df.loc[df['metrics/mAP50-95(M)'].idxmax(), 'epoch']})")

# Training loss summary (calculate total loss by summing all loss components)
print("\n=== Training Loss Summary ===")
print(f"Initial Total Loss: {(df['train/box_loss'] + df['train/seg_loss'] + df['train/cls_loss'] + df['train/dfl_loss']).iloc[0]:.4f}")
print(f"Final Total Loss: {(df['train/box_loss'] + df['train/seg_loss'] + df['train/cls_loss'] + df['train/dfl_loss']).iloc[-1]:.4f}")
print(f"Loss Reduction: {((df['train/box_loss'] + df['train/seg_loss'] + df['train/cls_loss'] + df['train/dfl_loss']).iloc[0] - (df['train/box_loss'] + df['train/seg_loss'] + df['train/cls_loss'] + df['train/dfl_loss']).iloc[-1]):.4f}")