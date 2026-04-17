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
        """Export aggregated results as CSV"""
        # Create a comprehensive CSV with all metrics
        csv_path = self.config.temp_dir / f"results_{timestamp}.csv"
        
        # Scan for all result files and aggregate
        data = []
        
        # This is a simplified version - could be enhanced
        # to parse actual analysis results from saved metadata
        
        results_dir = self.config.results_dir
        
        # Add header
        data.append({
            'Timestamp': timestamp,
            'Session': 'Alfalfa Analysis',
            'Export_Format': 'CSV'
        })
        
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        
        return str(csv_path)
    
    def _export_excel(self, timestamp: str) -> str:
        """Export results as formatted Excel workbook"""
        excel_path = self.config.temp_dir / f"results_{timestamp}.xlsx"
        
        # Create workbook with multiple sheets
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = [{
                'Export_Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Session': 'Alfalfa Cell Analysis'
            }]
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Could add more sheets for detailed results
        
        return str(excel_path)
    
    def _export_zip(self, timestamp: str) -> str:
        """Export all result files as ZIP archive"""
        zip_path = self.config.temp_dir / f"results_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all processed images
            for img in self.config.processed_dir.glob("*.*"):
                if img.suffix in ['.jpg', '.png']:
                    zipf.write(img, f"processed/{img.name}")
            
            # Add all result images
            for img in self.config.results_dir.glob("*.*"):
                if img.suffix in ['.jpg', '.png']:
                    zipf.write(img, f"results/{img.name}")
            
            # Add a README
            readme_content = f"""
Alfalfa Cell Segmentation Analysis Results
==========================================

Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Contents:
- processed/ : Segmented and background-removed images
- results/   : Chemical analysis visualizations (lignin, pectin)

For questions, contact your research coordinator.
            """.strip()
            
            zipf.writestr("README.txt", readme_content)
        
        return str(zip_path)
