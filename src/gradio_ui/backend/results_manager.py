"""
Results Manager for Gradio UI

Handles results aggregation, session management, and export functionality.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, List
import json
import zipfile
import pandas as pd

# Add repo root to path
repo_root = Path(__file__).parents[3]
sys.path.insert(0, str(repo_root))


class ResultsManager:
    """Manages analysis results and export functionality"""
    
    def __init__(self, config):
        """
        Initialize results manager
        
        Args:
            config: UIConfig instance
        """
        self.config = config
        
    def get_session_summary(self) -> Tuple[str, List[str]]:
        """
        Get summary of current session results
        
        Returns:
            (summary_text, list_of_result_image_paths)
        """
        try:
            summary_lines = ["📊 SESSION SUMMARY\n"]
            summary_lines.append("=" * 40 + "\n")
            
            # Count processed images
            processed_dir = self.config.processed_dir
            jpg_files = list(processed_dir.glob("*.jpg"))
            png_files = list(processed_dir.glob("*.png"))
            
            summary_lines.append(f"📁 Processed Images: {len(jpg_files)}")
            summary_lines.append(f"📁 Background-Removed: {len(png_files)}")
            
            # Count segmentation results
            seg_files = list(processed_dir.glob("*_segmented_*.jpg"))
            summary_lines.append(f"🔬 Segmented Images: {len(seg_files)}")
            
            # Count analysis results
            results_dir = self.config.results_dir
            lignin_files = list(results_dir.glob("*_lignin_*.jpg"))
            pectin_files = list(results_dir.glob("*_pectin_*.jpg"))
            
            summary_lines.append(f"🧪 Lignin Analyses: {len(lignin_files)}")
            summary_lines.append(f"🧪 Pectin Analyses: {len(pectin_files)}")
            
            # Total
            total_analyses = len(lignin_files) + len(pectin_files)
            summary_lines.append(f"\n✅ Total Analyses: {total_analyses}")
            
            # Storage info
            summary_lines.append(f"\n📂 Results Location:")
            summary_lines.append(f"   {results_dir}")
            
            # Collect all result images for gallery
            result_images = []
            result_images.extend([str(f) for f in seg_files])
            result_images.extend([str(f) for f in lignin_files])
            result_images.extend([str(f) for f in pectin_files])
            
            summary = "\n".join(summary_lines)
            return summary, result_images
            
        except Exception as e:
            return f"❌ Error getting session summary: {str(e)}", []
    
    def export_results(self, format: str) -> str:
        """
        Export all results in specified format
        
        Args:
            format: "CSV", "Excel", or "ZIP (All Files)"
            
        Returns:
            Path to exported file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == "CSV":
                return self._export_csv(timestamp)
            elif format == "Excel":
                return self._export_excel(timestamp)
            elif format == "ZIP (All Files)":
                return self._export_zip(timestamp)
            else:
                return None
                
        except Exception as e:
            print(f"Export error: {e}")
            return None
    
    def _export_csv(self, timestamp: str) -> str:
        """Export aggregated results as CSV with actual metrics data"""
        csv_path = self.config.temp_dir / f"results_{timestamp}.csv"

        # Collect all JSON metrics files
        results_dir = self.config.results_dir
        metrics_files = list(results_dir.glob("*_metrics.json"))

        if not metrics_files:
            # No data yet, create placeholder
            data = [{
                'Note': 'No analysis data available yet',
                'Export_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)
            return str(csv_path)

        # Read all metrics and aggregate
        all_data = []
        for metrics_file in sorted(metrics_files):
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                    all_data.append(metrics)
            except Exception as e:
                print(f"Error reading {metrics_file}: {e}")

        # Create DataFrame with actual data
        df = pd.DataFrame(all_data)

        # Reorder columns for better readability
        preferred_order = ['image_name', 'analysis_type', 'timestamp',
                          'pixels_detected', 'total_pixels', 'ratio',
                          'area_microns2', 'sensitivity']

        # Only use columns that exist
        columns = [col for col in preferred_order if col in df.columns]
        df = df[columns]

        df.to_csv(csv_path, index=False)

        return str(csv_path)
    
    def _export_excel(self, timestamp: str) -> str:
        """Export results as formatted Excel workbook with actual data"""
        excel_path = self.config.temp_dir / f"results_{timestamp}.xlsx"

        # Collect all metrics
        results_dir = self.config.results_dir
        metrics_files = list(results_dir.glob("*_metrics.json"))

        # Create workbook with multiple sheets
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = [{
                'Export_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Project': 'Alfalfa Cell Segmentation Analysis',
                'Total_Analyses': len(metrics_files),
                'Lignin_Analyses': len([f for f in metrics_files if 'lignin' in f.name]),
                'Pectin_Analyses': len([f for f in metrics_files if 'pectin' in f.name])
            }]
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)

            # Read all metrics data
            if metrics_files:
                all_data = []
                for metrics_file in sorted(metrics_files):
                    try:
                        with open(metrics_file, 'r') as f:
                            metrics = json.load(f)
                            all_data.append(metrics)
                    except Exception as e:
                        print(f"Error reading {metrics_file}: {e}")

                if all_data:
                    # All Results sheet
                    df_all = pd.DataFrame(all_data)
                    df_all.to_excel(writer, sheet_name='All Results', index=False)

                    # Separate sheets for lignin and pectin
                    lignin_data = [d for d in all_data if d.get('analysis_type') == 'Lignin (PG)']
                    if lignin_data:
                        df_lignin = pd.DataFrame(lignin_data)
                        df_lignin.to_excel(writer, sheet_name='Lignin Results', index=False)

                    pectin_data = [d for d in all_data if d.get('analysis_type') == 'Pectin (RR)']
                    if pectin_data:
                        df_pectin = pd.DataFrame(pectin_data)
                        df_pectin.to_excel(writer, sheet_name='Pectin Results', index=False)

        return str(excel_path)
    
    def _export_zip(self, timestamp: str) -> str:
        """Export all result files as ZIP archive with data"""
        zip_path = self.config.temp_dir / f"results_{timestamp}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all processed images
            for img in self.config.processed_dir.glob("*.*"):
                if img.suffix in ['.jpg', '.png']:
                    zipf.write(img, f"processed/{img.name}")

            # Add all result images and JSON metrics
            for file in self.config.results_dir.glob("*.*"):
                if file.suffix in ['.jpg', '.png', '.json']:
                    zipf.write(file, f"results/{file.name}")

            # Generate and add CSV with all metrics
            csv_temp = self._export_csv(timestamp)
            if Path(csv_temp).exists():
                zipf.write(csv_temp, f"data/analysis_results_{timestamp}.csv")

            # Add a comprehensive README
            metrics_count = len(list(self.config.results_dir.glob("*_metrics.json")))
            readme_content = f"""
Alfalfa Cell Segmentation Analysis Results
==========================================

Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Analyses: {metrics_count}

Contents:
---------
1. processed/
   - Segmented and background-removed images
   - Original processed JPG files

2. results/
   - Chemical analysis visualization images
   - *_lignin_detected.jpg : Lignin detection overlays
   - *_pectin_detected.jpg : Pectin detection overlays
   - *_metrics.json : Raw quantitative data for each analysis

3. data/
   - analysis_results_{timestamp}.csv : Consolidated metrics table
     Columns: image_name, analysis_type, timestamp, pixels_detected,
              total_pixels, ratio, area_microns2, sensitivity

Data Description:
-----------------
- pixels_detected: Number of pixels matching the chemical stain color
- total_pixels: Total non-white pixels in the image
- ratio: pixels_detected / total_pixels (0-1 scale)
- area_microns2: Detected area in square microns
- sensitivity: Detection sensitivity used (1-10 scale)

For questions, contact your research coordinator.
            """.strip()

            zipf.writestr("README.txt", readme_content)

        return str(zip_path)
