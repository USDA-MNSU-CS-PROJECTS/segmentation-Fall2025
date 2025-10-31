#!/bin/bash
#SBATCH --job-name=alfalfa-pipeline
#SBATCH --output=alfalfa_pipeline_%j.out
#SBATCH --error=alfalfa_pipeline_%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1

# Alfalfa Segmentation Pipeline - SLURM Job Script
# This script runs the complete image processing pipeline on a supercomputer

echo "Starting Alfalfa Segmentation Pipeline Job"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to repository root directory (critical for relative paths)
cd "$REPO_ROOT" || exit 1
echo "Working directory: $(pwd)"

# Load modules (adjust based on your supercomputer)
# Comment out or modify based on your system's available modules
module load python/3.10 2>/dev/null || echo "Warning: python/3.10 module not found"
module load cuda/11.8 2>/dev/null || echo "Warning: cuda/11.8 module not found"
module load gcc/9.3.0 2>/dev/null || echo "Warning: gcc/9.3.0 module not found"

# Create virtual environment (if it doesn't exist)
if [ ! -d "alfalfa_env" ]; then
    echo "Setting up Python environment..."
    python -m venv alfalfa_env
fi
source alfalfa_env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Installing basic dependencies..."
    pip install numpy opencv-python pillow ultralytics pandas
fi

# Additional ML dependencies (if needed)
# Uncomment if PyTorch is not in requirements.txt
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# pip install scikit-learn matplotlib seaborn

# Set environment variable to indicate we're running in SLURM
export SLURM_JOB_RUNNING=1

# Run the pipeline
echo "Starting pipeline execution..."
python src/main/pipeline/pipeline.py --config config/pipeline_config.json

# Check if pipeline completed successfully
if [ $? -eq 0 ]; then
    echo "Pipeline completed successfully!"
else
    echo "Pipeline failed with exit code $?"
    exit 1
fi

echo "Job completed at: $(date)"
echo "Total runtime: $SECONDS seconds"
