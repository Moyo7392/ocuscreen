import cv2
import numpy as np
import torch


class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model, self.activations, self.gradients = model, None, None
        self.forward_handle = target_layer.register_forward_hook(self._forward)
        self.backward_handle = target_layer.register_full_backward_hook(self._backward)

    def _forward(self, _module, _inputs, output): self.activations = output.detach()
    def _backward(self, _module, _grad_input, grad_output): self.gradients = grad_output[0].detach()

    def generate(self, tensor: torch.Tensor, class_index: int) -> np.ndarray:
        self.model.zero_grad(set_to_none=True)
        logits = self.model(tensor)
        logits[:, class_index].sum().backward()
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = torch.relu((weights * self.activations).sum(dim=1))[0]
        cam -= cam.min(); cam /= cam.max().clamp_min(1e-8)
        return cam.cpu().numpy()

    def close(self): self.forward_handle.remove(); self.backward_handle.remove()


def overlay_heatmap(image_bgr: np.ndarray, cam: np.ndarray) -> np.ndarray:
    height, width = image_bgr.shape[:2]
    heatmap = cv2.applyColorMap(np.uint8(255 * cv2.resize(cam, (width, height))), cv2.COLORMAP_JET)
    return cv2.addWeighted(image_bgr, 0.58, heatmap, 0.42, 0)
