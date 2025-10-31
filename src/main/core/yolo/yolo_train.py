"""
Minimal YOLO11 segmentation training script.

Usage (PowerShell):
  python .\\src\\main\\core\\yolo\\yolo_train.py --epochs 100 --imgsz 640

Defaults:
  - weights: <repo>/yolo11n-seg.pt (exists in repo root)
  - data:    <repo>/src/data/yolo_train/data.yaml
  - project: <repo>/src/data/yolo_results/runs/segment
This will save weights under src/data/yolo_results/runs/segment/<run-name>/weights/
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import argparse
import logging
import os


def resolve_defaults() -> tuple[Path, Path, Path, int]:
    # File is at: <repo>/src/main/core/yolo/yolo_train.py
    # Repo root = parents[4] (one extra level due to yolo/ subfolder)
    here = Path(__file__).resolve()
    repo = here.parents[4]
    weights = repo / "yolo11n-seg.pt"
    data = repo / "src" / "data" / "yolo_train" / "data.yaml"
    project = repo / "src" / "data" / "yolo_results" / "runs" / "segment"
    # Default epochs for training (edit this value to change default)
    default_epochs = 150
    return weights, data, project, default_epochs


def parse_args() -> argparse.Namespace:
    w, d, p, default_epochs = resolve_defaults()
    ap = argparse.ArgumentParser(description="Minimal YOLO11 segmentation training")
    ap.add_argument("--weights", type=Path, default=w)
    ap.add_argument("--data", type=Path, default=d)
    ap.add_argument("--epochs", type=int, default=default_epochs)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=4, help="Batch size (default 4 for memory efficiency)") # If this breaks, try reducing default to 2 (-1 was original)
    ap.add_argument("--project", type=Path, default=p)
    ap.add_argument("--name", type=str, default=None)
    ap.add_argument("--save_period", type=int, default=5, help="Save checkpoint every N epochs (default 5)")
    ap.add_argument("--quiet", action="store_true", help="Reduce console output to epoch and % only")

    # Augmentation options (common knobs)
    ap.add_argument("--degrees", type=float, default=0.0)
    ap.add_argument("--translate", type=float, default=0.1)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--shear", type=float, default=0.0)
    ap.add_argument("--perspective", type=float, default=0.0)
    ap.add_argument("--flipud", type=float, default=0.0)
    ap.add_argument("--fliplr", type=float, default=0.5)
    ap.add_argument("--hsv_h", type=float, default=0.015)
    ap.add_argument("--hsv_s", type=float, default=0.7)
    ap.add_argument("--hsv_v", type=float, default=0.4)
    ap.add_argument("--mosaic", type=float, default=1.0)
    ap.add_argument("--mixup", type=float, default=0.0)
    ap.add_argument("--copy_paste", type=float, default=0.0)
    ap.add_argument("--erasing", type=float, default=0.4)
    ap.add_argument("--auto_augment", type=str, default="randaugment")
    ap.add_argument("--close_mosaic", type=int, default=10)
    ap.add_argument("--device", type=str, default=None, help="Device to use for training (e.g., '0', '1', 'cpu', 'cuda'). If not specified, auto-detects.")
    return ap.parse_args()


def auto_device() -> str:
    """Automatically detect and return the best device for training"""
    try:
        import torch  # type: ignore
        if torch.cuda.is_available():
            device_id = torch.cuda.current_device()
            device_name = torch.cuda.get_device_name(device_id)
            print(f"GPU detected: {device_name} (CUDA device {device_id})")
            return str(device_id)
        else:
            print("No GPU detected, using CPU")
            return "cpu"
    except ImportError:
        print("PyTorch not found, using CPU")
        return "cpu"
    except Exception as e:
        print(f"Error detecting device: {e}, using CPU")
        return "cpu"


def main() -> None:
    args = parse_args()

    from ultralytics import YOLO
    from ultralytics.utils import LOGGER

    # Reduce Ultralytics logs when quiet, and we print our own concise progress
    if args.quiet:
        LOGGER.setLevel(logging.WARNING)
        # Disable rich to minimize fancy tables
        os.environ["RICH_DISABLE"] = "1"

    model = YOLO(str(args.weights))
    run_name = args.name or f"alfalfa-minimal-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Determine device to use
    device = args.device if args.device is not None else auto_device()
    
    # Validate device if CUDA is requested
    if device in ["cuda", "0", "1"] or (isinstance(device, str) and device.isdigit()):
        try:
            import torch  # type: ignore
            if not torch.cuda.is_available():
                raise RuntimeError(
                    "CUDA/GPU requested but not available. "
                    "Install PyTorch with CUDA support: "
                    "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
                )
            if isinstance(device, str) and device.isdigit() and int(device) >= torch.cuda.device_count():
                raise RuntimeError(f"GPU device {device} requested but only {torch.cuda.device_count()} GPU(s) available")
        except ImportError:
            raise ImportError("PyTorch not installed. Install with: pip install torch torchvision torchaudio")
    
    print(f"Using device: {device}")

    # Simple progress callback: print only epoch and %
    def _on_fit_epoch_end(trainer):
        e = trainer.epoch + 1
        total = trainer.epochs
        pct = (e / total * 100.0) if total else 0.0
        print(f"\rEpoch {e}/{total} - {pct:.1f}%", end="", flush=True)
        if e == total:
            print()  # newline on finish

    # Register callback via API (some versions don't accept callbacks in train())
    try:
        model.add_callback("on_fit_epoch_end", _on_fit_epoch_end)
    except Exception:
        # If callbacks API not available, continue without custom progress
        pass

    results = model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        project=str(args.project),
        name=run_name,
        save_period=args.save_period,
        task="segment",
        verbose=not args.quiet,
        exist_ok=True,
        plots=not args.quiet,
        # Memory optimization
        workers=2,  # Reduce number of data loading workers // if this breaks, try reducing to 1
        # Augmentations
        degrees=args.degrees,
        translate=args.translate,
        scale=args.scale,
        shear=args.shear,
        perspective=args.perspective,
        flipud=args.flipud,
        fliplr=args.fliplr,
        hsv_h=args.hsv_h,
        hsv_s=args.hsv_s,
        hsv_v=args.hsv_v,
        mosaic=args.mosaic,
        mixup=args.mixup,
        copy_paste=args.copy_paste,
        erasing=args.erasing,
        auto_augment=args.auto_augment,
        close_mosaic=args.close_mosaic,
    )
    print("Training complete. Results dir:", (Path(str(args.project)) / run_name))


if __name__ == "__main__":
    main()
