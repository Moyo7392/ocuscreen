from dataclasses import dataclass
import cv2
import numpy as np


@dataclass(frozen=True)
class QualityResult:
    accepted: bool
    reason: str | None = None
    blur_score: float = 0.0
    illumination: float = 0.0


def assess_quality(image: np.ndarray, blur_threshold: float = 35.0) -> QualityResult:
    """Conservative acquisition checks; rejection means the model is never called."""
    height, width = image.shape[:2]
    if min(height, width) < 224:
        return QualityResult(False, "Image dimensions are too small. Please submit a photograph at least 224 × 224 pixels.")
    ratio = width / height
    if not 0.75 <= ratio <= 1.34:
        return QualityResult(False, "Image proportions do not resemble a retinal fundus photograph.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    illumination = float(gray.mean())
    if blur < blur_threshold:
        return QualityResult(False, "Image is too blurred to grade reliably. Please submit a clearer photograph.", blur, illumination)
    if illumination < 25:
        return QualityResult(False, "Image is too dark to grade reliably. Please improve illumination and try again.", blur, illumination)
    if illumination > 235:
        return QualityResult(False, "Image is overexposed. Please reduce illumination and try again.", blur, illumination)

    # Fundus images normally contain a circular field surrounded by a darker border.
    center = gray[height // 4: 3 * height // 4, width // 4: 3 * width // 4]
    edge = np.concatenate((gray[: height // 8].ravel(), gray[-height // 8:].ravel()))
    if float(center.mean()) - float(edge.mean()) < 8:
        return QualityResult(False, "The image does not contain a clearly visible retinal field.", blur, illumination)
    return QualityResult(True, blur_score=blur, illumination=illumination)
