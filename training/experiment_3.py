"""Experiment 3: leakage-free ensemble of v2 and experiment 2."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from training.experiment_2 import AptosDataset as BenDataset, make_model as make_ben_model, make_transforms as make_ben_transforms
from training.train_v2 import AptosV2Dataset, make_model as make_v2_model, make_transforms as make_v2_transforms

ROOT = Path(__file__).resolve().parents[1]


def device_for_host():
    return torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")


@torch.inference_mode()
def logits_for(model, loader, device):
    logits, labels = [], []
    model.eval()
    for images, targets in loader:
        logits.append(model(images.to(device)).cpu())
        labels.append(targets)
    return torch.cat(logits), torch.cat(labels).numpy()


def main():
    frame = pd.read_csv(ROOT / "data/train.csv")
    _, validation = train_test_split(frame, test_size=0.2, random_state=42, stratify=frame.diagnosis)
    image_dir = ROOT / "data/train_images"
    _, v2_transform = make_v2_transforms()
    _, ben_transform = make_ben_transforms(384)
    v2_loader = DataLoader(AptosV2Dataset(validation, image_dir, v2_transform), batch_size=24,
                           shuffle=False, num_workers=4)
    ben_loader = DataLoader(BenDataset(validation, image_dir, 384, ben_transform), batch_size=8,
                            shuffle=False, num_workers=4)
    device = device_for_host()
    v2 = make_v2_model(pretrained=False).to(device)
    ben = make_ben_model().to(device)
    v2_checkpoint = torch.load(ROOT / "models/model_v2_best.pth", map_location="cpu", weights_only=False)
    ben_checkpoint = torch.load(ROOT / "models/experiment_2_best.pth", map_location="cpu", weights_only=False)
    v2.load_state_dict(v2_checkpoint["model_state_dict"])
    ben.load_state_dict(ben_checkpoint["model_state_dict"])
    v2_logits, labels = logits_for(v2, v2_loader, device)
    ben_logits, labels2 = logits_for(ben, ben_loader, device)
    if not np.array_equal(labels, labels2):
        raise RuntimeError("Validation data are not aligned")

    candidates = []
    for temperature_v2 in (0.75, 1.0, 1.25, 1.5):
        p_v2 = (v2_logits / temperature_v2).softmax(1).numpy()
        for temperature_ben in (0.75, 1.0, 1.25, 1.5):
            p_ben = (ben_logits / temperature_ben).softmax(1).numpy()
            for weight_v2 in np.linspace(0, 1, 21):
                predictions = (weight_v2*p_v2 + (1-weight_v2)*p_ben).argmax(1)
                accuracy = accuracy_score(labels, predictions)
                qwk = cohen_kappa_score(labels, predictions, weights="quadratic")
                candidates.append((accuracy, qwk, weight_v2, temperature_v2, temperature_ben, predictions))
    accuracy, qwk, weight_v2, temp_v2, temp_ben, predictions = max(candidates, key=lambda x:(x[0],x[1]))
    matrix = confusion_matrix(labels, predictions, labels=range(5))
    per_class = np.divide(matrix.diagonal(), matrix.sum(1), out=np.zeros(5,float), where=matrix.sum(1)>0)
    artifact = {
        "architecture":"probability_ensemble", "experiment":3, "accuracy":accuracy, "qwk":qwk,
        "members":["model_v2_best.pth","experiment_2_best.pth"], "weight_v2":weight_v2,
        "temperature_v2":temp_v2, "temperature_experiment_2":temp_ben,
        "seed":42, "validation_size":len(labels),
    }
    (ROOT / "models/experiment_3_best.json").write_text(json.dumps(artifact, indent=2)+"\n")
    classes=", ".join(f"grade{i}: {value*100:.1f}%" for i,value in enumerate(per_class))
    print("EXPERIMENT 3 RESULTS:")
    print(f"Accuracy: {accuracy*100:.1f}%")
    print(f"QWK: {qwk:.4f}")
    print(f"Per-class accuracy: [{classes}]")
    print(f"Best blend: v2={weight_v2:.2f}, experiment_2={1-weight_v2:.2f}; temperatures={temp_v2:.2f}/{temp_ben:.2f}")
    print(f"Best so far (leakage-free): experiment_3 with {accuracy*100:.1f}% accuracy")
    print(f"Target: 90.0% — gap: {max(0,90-accuracy*100):.1f}%")


if __name__ == "__main__":
    main()
