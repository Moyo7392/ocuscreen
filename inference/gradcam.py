from __future__ import annotations

import base64
import io

import cv2
import numpy as np
import torch
from PIL import Image


class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.activations = None
        self.gradients = None
        self.forward_handle = target_layer.register_forward_hook(self._save_activations)
        self.backward_handle = target_layer.register_full_backward_hook(self._save_gradients)

    def _save_activations(self, _module, _inputs, output):
        self.activations = output.detach()

    def _save_gradients(self, _module, _grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, tensor: torch.Tensor, class_index: int) -> np.ndarray:
        self.model.zero_grad(set_to_none=True)
        logits = self.model(tensor)
        logits[0, class_index].backward()
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = torch.relu((weights * self.activations).sum(dim=1))[0]
        cam -= cam.min()
        cam /= cam.max().clamp_min(1e-8)
        return cam.cpu().numpy()


def overlay_data_url(image: Image.Image, cam: np.ndarray) -> str:
    rgb = np.asarray(image.convert("RGB"))
    resized = cv2.resize(cam, image.size, interpolation=cv2.INTER_LINEAR)
    heatmap = cv2.applyColorMap(np.uint8(255 * resized), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    overlay = np.uint8(np.clip(rgb * 0.56 + heatmap * 0.44, 0, 255))
    output = io.BytesIO()
    Image.fromarray(overlay).save(output, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def hotspot_regions(cam: np.ndarray, limit: int = 3) -> list[dict]:
    """Return the largest high-activation regions using normalized coordinates."""
    normalized = np.clip(cam, 0.0, 1.0)
    mask = np.uint8(normalized >= 0.8 * float(normalized.max()))
    count, _labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    components = sorted(
        range(1, count), key=lambda index: int(stats[index, cv2.CC_STAT_AREA]), reverse=True
    )[:limit]
    height, width = normalized.shape
    strength_names = ["High activation area", "Secondary activation", "Minor activation"]
    regions = []
    for rank, component in enumerate(components):
        x, y = centroids[component]
        x_norm = float(x / max(width - 1, 1))
        y_norm = float(y / max(height - 1, 1))
        regions.append({
            "id": rank + 1,
            "x": round(x_norm, 4),
            "y": round(y_norm, 4),
            "area": int(stats[component, cv2.CC_STAT_AREA]),
            "activation": round(float(normalized[_labels == component].mean()), 4),
            "anatomy": anatomy_name(x_norm, y_norm),
            "description": strength_names[min(rank, len(strength_names) - 1)],
        })
    return regions


def anatomy_name(x: float, y: float) -> str:
    """Describe image-relative retinal anatomy without assuming eye laterality."""
    if abs(x - 0.5) < 0.11 and abs(y - 0.5) < 0.11:
        return "foveal / macular region"
    if y < 0.34:
        return "superior arcade"
    if y > 0.66:
        return "inferior arcade"
    if x < 0.35:
        return "nasal quadrant / optic disc region"
    if x > 0.65:
        return "temporal quadrant"
    return "macular region"
