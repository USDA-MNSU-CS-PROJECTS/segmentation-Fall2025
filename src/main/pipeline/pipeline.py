#!/usr/bin/env python3
"""
Alfalfa Segmentation Pipeline - Main Orchestrator

This module serves as the main entry point and orchestrator for the complete alfalfa image segmentation pipeline.
It coordinates the execution of all pipeline stages in the correct sequence, from raw ND2 microscopy files
through preprocessing to machine learning data preparation.

Pipeline stages:
1. ND2 to TIFF conversion - Converts Nikon Digital microscopy files to standard TIFF format
2. Image preprocessing - Removes backgrounds and crops images to focus on plant subjects
3. ML data preparation - Organizes processed images into training/validation/test datasets
4. TODO: Machine Learning Training - Trains a CNN model to classify cell wall types

Key features:
- Configurable pipeline execution (can skip individual stages)
- Comprehensive logging and error handling
- Command-line interface with flexible options
- Automatic path resolution and directory management
- Progress tracking and timing information
- Robust error recovery and reporting
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
sys.path.append(str(core_dir))

try:
    from tiff_converter import main as convert_nd2_to_tiff  # type: ignore
    from image_preprocessing import main as preprocess_images  # type: ignore
except ImportError:
    # This will be resolved at runtime when sys.path is set
    convert_nd2_to_tiff = None
    preprocess_images = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alfalfa_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AlfalfaPipeline:
    """Main pipeline orchestrator for alfalfa image processing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize pipeline with configuration"""
        self.config = config or self._default_config()
        self.start_time = time.time()
        
        # Setup paths
        self.current_dir = Path(__file__).parent
        self.src_dir = self.current_dir.parent.parent.parent
        self.data_dir = self.src_dir / "src" / "data"
        
        logger.info(f"Pipeline initialized with config: {self.config}")
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration parameters"""
        return {
            "run_tiff_conversion": True,
            "run_preprocessing": True,
            "run_ml_prep": True,
            "max_images": None,  # None = process all
            "expansions_pixels": 25,
            "crop_margin": 100,
            "ml_train_split": 0.8,
            "ml_val_split": 0.1,
            "ml_test_split": 0.1
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
    
    def run_preprocessing(self) -> bool:
        """Run background removal preprocessing"""
        if not self.config["run_preprocessing"]:
            logger.info("Skipping preprocessing (disabled in config)")
            return True
            
        if preprocess_images is None:
            logger.error("Image preprocessor not available - check imports. Please check the imports in the pipeline.py file.")
            return False
            
        logger.info("Starting image preprocessing...")
        try:
            preprocess_images()
            logger.info("Image preprocessing completed successfully")
            return True
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return False
    
    def prepare_ml_data(self) -> bool:
        """Prepare data for machine learning training"""
        if not self.config["run_ml_prep"]:
            logger.info("Skipping ML data preparation (disabled in config)")
            return True
            
        logger.info("Preparing data for machine learning...")
        
        try:
            from ml_data_prep import prepare_training_data
            prepare_training_data(self.config)
            logger.info("ML data preparation completed successfully")
            return True
        except Exception as e:
            logger.error(f"ML data preparation failed: {e}. Please check the imports in the pipeline.py file.")
            return False
    
    def run_full_pipeline(self) -> bool:
        """Run the complete pipeline"""
        logger.info("=" * 60)
        logger.info("STARTING ALFALFA SEGMENTATION PIPELINE")
        logger.info("=" * 60)
        
        # Check inputs
        if not self.check_inputs():
            return False
        
        # Run pipeline steps
        steps = [
            ("TIFF Conversion", self.run_tiff_conversion),
            ("Image Preprocessing", self.run_preprocessing),
            ("ML Data Preparation", self.prepare_ml_data)
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
    parser.add_argument("--skip-preprocessing", action="store_true", help="Skip preprocessing")
    parser.add_argument("--skip-ml", action="store_true", help="Skip ML data preparation")
    parser.add_argument("--max-images", type=int, help="Maximum number of images to process")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Override with command line arguments
    if args.skip_tiff:
        config["run_tiff_conversion"] = False
    if args.skip_preprocessing:
        config["run_preprocessing"] = False
    if args.skip_ml:
        config["run_ml_prep"] = False
    if args.max_images:
        config["max_images"] = args.max_images
    
    # Run pipeline
    pipeline = AlfalfaPipeline(config)
    success = pipeline.run_full_pipeline()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
