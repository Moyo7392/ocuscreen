"""Experiment 1: evaluate the v1/v2 checkpoint ensemble on the seed-42 split."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from training.train import AptosDataset, make_model as make_v1_model
from training.train_v2 import AptosV2Dataset, make_model as make_v2_model, make_transforms
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[1]
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def device_for_host() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@torch.inference_mode()
def probabilities(model, loader, device):
    output, labels = [], []
    model.eval()
    for images, targets in loader:
        output.append(model(images.to(device)).softmax(1).cpu())
        labels.append(targets)
    return torch.cat(output).numpy(), torch.cat(labels).numpy()


def metrics(labels, predictions):
    matrix = confusion_matrix(labels, predictions, labels=range(5))
    per_class = np.divide(
        matrix.diagonal(), matrix.sum(axis=1),
        out=np.zeros(5, dtype=float), where=matrix.sum(axis=1) != 0,
    )
    return accuracy_score(labels, predictions), cohen_kappa_score(
        labels, predictions, weights="quadratic"
    ), per_class


def main():
    frame = pd.read_csv(ROOT / "data" / "train.csv")
    _, validation = train_test_split(
        frame, test_size=0.2, random_state=42, stratify=frame.diagnosis
    )
    v1_transform = transforms.Compose([
        transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(MEAN, STD)
    ])
    _, v2_transform = make_transforms()
    image_dir = ROOT / "data" / "train_images"
    v1_loader = DataLoader(AptosDataset(validation, image_dir, v1_transform), batch_size=32,
                           shuffle=False, num_workers=4)
    v2_loader = DataLoader(AptosV2Dataset(validation, image_dir, v2_transform), batch_size=32,
                           shuffle=False, num_workers=4)
    device = device_for_host()
    v1 = make_v1_model(pretrained=False).to(device)
    v2 = make_v2_model(pretrained=False).to(device)
    v1.load_state_dict(torch.load(ROOT / "models/model_best.pth", map_location="cpu",
                                  weights_only=False)["model_state_dict"])
    v2.load_state_dict(torch.load(ROOT / "models/model_v2_best.pth", map_location="cpu",
                                  weights_only=False)["model_state_dict"])
    p1, labels = probabilities(v1, v1_loader, device)
    p2, labels2 = probabilities(v2, v2_loader, device)
    if not np.array_equal(labels, labels2):
        raise RuntimeError("Validation loaders are not aligned")

    candidates = []
    for weight_v1 in np.linspace(0, 1, 21):
        predictions = (weight_v1 * p1 + (1 - weight_v1) * p2).argmax(1)
        accuracy, qwk, per_class = metrics(labels, predictions)
        candidates.append((accuracy, qwk, weight_v1, per_class))
        print(f"blend v1={weight_v1:.2f} v2={1-weight_v1:.2f}: accuracy={accuracy:.4f} qwk={qwk:.4f}")
    accuracy, qwk, weight_v1, per_class = max(candidates, key=lambda row: (row[0], row[1]))
    shutil.copy2(ROOT / ("models/model_best.pth" if weight_v1 >= 0.5 else "models/model_v2_best.pth"),
                 ROOT / "models/experiment_1_best.pth")
    classes = ", ".join(f"grade{i}: {value*100:.1f}%" for i, value in enumerate(per_class))
    print("\nEXPERIMENT 1 RESULTS:")
    print(f"Accuracy: {accuracy*100:.1f}%")
    print(f"QWK: {qwk:.4f}")
    print(f"Per-class accuracy: [{classes}]")
    print(f"Best blend: v1={weight_v1:.2f}, v2={1-weight_v1:.2f}")
    print(f"Best so far: experiment_1 with {accuracy*100:.1f}% accuracy")
    print(f"Target: 90.0% — gap: {max(0, 90-accuracy*100):.1f}%")


if __name__ == "__main__":
    main()
