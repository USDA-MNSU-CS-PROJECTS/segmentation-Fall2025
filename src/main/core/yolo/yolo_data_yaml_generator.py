"""
Utility to generate a YOLO data.yaml for segmentation training.

This script reads classes from `classes.txt` in the dataset root and writes a
`data.yaml` that points to the images used for training/validation.

Behavior:
- If split folders exist at `dataset_root/splits/images/{train,val}`, those are used.
- Otherwise it falls back to using `dataset_root/images` for both train and val
  (you can still train, but it's recommended to create a proper split later).

Usage (PowerShell):
  python .\src\main\core\yolo\yolo_data_yaml_generator.py --dataset-root .\src\data\yolo_train
  # Optional custom output path:
  python .\src\main\core\yolo\yolo_data_yaml_generator.py --dataset-root .\src\data\yolo_train --out .\src\data\yolo_train\data.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List


def read_classes(classes_txt: Path) -> List[str]:
	if not classes_txt.exists():
		raise FileNotFoundError(f"classes.txt not found: {classes_txt}")
	names = [ln.strip() for ln in classes_txt.read_text(encoding="utf-8").splitlines() if ln.strip()]
	if not names:
		raise ValueError(f"No class names found in: {classes_txt}")
	return names


def detect_image_dirs(dataset_root: Path) -> tuple[Path, Path]:
	"""Return (train_images_dir, val_images_dir) based on available folders.

	Preference order:
	  1) dataset_root/splits/images/train and .../val
	  2) fallback to dataset_root/images for both train and val
	"""
	splits_train = dataset_root / "splits" / "images" / "train"
	splits_val = dataset_root / "splits" / "images" / "val"
	if splits_train.exists() and splits_val.exists():
		return splits_train, splits_val
	# Fallback
	images = dataset_root / "images"
	if not images.exists():
		raise FileNotFoundError(
			f"Images folder not found. Expected either '{splits_train.parent}' or '{images}'."
		)
	return images, images


def write_data_yaml(out_path: Path, dataset_root: Path, train_images: Path, val_images: Path, class_names: List[str]) -> None:
	# Build relative paths under dataset_root so YAML is portable
	lines: List[str] = []
	lines.append(f"path: {dataset_root.as_posix()}")
	lines.append(f"train: {train_images.relative_to(dataset_root).as_posix()}")
	lines.append(f"val: {val_images.relative_to(dataset_root).as_posix()}")
	lines.append("names:")
	for i, name in enumerate(class_names):
		lines.append(f"  {i}: {name}")
	out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def default_dataset_root() -> Path:
	# File is at: <repo>/src/main/core/yolo/yolo_data_yaml_generator.py
	# Repo root = parents[4] (one extra level due to yolo/ subfolder)
	here = Path(__file__).resolve()
	repo_root = here.parents[4]
	return repo_root / "src" / "data" / "yolo_train"


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Generate data.yaml for YOLO segmentation")
	p.add_argument("--dataset-root", type=Path, default=default_dataset_root(),
				   help="Dataset root containing images/, labels/, classes.txt (default: src/data/yolo_train)")
	p.add_argument("--out", type=Path, default=None,
				   help="Output path for data.yaml (default: <dataset-root>/data.yaml)")
	return p.parse_args()


def main() -> None:
	args = parse_args()
	dataset_root: Path = args.dataset_root
	out_path: Path = args.out or (dataset_root / "data.yaml")

	classes_txt = dataset_root / "classes.txt"
	class_names = read_classes(classes_txt)
	train_images, val_images = detect_image_dirs(dataset_root)

	out_path.parent.mkdir(parents=True, exist_ok=True)
	write_data_yaml(out_path, dataset_root, train_images, val_images, class_names)
	print(f"Wrote data.yaml -> {out_path}")


if __name__ == "__main__":
	main()

