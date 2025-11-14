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
    """Resolve default paths and settings for YOLO training.
    
    Calculates repository-relative paths for weights, dataset configuration,
    and output directory based on the script's location. The script is located
    at: <repo>/src/main/core/yolo/yolo_train.py
    
    Returns:
        tuple: (weights_path, data_yaml_path, project_path, default_epochs)
            - weights_path: Path to pre-trained YOLO weights (yolo11n-seg.pt)
            - data_yaml_path: Path to dataset configuration (data.yaml)
            - project_path: Output directory for training runs
            - default_epochs: Default number of training epochs
    """
    # File is at: <repo>/src/main/core/yolo/yolo_train.py
    # Repo root = parents[4] (one extra level due to yolo/ subfolder)
    here = Path(__file__).resolve()
    repo = here.parents[4]
    
    # Default paths relative to repository root
    weights = repo / "yolo11n-seg.pt"  # Pre-trained YOLO11 nano segmentation model
    data = repo / "src" / "data" / "yolo_train" / "data.yaml"  # Dataset config
    project = repo / "src" / "data" / "yolo_results" / "runs" / "segment"  # Output dir
    
    # Default epochs for training (edit this value to change default)
    default_epochs = 150
    
    return weights, data, project, default_epochs


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for YOLO training.
    
    Sets up argument parser with defaults for training parameters, data augmentation,
    and output settings. All arguments can be overridden from the command line.
    
    Returns:
        Parsed arguments namespace
    """
    w, d, p, default_epochs = resolve_defaults()
    ap = argparse.ArgumentParser(description="Minimal YOLO11 segmentation training")
    
    # Core training parameters
    ap.add_argument("--weights", type=Path, default=w,
                    help="Path to pre-trained weights file (.pt)")
    ap.add_argument("--data", type=Path, default=d,
                    help="Path to dataset YAML configuration file")
    ap.add_argument("--epochs", type=int, default=default_epochs,
                    help="Number of training epochs")
    ap.add_argument("--imgsz", type=int, default=640,
                    help="Input image size (width and height in pixels)")
    ap.add_argument("--batch", type=int, default=4,
                    help="Batch size (default 4 for memory efficiency). If OOM errors occur, try reducing to 2.")
    ap.add_argument("--project", type=Path, default=p,
                    help="Project directory for saving training runs")
    ap.add_argument("--name", type=str, default=None,
                    help="Run name (auto-generated if not specified)")
    ap.add_argument("--save_period", type=int, default=5,
                    help="Save checkpoint every N epochs (default 5)")
    ap.add_argument("--quiet", action="store_true",
                    help="Reduce console output to epoch and % only")

    # Data augmentation options
    # These control how training images are transformed to increase dataset diversity
    ap.add_argument("--degrees", type=float, default=0.0,
                    help="Rotation augmentation range in degrees")
    ap.add_argument("--translate", type=float, default=0.1,
                    help="Translation augmentation (fraction of image size)")
    ap.add_argument("--scale", type=float, default=0.5,
                    help="Scale augmentation range (0.5 = ±50% scaling)")
    ap.add_argument("--shear", type=float, default=0.0,
                    help="Shear augmentation range in degrees")
    ap.add_argument("--perspective", type=float, default=0.0,
                    help="Perspective transformation augmentation")
    ap.add_argument("--flipud", type=float, default=0.0,
                    help="Probability of vertical flip (0.0-1.0)")
    ap.add_argument("--fliplr", type=float, default=0.5,
                    help="Probability of horizontal flip (0.0-1.0)")
    ap.add_argument("--hsv_h", type=float, default=0.015,
                    help="HSV hue augmentation factor")
    ap.add_argument("--hsv_s", type=float, default=0.7,
                    help="HSV saturation augmentation factor")
    ap.add_argument("--hsv_v", type=float, default=0.4,
                    help="HSV value (brightness) augmentation factor")
    ap.add_argument("--mosaic", type=float, default=1.0,
                    help="Mosaic augmentation probability (combines 4 images)")
    ap.add_argument("--mixup", type=float, default=0.0,
                    help="Mixup augmentation probability (blends 2 images)")
    ap.add_argument("--copy_paste", type=float, default=0.0,
                    help="Copy-paste augmentation probability")
    ap.add_argument("--erasing", type=float, default=0.4,
                    help="Random erasing augmentation probability")
    ap.add_argument("--auto_augment", type=str, default="randaugment",
                    help="Auto augmentation policy (e.g., 'randaugment', 'autoaugment')")
    ap.add_argument("--close_mosaic", type=int, default=10,
                    help="Disable mosaic augmentation in last N epochs")
    ap.add_argument("--device", type=str, default=None,
                    help="Device to use for training (e.g., '0', '1', 'cpu', 'cuda'). If not specified, auto-detects.")
    
    return ap.parse_args()


def auto_device() -> str:
    """Automatically detect and return the best device for training.
    
    Checks for CUDA-capable GPU availability and returns the appropriate
    device string. Falls back to CPU if no GPU is available or if PyTorch
    is not properly installed.
    
    Returns:
        Device string: GPU device ID (e.g., '0', '1') or 'cpu'
    """
    try:
        import torch  # type: ignore
        if torch.cuda.is_available():
            # GPU is available - use the current CUDA device
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
    """Main training function for YOLO segmentation model.
    
    Loads model, configures training parameters, sets up device (GPU/CPU),
    and runs the training loop. Saves checkpoints and training metrics.
    """
    args = parse_args()

    from ultralytics import YOLO
    from ultralytics.utils import LOGGER

    # Reduce Ultralytics logs when quiet mode is enabled
    # This provides cleaner console output with only essential progress info
    if args.quiet:
        LOGGER.setLevel(logging.WARNING)
        # Disable rich formatting to minimize fancy tables and progress bars
        os.environ["RICH_DISABLE"] = "1"

    # Load pre-trained YOLO model (yolo11n-seg.pt)
    model = YOLO(str(args.weights))
    
    # Generate run name if not specified (includes timestamp for uniqueness)
    run_name = args.name or f"alfalfa-minimal-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Determine device to use (GPU or CPU)
    device = args.device if args.device is not None else auto_device()
    
    # Validate device if CUDA/GPU is requested
    if device in ["cuda", "0", "1"] or (isinstance(device, str) and device.isdigit()):
        try:
            import torch  # type: ignore
            if not torch.cuda.is_available():
                raise RuntimeError(
                    "CUDA/GPU requested but not available. "
                    "Install PyTorch with CUDA support: "
                    "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
                )
            # Validate that requested GPU device exists
            if isinstance(device, str) and device.isdigit() and int(device) >= torch.cuda.device_count():
                raise RuntimeError(f"GPU device {device} requested but only {torch.cuda.device_count()} GPU(s) available")
        except ImportError:
            raise ImportError("PyTorch not installed. Install with: pip install torch torchvision torchaudio")
    
    print(f"Using device: {device}")

    # Custom progress callback for concise epoch progress
    # Prints only epoch number and percentage complete
    def _on_fit_epoch_end(trainer):
        """Callback function called at the end of each training epoch."""
        e = trainer.epoch + 1
        total = trainer.epochs
        pct = (e / total * 100.0) if total else 0.0
        # Print on same line, overwriting previous output
        print(f"\rEpoch {e}/{total} - {pct:.1f}%", end="", flush=True)
        if e == total:
            print()  # newline on finish

    # Register callback via API (some YOLO versions don't accept callbacks in train())
    try:
        model.add_callback("on_fit_epoch_end", _on_fit_epoch_end)
    except Exception:
        # If callbacks API not available, continue without custom progress
        # YOLO will use its default progress display
        pass

    # Start training with configured parameters
    results = model.train(
        # Dataset and model configuration
        data=str(args.data),  # Path to dataset YAML file
        epochs=args.epochs,  # Number of training epochs
        imgsz=args.imgsz,  # Input image size (640x640 default)
        batch=args.batch,  # Batch size
        device=device,  # GPU or CPU
        task="segment",  # Segmentation task (not detection)
        
        # Output configuration
        project=str(args.project),  # Output directory
        name=run_name,  # Run name (creates subdirectory)
        save_period=args.save_period,  # Checkpoint save frequency
        exist_ok=True,  # Allow overwriting existing runs
        verbose=not args.quiet,  # Verbose output
        plots=not args.quiet,  # Generate training plots
        
        # Memory optimization
        workers=2,  # Number of data loading workers (reduce to 1 if memory issues occur)
        
        # Data augmentation parameters
        # These control how training images are transformed during training
        degrees=args.degrees,  # Rotation
        translate=args.translate,  # Translation
        scale=args.scale,  # Scaling
        shear=args.shear,  # Shearing
        perspective=args.perspective,  # Perspective transform
        flipud=args.flipud,  # Vertical flip probability
        fliplr=args.fliplr,  # Horizontal flip probability
        hsv_h=args.hsv_h,  # HSV hue augmentation
        hsv_s=args.hsv_s,  # HSV saturation augmentation
        hsv_v=args.hsv_v,  # HSV value (brightness) augmentation
        mosaic=args.mosaic,  # Mosaic augmentation (combines 4 images)
        mixup=args.mixup,  # Mixup augmentation (blends 2 images)
        copy_paste=args.copy_paste,  # Copy-paste augmentation
        erasing=args.erasing,  # Random erasing
        auto_augment=args.auto_augment,  # Auto augmentation policy
        close_mosaic=args.close_mosaic,  # Disable mosaic in last N epochs
    )
    
    # Print final results directory location
    print("Training complete. Results dir:", (Path(str(args.project)) / run_name))


if __name__ == "__main__":
    main()
