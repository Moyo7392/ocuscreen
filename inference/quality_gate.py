from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image


@dataclass
class QualityResult:
    accepted: bool
    reason: str | None = None
    blur_score: float | None = None


def assess_quality(image: Image.Image, blur_threshold: float = 18.0) -> QualityResult:
    width, height = image.size
    if min(width, height) < 224 or max(width, height) > 12000:
        return QualityResult(False, "Image dimensions are not suitable for reliable grading.")
    rgb = np.asarray(image.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if score < blur_threshold:
        return QualityResult(False, "Image is too blurred to grade reliably.", score)
    return QualityResult(True, blur_score=score)

