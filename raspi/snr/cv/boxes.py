from typing import List

import numpy as np
import cv2


def apply_boxes(frame: np.array, rects: List, color, thickness) -> np.array:
    # Demo rectangles
    for r in rects:
        x, y, w, h = r
        # Draw a green rectangle to visualize the bounding rect
        cv2.rectangle(frame,
                      (x, y), (x+w, y+h),
                      color,
                      thickness)

    return frame
