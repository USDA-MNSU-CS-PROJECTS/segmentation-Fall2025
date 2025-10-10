# Alfalfa Segmentation Pipeline 🌱

## Overview

This project develops an image analysis pipeline to quantify **lignin** and **pectin** distribution in alfalfa stem cross-sections.  
The pipeline uses ~15,000 microscopy images (`.nd2` format) to perform preprocessing, segmentation, and classification of four distinct cell wall types:

1. **Thin-walled, non-lignified** - Thin cell walls with low lignin content
2. **Thick-walled, non-lignified** - Thick cell walls with low lignin content
3. **Thin-walled, lignified** - Thin cell walls with high lignin content
4. **Thick-walled, lignified** - Thick cell walls with high lignin content

**Current Status**: Filename-based organization complete ✅  
**Next Phase**: Integrating image analysis for real classification

Results will inform USDA research on alfalfa improvement and provide insights into how lignin and pectin dynamics change across fermentation time points (T0, T4, T8, T24, T48, T96).

---

## Features

### **Current Pipeline Features**

- ✅ **ND2 → TIFF Conversion** (batch processing)
- ✅ **Background Removal** (AI-powered preprocessing)
- ✅ **Filename Parsing** (plant ID, region, time point extraction)
- ✅ **Organized Data Structure** (by plant ID and class)
- ✅ **ML Data Preparation** (train/val/test splits)
- ✅ **Supercomputer Ready** (SLURM/PBS job scripts)

### **Upcoming Features** (Image Analysis Integration)

- 🔄 **Cell Wall Detection** and boundary identification
- 🔄 **Lignin/Pectin Analysis** and color thresholding
- 🔄 **Thickness Measurement** and segmentation
- 🔄 **Real Classification** (replacing filename-based labels)

---

## Repository Structure

```
alfalfa-segmentation/
├── README.md
├── SUPERCOMPUTER_GUIDE.md
├── requirements.txt             # Python dependencies
├── setup.sh                    # Setup script
├── test_pipeline.py            # Test script
├── config/
│   ├── pipeline_config.json    # Pipeline configuration
│   └── ml_config.json         # ML training configuration
├── scripts/
│   ├── slurm_job.sh           # SLURM job script
│   └── pbs_job.sh            # PBS job script
└── src/
    ├── data/
    │   ├── nd2_images/
    │   │   └── input_images/    # Place .nd2 files here
    │   ├── output_images/
    │   │   ├── jpg_images/          # Generated .jpg
    │   │   ├── tiff_images/         # Generated .tif/.tiff
    │   │   └── preprocessed_images/ # Background-removed .png outputs
    │   └── ml_data/                   # ML training datasets
    │       ├── train/                  # Training images (organized by class/plant)
    │       ├── val/                    # Validation images (organized by class/plant)
    │       ├── test/                   # Test images (organized by class/plant)
    │       └── dataset_info.json       # Dataset metadata and plant organization
    └── main/
        ├── core/
        │   ├── tiff_converter.py       # ND2 → 8-bit TIFF (batch)
        │   └── image_preprocessing.py   # Background removal on TIFF (batch)
        └── pipeline/
            ├── pipeline.py             # Main pipeline orchestrator
            ├── ml_data_prep.py         # ML data preparation
            ├── ml_training.py          # CNN training script
            ├── PIPELINE_SUMMARY.md     # Pipeline documentation
            └── SUPERCOMPUTER_GUIDE.md  # Supercomputer usage guide
```

---

## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/<your-org>/alfalfa-segmentation.git
cd alfalfa-segmentation
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Recommended Python version: **3.10+** (tested with 3.12)

---

## Local Usage (Your Computer)

### Quick Start

1. **Setup**: Run the setup script

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

**⚠️ WARNING:** Try not to push up or commit any .nd2 or .tiff images, this may break the repository. Instead, just run things locally and use the pipeline in any future work (pipeline
work in progress)

2. **Add Images**: Place your `.nd2` files into: `src/data/nd2_images/input_images`

3. **Run Individual Steps**:

   **Convert ND2 → TIFF:**

   ```bash
   python src/main/core/tiff_converter.py
   ```

   **Remove Backgrounds:**

   ```bash
   python src/main/core/image_preprocessing.py
   ```

   **Run Complete Pipeline:**

   ```bash
   python src/main/pipeline/pipeline.py
   ```

### Local Pipeline Options

- `--skip-tiff`: Skip ND2 to TIFF conversion
- `--skip-preprocessing`: Skip background removal
- `--skip-ml`: Skip ML data preparation
- `--max-images N`: Process only N images
- `--config FILE`: Use custom configuration file

---

## Supercomputer Usage (Large-Scale Processing)

**⚠️ For processing thousands of images on supercomputers, see the [Supercomputer Guide](src/main/pipeline/SUPERCOMPUTER_GUIDE.md)**

### Quick Supercomputer Start

1. **Upload your project** to the supercomputer
2. **Add ND2 files** to `src/data/nd2_images/input_images/`
3. **Submit job**:
   ```bash
   sbatch scripts/slurm_job.sh    # SLURM systems
   qsub scripts/pbs_job.sh        # PBS systems
   ```

### What Supercomputer Processing Includes

- **ND2 → TIFF Conversion** (batch processing)
- **Background Removal** (AI-powered preprocessing)
- **ML Data Preparation** (train/val/test splits)
- **CNN Training** (cell wall classification model)
- **Results & Visualizations** (training curves, metrics)

---

## Filename Structure & Classification

### **Filename Pattern**

`YYYY0XXX[abcd]_T[timepoint]_10xstitch_PG_removed.png`

**Example**: `20240780a_T0_10xstitch_PG_removed.png`

- `20240` = Year + space
- `780` = Plant ID (same plant = same 3-digit ID)
- `a,b,c,d` = 4 cross regions of the same plant
- `T0` = Time point (T0=before digestion, future: T4,T8,T24,T48,T96)

### **Current Classification** (TEMPORARY)

- `a` → `thin_non_lignified` (class 0)
- `b` → `thick_non_lignified` (class 1)
- `c` → `thin_lignified` (class 2)
- `d` → `thick_lignified` (class 3)

### **Future Classification** (WITH IMAGE ANALYSIS)

- **Thin walls + Low lignin** → `thin_non_lignified`
- **Thick walls + Low lignin** → `thick_non_lignified`
- **Thin walls + High lignin** → `thin_lignified`
- **Thick walls + High lignin** → `thick_lignified`

## Deliverables

---

## Team

- **Student Developer:** Evan Darling, Dade Willms, JaeJun Lee, Aaron Hansen

---

## Acknowledgements

This project is supported by the **USDA Agricultural Research Service**.  
Student contributions may be acknowledged in a future crop science journal publication.
