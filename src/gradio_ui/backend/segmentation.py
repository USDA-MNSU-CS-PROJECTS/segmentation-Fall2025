"""
YOLO Segmentation Engine for Gradio UI

Wraps the existing YOLO detection and background removal logic
into a simple interface for the web UI.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
import cv2
import numpy as np
from ultralytics import YOLO

# Add repo root to path
repo_root = Path(__file__).parents[3]
sys.path.insert(0, str(repo_root))


class SegmentationEngine:
    """Handles YOLO-based cell segmentation for Gradio UI"""
    
    def __init__(self, config):
        """
        Initialize segmentation engine
        
        Args:
            config: UIConfig instance with model path and settings
        """
        self.config = config
        self.model = None
        self.model_loaded = False
        
    def _load_model(self) -> Tuple[bool, str]:
        """
        Load YOLO model (lazy loading)
        
        Returns:
            (success, message)
        """
        if self.model_loaded and self.model is not None:
            return True, "Model already loaded"
            
        try:
            model_path = self.config.model_path
            
            if not model_path.exists():
                return False, f"❌ Model not found at: {model_path}"
            
            self.model = YOLO(str(model_path))
            self.model_loaded = True
            
            return True, f"✅ Model loaded from: {model_path.name}"
            
        except Exception as e:
            return False, f"❌ Error loading model: {str(e)}"
    
    def check_model_status(self, model_path: str = None) -> str:
        """
        Check if model exists and is loadable
        
        Args:
            model_path: Optional path to model (uses config default if None)
            
        Returns:
            Status message
        """
        if model_path:
            path = Path(model_path)
        else:
            path = self.config.model_path
            
        if not path.exists():
            return f"❌ Model not found\nPath: {path}\n\nPlease download from handover materials or train a new model."
            
        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        
        # Try loading
        try:
            test_model = YOLO(str(path))
            return f"✅ Model is valid!\n\nPath: {path}\nSize: {size_mb:.2f} MB\nStatus: Ready to use"
        except Exception as e:
            return f"❌ Model file exists but cannot be loaded\n\nError: {str(e)}"
    
    def run_segmentation(
        self, 
        image_path: str, 
        confidence: float = 0.25
    ) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
        """
        Run YOLO segmentation on an image
        
        Args:
            image_path: Path to image file
            confidence: Confidence threshold (0.1-0.9)
            
        Returns:
            (status_message, original_path, segmented_path, background_removed_path)
        """
        try:
            # Load model if needed
            success, msg = self._load_model()
            if not success:
                return msg, None, None, None
            
            # Validate input
            image_path = Path(image_path)
            if not image_path.exists():
                return f"❌ Image not found: {image_path}", None, None, None
            
            # Read image
            img = cv2.imread(str(image_path))
            if img is None:
                return f"❌ Could not read image: {image_path}", None, None, None
            
            # Run inference
            results = self.model.predict(
                source=img,
                conf=confidence,
                iou=self.config.iou_threshold,
                max_det=self.config.max_det,
                verbose=False
            )
            
            # Get detection count
            num_detections = len(results[0].boxes) if results[0].boxes is not None else 0
            
            # Create output paths
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = image_path.stem
            
            # Save original (copy for display)
            original_save = self.config.processed_dir / f"{base_name}_original.jpg"
            cv2.imwrite(str(original_save), img)
            
            # Create and save segmented visualization
            segmented_img = results[0].plot()  # Draw boxes and masks
            segmented_save = self.config.processed_dir / f"{base_name}_segmented_{timestamp}.jpg"
            cv2.imwrite(str(segmented_save), segmented_img)
            
            # Create background-removed version
            bg_removed = self._remove_background(img, results[0])
            bg_removed_save = self.config.processed_dir / f"{base_name}_nobg_{timestamp}.png"
            cv2.imwrite(str(bg_removed_save), bg_removed)
            
            # Status message
            status = f"""✅ Segmentation complete!
            
Detections: {num_detections} cell(s) found
Confidence: {confidence}
Model: {self.config.model_path.name}

Outputs saved to: {self.config.processed_dir.name}/
"""
            
            return status, str(original_save), str(segmented_save), str(bg_removed_save)
            
        except Exception as e:
            return f"❌ Error during segmentation: {str(e)}", None, None, None
    
    def _remove_background(self, image: np.ndarray, result) -> np.ndarray:
        """
        Remove background using segmentation masks
        
        Args:
            image: Original image
            result: YOLO result object
            
        Returns:
            Image with background removed (white background)
        """
        # Create white canvas
        canvas = np.ones_like(image) * 255
        
        # Check if we have masks
        if result.masks is None or len(result.masks) == 0:
            # No masks, return original on white background
            return canvas
        
        # Get all masks
        masks = result.masks.data.cpu().numpy()  # Shape: (N, H, W)
        
        # Resize masks to image size if needed
        h, w = image.shape[:2]
        combined_mask = np.zeros((h, w), dtype=np.uint8)
        
        for mask in masks:
            # Resize mask to image dimensions
            resized_mask = cv2.resize(mask, (w, h))
            # Threshold to binary
            binary_mask = (resized_mask > 0.5).astype(np.uint8)
            # Add to combined mask
            combined_mask = cv2.bitwise_or(combined_mask, binary_mask)
        
        # Apply mask: keep detected regions, white background elsewhere
        for c in range(3):  # For each color channel
            canvas[:, :, c] = np.where(combined_mask, image[:, :, c], 255)
        
        return canvas
