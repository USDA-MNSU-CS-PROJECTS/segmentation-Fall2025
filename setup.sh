#!/bin/bash
# Setup script for Alfalfa Segmentation Pipeline
# This script prepares the environment for running on a supercomputer

echo "Setting up Alfalfa Segmentation Pipeline..."

# Create necessary directories
echo "Creating directory structure..."
mkdir -p src/data/nd2_images/input_images
mkdir -p src/data/output_images/{tiff_images,jpg_images,preprocessed_images}
mkdir -p src/data/ml_data/{train,val,test}
mkdir -p src/main/pipeline
mkdir -p models
mkdir -p config
mkdir -p scripts

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/slurm_job.sh
chmod +x scripts/pbs_job.sh

# Create a simple test script
echo "Creating test script..."
cat > test_pipeline.py << 'EOF'
#!/usr/bin/env python3
"""Simple test script to verify pipeline setup"""

import os
import sys
from pathlib import Path

def test_setup():
    """Test if the pipeline is properly set up"""
    print("Testing Alfalfa Segmentation Pipeline Setup...")
    
    # Check if required directories exist
    required_dirs = [
        "src/data/nd2_images/input_images",
        "src/data/output_images",
        "config",
        "scripts"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing directory: {dir_path}")
            return False
        else:
            print(f"✅ Directory exists: {dir_path}")
    
    # Check if required files exist
    required_files = [
        "src/main/core/pipeline.py",
        "src/main/core/tiff_converter.py", 
        "src/main/core/image_preprocessing.py",
        "src/main/core/ml_training.py",
        "config/pipeline_config.json",
        "config/ml_config.json",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing file: {file_path}")
            return False
        else:
            print(f"✅ File exists: {file_path}")
    
    print("\n🎉 Setup test passed! Pipeline is ready to use.")
    print("\nNext steps:")
    print("1. Add your ND2 files to src/data/nd2_images/input_images/")
    print("2. Submit a job: sbatch scripts/slurm_job.sh (or qsub scripts/pbs_job.sh)")
    print("3. Monitor your job and check the output logs")
    
    return True

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)
EOF

chmod +x test_pipeline.py

echo "✅ Setup complete!"
echo ""
echo "To test your setup, run:"
echo "python test_pipeline.py"
echo ""
echo "To start processing, add ND2 files to src/data/nd2_images/input_images/ and submit a job!"
