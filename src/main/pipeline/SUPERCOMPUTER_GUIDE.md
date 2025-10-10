# Supercomputer Usage Guide for Alfalfa Segmentation Pipeline 🖥️

This guide will help you run the alfalfa segmentation pipeline on a supercomputer for processing large-scale microscopy images and training machine learning models.

## Overview

The pipeline processes ND2 microscopy images through three main stages:

1. **ND2 → TIFF Conversion**: Convert microscopy files to standard TIFF format
2. **Image Preprocessing**: Remove backgrounds and prepare images for ML
3. **ML Training**: Train CNN models to classify cell wall types

## Prerequisites

### 1. Supercomputer Access

- Access to a SLURM or PBS-based supercomputer
- Basic familiarity with command line and job submission
- Sufficient storage quota for your images and outputs

### 2. Data Preparation

- Upload your ND2 files to: `src/data/nd2_images/input_images/`
- Ensure you have enough storage space (ND2 files can be large)

## Quick Start

### Step 1: Upload Your Code

```bash
# Upload your entire project directory to the supercomputer
scp -r alfalfa-segmentation/ username@supercomputer.edu:/path/to/your/workspace/
```

### Step 2: Submit a Job

```bash
# For SLURM systems
sbatch scripts/slurm_job.sh

# For PBS systems
qsub scripts/pbs_job.sh
```

### Step 3: Monitor Your Job

```bash
# Check job status (SLURM)
squeue -u $USER

# Check job status (PBS)
qstat -u $USER

# View output logs
tail -f alfalfa_pipeline_<JOB_ID>.out
```

## Detailed Usage

### Job Scripts

#### SLURM Job Script (`scripts/slurm_job.sh`)

- **Resources**: 1 node, 8 CPUs, 32GB RAM, 1 GPU
- **Runtime**: 4 hours maximum
- **Partition**: GPU partition (adjust as needed)

#### PBS Job Script (`scripts/pbs_job.sh`)

- **Resources**: 1 node, 8 processors, 32GB RAM
- **Runtime**: 4 hours maximum
- **Queue**: GPU queue (adjust as needed)

### Configuration Files

#### Pipeline Configuration (`config/pipeline_config.json`)

```json
{
  "run_tiff_conversion": true,
  "run_preprocessing": true,
  "run_ml_prep": true,
  "max_images": null,
  "expansions_pixels": 25,
  "crop_margin": 100,
  "ml_train_split": 0.8,
  "ml_val_split": 0.1,
  "ml_test_split": 0.1
}
```

#### ML Configuration (`config/ml_config.json`)

```json
{
  "epochs": 20,
  "batch_size": 16,
  "learning_rate": 0.001,
  "num_classes": 4,
  "num_workers": 4
}
```

### Running Individual Components

#### 1. Full Pipeline

```bash
python src/main/pipeline/pipeline.py --config config/pipeline_config.json
```

#### 2. ND2 to TIFF Conversion Only

```bash
python src/main/core/pipeline.py --skip-preprocessing --skip-ml
```

#### 3. Preprocessing Only

```bash
python src/main/core/pipeline.py --skip-tiff --skip-ml
```

#### 4. ML Training Only

```bash
python src/main/pipeline/ml_training.py --config config/ml_config.json
```

## Output Structure

After running the pipeline, you'll have:

```
src/data/
├── nd2_images/input_images/          # Your input ND2 files
├── output_images/
│   ├── tiff_images/                  # Converted TIFF files
│   ├── jpg_images/                   # Optional JPG conversions
│   └── preprocessed_images/          # Background-removed images
├── ml_training_data/                 # ML training data
│   ├── train/                        # Training images
│   ├── val/                          # Validation images
│   ├── test/                         # Test images
│   └── dataset_info.json            # Dataset metadata
└── models/                           # Trained models
    ├── best_model.pth               # Best performing model
    ├── final_model.pth              # Final epoch model
    ├── training_history.json        # Training metrics
    └── training_curves.png          # Training plots
```

## Troubleshooting

### Common Issues

#### 1. Module Loading Errors

```bash
# Check available modules
module avail python
module avail cuda

# Load correct versions
module load python/3.10
module load cuda/11.8
```

#### 2. Memory Issues

- Reduce `batch_size` in ML config
- Process fewer images at once by setting `max_images`
- Request more memory in job script

#### 3. GPU Issues

- Check GPU availability: `nvidia-smi`
- Ensure CUDA modules are loaded
- Verify PyTorch CUDA installation

#### 4. File Path Issues

- Ensure all paths are correct
- Check file permissions
- Verify input files exist

### Performance Optimization

#### 1. Resource Allocation

- **Small datasets** (< 100 images): 4 CPUs, 16GB RAM
- **Medium datasets** (100-1000 images): 8 CPUs, 32GB RAM
- **Large datasets** (> 1000 images): 16 CPUs, 64GB RAM, 2 GPUs

#### 2. Parallel Processing

- Increase `num_workers` for data loading
- Use multiple GPUs for large models
- Process images in batches

#### 3. Storage Optimization

- Use compression for TIFF files
- Clean up intermediate files
- Archive old results

## Advanced Usage

### Custom Job Scripts

Create custom job scripts for specific tasks:

```bash
#!/bin/bash
#SBATCH --job-name=custom-task
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

# Your custom commands here
python src/main/core/ml_training.py --epochs 50 --batch-size 32
```

### Batch Processing

Process multiple datasets:

```bash
for dataset in dataset1 dataset2 dataset3; do
    cp -r src/data/nd2_images/input_images_$dataset src/data/nd2_images/input_images/
    sbatch scripts/slurm_job.sh
    # Wait for completion before next dataset
done
```

### Monitoring and Logging

- Check job logs regularly
- Monitor resource usage
- Set up email notifications for job completion
- Use `sacct` (SLURM) or `qstat -f` (PBS) for detailed job info

## Best Practices

1. **Test Locally First**: Run small tests on your local machine
2. **Start Small**: Begin with a subset of images
3. **Monitor Resources**: Watch CPU, memory, and GPU usage
4. **Save Checkpoints**: Models are saved automatically
5. **Clean Up**: Remove temporary files to save storage
6. **Document Results**: Keep track of experiments and results

## Support

For issues specific to your supercomputer:

- Check your institution's HPC documentation
- Contact your HPC support team
- Review system-specific module documentation

For pipeline issues:

- Check the logs in `alfalfa_pipeline_<JOB_ID>.out`
- Verify all dependencies are installed
- Ensure input data format is correct

## Next Steps

After successful pipeline execution:

1. **Evaluate Results**: Check model performance metrics
2. **Visualize Data**: Review training curves and confusion matrices
3. **Iterate**: Adjust hyperparameters and retrain
4. **Scale Up**: Process larger datasets
5. **Deploy**: Use trained models for inference

Happy computing! 🚀
