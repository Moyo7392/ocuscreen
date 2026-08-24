"""Train OcuScreen's EfficientNet-B0 grader on APTOS 2019."""
from __future__ import annotations

import argparse
import copy
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import classification_report, cohen_kappa_score, confusion_matrix
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm import tqdm
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


class AptosDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, image_dir: Path, transform):
        self.frame = frame.reset_index(drop=True)
        self.image_dir = image_dir
        self.transform = transform

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, index):
        row = self.frame.iloc[index]
        path = self.image_dir / f"{row.id_code}.png"
        with Image.open(path) as image:
            image = image.convert("RGB")
        return self.transform(image), int(row.diagnosis)


def device_for_host() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def make_model(pretrained: bool = True) -> nn.Module:
    weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.efficientnet_b0(weights=weights)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 5)
    return model


def set_backbone_trainable(model: nn.Module, trainable: bool) -> None:
    for parameter in model.features.parameters():
        parameter.requires_grad = trainable


def run_epoch(model, loader, loss_fn, device, optimizer=None):
    training = optimizer is not None
    model.train(training)
    total_loss, labels, predictions = 0.0, [], []
    context = torch.enable_grad() if training else torch.inference_mode()
    with context:
        for images, targets in tqdm(loader, leave=False):
            images, targets = images.to(device), targets.to(device)
            if training:
                optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = loss_fn(logits, targets)
            if training:
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * images.size(0)
            labels.extend(targets.cpu().tolist())
            predictions.extend(logits.argmax(1).cpu().tolist())
    qwk = cohen_kappa_score(labels, predictions, weights="quadratic")
    return total_loss / len(loader.dataset), qwk, labels, predictions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=4316)
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    csv_path, image_dir = args.data_dir / "train.csv", args.data_dir / "train_images"
    if not csv_path.exists() or not image_dir.exists():
        raise FileNotFoundError(f"Expected {csv_path} and {image_dir}. See README.md.")

    frame = pd.read_csv(csv_path)
    train_frame, val_frame = train_test_split(
        frame, test_size=0.2, random_state=args.seed, stratify=frame.diagnosis
    )
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)), transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(), transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(), transforms.Normalize(MEAN, STD),
    ])
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(MEAN, STD)
    ])
    train_loader = DataLoader(AptosDataset(train_frame, image_dir, train_transform),
                              batch_size=args.batch_size, shuffle=True, num_workers=args.workers,
                              pin_memory=True)
    val_loader = DataLoader(AptosDataset(val_frame, image_dir, val_transform),
                            batch_size=args.batch_size, shuffle=False, num_workers=args.workers,
                            pin_memory=True)

    device = device_for_host()
    print(f"Training on {device}")
    model = make_model().to(device)
    set_backbone_trainable(model, False)
    counts = np.bincount(train_frame.diagnosis, minlength=5)
    weights = len(train_frame) / (5 * counts)
    loss_fn = nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32, device=device))
    optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    best_qwk, best_state = -1.0, None
    output = ROOT / "models" / "model_best.pth"
    output.parent.mkdir(exist_ok=True)

    for epoch in range(args.epochs):
        if epoch == 5:
            set_backbone_trainable(model, True)
            optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs - epoch)
        train_loss, train_qwk, _, _ = run_epoch(model, train_loader, loss_fn, device, optimizer)
        val_loss, val_qwk, labels, predictions = run_epoch(model, val_loader, loss_fn, device)
        scheduler.step()
        print(f"Epoch {epoch + 1:02d}/{args.epochs}: train loss={train_loss:.4f} "
              f"QWK={train_qwk:.4f} | val loss={val_loss:.4f} QWK={val_qwk:.4f}")
        if val_qwk > best_qwk:
            best_qwk = val_qwk
            best_state = copy.deepcopy(model.state_dict())
            torch.save({"model_state_dict": best_state, "qwk": best_qwk,
                        "epoch": epoch + 1, "model_version": "1.0.0"}, output)

    model.load_state_dict(best_state)
    _, final_qwk, labels, predictions = run_epoch(model, val_loader, loss_fn, device)
    matrix = confusion_matrix(labels, predictions, labels=range(5))
    print("Confusion matrix:\n", matrix)
    print(classification_report(labels, predictions, labels=range(5), digits=4, zero_division=0))
    print(f"Final best validation QWK: {final_qwk:.4f}")
    plt.figure(figsize=(6, 5)); plt.imshow(matrix, cmap="Blues"); plt.colorbar()
    plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.tight_layout()
    plt.savefig(ROOT / "models" / "confusion_matrix.png", dpi=160)


if __name__ == "__main__":
    main()

