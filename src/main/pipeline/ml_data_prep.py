#!/usr/bin/env python3
"""
Machine Learning Data Preparation for Alfalfa Segmentation
Prepares preprocessed images for training ML models to classify cell wall types
Organizes data by plant ID, region, and time point based on filename structure

TODO: INTEGRATION WITH TEAMMATES' IMAGE ANALYSIS WORK
=====================================================
Current state: Uses filename-based classification (a,b,c,d -> 4 classes)
Future state: Will use actual image analysis for classification

INTEGRATION POINTS:
1. Cell wall detection and identification
2. Lignin/pectin color thresholding and quantification  
3. Cell wall segmentation and thickness measurement

CLASSIFICATION LOGIC TO IMPLEMENT:
- thin_non_lignified: Thin walls + Low lignin
- thick_non_lignified: Thick walls + Low lignin
- thin_lignified: Thin walls + High lignin
- thick_lignified: Thick walls + High lignin

FILES TO UPDATE:
- Lines 117-172: Replace filename-based labels with image analysis
- Lines 276-287: Add image analysis results to metadata
- Add new functions for integrating teammates' analysis modules
"""

import os
import json
import shutil
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, NamedTuple
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from collections import defaultdict

logger = logging.getLogger(__name__)

class ImageInfo(NamedTuple):
    """Structure to hold parsed image information"""
    filename: str
    year: str
    plant_id: str
    region: str
    time_point: str
    full_plant_id: str  # year + plant_id (e.g., "20240780")
    full_id: str       # complete identifier (e.g., "20240780a_T0")

def parse_filename(filename: str) -> ImageInfo:
    """
    Parse filename to extract plant information
    
    Expected format: YYYY0XXX[abcd]_T[timepoint]_10xstitch_PG_removed.png
    Example: 20240780a_T0_10xstitch_PG_removed.png
    
    Args:
        filename: The filename to parse
        
    Returns:
        ImageInfo object with parsed information
    """
    # Remove extension
    base_name = filename.replace('_removed.png', '')
    
    # Pattern: YYYY0XXX[abcd]_T[timepoint]_10xstitch_PG
    pattern = r'(\d{4})0(\d{3})([abcd])_T(\d+)_10xstitch_PG'
    match = re.match(pattern, base_name)
    
    if not match:
        raise ValueError(f"Filename '{filename}' doesn't match expected pattern")
    
    year, plant_id, region, time_point = match.groups()
    full_plant_id = f"{year}0{plant_id}"
    full_id = f"{full_plant_id}{region}_T{time_point}"
    
    return ImageInfo(
        filename=filename,
        year=year,
        plant_id=plant_id,
        region=region,
        time_point=time_point,
        full_plant_id=full_plant_id,
        full_id=full_id
    )

def prepare_training_data(config: Dict[str, Any]) -> None:
    """
    Prepare preprocessed images for machine learning training
    Organizes data by plant ID and creates 4-class classification structure
    
    Args:
        config: Configuration dictionary with ML parameters
    """
    # Setup paths
    current_dir = Path(__file__).parent
    src_dir = current_dir.parent.parent.parent
    data_dir = src_dir / "src" / "data"
    
    preprocessed_dir = data_dir / "output_images" / "preprocessed_images"
    ml_data_dir = data_dir / "ml_data"
    
    # Create organized ML data directory structure
    train_dir = ml_data_dir / "train"
    val_dir = ml_data_dir / "val"
    test_dir = ml_data_dir / "test"
    
    for dir_path in [ml_data_dir, train_dir, val_dir, test_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Get all preprocessed images
    image_files = list(preprocessed_dir.glob("*_removed.png"))
    
    if not image_files:
        raise FileNotFoundError(f"No preprocessed images found in {preprocessed_dir}")
    
    logger.info(f"Found {len(image_files)} preprocessed images")
    
    # Parse filenames and organize by plant
    image_info_list = []
    plant_groups = defaultdict(list)
    
    for img_file in image_files:
        try:
            img_info = parse_filename(img_file.name)
            image_info_list.append((img_file, img_info))
            plant_groups[img_info.full_plant_id].append((img_file, img_info))
        except ValueError as e:
            logger.warning(f"Skipping file {img_file.name}: {e}")
            continue
    
    logger.info(f"Successfully parsed {len(image_info_list)} images")
    logger.info(f"Found {len(plant_groups)} unique plants")
    
    # TODO: REPLACE THIS SECTION WITH IMAGE ANALYSIS
    # Currently using filename-based labels (a,b,c,d -> 0,1,2,3)
    # NEED TO UPDATE: Replace region_to_class mapping with actual image analysis
    
    # FUTURE INTEGRATION POINT:
    # 1. Load each image and analyze cell wall characteristics
    # 2. Use cell wall detection to identify cell boundaries
    # 3. Use color thresholding to detect lignin vs pectin levels
    # 4. Use segmentation to classify into 4 types:
    #    - thin_non_lignified (class 0): Thin cell walls, low lignin
    #    - thick_non_lignified (class 1): Thick cell walls, low lignin  
    #    - thin_lignified (class 2): Thin cell walls, high lignin
    #    - thick_lignified (class 3): Thick cell walls, high lignin
    
    labels = []
    valid_files = []
    
    for img_file, img_info in image_info_list:
        # CURRENT: Filename-based classification (TEMPORARY)
        region_to_class = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
        if img_info.region in region_to_class:
            labels.append(region_to_class[img_info.region])
            valid_files.append(img_file)
        
        # FUTURE: Replace above with image analysis
        # Example integration:
        # try:
        #     # Load image
        #     image = cv2.imread(str(img_file))
        #     
        #     # Cell wall detection
        #     cell_walls = detect_cell_walls(image)
        #     
        #     # Lignin/pectin analysis
        #     lignin_level = analyze_lignin(image)
        #     pectin_level = analyze_pectin(image)
        #     
        #     # Thickness measurement
        #     wall_thickness = measure_thickness(cell_walls)
        #     
        #     # Classify based on actual measurements
        #     if wall_thickness < threshold_thin and lignin_level < threshold_lignin:
        #         label = 0  # thin_non_lignified
        #     elif wall_thickness >= threshold_thin and lignin_level < threshold_lignin:
        #         label = 1  # thick_non_lignified
        #     elif wall_thickness < threshold_thin and lignin_level >= threshold_lignin:
        #         label = 2  # thin_lignified
        #     else:
        #         label = 3  # thick_lignified
        #     
        #     labels.append(label)
        #     valid_files.append(img_file)
        #     
        # except Exception as e:
        #     logger.warning(f"Failed to analyze {img_file.name}: {e}")
        #     continue
    
    # Split data ensuring we don't split plants across sets
    train_files, temp_files, train_labels, temp_labels = train_test_split(
        valid_files, labels, 
        test_size=(1 - config["ml_train_split"]), 
        random_state=42,
        stratify=labels
    )
    
    val_files, test_files, val_labels, test_labels = train_test_split(
        temp_files, temp_labels,
        test_size=config["ml_test_split"] / (config["ml_val_split"] + config["ml_test_split"]),
        random_state=42,
        stratify=temp_labels
    )
    
    # Copy files to appropriate directories with organized structure
    copy_files_to_split_organized(train_files, train_labels, train_dir, "train")
    copy_files_to_split_organized(val_files, val_labels, val_dir, "val")
    copy_files_to_split_organized(test_files, test_labels, test_dir, "test")
    
    # Create comprehensive metadata files
    create_comprehensive_metadata(train_files, train_labels, train_dir, "train")
    create_comprehensive_metadata(val_files, val_labels, val_dir, "val")
    create_comprehensive_metadata(test_files, test_labels, test_dir, "test")
    
    # Create overall dataset info with plant-level organization
    dataset_info = {
        "total_images": len(valid_files),
        "train_images": len(train_files),
        "val_images": len(val_files),
        "test_images": len(test_files),
        "total_plants": len(plant_groups),
        "classes": ["thin_non_lignified", "thick_non_lignified", "thin_lignified", "thick_lignified"],
        "class_distribution": {
            "train": np.bincount(train_labels).tolist(),
            "val": np.bincount(val_labels).tolist(),
            "test": np.bincount(test_labels).tolist()
        },
        "plant_organization": {
            plant_id: [img_info.full_id for _, img_info in group] 
            for plant_id, group in plant_groups.items()
        }
    }
    
    with open(ml_data_dir / "dataset_info.json", 'w') as f:
        json.dump(dataset_info, f, indent=2)
    
    logger.info(f"ML data preparation complete!")
    logger.info(f"Train: {len(train_files)} images")
    logger.info(f"Val: {len(val_files)} images")
    logger.info(f"Test: {len(test_files)} images")
    logger.info(f"Total plants: {len(plant_groups)}")

def copy_files_to_split_organized(files: List[Path], labels: List[int], 
                                 target_dir: Path, split_name: str) -> None:
    """Copy files to train/val/test directories with organized structure"""
    class_names = ["thin_non_lignified", "thick_non_lignified", "thin_lignified", "thick_lignified"]
    
    for img_file, label in zip(files, labels):
        # Parse filename to get plant info
        try:
            img_info = parse_filename(img_file.name)
            
            # Create organized directory structure: class/plant_id/
            class_name = class_names[label]
            class_dir = target_dir / class_name
            plant_dir = class_dir / img_info.full_plant_id
            plant_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file with descriptive name
            target_file = plant_dir / f"{img_info.full_id}_removed.png"
            shutil.copy2(img_file, target_file)
            
        except ValueError as e:
            logger.warning(f"Skipping file {img_file.name}: {e}")
            continue
    
    logger.info(f"Copied {len(files)} images to {split_name} directory")

def create_comprehensive_metadata(files: List[Path], labels: List[int], 
                                target_dir: Path, split_name: str) -> None:
    """Create comprehensive metadata file for the split"""
    class_names = ["thin_non_lignified", "thick_non_lignified", "thin_lignified", "thick_lignified"]
    metadata = []
    
    for img_file, label in zip(files, labels):
        try:
            img_info = parse_filename(img_file.name)
            
            # CURRENT: Basic metadata with filename-based classification
            metadata_entry = {
                "filename": img_file.name,
                "label": int(label),
                "class": class_names[label],
                "plant_id": img_info.full_plant_id,
                "region": img_info.region,
                "time_point": img_info.time_point,
                "year": img_info.year,
                "full_id": img_info.full_id,
                "organized_path": f"{class_names[label]}/{img_info.full_plant_id}/{img_info.full_id}_removed.png"
            }
            
            # TODO: ADD IMAGE ANALYSIS RESULTS TO METADATA
            # FUTURE INTEGRATION: Include actual image analysis measurements
            # Example additional fields to add:
            # metadata_entry.update({
            #     "cell_wall_thickness": wall_thickness_measurement,
            #     "lignin_level": lignin_concentration,
            #     "pectin_level": pectin_concentration,
            #     "cell_wall_count": number_of_detected_walls,
            #     "analysis_confidence": confidence_score,
            #     "analysis_method": "image_analysis_integrated",
            #     "analysis_timestamp": datetime.now().isoformat()
            # })
            
            metadata.append(metadata_entry)
            
        except ValueError as e:
            logger.warning(f"Skipping metadata for {img_file.name}: {e}")
            continue
    
    with open(target_dir / f"{split_name}_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create plant-level summary
    plant_summary = defaultdict(lambda: defaultdict(int))
    for item in metadata:
        plant_summary[item["plant_id"]][item["class"]] += 1
    
    with open(target_dir / f"{split_name}_plant_summary.json", 'w') as f:
        json.dump(dict(plant_summary), f, indent=2)

# TODO: INTEGRATION FUNCTIONS FOR IMAGE ANALYSIS
# ===============================================
# These functions will be implemented once image analysis modules are available

def integrate_cell_wall_detection(image_path: str) -> dict:
    """
    TODO: Integrate cell wall detection
    Expected input: Path to preprocessed image
    Expected output: Dictionary with cell wall detection results
    """
    # Placeholder for cell wall detection
    # Example return structure:
    # return {
    #     "cell_walls_detected": True,
    #     "wall_boundaries": [...],  # List of detected wall coordinates
    #     "detection_confidence": 0.95,
    #     "method": "thresholding"
    # }
    pass

def integrate_lignin_pectin_analysis(image_path: str) -> dict:
    """
    TODO: Integrate lignin/pectin color analysis
    Expected input: Path to preprocessed image
    Expected output: Dictionary with lignin/pectin measurements
    """
    # Placeholder for color thresholding analysis
    # Example return structure:
    # return {
    #     "lignin_level": 0.75,      # 0-1 scale
    #     "pectin_level": 0.25,      # 0-1 scale
    #     "lignin_threshold": 0.5,   # Threshold used
    #     "pectin_threshold": 0.3,   # Threshold used
    #     "analysis_method": "color_thresholding"
    # }
    pass

def integrate_thickness_measurement(image_path: str, cell_walls: dict) -> dict:
    """
    TODO: Integrate cell wall thickness measurement
    Expected input: Path to image + cell wall detection results
    Expected output: Dictionary with thickness measurements
    """
    # Placeholder for thickness measurement
    # Example return structure:
    # return {
    #     "average_thickness": 2.5,    # pixels or micrometers
    #     "thickness_distribution": [...],  # List of thickness measurements
    #     "thick_walls_count": 15,    # Number of thick walls
    #     "thin_walls_count": 8,      # Number of thin walls
    #     "thickness_threshold": 2.0,  # Threshold used for thick/thin
    #     "measurement_method": "segmentation"
    # }
    pass

def classify_cell_wall_type(lignin_analysis: dict, thickness_analysis: dict) -> int:
    """
    TODO: Implement classification logic based on image analysis results
    Expected input: Results from lignin and thickness analysis
    Expected output: Class label (0-3)
    """
    # Classification logic:
    # if thickness < threshold_thin and lignin < threshold_lignin:
    #     return 0  # thin_non_lignified
    # elif thickness >= threshold_thin and lignin < threshold_lignin:
    #     return 1  # thick_non_lignified
    # elif thickness < threshold_thin and lignin >= threshold_lignin:
    #     return 2  # thin_lignified
    # else:
    #     return 3  # thick_lignified
    pass

if __name__ == "__main__":
    # Test the function
    config = {
        "ml_train_split": 0.8,
        "ml_val_split": 0.1,
        "ml_test_split": 0.1
    }
    prepare_training_data(config)
