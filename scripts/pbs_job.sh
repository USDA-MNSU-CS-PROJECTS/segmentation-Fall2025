#!/bin/bash
#PBS -N alfalfa-pipeline
#PBS -o alfalfa_pipeline_${PBS_JOBID}.out
#PBS -e alfalfa_pipeline_${PBS_JOBID}.err
#PBS -l walltime=04:00:00
#PBS -l nodes=1:ppn=8
#PBS -l mem=32gb
#PBS -q gpu

# Alfalfa Segmentation Pipeline - PBS Job Script
# This script runs the complete image processing pipeline on a supercomputer

echo "Starting Alfalfa Segmentation Pipeline Job"
echo "Job ID: $PBS_JOBID"
echo "Node: $PBS_O_HOST"
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
