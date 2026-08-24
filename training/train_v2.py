"""Train OcuScreen v2 with CLAHE preprocessing and EfficientNet-B3.

This script intentionally writes progress to training/train_v2.log and saves the
best validation-QWK checkpoint as models/model_v2_best.pth.
"""
from __future__ import annotations

import argparse
import copy
import logging
import random
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import accuracy_score, classification_report, cohen_kappa_score, confusion_matrix
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = Path(__file__).with_name("train_v2.log")
MODEL_PATH = ROOT / "models" / "model_v2_best.pth"
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
GRADE_NAMES = ["No DR", "Mild NPDR", "Moderate NPDR", "Severe NPDR", "Proliferative DR"]


def preprocess_fundus(image_path: str | Path, target_size: int = 224) -> np.ndarray:
    """Crop the retinal ROI, enhance local contrast, denoise, and resize."""
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        contour = max(contours, key=cv2.contourArea)
        x, y, width, height = cv2.boundingRect(contour)
        if width > 0 and height > 0:
            image = image[y:y + height, x:x + width]

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    blue, green, red = cv2.split(image)
    enhanced = cv2.merge((clahe.apply(blue), clahe.apply(green), clahe.apply(red)))
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
    enhanced = cv2.resize(enhanced, (target_size, target_size), interpolation=cv2.INTER_AREA)
    # OpenCV produces BGR; torchvision's ToPILImage expects RGB channel order.
    return cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)


class AptosV2Dataset(Dataset):
    def __init__(self, frame: pd.DataFrame, image_dir: Path, transform: transforms.Compose):
        self.frame = frame.reset_index(drop=True)
        self.image_dir = image_dir
        self.transform = transform

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        row = self.frame.iloc[index]
        image = preprocess_fundus(self.image_dir / f"{row.id_code}.png")
        return self.transform(image), int(row.diagnosis)


def make_transforms() -> tuple[transforms.Compose, transforms.Compose]:
    train_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.ToTensor(),
        transforms.RandomErasing(p=0.2),
        transforms.Normalize(mean=MEAN, std=STD),
    ])
    validation_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=MEAN, std=STD),
    ])
    return train_transform, validation_transform


def make_model(pretrained: bool = True) -> nn.Module:
    weights = models.EfficientNet_B3_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.efficientnet_b3(weights=weights)
    model.classifier = nn.Sequential(nn.Dropout(p=0.4), nn.Linear(1536, 5))
    return model


def set_backbone_trainable(model: nn.Module, trainable: bool) -> None:
    for parameter in model.features.parameters():
        parameter.requires_grad = trainable


def device_for_host() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def mixup_data(
    inputs: torch.Tensor, targets: torch.Tensor, alpha: float = 0.4
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, float]:
    """Blend randomly paired images and preserve both target vectors."""
    coefficient = float(np.random.beta(alpha, alpha)) if alpha > 0 else 1.0
    permutation = torch.randperm(inputs.size(0), device=inputs.device)
    mixed = coefficient * inputs + (1.0 - coefficient) * inputs[permutation]
    return mixed, targets, targets[permutation], coefficient


def mixup_criterion(
    criterion: nn.Module,
    predictions: torch.Tensor,
    targets_a: torch.Tensor,
    targets_b: torch.Tensor,
    coefficient: float,
) -> torch.Tensor:
    return coefficient * criterion(predictions, targets_a) + (1.0 - coefficient) * criterion(predictions, targets_b)


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.CosineAnnealingWarmRestarts,
    device: torch.device,
    epoch: int,
) -> tuple[float, float, float]:
    model.train()
    total_loss = 0.0
    labels: list[int] = []
    predictions: list[int] = []
    for batch_index, (images, targets) in enumerate(loader):
        images, targets = images.to(device), targets.to(device)
        mixed, targets_a, targets_b, coefficient = mixup_data(images, targets, alpha=0.4)
        optimizer.zero_grad(set_to_none=True)
        logits = model(mixed)
        loss = mixup_criterion(criterion, logits, targets_a, targets_b, coefficient)
        loss.backward()
        optimizer.step()
        scheduler.step(epoch + batch_index / max(len(loader), 1))
        total_loss += loss.item() * images.size(0)
        labels.extend(targets.cpu().tolist())
        predictions.extend(logits.argmax(dim=1).detach().cpu().tolist())
    return (
        total_loss / len(loader.dataset),
        accuracy_score(labels, predictions),
        cohen_kappa_score(labels, predictions, weights="quadratic"),
    )


@torch.inference_mode()
def validate(
    model: nn.Module, loader: DataLoader, criterion: nn.Module, device: torch.device
) -> tuple[float, float, float, list[int], list[int]]:
    model.eval()
    total_loss = 0.0
    labels: list[int] = []
    predictions: list[int] = []
    for images, targets in loader:
        images, targets = images.to(device), targets.to(device)
        logits = model(images)
        loss = criterion(logits, targets)
        total_loss += loss.item() * images.size(0)
        labels.extend(targets.cpu().tolist())
        predictions.extend(logits.argmax(dim=1).cpu().tolist())
    return (
        total_loss / len(loader.dataset),
        accuracy_score(labels, predictions),
        cohen_kappa_score(labels, predictions, weights="quadratic"),
        labels,
        predictions,
    )


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("ocuscreen-v2")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train OcuScreen v2")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--epochs", type=int, default=35)
    parser.add_argument("--freeze-epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("Training started", flush=True)
    logger = configure_logging()
    seed_everything(args.seed)
    csv_path = args.data_dir / "train.csv"
    image_dir = args.data_dir / "train_images"
    if not csv_path.exists() or not image_dir.exists():
        raise FileNotFoundError(f"Expected {csv_path} and {image_dir}")

    frame = pd.read_csv(csv_path)
    train_frame, validation_frame = train_test_split(
        frame,
        test_size=0.2,
        random_state=args.seed,
        stratify=frame.diagnosis,
    )
    train_transform, validation_transform = make_transforms()
    train_loader = DataLoader(
        AptosV2Dataset(train_frame, image_dir, train_transform),
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.workers,
        pin_memory=torch.cuda.is_available(),
        persistent_workers=args.workers > 0,
    )
    validation_loader = DataLoader(
        AptosV2Dataset(validation_frame, image_dir, validation_transform),
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.workers,
        pin_memory=torch.cuda.is_available(),
        persistent_workers=args.workers > 0,
    )

    device = device_for_host()
    model = make_model(pretrained=True).to(device)
    set_backbone_trainable(model, False)
    counts = np.bincount(train_frame.diagnosis, minlength=5)
    class_weights = len(train_frame) / (5.0 * counts)
    criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights, dtype=torch.float32, device=device),
        label_smoothing=0.1,
    )
    # Include frozen parameters now so they begin updating immediately when unfrozen.
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=5, T_mult=2, eta_min=1e-6
    )
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    best_qwk = float("-inf")
    best_state: dict[str, torch.Tensor] | None = None

    logger.info("device=%s epochs=%d batch_size=%d train=%d validation=%d", device, args.epochs, args.batch_size, len(train_frame), len(validation_frame))
    logger.info("class_counts=%s class_weights=%s", counts.tolist(), class_weights.round(4).tolist())

    for epoch in range(args.epochs):
        if epoch == args.freeze_epochs:
            set_backbone_trainable(model, True)
            logger.info("Backbone unfrozen at epoch %d", epoch + 1)

        train_loss, train_accuracy, train_qwk = train_epoch(
            model, train_loader, criterion, optimizer, scheduler, device, epoch
        )
        validation_loss, validation_accuracy, validation_qwk, _, _ = validate(
            model, validation_loader, criterion, device
        )
        logger.info(
            "epoch=%02d/%02d train_loss=%.5f train_accuracy=%.4f train_qwk=%.4f "
            "val_loss=%.5f val_accuracy=%.4f val_qwk=%.4f lr=%.8f",
            epoch + 1,
            args.epochs,
            train_loss,
            train_accuracy,
            train_qwk,
            validation_loss,
            validation_accuracy,
            validation_qwk,
            optimizer.param_groups[0]["lr"],
        )
        if validation_qwk > best_qwk:
            best_qwk = validation_qwk
            best_state = copy.deepcopy(model.state_dict())
            torch.save(
                {
                    "model_state_dict": best_state,
                    "architecture": "efficientnet_b3",
                    "model_version": "2.0.0",
                    "epoch": epoch + 1,
                    "qwk": validation_qwk,
                    "accuracy": validation_accuracy,
                    "input_size": 224,
                    "preprocessing": "circular_roi_clahe_rgb_gaussian_blur",
                    "normalization_mean": MEAN,
                    "normalization_std": STD,
                    "grade_names": GRADE_NAMES,
                },
                MODEL_PATH,
            )
            logger.info("Saved new best checkpoint: qwk=%.4f accuracy=%.4f", validation_qwk, validation_accuracy)

    if best_state is None:
        raise RuntimeError("Training completed without producing a checkpoint")
    model.load_state_dict(best_state)
    final_loss, final_accuracy, final_qwk, labels, predictions = validate(
        model, validation_loader, criterion, device
    )
    matrix = confusion_matrix(labels, predictions, labels=range(5))
    report = classification_report(
        labels,
        predictions,
        labels=range(5),
        target_names=GRADE_NAMES,
        digits=4,
        zero_division=0,
    )
    logger.info("Best-checkpoint validation loss: %.5f", final_loss)
    logger.info("Confusion matrix:\n%s", matrix)
    logger.info("Per-class classification report:\n%s", report)
    logger.info("Final QWK: %.4f", final_qwk)
    logger.info("v1 accuracy: 80.5%% | v2 accuracy: %.1f%%", final_accuracy * 100.0)
    logger.info("Checkpoint: %s", MODEL_PATH)
    print("Training complete", flush=True)


if __name__ == "__main__":
    main()
