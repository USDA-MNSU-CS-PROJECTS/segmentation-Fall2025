"""
Configuration management for Gradio UI

Handles all settings and paths for the web interface.
"""

import json
from pathlib import Path
from typing import Any, Dict


class UIConfig:
    """Configuration manager for Gradio UI"""
    
    def __init__(self):
        """Initialize configuration with default values"""
        # Paths
        self.repo_root = Path(__file__).parents[2]  # gradio_ui/config.py -> repo root
        self.temp_dir = self.repo_root / "src/gradio_ui/temp"
        self.uploads_dir = self.temp_dir / "uploads"
        self.processed_dir = self.temp_dir / "processed"
        self.results_dir = self.temp_dir / "results"
        self.cache_dir = self.temp_dir / "cache"
        
        # Model paths
        self.model_path = self._find_model_path()
        
        # Detection parameters
        self.confidence_default = 0.25
        self.iou_threshold = 0.45
        self.max_det = 300
        
        # Chemical analysis parameters
        self.pixel_to_micron_fallback = 0.9785316641067333
        self.lignin_sensitivity = 5  # 1-10 scale
        self.pectin_sensitivity = 5  # 1-10 scale
        
        # Image processing
        self.supported_formats = ['.nd2', '.tiff', '.tif', '.jpg', '.jpeg', '.png']
        self.max_image_size = (4000, 4000)  # Max dimensions for display
        
        # Create directories
        self._ensure_directories()
        
        # Load saved settings if they exist
        self.load_settings()
        
    def _find_model_path(self) -> Path:
        """Find the trained YOLO model automatically"""
        # Search for best.pt in common locations
        search_paths = [
            self.repo_root / "src/data/yolo_results/runs/segment",
            self.repo_root / "runs/segment",
            self.repo_root / "weights"
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                # Find all run folders and get most recent
                run_folders = [d for d in search_path.iterdir() if d.is_dir()]
                if run_folders:
                    latest_run = max(run_folders, key=lambda p: p.stat().st_mtime)
                    best_pt = latest_run / "weights/best.pt"
                    if best_pt.exists():
                        return best_pt
        
        # Default path if not found
        return self.repo_root / "src/data/yolo_results/runs/segment/latest/weights/best.pt"
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.temp_dir, self.uploads_dir, self.processed_dir, 
                         self.results_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from config file"""
        config_file = self.cache_dir / "settings.json"
        
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file, 'r') as f:
                settings = json.load(f)
                
            # Apply loaded settings
            if 'model_path' in settings:
                self.model_path = Path(settings['model_path'])
            if 'confidence_default' in settings:
                self.confidence_default = settings['confidence_default']
            if 'iou_threshold' in settings:
                self.iou_threshold = settings['iou_threshold']
            if 'pixel_to_micron_fallback' in settings:
                self.pixel_to_micron_fallback = settings['pixel_to_micron_fallback']
            if 'lignin_sensitivity' in settings:
                self.lignin_sensitivity = settings['lignin_sensitivity']
            if 'pectin_sensitivity' in settings:
                self.pectin_sensitivity = settings['pectin_sensitivity']
                
            return settings
            
        except Exception as e:
            print(f"Warning: Could not load settings: {e}")
            return {}
    
    def save_settings(self, model_path=None, confidence=None, iou=None, 
                     pixel_micron=None, lignin_sens=None, pectin_sens=None):
        """Save current settings to config file
        
        Args:
            model_path: Path to YOLO model
            confidence: Default confidence threshold
            iou: IOU threshold for NMS
            pixel_micron: Pixel to micron conversion factor
            lignin_sens: Lignin detection sensitivity
            pectin_sens: Pectin detection sensitivity
            
        Returns:
            Status message
        """
        # Update settings if provided
        if model_path is not None:
            self.model_path = Path(model_path)
        if confidence is not None:
            self.confidence_default = confidence
        if iou is not None:
            self.iou_threshold = iou
        if pixel_micron is not None:
            self.pixel_to_micron_fallback = pixel_micron
        if lignin_sens is not None:
            self.lignin_sensitivity = lignin_sens
        if pectin_sens is not None:
            self.pectin_sensitivity = pectin_sens
        
        # Save to file
        config_file = self.cache_dir / "settings.json"
        
        try:
            settings = {
                'model_path': str(self.model_path),
                'confidence_default': self.confidence_default,
                'iou_threshold': self.iou_threshold,
                'pixel_to_micron_fallback': self.pixel_to_micron_fallback,
                'lignin_sensitivity': self.lignin_sensitivity,
                'pectin_sensitivity': self.pectin_sensitivity
            }
            
            with open(config_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
            return "✅ Settings saved successfully!"
            
        except Exception as e:
            return f"❌ Error saving settings: {e}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model
        
        Returns:
            Dictionary with model information
        """
        return {
            'path': str(self.model_path),
            'exists': self.model_path.exists(),
            'size': self.model_path.stat().st_size if self.model_path.exists() else 0,
            'modified': self.model_path.stat().st_mtime if self.model_path.exists() else 0
        }
