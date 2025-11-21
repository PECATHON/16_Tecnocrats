# Chart Detection - Quick Examples

## What's New?

Your system now has a dedicated **📉 Charts** tab to:
- ✅ Automatically detect bar, pie, and line charts
- ✅ Extract data from charts
- ✅ Visualize extracted data
- ✅ Export chart data to CSV/XLSX/JSON

---

## Quick Start

### 1. Upload Image with Chart
```
Go to: 📤 Upload & Extract
Choose: Image with bar/pie/line chart
Click: 🔍 Extract Data
```

### 2. View Detected Charts
```
Go to: 📉 Charts (new tab!)
Select: Your extracted file
Click: 🔍 Detect Charts in Image
```

### 3. See Results
- Chart type detected (Bar/Pie/Line)
- Confidence score (0-100%)
- Extracted data points
- Visual representation

---

## Example: Bar Chart

### Input Image:
```
  ┌─────────────────────┐
  │                     │
  │   Sales by Region   │
  │                     │
  │   ███ North         │
  │   █████ South       │
  │   ███████ East      │
  │                     │
  └─────────────────────┘
```

### Detected Output:
```
Chart Type: BAR_CHART
Confidence: 72%

Data Points:
├─ Bar_1: value = 42.5
├─ Bar_2: value = 67.3
└─ Bar_3: value = 89.1
```

### Visualization:
A Plotly bar chart showing the extracted values

---

## Example: Pie Chart

### Input Image:
```
  ┌─────────────────────┐
  │  Market Share       │
  │                     │
  │      ╱──╲           │
  │    ╱  45% ╲         │
  │   │30% 25% │        │
  │    ╲      ╱         │
  │      ╲──╱           │
  └─────────────────────┘
```

### Detected Output:
```
Chart Type: PIE_CHART
Confidence: 85%

Data Points:
├─ Slice_1: center=(150,150), radius=100
├─ Slice_2: center=(150,150), radius=100
└─ Slice_3: center=(150,150), radius=100
```

### Note:
Pie slices detected by geometry; percentages require OCR enhancement

---

## Example: Line Chart

### Input Image:
```
  ┌─────────────────────┐
  │ Growth Trend        │
  │ 100│          ◆     │
  │  80│       ◆   ◆    │
  │  60│    ◆   ◆       │
  │  40│ ◆         ◆    │
  │  20└────────────────│
  └─────────────────────┘
```

### Detected Output:
```
Chart Type: LINE_CHART
Confidence: 68%

Data Points:
├─ Point_1: x=0.100, y=0.350
├─ Point_2: x=0.275, y=0.520
├─ Point_3: x=0.450, y=0.750
└─ Point_4: x=0.625, y=0.900
```

### Visualization:
A Plotly line chart showing trend

---

## Detection Sensitivity Explained

**Slider Range: 0.3 - 0.9**

### Conservative (0.3 - 0.5)
- Only very obvious charts
- Few false positives
- May miss some charts

**Use When:** You want only high-confidence detections

### Balanced (0.5 - 0.7) ✅ **RECOMMENDED**
- Good balance
- Most charts detected
- Occasional false positives

**Use When:** General usage

### Aggressive (0.7 - 0.9)
- Detects many potential charts
- More false positives
- May include non-chart elements

**Use When:** You want to find all possible charts

---

## Real-World Usage Scenarios

### Scenario 1: Extract Financial Report Charts

```
Input:  PDF with 5 charts (bar, pie, line)
        
Step 1: Upload PDF/screenshot
Step 2: Extract Data → Auto-detects all 3 types
Step 3: Go to Charts tab
Step 4: View each chart's data
Step 5: Export to Excel for analysis
```

### Scenario 2: Verify Chart Accuracy

```
Input:  Chart image with known values
        
Step 1: Upload chart
Step 2: Run detection
Step 3: Check extracted values
Step 4: Compare with source document
Result: Confidence score helps assess accuracy
```

### Scenario 3: Batch Extract Charts

```
Input:  Multiple presentation slides
        
Step 1: Upload images (use Batch Processing)
Step 2: System detects all charts
Step 3: Export combined results
Step 4: Analyze all data in one file
```

---

## Tips for Best Results

### 📸 Image Quality
- Use high-resolution images (300+ DPI)
- Avoid blurry or rotated images
- Ensure good lighting/contrast

### 📊 Chart Clarity
- Use professional chart tools
- Avoid handwritten charts
- Ensure clear chart titles
- Use distinct colors for bars

### 🎯 Crop Smart
- Isolate individual charts
- Remove surrounding text
- Leave small margin around chart
- Avoid multiple charts in one image

### ⚙️ Settings
- Default sensitivity (0.7) works for most
- Increase for complex documents
- Decrease for cleaner charts

---

## Understanding Confidence Scores

Each detection includes a **Confidence Score** (0.0 - 1.0):

```
0.90-1.00: Excellent - Trust the data ✅
0.70-0.89: Good - Usually accurate ✅
0.50-0.69: Fair - Verify before use ⚠️
Below 0.50: Poor - Manual review needed ❌
```

**Why confidence varies:**
- Image quality
- Chart complexity
- Background noise
- Chart size
- Detection algorithm limitations

---

## Interpreting Extracted Data

### Bar Chart Values

```
value = 42.5
```
- Normalized height (0-100 scale)
- Relative to chart maximum
- Multiply by chart axis to get actual value

### Pie Chart Data

```
center = (150, 150)  # Circle center in pixels
radius = 100         # Circle radius in pixels
```
- Geometric positions
- Can calculate angles for slices

### Line Chart Points

```
x = 0.350    # Normalized x-coordinate (0-1)
y = 0.520    # Normalized y-coordinate (0-1)
```
- Normalized to chart axes
- Sort by x for time series
- Multiply by axis ranges for actual values

---

## Combining Table + Chart Detection

Your system can extract **BOTH** from same image:

```
Image with table AND chart:

┌────────────────┬─────────────┐
│  Q1  │  Q2  │  │  Sales      │
│  100 │  120 │  │   ███ Q1    │
│  150 │  180 │  │   █████ Q2  │
└────────────────┴─────────────┘

Results:
✅ Table extracted: 2×2 grid
✅ Chart detected: Bar chart
✅ Both available in separate tabs
```

**How to use:**
1. Extract → Gets tables + charts
2. View table in **📊 Data Viewer** tab
3. View chart in **📉 Charts** tab
4. Export both together

---

## Troubleshooting

### "No charts detected in this image"

**Check:**
1. Is there actually a chart visible?
2. Is chart at least 100×100 pixels?
3. Try increasing sensitivity slider

**Solutions:**
- Upload clearer image
- Crop to isolate chart
- Check image format (use PNG/JPG)

### "Low confidence detection"

**Meaning:**
- Chart detected but may be inaccurate
- Consider manual verification

**Solutions:**
- Review extracted values visually
- Check if chart matches expected values
- Try higher resolution image

### "Wrong chart type detected"

**Example:** Bar chart detected as line chart

**Causes:**
- Mixed chart styling
- Unclear visual structure

**Solutions:**
- Simplify chart appearance
- Ensure consistent line types
- Crop to remove confusing elements

---

## Export & Use

After detecting charts:

### 1. View Data
- In Charts tab
- See all data points with confidence

### 2. Export
```
Go to: 📥 Download Results
Choose: Chart file
Select: Format (CSV/XLSX/JSON)
Click: ⬇️ Export Data
```

### 3. Use Elsewhere
```
CSV  → Excel, Python, R, databases
XLSX → Excel with formatting, pivot tables
JSON → Web apps, APIs, databases
```

---

## Performance Notes

| Metric | Value |
|--------|-------|
| Detection Speed | 0.5-2s per image |
| Max Image Size | 4000×4000 pixels |
| Max Charts/Image | ~10 (depends on size) |
| Memory/Image | ~50MB |
| Concurrent Uploads | Sequential processing |

---

## Next Steps

1. **Try it now**: Upload an image with a chart
2. **Check accuracy**: View extracted data
3. **Adjust settings**: Use sensitivity slider
4. **Export results**: Save as CSV/XLSX/JSON
5. **Combine data**: Extract tables and charts together

---

## FAQ

**Q: Can it detect 3D charts?**
A: No, currently supports bar, pie, and line charts only.

**Q: What about scatter plots?**
A: Limited support - detected as line charts.

**Q: Can it read axis labels?**
A: Not directly - use OCR output in Debug tab.

**Q: Is the data 100% accurate?**
A: No - confidence scores help assess accuracy.

**Q: Can I export chart data?**
A: Yes! CSV, XLSX, and JSON formats.

**Q: How do I extract from PDFs?**
A: Convert page to image first, then upload.

---

Happy chart extracting! 📊📈🥧
