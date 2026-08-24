import numpy as np
from PIL import Image

from inference.quality_gate import assess_quality


def test_rejects_small_image():
    result = assess_quality(Image.new("RGB", (100, 100)))
    assert not result.accepted


def test_rejects_blurred_image():
    result = assess_quality(Image.new("RGB", (512, 512), "gray"))
    assert not result.accepted
    assert "blurred" in result.reason


def test_accepts_sharp_image():
    array = np.indices((512, 512)).sum(axis=0) % 2 * 255
    image = Image.fromarray(np.uint8(array)).convert("RGB")
    assert assess_quality(image).accepted

