import numpy as np

from inference.gradcam import hotspot_regions


def test_hotspots_are_ranked_by_area_with_normalized_centers():
    cam = np.zeros((100, 100), dtype=np.float32)
    cam[10:30, 10:30] = 1.0
    cam[70:80, 70:80] = 0.9

    regions = hotspot_regions(cam)

    assert [region["id"] for region in regions] == [1, 2]
    assert regions[0]["area"] == 400
    assert 0 <= regions[0]["x"] <= 1
    assert 0 <= regions[0]["y"] <= 1
    assert regions[0]["anatomy"] == "superior arcade"


def test_hotspots_return_at_most_three_regions():
    cam = np.zeros((50, 50), dtype=np.float32)
    for offset in (2, 12, 22, 32):
        cam[offset:offset + 4, offset:offset + 4] = 1.0

    assert len(hotspot_regions(cam)) == 3
