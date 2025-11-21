# backend/services/chart_extractor.py
"""
Chart detection and data extraction from images.
Detects bar charts, pie charts, line graphs, and extracts quantitative data.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image


def detect_chart_regions(img_bgr: np.ndarray) -> List[Dict[str, Any]]:
    """
    Detect potential chart regions in an image using contour analysis.
    
    Returns:
        List of dict with keys: type, bbox, confidence, region_img
    """
    if img_bgr is None or img_bgr.size == 0:
        return []
    
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    chart_regions = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by area (avoid very small/large regions)
        if area < 5000 or area > img_bgr.shape[0] * img_bgr.shape[1] * 0.8:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        
        # Extract region
        region = img_bgr[y:y+h, x:x+w]
        
        # Classify chart type based on heuristics
        chart_type = _classify_chart_type(region)
        
        if chart_type:
            chart_regions.append({
                "type": chart_type,
                "bbox": (x, y, w, h),
                "confidence": 0.7,
                "region_img": region,
                "area": area,
            })
    
    return chart_regions


def _classify_chart_type(region: np.ndarray) -> Optional[str]:
    """
    Classify the type of chart (bar, pie, line, etc.) using heuristics.
    """
    if region is None or region.size == 0:
        return None
    
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    
    # Detect circles (pie charts)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
        param1=50, param2=30, minRadius=10, maxRadius=100
    )
    if circles is not None and len(circles[0]) > 0:
        return "pie_chart"
    
    # Detect lines (bar or line charts)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=20, maxLineGap=10)
    
    if lines is not None and len(lines) > 10:
        # Count horizontal vs vertical lines
        horizontal = sum(1 for line in lines if abs(line[0][1] - line[0][3]) < 5)
        vertical = sum(1 for line in lines if abs(line[0][0] - line[0][2]) < 5)
        
        if horizontal > vertical * 1.5:
            return "bar_chart"
        else:
            return "line_chart"
    
    return None


def extract_bar_chart_data(region: np.ndarray, ocr_text: str = "") -> List[Dict[str, Any]]:
    """
    Extract data from bar charts (x-axis labels, y-axis values).
    
    Returns:
        List of dict with keys: label, value, confidence
    """
    data_points = []
    
    if region is None or region.size == 0:
        return data_points
    
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    
    # Detect bars using morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
    morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Bar should be reasonably sized
        if w < 10 or h < 10:
            continue
        
        area = w * h
        
        # Estimate value from bar height (normalized)
        normalized_height = h / region.shape[0]
        estimated_value = normalized_height * 100  # Scale to 0-100
        
        data_points.append({
            "label": f"Bar_{len(data_points)}",
            "value": round(estimated_value, 2),
            "confidence": 0.6,
            "bbox": (x, y, w, h),
        })
    
    # Sort by position (left to right)
    data_points.sort(key=lambda p: p["bbox"][0])
    
    return data_points


def extract_pie_chart_data(region: np.ndarray) -> List[Dict[str, Any]]:
    """
    Extract data from pie charts (slice labels, percentages).
    
    Returns:
        List of dict with keys: label, percentage, confidence
    """
    data_points = []
    
    if region is None or region.size == 0:
        return data_points
    
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    
    # Detect circles
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
        param1=50, param2=30, minRadius=10, maxRadius=100
    )
    
    if circles is not None:
        for circle in circles[0]:
            x, y, radius = circle
            
            # Estimate slice angles from contours
            # This is a simplified heuristic
            data_points.append({
                "label": f"Slice_{len(data_points)}",
                "percentage": 25.0,  # Placeholder
                "confidence": 0.5,
                "center": (int(x), int(y)),
                "radius": int(radius),
            })
    
    return data_points


def extract_line_chart_data(region: np.ndarray) -> List[Dict[str, Any]]:
    """
    Extract data from line charts (x-axis points, y-axis values).
    
    Returns:
        List of dict with keys: x, y, confidence
    """
    data_points = []
    
    if region is None or region.size == 0:
        return data_points
    
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    
    # Detect line points using corner detection
    corners = cv2.goodFeaturesToTrack(
        gray, maxCorners=20, qualityLevel=0.01, minDistance=10
    )
    
    if corners is not None:
        for corner in corners:
            x, y = corner[0]
            # Normalize coordinates
            norm_x = x / region.shape[1]
            norm_y = (region.shape[0] - y) / region.shape[0]
            
            data_points.append({
                "x": round(norm_x, 3),
                "y": round(norm_y, 3),
                "confidence": 0.6,
                "pixel_pos": (int(x), int(y)),
            })
    
    # Sort by x coordinate
    data_points.sort(key=lambda p: p["x"])
    
    return data_points


def extract_chart_legend(region: np.ndarray) -> List[Dict[str, str]]:
    """
    Extract legend information from chart (colors, labels).
    
    Returns:
        List of dict with keys: color, label
    """
    legend_items = []
    
    if region is None or region.size == 0:
        return legend_items
    
    # Detect distinct colors in the image
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    
    # Find dominant colors (simplified approach)
    pixels = hsv.reshape((-1, 3))
    pixels = np.float32(pixels)
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, _, centers = cv2.kmeans(pixels, 3, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    centers = np.uint8(centers)
    
    for idx, center in enumerate(centers):
        h, s, v = center
        # Convert HSV to BGR for display
        bgr_color = cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2BGR)[0][0]
        
        legend_items.append({
            "color_hsv": tuple(center),
            "color_bgr": tuple(bgr_color),
            "label": f"Category_{idx}",
        })
    
    return legend_items
