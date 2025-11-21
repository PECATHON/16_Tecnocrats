# QUICKSTART Guide - Intelligent Data Extractor

## ⚡ 30-Second Setup

### 1. Prerequisites Check
```bash
# Verify Python 3.9+
python --version

# Verify Tesseract OCR installed
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

### 2. Backend Setup (5 minutes)
```bash
cd backend

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set Tesseract path
$env:PATH += ";C:\Program Files\Tesseract-OCR"

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### 3. Frontend Setup (5 minutes)
Open NEW PowerShell window:
```bash
cd frontend

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run streamlit_enhanced_app.py --server.port 8502
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8502
```

### 4. Access Dashboard
Open browser: **http://localhost:8502**

---

## 🎯 First Time Usage

### Step 1: Upload Image
1. In "📤 Upload & Extract" tab
2. Click "Upload images or PDFs"
3. Select an image with a table or chart
4. Enter a job name (e.g., "first_test")

### Step 2: Extract Data
1. Select extraction mode:
   - **Full Auto-Detection**: Detects all tables/charts automatically
   - **Manual Region Selection**: Choose specific region
2. Click "🔍 Extract Data"
3. Wait for processing (1-5 seconds)

### Step 3: View Results
1. Go to "📊 Data Viewer" tab
2. Select your file
3. See extracted table, row/column counts
4. View raw OCR text

### Step 4: Validate Data
1. Go to "✅ Validation" tab
2. Select file to validate
3. Click "🔍 Validate Data"
4. Review:
   - ✅ Data quality status
   - ⚠️ Warnings (if any)
   - ❌ Errors (if any)

### Step 5: Get Insights
1. Go to "📈 Insights" tab
2. Click "📊 Generate Insights"
3. View:
   - Statistics (rows, columns)
   - Top categories (bar chart)
   - Trends (if available)
   - Data quality score (gauge)
   - Anomalies (if detected)

### Step 6: Export Data
1. Go to "📥 Download Results"
2. Select file
3. Choose formats (CSV, XLSX, JSON)
4. Click "⬇️ Export Data"
5. Files saved to `backend/exports/`

---

## 📊 Example: Processing a Financial Report

### Sample Report Image
Imagine a report with:
- A data table (sales by quarter)
- A bar chart (revenue trend)
- A pie chart (market share)

### Processing Steps

1. **Upload** the PDF/image page
2. **Auto-detection** finds:
   - Table with 4 rows × 5 columns
   - Bar chart with 12 data points
   - Pie chart with 8 segments

3. **Extract & Validate**:
   - Table: 100% complete, no anomalies
   - Quality Score: 95%

4. **Generate Summary**:
   - Total Revenue: $1.2M
   - Best Quarter: Q3 (+15% trend)
   - Market Leader: Category A (42%)

5. **Export** to CSV/XLSX/JSON with metadata

---

## 🚀 Running Different Scenarios

### Scenario 1: Single Table Extraction
```
1. Upload image with table
2. Auto-detection mode
3. Check "Data Viewer" tab
4. Click "Validate Data"
5. Export to CSV
```

### Scenario 2: Multi-Chart Analysis
```
1. Upload image with multiple charts
2. Auto-detection mode
3. Check detected charts in results
4. Go to "Insights" for trend analysis
5. Export all data
```

### Scenario 3: Batch Processing
```
1. Upload multiple images (5+)
2. System processes all automatically
3. View results per file in "Data Viewer"
4. Validate each file separately
5. Bulk export all results
```

---

## 🔧 Common Tasks

### Change Backend Port
```bash
# Instead of:
uvicorn app.main:app --port 8001

# Use:
uvicorn app.main:app --port 9000

# Update frontend to match:
# In streamlit_enhanced_app.py, change:
# BACKEND_URL = "http://localhost:9000"
```

### Enable Debug Logging
```bash
# Backend
uvicorn app.main:app --reload --log-level debug

# Frontend
streamlit run streamlit_enhanced_app.py --logger.level=debug
```

### Test API Directly
```bash
# Check if backend is running
curl http://localhost:8001/

# Test image upload
curl -X POST http://localhost:8001/upload_image \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "...", "job_name": "test", "page": 1}'
```

### Clear Cached Data
```bash
# Remove extracted images and exports
rm -r backend/outputs/*
rm -r backend/exports/*
```

---

## ⚠️ Troubleshooting Quick Fixes

### Problem: Port 8001 already in use
```bash
# Find process using port 8001
netstat -ano | findstr :8001

# Kill process
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --port 8002
```

### Problem: Streamlit can't connect to backend
```bash
# Check if backend is running
curl http://localhost:8001/

# If not running, start backend first in separate terminal
# Check BACKEND_URL in streamlit_enhanced_app.py matches
```

### Problem: OCR not working
```bash
# Verify Tesseract installed
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version

# Add to PATH
$env:PATH += ";C:\Program Files\Tesseract-OCR"

# Restart both backend and frontend
```

### Problem: "No module named" errors
```bash
# Reinstall requirements
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --force-reinstall

# Or create fresh venv
rm -r .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📈 Performance Tips

### For Large Images
- Use "Manual Region Selection" to extract only needed area
- This reduces OCR time by 50-70%

### For Batch Processing
- Process 10-20 images at once (depends on file size)
- Each image: ~3-5 seconds
- Batch of 10: ~30-50 seconds total

### For Real-time Usage
- Keep small images (<5MB)
- Use PNG format for best quality
- Pre-crop images to table regions

---

## 🎓 Learning Resources

### Key Components to Understand

1. **Image Upload**
   - Converts image → Base64 → Backend → Saved with ID

2. **Table Extraction**
   - Image → Preprocessing → OCR (Tesseract) → Parsing → Structured table

3. **Chart Detection**
   - Image → Edge/contour detection → Chart type classification → Data point extraction

4. **Data Validation**
   - Check completeness, consistency, type matching
   - Detect duplicates and anomalies
   - Calculate quality score

5. **Export**
   - Table → DataFrame → CSV/XLSX/JSON with metadata

### Code Entry Points
- **Frontend**: `streamlit_enhanced_app.py` (lines 1-50 for setup)
- **Backend**: `app/main.py` (lines 1-50 for endpoints)
- **Table Logic**: `services/table_extractor.py`
- **Chart Logic**: `services/chart_extractor.py`
- **Validation**: `services/data_validator.py`

---

## 🎯 Next Steps

After successful setup:

1. ✅ Try with sample business report
2. ✅ Test all extraction modes
3. ✅ Export in all formats
4. ✅ Review validation reports
5. ✅ Customize for your use case

---

## 📞 Need Help?

### Common Issues & Solutions
See `COMPREHENSIVE_README.md` → Troubleshooting section

### Check Logs
- **Backend**: Look at terminal running uvicorn
- **Frontend**: Check Streamlit terminal
- **Files**: Check `backend/outputs/` and `backend/exports/`

### Verify Setup
```bash
# Terminal 1 - Backend
curl http://localhost:8001/

# Terminal 2 - Frontend
# Should open at http://localhost:8502

# Try uploading small test image
# Expected: Success message with image dimensions
```

---

**You're ready to go!** 🚀

Start with small test images, then scale up. Happy extracting!

---

**Version**: 2.0 | **Last Updated**: Nov 21, 2024
