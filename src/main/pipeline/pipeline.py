#!/usr/bin/env python3
"""
Alfalfa Segmentation Pipeline - Main Orchestrator

This module serves as the main entry point and orchestrator for the complete alfalfa image segmentation pipeline.
It coordinates the execution of all pipeline stages in the correct sequence, from raw ND2 microscopy files
through YOLO-based segmentation and background removal.

Pipeline stages:
1. ND2 to TIFF conversion - Converts Nikon Digital microscopy files to standard TIFF format
2. TIFF to JPG conversion - Converts TIFF files to JPG format for visualization
3. PAUSE - Manual step for user to set up yolo_train folder with images and labels
4. YOLO data.yaml generation - Creates data.yaml file for YOLO training
5. YOLO training - Trains YOLO segmentation model
6. YOLO detection - Runs inference on images using trained model
7. YOLO background removal - Removes background using trained segmentation model
8. Lignin detection - Detects lignin regions in processed images
9. Pectin detection - Detects pectin regions in processed images

Key features:
- Configurable pipeline execution (can skip individual stages)
- Comprehensive logging and error handling
- Command-line interface with flexible options
- Automatic path resolution and directory management
- Progress tracking and timing information
- Robust error recovery and reporting
- Manual pause for user intervention
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the core module to path for imports
current_dir = Path(__file__).parent
core_dir = current_dir.parent / "core"
yolo_dir = core_dir / "yolo"
detectors_dir = core_dir / "detectors"
sys.path.append(str(core_dir))
sys.path.append(str(yolo_dir))
sys.path.append(str(detectors_dir))

try:
    from tiff_converter import main as convert_nd2_to_tiff  # type: ignore
    from jpg_converter import main as convert_tiff_to_jpg  # type: ignore
    from yolo_data_yaml_generator import main as generate_yolo_data_yaml  # type: ignore
    from yolo_train import main as train_yolo_model  # type: ignore
    from yolo_detection import main as run_yolo_detection  # type: ignore
    from yolo_background_removal import main as run_yolo_background_removal  # type: ignore
except ImportError:
    # This will be resolved at runtime when sys.path is set
    convert_nd2_to_tiff = None
    convert_tiff_to_jpg = None
    generate_yolo_data_yaml = None
    train_yolo_model = None
    run_yolo_detection = None
    run_yolo_background_removal = None

# Detector imports will be handled dynamically due to parentheses in filenames
run_lignin_detection = None
run_pectin_detection = None

# Configure logging - use absolute path for log file (important for SLURM)
log_file = Path(__file__).resolve().parent.parent.parent.parent / 'alfalfa_pipeline.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AlfalfaPipeline:
    """Main pipeline orchestrator for alfalfa image processing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize pipeline with configuration"""
        self.start_time = time.time()
        
        # Setup paths first - use resolve() for absolute paths (important for SLURM)
        self.current_dir = Path(__file__).resolve().parent
        self.src_dir = self.current_dir.parent.parent.parent
        self.data_dir = self.src_dir / "src" / "data"
        
        # Ensure we're in the right directory structure
        if not self.src_dir.exists():
            # Try alternative: assume we're at repo root
            potential_repo_root = Path.cwd()
            potential_data_dir = potential_repo_root / "src" / "data"
            if potential_data_dir.exists():
                self.src_dir = potential_repo_root
                self.data_dir = potential_data_dir
                logger.info(f"Using alternative path resolution: {self.data_dir}")
        
        # Load configuration
        if config is None:
            loaded_config = self._load_config_file()
            if loaded_config:
                # Merge loaded config with defaults to ensure all keys exist
                default_config = self._default_config()
                default_config.update(loaded_config)
                config = default_config
            else:
                config = self._default_config()
        self.config = config
        
        logger.info(f"Pipeline initialized with config: {self.config}")
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from config file if it exists"""
        config_path = self.current_dir.parent.parent.parent.parent / "config" / "pipeline_config.json"
        if config_path.exists():
            try:
                import json
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from: {config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config file {config_path}: {e}")
                logger.info("Using default configuration")
        return None
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration parameters"""
        return {
            "run_tiff_conversion": True,
            "run_jpg_conversion": True,
            "run_yolo_data_yaml": True,
            "run_yolo_training": True,
            "run_yolo_detection": True,
            "run_yolo_background_removal": True,
            "run_lignin_detection": True,
            "run_pectin_detection": True,
            "max_images": None,  # None = process all
            "yolo_epochs": 100,
            "yolo_batch_size": 4,
            "yolo_image_size": 640,
            "yolo_conf_threshold": 0.25,
            "yolo_iou_threshold": 0.45,
            "yolo_canvas_size": 5000,
            "yolo_device": None,  # None = auto-detect, or specify "0", "1", "cpu", "cuda"
            "detector_conf_threshold": 0.25,
            "detector_mask_mode": "auto"
        }
    
    def check_inputs(self) -> bool:
        """Check if input ND2 files exist"""
        input_dir = self.data_dir / "nd2_images" / "input_images"
        
        if not input_dir.exists():
            logger.error(f"Input directory for nd2 images does not exist. Please create the input directory: {input_dir}")
            return False
            
        nd2_files = list(input_dir.glob("*.nd2"))
        if not nd2_files:
            logger.error(f"No ND2 files found in {input_dir}. Please add ND2 files to the input directory.")
            return False
            
        logger.info(f"Found {len(nd2_files)} ND2 files to process")
        return True
    
    def run_tiff_conversion(self) -> bool:
        """Run ND2 to TIFF conversion"""
        if not self.config["run_tiff_conversion"]:
            logger.info("Skipping TIFF conversion (disabled in config)")
            return True
            
        if convert_nd2_to_tiff is None:
            logger.error("TIFF converter not available - check imports. Please check the imports in the pipeline.py file.")
            return False
            
        logger.info("Starting ND2 to TIFF conversion...")
        try:
            convert_nd2_to_tiff()
            logger.info("TIFF conversion completed successfully")
            return True
        except Exception as e:
            logger.error(f"TIFF conversion failed: {e}")
            return False
    
    def run_jpg_conversion(self) -> bool:
        """Run TIFF to JPG conversion"""
        if not self.config["run_jpg_conversion"]:
            logger.info("Skipping JPG conversion (disabled in config)")
            return True
            
        if convert_tiff_to_jpg is None:
            logger.error("JPG converter not available - check imports. Please check the imports in the pipeline.py file.")
            return False
            
        logger.info("Starting TIFF to JPG conversion...")
        try:
            convert_tiff_to_jpg()
            logger.info("JPG conversion completed successfully")
            return True
        except Exception as e:
            logger.error(f"JPG conversion failed: {e}")
            return False
    
    def manual_pause_for_yolo_setup(self) -> bool:
        """Pause pipeline for manual YOLO training data setup"""
        # Skip manual pause if running in SLURM (non-interactive environment)
        if os.environ.get("SLURM_JOB_RUNNING") or os.environ.get("SLURM_JOB_ID"):
            logger.info("Running in SLURM environment - skipping manual pause")
            logger.info("Assuming YOLO training data is already set up")
            # Check if YOLO training data exists
            yolo_train_dir = self.data_dir / "yolo_train"
            if not yolo_train_dir.exists():
                logger.warning(f"YOLO training directory not found: {yolo_train_dir}")
                logger.warning("Pipeline may fail if training data is required")
            else:
                logger.info(f"YOLO training directory found: {yolo_train_dir}")
            return True
        
        # Interactive mode (local execution)
        logger.info("=" * 60)
        logger.info("MANUAL PAUSE: YOLO Training Data Setup Required")
        logger.info("=" * 60)
        logger.info("Please complete the following steps:")
        logger.info("1. Set up your yolo_train folder structure:")
        logger.info("   - src/data/yolo_train/images/ (put your training images here)")
        logger.info("   - src/data/yolo_train/labels/ (put your label files here)")
        logger.info("   - src/data/yolo_train/classes.txt (define your classes)")
        logger.info("")
        logger.info("2. Ensure your images and labels are properly formatted for YOLO")
        logger.info("3. When ready, press Enter to continue...")
        logger.info("=" * 60)
        
        try:
            input("Press Enter when you have completed the YOLO training data setup...")
            logger.info("Continuing with YOLO pipeline steps...")
            return True
        except KeyboardInterrupt:
            logger.info("Pipeline paused by user. You can resume later.")
            return False
    
    def run_yolo_data_yaml_generation(self) -> bool:
        """Generate YOLO data.yaml file"""
        if not self.config["run_yolo_data_yaml"]:
            logger.info("Skipping YOLO data.yaml generation (disabled in config)")
            return True
            
        if generate_yolo_data_yaml is None:
            logger.error("YOLO data.yaml generator not available - check imports")
            return False
            
        logger.info("Starting YOLO data.yaml generation...")
        try:
            # Set up paths for YOLO data.yaml generation
            yolo_train_dir = self.data_dir / "yolo_train"
            if not yolo_train_dir.exists():
                logger.error(f"YOLO training directory not found: {yolo_train_dir}")
                logger.error("Please set up the yolo_train folder structure first")
                return False
            
            # Temporarily modify sys.argv to pass arguments
            original_argv = sys.argv
            sys.argv = ["yolo_data_yaml_generator.py", "--dataset-root", str(yolo_train_dir)]
            
            try:
                generate_yolo_data_yaml()
                logger.info("YOLO data.yaml generation completed successfully")
                return True
            finally:
                sys.argv = original_argv
                
        except Exception as e:
            logger.error(f"YOLO data.yaml generation failed: {e}")
            return False
    
    def run_yolo_training(self) -> bool:
        """Run YOLO model training"""
        if not self.config["run_yolo_training"]:
            logger.info("Skipping YOLO training (disabled in config)")
            return True
            
        if train_yolo_model is None:
            logger.error("YOLO trainer not available - check imports")
            return False
            
        logger.info("Starting YOLO model training...")
        try:
            # Set up paths for YOLO training
            yolo_train_dir = self.data_dir / "yolo_train"
            data_yaml = yolo_train_dir / "data.yaml"
            
            if not data_yaml.exists():
                logger.error(f"YOLO data.yaml not found: {data_yaml}")
                logger.error("Please run YOLO data.yaml generation first")
                return False
            
            # Temporarily modify sys.argv to pass arguments
            original_argv = sys.argv
            sys.argv = [
                "yolo_train.py",
                "--data", str(data_yaml),
                "--epochs", str(self.config["yolo_epochs"]),
                "--batch", str(self.config["yolo_batch_size"]),
                "--imgsz", str(self.config["yolo_image_size"])
            ]
            # Add device argument if specified in config
            if self.config.get("yolo_device") is not None:
                sys.argv.extend(["--device", str(self.config["yolo_device"])])
            
            try:
                train_yolo_model()
                logger.info("YOLO training completed successfully")
                return True
            finally:
                sys.argv = original_argv
                
        except Exception as e:
            logger.error(f"YOLO training failed: {e}")
            return False
    
    def run_yolo_detection(self) -> bool:
        """Run YOLO detection on images"""
        if not self.config["run_yolo_detection"]:
            logger.info("Skipping YOLO detection (disabled in config)")
            return True
            
        if run_yolo_detection is None:
            logger.error("YOLO detector not available - check imports")
            return False
            
        logger.info("Starting YOLO detection...")
        try:
            # Temporarily modify sys.argv to pass arguments
            original_argv = sys.argv
            sys.argv = [
                "yolo_detection.py",
                "--folders", "jpg_images",
                "--conf", str(self.config["yolo_conf_threshold"]),
                "--iou", str(self.config["yolo_iou_threshold"])
            ]
            
            try:
                run_yolo_detection()
                logger.info("YOLO detection completed successfully")
                return True
            finally:
                sys.argv = original_argv
                
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
            return False
    
    def run_yolo_background_removal(self) -> bool:
        """Run YOLO background removal"""
        if not self.config["run_yolo_background_removal"]:
            logger.info("Skipping YOLO background removal (disabled in config)")
            return True
            
        if run_yolo_background_removal is None:
            logger.error("YOLO background removal not available - check imports")
            return False
            
        logger.info("Starting YOLO background removal...")
        try:
            # Temporarily modify sys.argv to pass arguments
            original_argv = sys.argv
            sys.argv = [
                "yolo_background_removal.py",
                "--input", "jpg_images",
                "--conf", str(self.config["yolo_conf_threshold"]),
                "--iou", str(self.config["yolo_iou_threshold"]),
                "--canvas-size", str(self.config["yolo_canvas_size"])
            ]
            
            try:
                run_yolo_background_removal()
                logger.info("YOLO background removal completed successfully")
                return True
            finally:
                sys.argv = original_argv
                
        except Exception as e:
            logger.error(f"YOLO background removal failed: {e}")
            return False
    
    def run_lignin_detection(self) -> bool:
        """Run lignin detection on processed images"""
        if not self.config["run_lignin_detection"]:
            logger.info("Skipping lignin detection (disabled in config)")
            return True
            
        logger.info("Starting lignin detection...")
        try:
            # Dynamically import the detector module
            import importlib.util
            detector_path = self.current_dir.parent / "core" / "detectors" / "Lignin(PG)_detector.py"
            spec = importlib.util.spec_from_file_location("lignin_detector", detector_path)
            lignin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lignin_module)
            
            # Temporarily modify sys.argv to pass arguments
            original_argv = sys.argv
            sys.argv = [
                "Lignin(PG)_detector.py",
                "--batch",
                "--conf", str(self.config["detector_conf_threshold"]),
                "--mask-mode", self.config["detector_mask_mode"]
            ]
            
            try:
                lignin_module.main()
                logger.info("Lignin detection completed successfully")
                return True
            finally:
                sys.argv = original_argv
                
        except Exception as e:
            logger.error(f"Lignin detection failed: {e}")
            return False
    
    def run_pectin_detection(self) -> bool:
        """Run pectin detection on processed images"""
        if not self.config["run_pectin_detection"]:
            logger.info("Skipping pectin detection (disabled in config)")
            return True
            
        logger.info("Starting pectin detection...")
        try:
            # Dynamically import the detector module
            import importlib.util
            detector_path = self.current_dir.parent / "core" / "detectors" / "Pectin(RR)_detector.py"
            spec = importlib.util.spec_from_file_location("pectin_detector", detector_path)
            pectin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pectin_module)
            
            # Temporarily modify sys.argv to pass arguments
            original_argv = sys.argv
            sys.argv = [
                "Pectin(RR)_detector.py",
                "--batch",
                "--conf", str(self.config["detector_conf_threshold"]),
                "--mask-mode", self.config["detector_mask_mode"]
            ]
            
            try:
                pectin_module.main()
                logger.info("Pectin detection completed successfully")
                return True
            finally:
                sys.argv = original_argv
                
        except Exception as e:
            logger.error(f"Pectin detection failed: {e}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """Run the complete pipeline"""
        logger.info("=" * 60)
        logger.info("STARTING ALFALFA SEGMENTATION PIPELINE")
        logger.info("=" * 60)
        
        # Check inputs only if TIFF or JPG conversion is enabled
        if self.config["run_tiff_conversion"] or self.config["run_jpg_conversion"]:
            if not self.check_inputs():
                return False
        else:
            logger.info("Skipping ND2 file check (TIFF and JPG conversion are disabled)")
        
        # Run pipeline steps
        steps = [
            ("TIFF Conversion", self.run_tiff_conversion),
            ("JPG Conversion", self.run_jpg_conversion),
            ("Manual YOLO Setup", self.manual_pause_for_yolo_setup),
            ("YOLO Data.yaml Generation", self.run_yolo_data_yaml_generation),
            ("YOLO Training", self.run_yolo_training),
            ("YOLO Detection", self.run_yolo_detection),
            ("YOLO Background Removal", self.run_yolo_background_removal),
            ("Lignin Detection", self.run_lignin_detection),
            ("Pectin Detection", self.run_pectin_detection)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n--- {step_name} ---")
            if not step_func():
                logger.error(f"Pipeline failed at step: {step_name}. Please check the imports in the pipeline.py file.")
                return False
        
        # Pipeline completed successfully
        elapsed_time = time.time() - self.start_time
        logger.info("=" * 60)
        logger.info(f"PIPELINE COMPLETED SUCCESSFULLY in {elapsed_time:.2f} seconds")
        logger.info("=" * 60)
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Alfalfa Segmentation Pipeline")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--skip-tiff", action="store_true", help="Skip TIFF conversion")
    parser.add_argument("--skip-jpg", action="store_true", help="Skip JPG conversion")
    parser.add_argument("--skip-yolo-data-yaml", action="store_true", help="Skip YOLO data.yaml generation")
    parser.add_argument("--skip-yolo-training", action="store_true", help="Skip YOLO training")
    parser.add_argument("--skip-yolo-detection", action="store_true", help="Skip YOLO detection")
    parser.add_argument("--skip-yolo-bg-removal", action="store_true", help="Skip YOLO background removal")
    parser.add_argument("--skip-lignin-detection", action="store_true", help="Skip lignin detection")
    parser.add_argument("--skip-pectin-detection", action="store_true", help="Skip pectin detection")
    parser.add_argument("--max-images", type=int, help="Maximum number of images to process")
    parser.add_argument("--yolo-epochs", type=int, help="Number of YOLO training epochs")
    parser.add_argument("--yolo-batch-size", type=int, help="YOLO training batch size")
    parser.add_argument("--yolo-image-size", type=int, help="YOLO training image size")
    parser.add_argument("--yolo-device", type=str, help="YOLO training device (e.g., '0', '1', 'cpu', 'cuda', or null for auto-detect)")
    parser.add_argument("--detector-conf", type=float, help="Detector confidence threshold")
    parser.add_argument("--detector-mask-mode", choices=['auto', 'yolo', 'nonwhite'], help="Detector mask mode")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        # Load default config file if no --config specified
        default_config_path = Path(__file__).parent.parent.parent.parent / "config" / "pipeline_config.json"
        if default_config_path.exists():
            try:
                import json
                with open(default_config_path, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"Failed to load default config: {e}")
                config = {}
    
    # Override with command line arguments
    if args.skip_tiff:
        config["run_tiff_conversion"] = False
    if args.skip_jpg:
        config["run_jpg_conversion"] = False
    if args.skip_yolo_data_yaml:
        config["run_yolo_data_yaml"] = False
    if args.skip_yolo_training:
        config["run_yolo_training"] = False
    if args.skip_yolo_detection:
        config["run_yolo_detection"] = False
    if args.skip_yolo_bg_removal:
        config["run_yolo_background_removal"] = False
    if args.skip_lignin_detection:
        config["run_lignin_detection"] = False
    if args.skip_pectin_detection:
        config["run_pectin_detection"] = False
    if args.max_images:
        config["max_images"] = args.max_images
    if args.yolo_epochs:
        config["yolo_epochs"] = args.yolo_epochs
    if args.yolo_batch_size:
        config["yolo_batch_size"] = args.yolo_batch_size
    if args.yolo_image_size:
        config["yolo_image_size"] = args.yolo_image_size
    if args.yolo_device is not None:
        # Handle "null" string as None for auto-detect
        config["yolo_device"] = None if args.yolo_device.lower() == "null" else args.yolo_device
    if args.detector_conf:
        config["detector_conf_threshold"] = args.detector_conf
    if args.detector_mask_mode:
        config["detector_mask_mode"] = args.detector_mask_mode
    
    # Run pipeline
    pipeline = AlfalfaPipeline(config)
    success = pipeline.run_full_pipeline()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
