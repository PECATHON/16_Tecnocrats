import cv2
import numpy as np

def preprocess_for_table(img_bgr, target_width=1600):
    """
    Basic preprocessing pipeline:
    - convert to gray
    - optional resize to target width (keeps aspect)
    - denoise, adaptive threshold
    - returns preprocessed grayscale image (uint8)
    """
    h, w = img_bgr.shape[:2]
    if w > target_width:
        scale = target_width / w
        img_bgr = cv2.resize(img_bgr, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # slight blur
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    # adaptive threshold (invert so table lines are white on black)
    th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 2)
    # morphological closing to join lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)
    return closed
