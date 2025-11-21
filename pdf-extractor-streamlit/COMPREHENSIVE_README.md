# Intelligent Data Extraction from Complex Business Reports

## 🎯 Overview

This is an AI-powered document understanding solution that intelligently extracts structured data from business reports, PDFs, and complex document images. It can detect and extract tables, charts, and text, converting them into clean, machine-readable formats (CSV, XLSX, JSON).

### ✨ Key Features

1. **Intelligent Element Detection**
   - Automatic detection of tables, charts (bar, pie, line), and text blocks
   - Smart bounding box identification
   - Support for merged cells and complex layouts

2. **Multi-Format Chart Extraction**
   - Bar charts: Extract values and labels
   - Pie charts: Extract segments and percentages
   - Line charts: Extract data points and trends
   - Legend extraction and color mapping

3. **Advanced Data Validation**
   - Detect duplicates and missing values
   - Identify data type inconsistencies
   - Flag structural anomalies
   - Quantifiable data quality scoring

4. **Multi-Format Export**
   - CSV with metadata headers
   - XLSX with separate metadata sheet
   - JSON with structured formatting
   - Auto-generated timestamps and metadata

5. **Data Insights & Analytics**
   - Trend detection and analysis
   - Top category identification
   - Statistical summaries (min, max, mean, median)
   - Anomaly detection using IQR method
   - Data quality scoring (0-100)

6. **Batch Processing**
   - Process multiple PDFs/images simultaneously
   - Concurrent processing support
   - Batch result aggregation
   - Error handling and logging

7. **Multi-Page PDF Support**
   - Extract all pages as images
   - Per-page processing
   - Metadata collection per page
   - Unified result aggregation

## 📦 System Architecture

```
pdf-extractor-streamlit/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI routes and endpoints
│   │   └── models.py               # Pydantic models for request/response
│   ├── services/
│   │   ├── chart_extractor.py      # Chart detection and data extraction
│   │   ├── data_validator.py       # Data quality and validation
│   │   ├── export_service.py       # Multi-format export
│   │   ├── pdf_processor.py        # Multi-page PDF handling
│   │   ├── summary_generator.py    # Insights and analytics
│   │   ├── table_extractor.py      # Table extraction from OCR
│   │   ├── ocr_engine.py           # Tesseract OCR integration
│   │   ├── preprocessor.py         # Image preprocessing
│   │   ├── pdf_loader.py           # PDF rendering
│   │   └── io.py                   # File I/O operations
│   └── requirements.txt
├── frontend/
│   ├── streamlit_enhanced_app.py   # Enhanced dashboard UI
│   ├── streamlit_app.py            # Original UI (legacy)
│   └── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Tesseract OCR (`C:\Program Files\Tesseract-OCR\tesseract.exe` on Windows)

### Installation

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows
   pip install -r requirements.txt
   ```

3. **Set Tesseract Path (Windows)**
   ```powershell
   $env:PATH += ";C:\Program Files\Tesseract-OCR"
   ```

### Running the Application

1. **Start Backend** (from backend directory):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Start Frontend** (from frontend directory):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   streamlit run streamlit_enhanced_app.py --server.port 8502
   ```

3. **Access Dashboard**
   - Open browser: `http://localhost:8502`

## 📡 API Endpoints

### Core Endpoints

#### 1. Upload Image
```
POST /upload_image
```
- **Request**: Base64 encoded image, job name, page number
- **Response**: Image ID, dimensions
- **Purpose**: Save image to backend for processing

#### 2. Extract Table
```
POST /extract_table
```
- **Request**: Image ID, bounding box coordinates
- **Response**: OCR text, raw/cleaned table, CSV path
- **Purpose**: Extract structured table data

#### 3. Detect Elements
```
POST /detect_elements
```
- **Request**: Image ID, region bbox
- **Response**: Tables, charts (with data), text blocks
- **Purpose**: Auto-detect all extractable elements

#### 4. Validate Data
```
POST /validate_data
```
- **Request**: Table data
- **Response**: Validation errors, warnings, statistics
- **Purpose**: Check data quality and consistency

#### 5. Export Data
```
POST /export_data
```
- **Request**: Table, export formats (csv/xlsx/json), filename
- **Response**: File paths for each format
- **Purpose**: Export in multiple formats with metadata

#### 6. Generate Summary
```
POST /generate_summary
```
- **Request**: Table data, include_trends, include_anomalies flags
- **Response**: Statistics, trends, anomalies, quality score
- **Purpose**: Generate data insights

## 🔧 Services Documentation

### Chart Extractor (`services/chart_extractor.py`)
Detects and extracts data from visual elements:
- **detect_chart_regions()**: Identifies chart areas
- **extract_bar_chart_data()**: Extracts bar values and labels
- **extract_pie_chart_data()**: Extracts pie segments
- **extract_line_chart_data()**: Extracts line data points
- **extract_chart_legend()**: Extracts color mapping

### Data Validator (`services/data_validator.py`)
Comprehensive data quality checking:
- **validate_table()**: Full validation suite
- **_check_structural_integrity()**: Row/column consistency
- **_check_for_duplicates()**: Duplicate detection
- **_check_for_missing_values()**: Null/empty detection
- **_check_data_types()**: Type consistency
- **sanitize_table()**: Clean and normalize data

### Export Service (`services/export_service.py`)
Multi-format export with metadata:
- **export_to_csv()**: CSV with optional headers
- **export_to_xlsx()**: Excel with metadata sheet
- **export_to_json()**: Structured JSON
- **export_to_all_formats()**: Batch export
- **create_manifest()**: Export manifest file

### PDF Processor (`services/pdf_processor.py`)
Multi-page PDF handling:
- **extract_page_image()**: Render single page
- **extract_all_pages_as_images()**: Batch page extraction
- **get_page_metadata()**: Page information
- **process_batch_pdfs()**: Concurrent PDF processing

### Summary Generator (`services/summary_generator.py`)
Data insights and analytics:
- **get_basic_statistics()**: Rows, columns, numeric summaries
- **get_top_categories()**: Top N values
- **get_trends()**: Linear trend analysis
- **get_data_quality_score()**: Quality metrics
- **get_anomalies()**: Outlier detection (IQR method)

## 📊 Data Quality Metrics

### Quality Score Components
- **Completeness**: % of non-null cells (0-100)
- **Consistency**: % of columns with single data type (0-100)
- **Uniqueness**: % of unique rows (0-100)
- **Overall**: Average of above metrics

### Anomaly Detection
Uses Interquartile Range (IQR) method for numeric columns:
- Q1 (25th percentile)
- Q3 (75th percentile)
- IQR = Q3 - Q1
- Outliers: values < Q1-1.5×IQR or > Q3+1.5×IQR

## 🎨 Frontend Features

### Dashboard Tabs

1. **📤 Upload & Extract**
   - File upload (multi-file support)
   - Auto-detection or manual region selection
   - Real-time progress tracking
   - Element detection results

2. **📊 Data Viewer**
   - Interactive data table display
   - Row/column/cell statistics
   - Raw OCR text viewing

3. **✅ Validation**
   - Data quality checks
   - Error and warning display
   - Detailed validation report

4. **📈 Insights**
   - Statistical summaries
   - Top category charts
   - Trend analysis
   - Data quality gauge
   - Anomaly alerts

5. **📥 Download**
   - Multi-format export
   - Batch download
   - Metadata inclusion

## 📋 Example Workflows

### Workflow 1: Single Table Extraction
```
1. Upload image with table
2. System auto-detects table region
3. Performs OCR and structure recognition
4. Validates extracted data
5. Export to CSV/XLSX/JSON
6. View quality metrics
```

### Workflow 2: Multi-Chart Analysis
```
1. Upload image with multiple charts
2. Auto-detect chart regions (bar, pie, line)
3. Extract values from each chart
4. Combine into unified dataset
5. Generate trend analysis
6. Export with metadata
```

### Workflow 3: Batch PDF Processing
```
1. Upload multiple PDFs
2. Extract all pages as images
3. Process each page independently
4. Aggregate results
5. Validate combined dataset
6. Export all results
7. Generate batch report
```

## 🔍 Supported File Types

| Format | Support | Notes |
|--------|---------|-------|
| PNG | ✅ | Recommended for best quality |
| JPG/JPEG | ✅ | Suitable for photographs |
| PDF | ✅ | Multi-page support |
| TIFF | ✅ | Scanned documents |
| GIF | ⚠️ | Limited support |

## 📤 Export Formats

### CSV
```
# Exported at: 2024-01-15 10:30:45
# Rows: 10
# Columns: 5
Column1,Column2,Column3,Column4,Column5
...
```

### XLSX
- Data sheet with formatted table
- Metadata sheet with quality metrics
- Automatic column width adjustment

### JSON
```json
{
  "metadata": {
    "exported_at": "2024-01-15T10:30:45",
    "record_count": 10
  },
  "data": [
    {"Column1": "value1", "Column2": "value2", ...},
    ...
  ]
}
```

## 🛠️ Advanced Configuration

### Environment Variables
```bash
# Backend
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
OCR_LANG=eng
OUTPUT_DIR=outputs

# Frontend
BACKEND_URL=http://localhost:8001
```

### Backend Configuration (main.py)
- CORS origins
- Upload limits
- Timeout settings
- OCR parameters

### Frontend Configuration (streamlit_enhanced_app.py)
- Page layout
- Export formats
- Validation rules
- Visualization options

## 🐛 Troubleshooting

### Issue: "No module named 'pytesseract'"
**Solution**: Install pytesseract and ensure Tesseract is in system PATH
```bash
pip install pytesseract
$env:PATH += ";C:\Program Files\Tesseract-OCR"
```

### Issue: "Chart detection returns empty"
**Solution**: 
- Ensure image quality is sufficient
- Check chart has clear boundaries
- Verify image contrast

### Issue: "ModuleNotFoundError: No module named 'fitz'"
**Solution**: Install PyMuPDF
```bash
pip install PyMuPDF
```

### Issue: Backend port already in use
**Solution**: Change port or kill existing process
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

## 📚 Dependencies

### Backend
- fastapi
- uvicorn
- pydantic
- pillow
- opencv-python
- pandas
- numpy
- pytesseract
- PyMuPDF
- openpyxl

### Frontend
- streamlit
- requests
- pandas
- pillow
- plotly

## 📈 Performance Metrics

| Operation | Typical Time | Scalability |
|-----------|-------------|------------|
| Image upload | 100-500ms | Per image |
| Table extraction | 1-5s | Image size dependent |
| Chart detection | 2-8s | Complexity dependent |
| Data validation | 50-200ms | Row count dependent |
| PDF processing | 10-60s | Page count dependent |
| Batch (10 PDFs) | 2-5min | Parallel processing |

## 🔐 Security Considerations

1. **File Upload**
   - Validate file types
   - Limit file size
   - Scan for malicious content

2. **Data Handling**
   - Encrypt sensitive data
   - Implement access controls
   - Regular backups

3. **API Security**
   - Rate limiting
   - Input validation
   - CORS restrictions

## 🎓 Future Enhancements

- [ ] Machine learning for improved chart detection
- [ ] Handwriting recognition
- [ ] Table structure reconstruction (merged cells)
- [ ] Real-time collaborative editing
- [ ] Advanced anomaly detection (ML-based)
- [ ] Natural language querying
- [ ] API rate limiting
- [ ] User authentication
- [ ] Cloud storage integration
- [ ] WebSocket support for real-time processing

## 📞 Support & Contributions

For issues, questions, or contributions:
1. Check troubleshooting section
2. Review API documentation
3. Check backend logs
4. Enable debug mode in Streamlit

## 📄 License

This project is provided as-is for educational and commercial use.

---

**Last Updated**: November 21, 2024
**Version**: 2.0 (Enhanced)
