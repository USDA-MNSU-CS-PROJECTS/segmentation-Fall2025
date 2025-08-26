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
- 📂 Load and preprocess `.nd2` microscopy images  
- 🖼️ Segment alfalfa cell walls using classical and/or deep learning methods  
- 📊 Quantify stain intensity for lignin (phloroglucinol) and pectin (ruthenium red)  
- 🧪 Compare cell wall properties across alfalfa lines and fermentation stages  
- ✅ Validation methods for quality assurance (manual SME checks + metrics)  
- 📑 Reproducible pipeline with exportable datasets  

---

## Repository Structure
```
alfalfa-segmentation-pipeline/
│── data/               # Input .nd2 files or converted images
│── notebooks/          # Jupyter notebooks for exploration & testing
│── src/                # Source code (preprocessing, segmentation, analysis)
│── outputs/            # Processed images, results, visualizations
│── docs/               # Documentation & protocols
│── README.md           # Project description (this file)
```

---

## Installation
Clone the repo and install dependencies:

```bash
git clone https://github.com/your-username/alfalfa-segmentation-pipeline.git
cd alfalfa-segmentation-pipeline
pip install -r requirements.txt
```

Recommended Python version: **3.10+**

---

## Usage
Example workflow:

```bash
# Convert raw .nd2 to .tif
python src/convert_nd2.py --input data/raw --output data/converted

# Run preprocessing pipeline
python src/preprocess.py --input data/converted --output data/preprocessed

# Run segmentation on sample dataset
python src/segment.py --input data/preprocessed --output outputs/results

# Generate summary statistics
python src/analyze.py --input outputs/results --output outputs/stats
```

---

## Deliverables
- ✅ Preprocessing & segmentation scripts  
- ✅ Validation methods with SME collaboration  
- ✅ Final datasets (ready for statistical analysis)  
- ✅ Written protocol for SMEs  
- ✅ Project presentation + documentation  

---

## Team
- **Student Developer:** [Your Name]  
- **Research Sponsor:** Dr. D. Jo Heuschele (USDA Agricultural Research Service)  
- **Subject Matter Experts (SMEs):** [To be added]  

---

## Acknowledgements
This project is supported by the **USDA Agricultural Research Service**.  
Student contributions may be acknowledged in a future crop science journal publication.  

---

## License
MIT License (or other, depending on project requirements)
