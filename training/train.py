"""Train EfficientNet-B0 and checkpoint the best validation quadratic-weighted kappa."""
import argparse
from pathlib import Path
import pandas as pd
import torch
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0
from torchvision.transforms import v2
import yaml
from dataset import AptosDataset

def run(config_path: str):
    cfg = yaml.safe_load(Path(config_path).read_text())
    torch.manual_seed(cfg["seed"])
    frame = pd.read_csv(cfg["labels_csv"])
    train_df, val_df = train_test_split(frame, test_size=.2, stratify=frame.diagnosis, random_state=cfg["seed"])
    base = [v2.Resize((224,224)), v2.ToImage(), v2.ToDtype(torch.float32, scale=True), v2.Normalize((.485,.456,.406),(.229,.224,.225))]
    train_transform = v2.Compose([v2.RandomHorizontalFlip(), v2.RandomVerticalFlip(), v2.RandomRotation(15), v2.ColorJitter(.15,.15), *base])
    val_transform = v2.Compose(base)
    loaders = {"train": DataLoader(AptosDataset(train_df, cfg["data_dir"], train_transform), cfg["batch_size"], shuffle=True), "val": DataLoader(AptosDataset(val_df, cfg["data_dir"], val_transform), cfg["batch_size"])}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT); model.classifier[1] = nn.Linear(1280, 5); model.to(device)
    counts = torch.tensor(cfg["class_counts"], dtype=torch.float); weights = counts.sum() / (len(counts) * counts)
    criterion = nn.CrossEntropyLoss(weight=weights.to(device)); optimizer = torch.optim.Adam(model.parameters(), lr=cfg["learning_rate"]); scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, cfg["epochs"])
    output = Path(cfg["output_dir"]); output.mkdir(parents=True, exist_ok=True); best = -1.0
    for epoch in range(cfg["epochs"]):
        model.train()
        for images, labels in loaders["train"]:
            optimizer.zero_grad(); loss = criterion(model(images.to(device)), labels.to(device)); loss.backward(); optimizer.step()
        scheduler.step(); model.eval(); predictions, targets = [], []
        with torch.no_grad():
            for images, labels in loaders["val"]: predictions.extend(model(images.to(device)).argmax(1).cpu().tolist()); targets.extend(labels.tolist())
        qwk = cohen_kappa_score(targets, predictions, weights="quadratic"); print(f"epoch={epoch+1} val_qwk={qwk:.4f}")
        if qwk > best: best = qwk; torch.save({"model_state_dict": model.state_dict(), "qwk": qwk, "epoch": epoch + 1}, output / "efficientnet_b0_aptos.pt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--config", default="training/config.yaml"); run(parser.parse_args().config)
