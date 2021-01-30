"""Numerical utilities
"""

__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import math
import numpy as np

def angle(line1, line2):
    assert len(line1) == len(line2) == 4
    x1, y1, x2, y2 = line1
    m1 = math.atan2(y1 - y2, x1 - x2)
    x1, y1, x2, y2 = line2
    m2 = math.atan2(y1 - y2, x1 - x2)
    return int((m1 - m2) / math.pi * 180)

def normalize_image(img: np.array) -> np.array:
    img = img - img.min()
    img = 255.0 * (img / img.max())
    return img.astype(np.uint8)
