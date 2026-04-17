"""
Chemical Analysis Engine for Gradio UI

Wraps the existing Lignin and Pectin detectors for the web interface.
"""

import sys
from pathlib import Path
from typing import Tuple, Optional, Dict
import cv2
import numpy as np
import pandas as pd

# Add repo root to path
repo_root = Path(__file__).parents[3]
sys.path.insert(0, str(repo_root))


class ChemicalAnalyzer:
    """Handles lignin and pectin chemical composition analysis"""
    
    def __init__(self, config):
        """
        Initialize chemical analyzer
        
        Args:
            config: UIConfig instance with settings
        """
        self.config = config
        
    def run_analysis(
        self, 
        image_path: str, 
        analysis_types: list
    ) -> Tuple[str, Optional[str], Optional[str], pd.DataFrame]:
        """
        Run chemical composition analysis
        
        Args:
            image_path: Path to background-removed image
            analysis_types: List of analyses to run ["Lignin (PG)", "Pectin (RR)"]
            
        Returns:
            (status_message, lignin_viz_path, pectin_viz_path, results_dataframe)
        """
        if not image_path:
            return "⚠️ No image selected", None, None, pd.DataFrame()
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return f"❌ Image not found: {image_path}", None, None, pd.DataFrame()
            
            # Read image
            img = cv2.imread(str(image_path))
            if img is None:
                return f"❌ Could not read image", None, None, pd.DataFrame()
            
            status_lines = ["🧪 Running chemical analysis...\n"]
            results = {}
            
            lignin_viz = None
            pectin_viz = None
            
            # Run selected analyses
            if "Lignin (PG)" in analysis_types:
                status_lines.append("🔴 Analyzing lignin (PG staining)...")
                lignin_data = self._analyze_lignin(img, image_path.stem)
                results['lignin'] = lignin_data
                lignin_viz = lignin_data['viz_path']
                status_lines.append(f"   ✅ Lignin ratio: {lignin_data['ratio']:.3f}")
            
            if "Pectin (RR)" in analysis_types:
                status_lines.append("🟣 Analyzing pectin (Ruthenium Red)...")
                pectin_data = self._analyze_pectin(img, image_path.stem)
                results['pectin'] = pectin_data
                pectin_viz = pectin_data['viz_path']
                status_lines.append(f"   ✅ Pectin ratio: {pectin_data['ratio']:.3f}")
            
            # Create results table
            table_data = self._create_results_table(results)
            
            status_lines.append(f"\n✅ Analysis complete!")
            status_lines.append(f"📁 Saved to: {self.config.results_dir.name}/")
            
            status = "\n".join(status_lines)
            return status, lignin_viz, pectin_viz, table_data
            
        except Exception as e:
            return f"❌ Error during analysis: {str(e)}", None, None, pd.DataFrame()
    
    def _analyze_lignin(self, img: np.ndarray, base_name: str) -> Dict:
        """
        Analyze lignin content using HSV color detection (red regions)
        
        Based on Lignin(PG)_detector.py logic
        """
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define red color range for lignin (PG staining)
        # Adjusted based on sensitivity setting
        sensitivity = self.config.lignin_sensitivity
        
        # Red wraps around in HSV (0-10 and 170-180)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10 + sensitivity, 255, 255])
        
        lower_red2 = np.array([170 - sensitivity, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        lignin_mask = cv2.bitwise_or(mask1, mask2)
        
        # Remove background (white pixels)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        non_white_mask = gray < 250
        lignin_mask = cv2.bitwise_and(lignin_mask, lignin_mask, mask=non_white_mask.astype(np.uint8))
        
        # Calculate metrics
        lignin_pixels = np.sum(lignin_mask > 0)
        total_pixels = np.sum(non_white_mask)
        lignin_ratio = lignin_pixels / total_pixels if total_pixels > 0 else 0
        
        # Calculate area in microns (if conversion available)
        area_microns2 = lignin_pixels * (self.config.pixel_to_micron_fallback ** 2)
        
        # Create visualization
        overlay = img.copy()
        overlay[lignin_mask > 0] = [0, 0, 255]  # Red overlay
        
        # Blend
        viz = cv2.addWeighted(img, 0.6, overlay, 0.4, 0)
        
        # Save visualization
        viz_name = f"{base_name}_lignin_detected.jpg"
        viz_path = self.config.results_dir / viz_name
        cv2.imwrite(str(viz_path), viz)
        
        return {
            'pixels': int(lignin_pixels),
            'ratio': float(lignin_ratio),
            'area_microns2': float(area_microns2),
            'viz_path': str(viz_path)
        }
    
    def _analyze_pectin(self, img: np.ndarray, base_name: str) -> Dict:
        """
        Analyze pectin content using HSV color detection (burgundy/deep red)
        
        Based on Pectin(RR)_detector.py logic
        """
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define burgundy/deep red range for pectin (Ruthenium Red)
        sensitivity = self.config.pectin_sensitivity
        
        # Burgundy color range (darker red-purple)
        lower_burgundy = np.array([160 - sensitivity, 40, 40])
        upper_burgundy = np.array([180, 255, 200])
        
        pectin_mask = cv2.inRange(hsv, lower_burgundy, upper_burgundy)
        
        # Remove background
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        non_white_mask = gray < 250
        pectin_mask = cv2.bitwise_and(pectin_mask, pectin_mask, mask=non_white_mask.astype(np.uint8))
        
        # Calculate metrics
        pectin_pixels = np.sum(pectin_mask > 0)
        total_pixels = np.sum(non_white_mask)
        pectin_ratio = pectin_pixels / total_pixels if total_pixels > 0 else 0
        
        # Calculate area
        area_microns2 = pectin_pixels * (self.config.pixel_to_micron_fallback ** 2)
        
        # Create visualization
        overlay = img.copy()
        overlay[pectin_mask > 0] = [128, 0, 128]  # Purple overlay
        
        viz = cv2.addWeighted(img, 0.6, overlay, 0.4, 0)
        
        # Save
        viz_name = f"{base_name}_pectin_detected.jpg"
        viz_path = self.config.results_dir / viz_name
        cv2.imwrite(str(viz_path), viz)
        
        return {
            'pixels': int(pectin_pixels),
            'ratio': float(pectin_ratio),
            'area_microns2': float(area_microns2),
            'viz_path': str(viz_path)
        }
    
    def _create_results_table(self, results: Dict) -> pd.DataFrame:
        """Create a formatted results table"""
        data = []
        
        if 'lignin' in results:
            lig = results['lignin']
            data.append(['Lignin Pixels', f"{lig['pixels']:,}", '-'])
            data.append(['Lignin Ratio', f"{lig['ratio']:.4f}", '-'])
            data.append(['Lignin Area (μm²)', f"{lig['area_microns2']:.2f}", '-'])
        
        if 'pectin' in results:
            pec = results['pectin']
            if 'lignin' in results:
                data[0] = ['Pixels', f"{results['lignin']['pixels']:,}", f"{pec['pixels']:,}"]
                data[1] = ['Ratio', f"{results['lignin']['ratio']:.4f}", f"{pec['ratio']:.4f}"]
                data[2] = ['Area (μm²)', f"{results['lignin']['area_microns2']:.2f}", f"{pec['area_microns2']:.2f}"]
            else:
                data.append(['Pectin Pixels', '-', f"{pec['pixels']:,}"])
                data.append(['Pectin Ratio', '-', f"{pec['ratio']:.4f}"])
                data.append(['Pectin Area (μm²)', '-', f"{pec['area_microns2']:.2f}"])
        
        df = pd.DataFrame(data, columns=['Metric', 'Lignin', 'Pectin'])
        return df
