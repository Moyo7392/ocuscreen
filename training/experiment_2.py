"""Leakage-free APTOS training with fundus preprocessing and ordinal-aware loss.

The model is initialized from ImageNet—not an existing OcuScreen checkpoint—and
is trained only on the random_state=42 training partition.
"""
from __future__ import annotations

import argparse
import copy
import random
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import models, transforms

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "experiment_2_best.pth"
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
GRADE_NAMES = ["grade0", "grade1", "grade2", "grade3", "grade4"]


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def device_for_host() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def crop_fundus(image: np.ndarray) -> np.ndarray:
    """Remove black camera borders using the largest illuminated component."""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = (gray > 10).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image
    x, y, width, height = cv2.boundingRect(max(contours, key=cv2.contourArea))
    if width < image.shape[1] * 0.25 or height < image.shape[0] * 0.25:
        return image
    return image[y:y + height, x:x + width]


def ben_graham(image: np.ndarray, size: int) -> Image.Image:
    """Crop, resize, and enhance local retinal contrast."""
    image = crop_fundus(image)
    image = cv2.resize(image, (size, size), interpolation=cv2.INTER_AREA)
    sigma = max(size / 30.0, 1.0)
    enhanced = cv2.addWeighted(image, 4.0, cv2.GaussianBlur(image, (0, 0), sigma), -4.0, 128)
    # Keep the non-retinal corners neutral after enhancement.
    yy, xx = np.ogrid[:size, :size]
    circle = (xx - size / 2) ** 2 + (yy - size / 2) ** 2 <= (size * 0.49) ** 2
    enhanced[~circle] = 128
    return Image.fromarray(enhanced)


class AptosDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, image_dir: Path, size: int, transform) -> None:
        self.frame = frame.reset_index(drop=True)
        self.image_dir = image_dir
        self.size = size
        self.transform = transform

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int):
        row = self.frame.iloc[index]
        path = self.image_dir / f"{row.id_code}.png"
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Could not read {path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.transform(ben_graham(image, self.size)), int(row.diagnosis)


def make_transforms(size: int):
    train = transforms.Compose([
        transforms.RandomResizedCrop(size, scale=(0.88, 1.0), ratio=(0.95, 1.05)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.12, contrast=0.12, saturation=0.08),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
        transforms.RandomErasing(p=0.1, scale=(0.01, 0.05)),
    ])
    validation = transforms.Compose([
        transforms.ToTensor(), transforms.Normalize(MEAN, STD)
    ])
    return train, validation


def make_model() -> nn.Module:
    model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
    model.classifier = nn.Sequential(nn.Dropout(0.35), nn.Linear(1536, 5))
    return model


class OrdinalAwareLoss(nn.Module):
    """Classification loss plus distance-aware expected-grade regression."""
    def __init__(self, class_weights: torch.Tensor, ordinal_weight: float = 0.2) -> None:
        super().__init__()
        self.ce = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.03)
        self.ordinal_weight = ordinal_weight
        self.register_buffer("grades", torch.arange(5, dtype=torch.float32))

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        expected = (logits.softmax(1) * self.grades).sum(1)
        ordinal = nn.functional.smooth_l1_loss(expected, targets.float(), beta=0.5)
        return self.ce(logits, targets) + self.ordinal_weight * ordinal


def score(labels: list[int], predictions: list[int]):
    return accuracy_score(labels, predictions), cohen_kappa_score(labels, predictions, weights="quadratic")


def run_epoch(model, loader, criterion, device, optimizer=None):
    training = optimizer is not None
    model.train(training)
    total_loss, labels, predictions = 0.0, [], []
    context = torch.enable_grad() if training else torch.inference_mode()
    with context:
        for images, targets in loader:
            images, targets = images.to(device), targets.to(device)
            if training:
                optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, targets)
            if training:
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 2.0)
                optimizer.step()
            total_loss += loss.item() * len(targets)
            labels.extend(targets.cpu().tolist())
            predictions.extend(logits.argmax(1).cpu().tolist())
    accuracy, qwk = score(labels, predictions)
    return total_loss / len(loader.dataset), accuracy, qwk, labels, predictions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--size", type=int, default=384)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    seed_everything(args.seed)

    frame = pd.read_csv(ROOT / "data" / "train.csv")
    train_frame, validation_frame = train_test_split(
        frame, test_size=0.2, random_state=args.seed, stratify=frame.diagnosis
    )
    train_transform, validation_transform = make_transforms(args.size)
    image_dir = ROOT / "data" / "train_images"
    train_dataset = AptosDataset(train_frame, image_dir, args.size, train_transform)
    validation_dataset = AptosDataset(validation_frame, image_dir, args.size, validation_transform)

    counts = np.bincount(train_frame.diagnosis, minlength=5)
    # Square-root balancing avoids overwhelming the natural grade-0 prevalence.
    sample_weights = 1.0 / np.sqrt(counts[train_frame.diagnosis.to_numpy()])
    sampler = WeightedRandomSampler(torch.as_tensor(sample_weights, dtype=torch.double),
                                    len(sample_weights), replacement=True)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, sampler=sampler,
                              num_workers=args.workers, persistent_workers=args.workers > 0)
    validation_loader = DataLoader(validation_dataset, batch_size=args.batch_size, shuffle=False,
                                   num_workers=args.workers, persistent_workers=args.workers > 0)

    device = device_for_host()
    model = make_model().to(device)
    for parameter in model.features.parameters():
        parameter.requires_grad = False
    # Mild loss balancing complements the moderate sampler without double-correcting.
    loss_weights = torch.as_tensor(np.sqrt(counts.max() / counts), dtype=torch.float32, device=device)
    criterion = OrdinalAwareLoss(loss_weights).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    best_accuracy, best_qwk, best_state, best_epoch = -1.0, -1.0, None, 0
    started = time.time()
    print(f"Experiment 2: device={device} train={len(train_frame)} validation={len(validation_frame)} "
          f"size={args.size} batch={args.batch_size}", flush=True)

    for epoch in range(args.epochs):
        if epoch == 2:
            for parameter in model.features.parameters():
                parameter.requires_grad = True
            optimizer = torch.optim.AdamW([
                {"params": model.features.parameters(), "lr": 3e-5},
                {"params": model.classifier.parameters(), "lr": 1e-4},
            ], weight_decay=1e-4)
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=args.epochs - epoch, eta_min=1e-6
            )
        train_loss, train_acc, train_qwk, _, _ = run_epoch(
            model, train_loader, criterion, device, optimizer
        )
        val_loss, val_acc, val_qwk, labels, predictions = run_epoch(
            model, validation_loader, criterion, device
        )
        scheduler.step()
        print(f"epoch={epoch+1:02d}/{args.epochs} train_loss={train_loss:.4f} "
              f"train_acc={train_acc:.4f} train_qwk={train_qwk:.4f} "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f} val_qwk={val_qwk:.4f}", flush=True)
        if (val_acc, val_qwk) > (best_accuracy, best_qwk):
            best_accuracy, best_qwk, best_epoch = val_acc, val_qwk, epoch + 1
            best_state = copy.deepcopy(model.state_dict())
            torch.save({
                "model_state_dict": best_state, "architecture": "efficientnet_b3",
                "experiment": 2, "epoch": best_epoch, "accuracy": best_accuracy,
                "qwk": best_qwk, "input_size": args.size, "seed": args.seed,
                "preprocessing": "circle_crop_ben_graham", "model_version": "3.0.0",
            }, MODEL_PATH)

    if best_state is None:
        raise RuntimeError("No checkpoint was produced")
    model.load_state_dict(best_state)
    _, accuracy, qwk, labels, predictions = run_epoch(model, validation_loader, criterion, device)
    matrix = confusion_matrix(labels, predictions, labels=range(5))
    per_class = np.divide(matrix.diagonal(), matrix.sum(1), out=np.zeros(5, float), where=matrix.sum(1)>0)
    classes = ", ".join(f"{name}: {value*100:.1f}%" for name, value in zip(GRADE_NAMES, per_class))
    if accuracy >= 0.90:
        import shutil
        shutil.copy2(MODEL_PATH, ROOT / "models" / "model_90_best.pth")
    print("\nEXPERIMENT 2 RESULTS:")
    print(f"Accuracy: {accuracy*100:.1f}%")
    print(f"QWK: {qwk:.4f}")
    print(f"Per-class accuracy: [{classes}]")
    print(f"Best so far: experiment_2 with {accuracy*100:.1f}% accuracy (epoch {best_epoch})")
    print(f"Target: 90.0% — gap: {max(0.0, 90-accuracy*100):.1f}%")
    print(f"Elapsed: {(time.time()-started)/60:.1f} minutes")


if __name__ == "__main__":
    main()
