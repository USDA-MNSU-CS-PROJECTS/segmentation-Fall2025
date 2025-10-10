#!/usr/bin/env python3
"""
Alfalfa Cell Wall Classification - Machine Learning Training Script

This script trains a CNN model to classify alfalfa stem cross-sections into 4 categories:
- thick_lignified: Thick cell walls with lignin
- thick_non_lignified: Thick cell walls without lignin  
- thin_lignified: Thin cell walls with lignin
- thin_non_lignified: Thin cell walls without lignin

Key Features:
- Custom CNN architecture with 4 convolutional blocks + MLP classifier
- Data augmentation (rotation, flipping, color jitter) for training
- Automatic model checkpointing (saves best validation accuracy)
- Training history tracking and visualization
- Configurable via command line args and JSON config file

Usage:
    python ml_training.py --config config/ml_config.json --epochs 50 --batch-size 32

Prerequisites:
- Run the main pipeline first to prepare training data in src/data/ml_data/
- Training data should be organized in train/val splits with metadata JSON files
- Data is organized in semantic folders: thick_lignified/, thick_non_lignified/, thin_lignified/, thin_non_lignified/

Outputs:
- src/data/models/best_model.pth: Best model based on validation accuracy
- src/data/models/final_model.pth: Final model after all epochs
- src/data/models/training_history.json: Training metrics and history
- src/data/models/training_curves.png: Loss and accuracy plots

Note: This is a standalone training script that runs independently of the main pipeline.
Run the main pipeline first to prepare data, then run this script to train the model.
"""

import os
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlfalfaDataset(Dataset):
    """Custom dataset for alfalfa images"""
    
    def __init__(self, data_dir: Path, split: str, transform=None):
        self.data_dir = data_dir
        self.split = split
        self.transform = transform
        
        # Load metadata
        metadata_file = data_dir / f"{split}_metadata.json"
        with open(metadata_file, 'r') as f:
            self.metadata = json.load(f)
        
        logger.info(f"Loaded {len(self.metadata)} images for {split} split")
    
    def __len__(self):
        return len(self.metadata)
    
    def __getitem__(self, idx):
        item = self.metadata[idx]
        
        # Load image using the organized path structure
        if 'organized_path' in item:
            # Use the organized path if available (new structure)
            img_path = self.data_dir / item['organized_path']
        else:
            # Fallback to old class-based structure
            img_path = self.data_dir / f"class_{item['label']}" / item['filename']
        
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, item['label']

class SimpleCNN(nn.Module):
    """Simple CNN for alfalfa cell wall classification"""
    
    def __init__(self, num_classes: int = 4):
        super(SimpleCNN, self).__init__()
        
        self.features = nn.Sequential(
            # First convolutional block
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Second convolutional block
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Third convolutional block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Fourth convolutional block
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

class AlfalfaTrainer:
    """Trainer class for alfalfa classification model"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Setup paths
        self.current_dir = Path(__file__).parent
        self.src_dir = self.current_dir.parent.parent.parent
        self.data_dir = self.src_dir / "src" / "data" / "ml_data"
        self.model_dir = self.src_dir / "src" / "data" / "models"
        self.model_dir.mkdir(exist_ok=True)
        
        # Data transforms
        self.train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Load datasets
        self.train_dataset = AlfalfaDataset(self.data_dir / "train", "train", self.train_transform)
        self.val_dataset = AlfalfaDataset(self.data_dir / "val", "val", self.val_transform)
        
        # Create data loaders
        self.train_loader = DataLoader(
            self.train_dataset, 
            batch_size=config["batch_size"], 
            shuffle=True, 
            num_workers=config["num_workers"]
        )
        self.val_loader = DataLoader(
            self.val_dataset, 
            batch_size=config["batch_size"], 
            shuffle=False, 
            num_workers=config["num_workers"]
        )
        
        # Initialize model
        self.model = SimpleCNN(num_classes=config["num_classes"]).to(self.device)
        
        # Loss and optimizer
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=config["learning_rate"])
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=10, gamma=0.1)
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
    
    def train_epoch(self) -> Tuple[float, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
            
            if batch_idx % 10 == 0:
                logger.info(f'Batch {batch_idx}/{len(self.train_loader)}, Loss: {loss.item():.4f}')
        
        avg_loss = total_loss / len(self.train_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    def validate(self) -> Tuple[float, float]:
        """Validate the model"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in self.val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = self.criterion(output, target)
                
                total_loss += loss.item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += target.size(0)
        
        avg_loss = total_loss / len(self.val_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    def train(self):
        """Train the model"""
        logger.info("Starting training...")
        
        best_val_acc = 0.0
        
        for epoch in range(self.config["epochs"]):
            logger.info(f"Epoch {epoch+1}/{self.config['epochs']}")
            
            # Train
            train_loss, train_acc = self.train_epoch()
            
            # Validate
            val_loss, val_acc = self.validate()
            
            # Update learning rate
            self.scheduler.step()
            
            # Store history
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(self.model.state_dict(), self.model_dir / "best_model.pth")
                logger.info(f"New best model saved with validation accuracy: {val_acc:.2f}%")
        
        # Save final model and training history
        torch.save(self.model.state_dict(), self.model_dir / "final_model.pth")
        
        history = {
            "train_losses": self.train_losses,
            "val_losses": self.val_losses,
            "train_accuracies": self.train_accuracies,
            "val_accuracies": self.val_accuracies,
            "best_val_accuracy": best_val_acc
        }
        
        with open(self.model_dir / "training_history.json", 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"Training completed! Best validation accuracy: {best_val_acc:.2f}%")
        
        # Plot training curves
        self.plot_training_curves()
    
    def plot_training_curves(self):
        """Plot training and validation curves"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Loss curves
        ax1.plot(self.train_losses, label='Train Loss')
        ax1.plot(self.val_losses, label='Validation Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Accuracy curves
        ax2.plot(self.train_accuracies, label='Train Accuracy')
        ax2.plot(self.val_accuracies, label='Validation Accuracy')
        ax2.set_title('Training and Validation Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy (%)')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.model_dir / "training_curves.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Training curves saved to src/data/models/training_curves.png")

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train alfalfa classification model")
    parser.add_argument("--config", type=str, default="config/ml_config.json", help="Path to config file")
    parser.add_argument("--epochs", type=int, default=20, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "num_classes": 4,
        "num_workers": 4
    }
    
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            file_config = json.load(f)
            config.update(file_config)
    
    logger.info(f"Training configuration: {config}")
    
    # Create trainer and train
    trainer = AlfalfaTrainer(config)
    trainer.train()

if __name__ == "__main__":
    main()
