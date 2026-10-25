import numpy as np
import cv2
import os
import sys

from color_detection import get_dominant_color, bgr_to_color_name
from realtime_camera import KalmanDistanceTracker

def run_tests():
    tracker = KalmanDistanceTracker()
    estimates = []
    for _ in range(10):
        val = tracker.update(50.0)
        estimates.append(val)
    
    assert abs(estimates[-1] - 50.0) < 1.0, "Kalman filter did not converge"

    red_bgr = (0, 0, 255)
    green_bgr = (0, 255, 0)
    blue_bgr = (255, 0, 0)

    assert bgr_to_color_name(red_bgr) == "แดง"
    assert bgr_to_color_name(green_bgr) == "เขียว"
    assert bgr_to_color_name(blue_bgr) in ["น้ำเงิน", "ฟ้า"]

    test_patch = np.zeros((60, 60, 3), dtype=np.uint8)
    test_patch[:, :] = [0, 255, 0]
    dominant = get_dominant_color(test_patch, k=2)
    assert bgr_to_color_name(dominant) == "เขียว"

    print("Project 20 Color Detection and Kalman Tracker tests passed")

if __name__ == "__main__":
    run_tests()
