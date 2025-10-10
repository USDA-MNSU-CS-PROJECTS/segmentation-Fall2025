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

# Load modules (adjust based on your supercomputer)
module load python/3.10
module load cuda/11.8
module load gcc/9.3.0

# Create virtual environment
echo "Setting up Python environment..."
python -m venv alfalfa_env
source alfalfa_env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Additional ML dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install scikit-learn matplotlib seaborn

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
