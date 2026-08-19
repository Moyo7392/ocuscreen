import os
from pathlib import Path
import torch
from torch import nn
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0


class RetinopathyModel:
    def __init__(self, weights_path: str | None = None, model_version: str | None = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Avoid downloading weights at service startup. A trained artifact is mandatory outside demo mode.
        self.model = efficientnet_b0(weights=None)
        self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features, 5)
        artifact = Path(weights_path or os.getenv("MODEL_WEIGHTS", "artifacts/efficientnet_b0_aptos.pt"))
        if not artifact.exists():
            raise FileNotFoundError(f"Model artifact not found: {artifact}. Set MODEL_WEIGHTS to a trained checkpoint.")
        checkpoint = torch.load(artifact, map_location=self.device, weights_only=True)
        self.model.load_state_dict(checkpoint.get("model_state_dict", checkpoint))
        self.model.to(self.device).eval()
        self.version = model_version or os.getenv("MODEL_VERSION", artifact.stem)
        self.target_layer = self.model.features[-1]

    def predict(self, tensor: torch.Tensor) -> tuple[int, float, torch.Tensor]:
        with torch.enable_grad():
            tensor = tensor.to(self.device).requires_grad_(True)
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)
            confidence, grade = probabilities.max(dim=1)
        return int(grade.item()), float(confidence.item()), logits
