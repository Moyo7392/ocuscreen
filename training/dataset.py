from pathlib import Path
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset

class AptosDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, image_dir: str, transform=None): self.frame, self.image_dir, self.transform = frame.reset_index(drop=True), Path(image_dir), transform
    def __len__(self): return len(self.frame)
    def __getitem__(self, index):
        row = self.frame.iloc[index]
        path = next((self.image_dir / f"{row.id_code}{ext}" for ext in (".png", ".jpg", ".jpeg") if (self.image_dir / f"{row.id_code}{ext}").exists()), None)
        if path is None: raise FileNotFoundError(row.id_code)
        image = Image.open(path).convert("RGB")
        return (self.transform(image) if self.transform else image), int(row.diagnosis)
