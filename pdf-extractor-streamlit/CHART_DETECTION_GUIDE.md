# Chart Detection Guide

## Overview

Your system can automatically detect and extract data from **three types of charts**:

1. **Bar Charts** - Extracts bar heights as values
2. **Pie Charts** - Detects slices and segments  
3. **Line Charts** - Extracts data points and coordinates

---

## Chart Detection Features

### Chart Types Supported

#### 1. **Bar Charts** 📊
- **Detection Method**: Horizontal vs vertical line analysis
- **Data Extracted**: Bar positions, heights (normalized to 0-100 scale)
- **Use Case**: Sales data, comparisons, performance metrics

**Example Output:**
```
Bar_1: value = 42.5
Bar_2: value = 67.3
Bar_3: value = 55.1
```

#### 2. **Pie Charts** 🥧
- **Detection Method**: Hough Circle Transform (detects circular shapes)
- **Data Extracted**: Circle center, radius, slice segments
- **Use Case**: Market share, percentages, distributions

**Example Output:**
```
Slice_1: center=(150, 150), radius=100
Slice_2: center=(150, 150), radius=100
Slice_3: center=(150, 150), radius=100
```

#### 3. **Line Charts** 📈
- **Detection Method**: Corner/feature detection with line tracing
- **Data Extracted**: X/Y coordinates of data points
- **Use Case**: Trends, time series, growth patterns

**Example Output:**
```
Point_1: x=0.100, y=0.250
Point_2: x=0.250, y=0.450
Point_3: x=0.400, y=0.520
```

---

## How to Use Chart Detection

### Step 1: Upload Image with Charts

1. Go to **📤 Upload & Extract** tab
2. Upload an image containing charts (PNG, JPG, JPEG)
3. Set Job Name
4. Ensure **Full Auto-Detection** mode is selected

### Step 2: Extract Data

1. Click **🔍 Extract Data** button
2. System will:
   - Run OCR to extract text
   - Detect charts using computer vision
   - Count and classify chart types
   - Show "Detected Elements" summary

### Step 3: View Chart Details

1. Go to **📉 Charts** tab (new tab!)
2. Select the file you just extracted
3. Click **🔍 Detect Charts in Image**
4. View:
   - Chart type (Bar/Pie/Line)
   - Confidence score
   - Extracted data points
   - Visual representations

---

## Understanding Detection Sensitivity

In the Charts tab, you can adjust **Detection Sensitivity** (0.3 - 0.9):

- **Low (0.3-0.5)**: Conservative detection, fewer false positives
- **Medium (0.5-0.7)**: Balanced, good default ✅
- **High (0.7-0.9)**: Aggressive, detects more (may include false positives)

---

## Detection Algorithm Details

### Bar Chart Detection

```
1. Apply edge detection (Canny)
2. Find line structures
3. Count horizontal vs vertical lines
4. If horizontal lines > vertical: classify as Bar Chart
5. Extract bar regions and measure heights
6. Normalize heights to 0-100 scale
```

**Heuristics:**
- Bars must be at least 10×10 pixels
- Minimum 2-3 distinct bars to qualify
- Bar height indicates relative value

### Pie Chart Detection

```
1. Convert to grayscale
2. Apply Hough Circle Transform
3. Look for circular shapes
4. If circles detected: classify as Pie Chart
5. Extract slice positions and angles
```

**Heuristics:**
- Circle radius: 10-100 pixels
- Detects up to 5 slices per pie
- Center coordinates normalized

### Line Chart Detection

```
1. Convert to grayscale
2. Apply corner/feature detection
3. Track connected points
4. If points form line pattern: classify as Line Chart
5. Extract (x,y) coordinates and sort by x
```

**Heuristics:**
- Detects up to 20 data points per chart
- Coordinates normalized to 0-1 range
- Points sorted left-to-right

---

## Accuracy & Limitations

### Accuracy Factors

| Factor | Impact |
|--------|--------|
| Image Quality | High - clearer charts = better detection |
| Chart Size | High - larger charts easier to detect |
| Chart Color | Medium - distinct colors help |
| Background | High - busy backgrounds reduce accuracy |
| Chart Type | Medium - pie detection most reliable |

### Known Limitations

❌ **Does NOT detect:**
- Scatter plots (only specialized scatter)
- Heat maps or color gradients
- 3D charts or complex visualizations
- Charts with handwritten elements
- Very small charts (< 5000 pixels²)

✅ **Works best with:**
- Clean, professional charts
- Single chart per image (or separate regions)
- Standard bar/pie/line formats
- High resolution images (300+ DPI)

---

## Confidence Scores

Each detected chart shows a **Confidence Score** (0-100%):

- **90-100%**: Very reliable, data highly accurate
- **70-89%**: Good detection, data mostly accurate
- **50-69%**: Fair detection, may need manual review
- **< 50%**: Low confidence, verify manually

**Tips to improve confidence:**
- Use higher quality images
- Ensure charts have clear borders/gridlines
- Remove background clutter
- Use standard chart types
- Increase chart size if possible

---

## Data Export

### Export Chart Data

After detecting charts, you can:

1. View extracted data in the table
2. Go to **📥 Download Results** tab
3. Export as:
   - **CSV**: Raw data points
   - **XLSX**: Excel with formatting
   - **JSON**: Hierarchical structure with metadata

### Example Exports

**CSV (Bar Chart):**
```
Label,Value,Confidence
Bar_1,42.5,0.6
Bar_2,67.3,0.6
Bar_3,55.1,0.6
```

**JSON (Line Chart):**
```json
{
  "chart_type": "line_chart",
  "detection_confidence": 0.72,
  "data_points": [
    {"x": 0.1, "y": 0.25, "confidence": 0.6},
    {"x": 0.25, "y": 0.45, "confidence": 0.6},
    {"x": 0.4, "y": 0.52, "confidence": 0.6}
  ]
}
```

---

## Troubleshooting

### Issue: No Charts Detected

**Possible Causes:**
1. Chart too small (< 5000 pixels²)
2. Low image quality or blurry
3. Chart type not supported
4. Chart embedded in text

**Solutions:**
- ✅ Use higher resolution image
- ✅ Crop to just the chart
- ✅ Try different sensitivity level
- ✅ Ensure chart has clear structure

### Issue: Wrong Chart Type Detected

**Example:** Bar chart detected as line chart

**Causes:**
1. Chart has mixed styling
2. Unclear line structure
3. Background interference

**Solutions:**
- ✅ Simplify chart appearance
- ✅ Remove background elements
- ✅ Ensure consistent line types

### Issue: Data Values Seem Wrong

**Causes:**
1. Low OCR quality
2. Chart scale not captured
3. Axis labels missing

**Solutions:**
- ✅ Check OCR text in debug info
- ✅ Review extracted values
- ✅ Manually verify high-value items

---

## API Reference

### Detect Elements Endpoint

```bash
POST /detect_elements
```

**Request:**
```json
{
  "image_id": "image_12345",
  "left": 0,
  "top": 0,
  "width": 1000,
  "height": 1000,
  "table_csv_path": null
}
```

**Response:**
```json
{
  "tables": [],
  "charts": [
    {
      "type": "bar_chart",
      "bbox": [100, 150, 400, 300],
      "confidence": 0.72,
      "data": [
        {"label": "Bar_1", "value": 42.5, "confidence": 0.6}
      ]
    }
  ],
  "text_blocks": []
}
```

### Chart Types

- `bar_chart` - Horizontal/vertical bars
- `pie_chart` - Circular segments
- `line_chart` - Connected data points

---

## Best Practices

✅ **DO:**
- Use clear, professional charts
- Ensure good image quality
- Crop to individual charts for best accuracy
- Verify extracted values make sense
- Use sensitivity slider to fine-tune
- Check confidence scores

❌ **DON'T:**
- Use blurry or low-res images
- Mix multiple chart types in one region
- Use heavily styled/3D charts
- Ignore low confidence scores
- Trust fully automated extraction for critical data

---

## Advanced Usage

### Manual Tuning

In `backend/services/chart_extractor.py`, you can adjust:

```python
# Bar chart detection thresholds
if area < 5000 or area > img_bgr.shape[0] * img_bgr.shape[1] * 0.8:
    continue  # Adjust size thresholds

# Pie chart detection parameters
circles = cv2.HoughCircles(
    gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
    param1=50, param2=30, minRadius=10, maxRadius=100  # Adjust radius
)
```

### Combining with Table Detection

System automatically:
1. Detects charts and tables separately
2. Extracts data from both
3. Allows viewing in different tabs
4. Exports combined results

---

## Performance

- **Detection Speed**: 500ms - 2s per image (depends on size/complexity)
- **Memory**: ~50MB per extraction
- **Max Image Size**: 4000×4000 pixels recommended
- **Concurrent**: Processed sequentially

---

## Version Information

- **System**: Intelligent Data Extractor v2.0
- **Chart Detection**: OpenCV 4.x with Hough Transforms
- **Detection Types**: 3 (Bar, Pie, Line)
- **Last Updated**: November 2024

---

## Next Steps

1. **Test with your charts**: Upload images with bar/pie/line charts
2. **Review extracted data**: Check accuracy in Charts tab
3. **Adjust sensitivity**: Find optimal detection level
4. **Export results**: Download as CSV/XLSX/JSON
5. **Combine with tables**: Extract both tables and charts from same document

**Happy charting!** 📊📈🥧

---

## Support

For issues or questions:
1. Check this guide for solutions
2. Review debug info in UI
3. Check backend logs for errors
4. Ensure image quality is good
5. Try test images with simple charts first
