# Table Detection Troubleshooting Guide

## Problem: No Tables Being Detected

This guide helps you diagnose and fix table detection issues.

---

## Quick Checklist

- [ ] Is Tesseract OCR installed and in PATH?
- [ ] Is the image quality good (not blurry, low-resolution)?
- [ ] Does the table have visible structure (lines, borders)?
- [ ] Are headers and data rows clearly separated?

---

## Root Causes

### 1. **Tesseract OCR Not Found or Not Working**

**Symptoms:**
- Error: "Tesseract not found" or "TesseractNotFoundError"
- OCR returns empty text

**Solution:**

**Windows:**
```powershell
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Run the installer and accept default location

# Add to PATH (PowerShell as Admin)
$env:PATH += ";C:\Program Files\Tesseract-OCR"
```

**Verify Installation:**
```powershell
tesseract --version
```

### 2. **Poor Image Quality**

**Symptoms:**
- OCR works but returns garbled text
- Tables detected as empty or with wrong data
- Random characters mixed with actual data

**Solution:**
- Upload higher resolution images (300+ DPI)
- Ensure images are not blurry or rotated
- Avoid partial/cut-off tables
- Use PNG or JPG format (avoid GIF/BMP)

### 3. **OCR Working But Table Not Extracted**

**Symptoms:**
- Debug shows OCR has text but no rows extracted
- Detection status: "no_valid_rows" or "no_table_found"

**Solution:**
The table detection heuristics may need tuning. Check:

```
Structure expected:
- Line 1: Headers (multiple words/numbers)
- Lines 2+: Data rows (label + values)
- Rows should have consistent format
```

---

## Debugging Steps

### Step 1: Enable Debug Information

In the Streamlit UI, after extraction, expand the **"🔍 Debug Info"** section:

```
Detection Status: [Shows what happened]
OCR Text Length: [Number of characters]
Raw Lines Found: [How many lines were detected]
Extracted Rows: [Final table rows]
OCR Text Preview: [First 500 characters]
```

### Step 2: Check OCR Output

Use the debug endpoint to see raw OCR output:

```bash
curl -X POST http://localhost:8001/debug_table_detection \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "your_image_id",
    "left": 0,
    "top": 0,
    "width": 1000,
    "height": 1000,
    "table_csv_path": null
  }'
```

**Look for:**
- `ocr_successful`: Should be `true`
- `total_characters`: Should be > 100 (depends on image)
- `lines`: Should show actual table content

### Step 3: Manual Region Selection

Instead of Full Auto-Detection:

1. Go to Settings → Select **"Manual Region Selection"**
2. Upload image
3. Use sliders to draw a box around the specific table
4. Extract from that region only

This helps isolate which part has the table.

---

## Table Format Requirements

For best results, tables should have:

```
Format: Structured (header row + data rows)

✅ GOOD:
Product    Q1    Q2    Q3
Sales      100   120   150
Profit     20    25    30

❌ AVOID:
- Merged cells
- Irregular spacing
- Missing columns
- Non-aligned data
- Text-heavy descriptions
```

---

## Advanced Tuning

If OCR works but rows still aren't detected, you can modify `/backend/services/table_extractor.py`:

### Modify `_select_table_block()` function:

Currently, the function looks for lines with:
- At least 2 tokens (words/numbers)
- Consistent structure

If your table has different formatting, you may need to adjust:

```python
# Line that checks token consistency
token_match = abs(len(tokens) - baseline_tokens) <= 2  # Change 2 to higher if flexible
```

### Modify `_parse_table_from_block()` function:

Currently accepts any row with at least 1 token.

For stricter validation, change:
```python
if len(tokens) < 1:  # Change to >= 2 for stricter parsing
    continue
```

---

## Common Issues & Solutions

| Issue | Check | Solution |
|-------|-------|----------|
| "No table found" | OCR text in debug | Image quality poor or not a table |
| "OCR text empty" | Terminal errors | Tesseract not installed/configured |
| "Table has wrong columns" | Debug OCR output | Spacing/alignment issue in table |
| "Some rows missing" | Compare OCR vs extracted | Modify token matching threshold |
| "Wrong data types" | Exported CSV | Check `_maybe_number()` function |

---

## Testing Recommendations

### Test with Sample Tables

1. **Simple Table** (2×2):
```
Year   Revenue
2022   1000
2023   1200
```

2. **Complex Table** (4×5):
```
Product  Q1    Q2    Q3    Q4
Sales    100   120   150   180
Profit   20    25    30    35
Growth   15%   20%   25%   28%
```

3. **Real Business Report**:
- Download a sample from web
- Extract specific table region
- Verify output matches source

---

## Performance Tips

1. **Crop Images Before Upload**
   - Smaller files = faster processing
   - Better accuracy on specific regions
   - Recommended: 400×300 to 1200×800 pixels

2. **Use Manual Selection**
   - Bypass auto-detection
   - Focus on specific table
   - Better for complex documents

3. **Batch Processing**
   - Upload multiple images at once
   - Processed sequentially
   - Better for consistency

---

## Getting Help

If tables still aren't detected:

1. **Check Backend Logs**
   ```powershell
   # Terminal where uvicorn is running
   # Look for error messages or warnings
   ```

2. **Export Debug Data**
   ```powershell
   # Check the outputs folder
   cat outputs/*/extracted.json
   ```

3. **Test OCR Directly**
   ```python
   from PIL import Image
   import pytesseract
   
   img = Image.open("your_image.png")
   text = pytesseract.image_to_string(img)
   print(text)
   ```

---

## Best Practices

✅ **DO:**
- Use high-quality scans (300+ DPI)
- Ensure tables have clear borders
- Test with simple tables first
- Check OCR output before debugging parsing
- Use manual region selection for complex documents
- Export results to validate

❌ **DON'T:**
- Use low-resolution/blurry images
- Mix multiple unrelated tables in one image
- Expect perfect detection on handwritten tables
- Ignore OCR errors
- Use tables without clear structure

---

## Version Information

- **System**: PDF Extractor v2.0
- **Last Updated**: November 2024
- **Backend**: FastAPI
- **OCR Engine**: Tesseract 5.0+

---

## Next Steps

1. Run backend with improved table detection
2. Test with your actual images
3. Check debug output if issues persist
4. Adjust parameters as needed
5. Export and validate results

Happy extracting! 🚀
