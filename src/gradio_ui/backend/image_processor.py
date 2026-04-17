"""
Image Processor for Gradio UI

Handles image uploads and conversion from ND2/TIFF to JPG format.
Wraps existing conversion logic from the pipeline.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
import shutil
import cv2
import numpy as np

# Add repo root to path
repo_root = Path(__file__).parents[3]
sys.path.insert(0, str(repo_root))


class ImageProcessor:
    """Handles image uploads and format conversions for Gradio UI"""
    
    def __init__(self, config):
        """
        Initialize image processor
        
        Args:
            config: UIConfig instance with paths and settings
        """
        self.config = config
        
    def process_uploads(self, files: List[str]) -> Tuple[str, List[str]]:
        """
        Process uploaded files and convert to JPG format
        
        Handles multiple file formats:
        - .nd2 → TIFF → JPG
        - .tiff/.tif → JPG
        - .jpg/.jpeg → copy to processed folder
        
        Args:
            files: List of file paths from Gradio upload
            
        Returns:
            (status_message, list_of_jpg_paths)
        """
        if not files or len(files) == 0:
            return "⚠️ No files uploaded", []
        
        try:
            processed_images = []
            status_lines = ["📤 Processing uploaded files...\n"]
            
            for file_path in files:
                file_path = Path(file_path)
                
                if not file_path.exists():
                    status_lines.append(f"⚠️  Skipped: {file_path.name} (not found)")
                    continue
                
                # Determine file type and process accordingly
                ext = file_path.suffix.lower()
                
                if ext == '.nd2':
                    jpg_path = self._process_nd2(file_path, status_lines)
                elif ext in ['.tiff', '.tif']:
                    jpg_path = self._process_tiff(file_path, status_lines)
                elif ext in ['.jpg', '.jpeg', '.png']:
                    jpg_path = self._process_jpg(file_path, status_lines)
                else:
                    status_lines.append(f"⚠️  Skipped: {file_path.name} (unsupported format)")
                    continue
                
                if jpg_path:
                    processed_images.append(str(jpg_path))
            
            # Summary
            status_lines.append(f"\n✅ Processed {len(processed_images)} image(s) successfully!")
            status_lines.append(f"📁 Saved to: {self.config.processed_dir.name}/")
            
            status = "\n".join(status_lines)
            return status, processed_images
            
        except Exception as e:
            return f"❌ Error processing files: {str(e)}", []
    
    def _process_nd2(self, nd2_path: Path, status_lines: List[str]) -> Optional[Path]:
        """Convert ND2 → TIFF → JPG"""
        try:
            status_lines.append(f"🔄 Converting: {nd2_path.name} (ND2 → JPG)")

            # Read ND2 file directly
            import nd2
            import tifffile

            # Open ND2 file
            with nd2.ND2File(str(nd2_path)) as nd2_file:
                # Get the image data (first frame/position if multiple)
                img_data = nd2_file.asarray()

                # Handle different array shapes
                if img_data.ndim == 4:  # (T, H, W, C) or similar
                    img_data = img_data[0]  # Take first frame
                elif img_data.ndim == 2:  # Grayscale
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_GRAY2BGR)

                # Normalize to 8-bit if needed
                if img_data.dtype != np.uint8:
                    # Normalize to 0-255
                    img_min = img_data.min()
                    img_max = img_data.max()
                    if img_max > img_min:
                        img_data = ((img_data - img_min) / (img_max - img_min) * 255).astype(np.uint8)
                    else:
                        img_data = np.zeros_like(img_data, dtype=np.uint8)

                # Convert BGR to RGB if needed (ND2 is usually RGB, OpenCV uses BGR)
                if img_data.shape[-1] == 3:
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)

            # Save directly as JPG
            jpg_name = f"{nd2_path.stem}.jpg"
            jpg_path = self.config.processed_dir / jpg_name
            cv2.imwrite(str(jpg_path), img_data, [cv2.IMWRITE_JPEG_QUALITY, 95])

            status_lines.append(f"   ✅ {nd2_path.name} → {jpg_path.name}")
            return jpg_path

        except Exception as e:
            status_lines.append(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _process_tiff(self, tiff_path: Path, status_lines: List[str]) -> Optional[Path]:
        """Convert TIFF → JPG"""
        try:
            status_lines.append(f"🔄 Converting: {tiff_path.name} (TIFF → JPG)")
            jpg_path = self._tiff_to_jpg(tiff_path, tiff_path.stem)
            status_lines.append(f"   ✅ {tiff_path.name} → {jpg_path.name}")
            return jpg_path
        except Exception as e:
            status_lines.append(f"   ❌ Error: {e}")
            return None
    
    def _process_jpg(self, jpg_path: Path, status_lines: List[str]) -> Optional[Path]:
        """Copy JPG/PNG to processed folder"""
        try:
            status_lines.append(f"📋 Copying: {jpg_path.name}")
            
            # Copy to processed directory
            dest = self.config.processed_dir / jpg_path.name
            shutil.copy2(jpg_path, dest)
            
            status_lines.append(f"   ✅ {jpg_path.name}")
            return dest
        except Exception as e:
            status_lines.append(f"   ❌ Error: {e}")
            return None
    
    def _tiff_to_jpg(self, tiff_path: Path, base_name: str) -> Path:
        """Convert TIFF to JPG using existing converter"""
        import cv2
        import numpy as np
        from PIL import Image
        
        # Read TIFF
        img = cv2.imread(str(tiff_path))
        
        if img is None:
            raise ValueError(f"Could not read TIFF: {tiff_path}")
        
        # Save as JPG
        jpg_name = f"{base_name}.jpg"
        jpg_path = self.config.processed_dir / jpg_name
        
        cv2.imwrite(str(jpg_path), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        return jpg_path
