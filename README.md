# Alfalfa Segmentation Pipeline 🌱

## Overview

This project develops an image analysis pipeline to quantify **lignin** and **pectin** distribution in alfalfa stem cross-sections.  
The pipeline uses ~15,000 microscopy images (`.nd2` format) to perform preprocessing, segmentation, and classification of four distinct cell wall types:

1. Thin-walled, non-lignified
2. Thick-walled, non-lignified
3. Thin-walled, lignified
4. Thick-walled, lignified

Results will inform USDA research on alfalfa improvement and provide insights into how lignin and pectin dynamics change across fermentation time points (0–96 hours).

---

## Features

---

## Repository Structure

```
alfalfa-segmentation/
├── README.md
├── requirements.txt             # Python dependencies
└── src/
    ├── data/
    │   ├── nd2_images/
    │   │   └── input_images/    # Place .nd2 files here
    │   └── main_images/
    │       └── output_images/
    │           ├── jpg_images/          # Generated .jpg
    │           ├── tiff_images/         # Generated .tif/.tiff
    │           └── preprocessed_images/ # Background-removed .png outputs
    └── main/
        └── core/
            ├── jpg_converter.py         # ND2 → JPG (batch)
            ├── tiff_converter.py        # ND2 → 8-bit TIFF (batch)
            └── image_preprocessing.py   # Background removal on TIFF (batch)
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

## Usage

1. Add input images

   **⚠️ WARNING:** Try not to push up or commit any .nd2 or .tiff images, this may break the repository. Instead, just run things locally and use the pipeline in any future work (pipeline work in progress)

- Place your `.nd2` files into: `src/data/nd2_images/input_images`

2. Convert ND2 → TIFF (batch)

```bash
python src/main/core/tiff_converter.py
```

- Outputs `.tiff` files to: `src/data/main_images/output_images/tiff_images`

3. Optional: Convert ND2 → JPG (batch)

```bash
python src/main/core/jpg_converter.py
```

- Outputs `.jpg` files to: `src/data/main_images/output_images/jpg_images`

4. Background removal on all TIFFs

```bash
python src/main/core/image_preprocessing.py
```

- Reads all `.tif/.tiff` from `src/data/main_images/output_images/tiff_images`
- Writes `<basename>_removed.png` to `src/data/main_images/output_images/preprocessed_images`

---

## Deliverables

---

## Team

- **Student Developer:** Evan Darling, Dade Willms, JaeJun Lee, Aaron Hansen

---

## Acknowledgements

This project is supported by the **USDA Agricultural Research Service**.  
Student contributions may be acknowledged in a future crop science journal publication.
