"""
Utility functions for Gradio UI backend

Helper functions for file handling, naming, and common operations.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import numpy as np


def safe_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    safe = re.sub(r'[^\w\s\-\.]', '', filename)
    safe = re.sub(r'[\s]+', '_', safe)
    return safe


def get_timestamp() -> str:
    """
    Get current timestamp for file naming
    
    Returns:
        Timestamp string in format: YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_base_name(file_path: str) -> str:
    """
    Get base name from file path (without extension)
    
    Args:
        file_path: Path to file
        
    Returns:
        Base name without extension
    """
    return Path(file_path).stem


def create_unique_filename(directory: Path, base_name: str, extension: str) -> Path:
    """
    Create unique filename by appending number if file exists
    
    Args:
        directory: Directory for file
        base_name: Base filename without extension
        extension: File extension (with or without dot)
        
    Returns:
        Unique file path
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # Try original name
    file_path = directory / f"{base_name}{extension}"
    if not file_path.exists():
        return file_path
    
    # Append numbers until unique
    counter = 1
    while True:
        file_path = directory / f"{base_name}_{counter}{extension}"
        if not file_path.exists():
            return file_path
        counter += 1


def get_available_images(directory: Path, pattern: str = "*.jpg") -> List[str]:
    """
    Get list of available images in directory
    
    Args:
        directory: Directory to search
        pattern: Glob pattern for files
        
    Returns:
        List of file paths as strings
    """
    if not directory.exists():
        return []
    
    files = list(directory.glob(pattern))
    return [str(f) for f in sorted(files)]


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, create if needed
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_temp_directory(directory: Path, keep_recent: int = 10):
    """
    Clean up old files in temp directory, keeping most recent
    
    Args:
        directory: Directory to clean
        keep_recent: Number of recent files to keep
    """
    if not directory.exists():
        return
    
    # Get all files with timestamps
    files = [(f, f.stat().st_mtime) for f in directory.glob("*.*")]
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Delete old files
    for file_path, _ in files[keep_recent:]:
        try:
            file_path.unlink()
        except:
            pass


def is_image_file(file_path: str) -> bool:
    """
    Check if file is a valid image file
    
    Args:
        file_path: Path to file
        
    Returns:
        True if image file
    """
    valid_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.nd2'}
    return Path(file_path).suffix.lower() in valid_extensions


def get_image_dimensions(image_array: np.ndarray) -> tuple:
    """
    Get image dimensions from numpy array
    
    Args:
        image_array: Image as numpy array
        
    Returns:
        (height, width, channels)
    """
    if len(image_array.shape) == 2:
        return (*image_array.shape, 1)
    return image_array.shape
