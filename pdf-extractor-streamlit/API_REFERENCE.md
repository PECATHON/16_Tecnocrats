# API Reference - Intelligent Data Extractor

## Base URL
```
http://localhost:8001
```

## Authentication
Currently no authentication. Can be added with JWT tokens.

## Response Format
All responses are JSON-formatted.

---

## Endpoints

### 1. Health Check
```
GET /
```

**Description**: Check if backend is running and get system info

**Response** (200 OK):
```json
{
  "status": "ok",
  "message": "Intelligent PDF/Image Data Extractor running",
  "version": "2.0",
  "features": [
    "Table extraction from images",
    "Chart detection and data extraction (bar, pie, line)",
    "Data validation and quality checking",
    "Multi-format export (CSV, XLSX, JSON)",
    "Data summary and insights generation",
    "Batch PDF processing"
  ]
}
```

---

### 2. Upload Image
```
POST /upload_image
```

**Description**: Upload and store an image for processing

**Request** (JSON):
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "job_name": "quarterly_report",
  "page": 1
}
```

**Response** (200 OK):
```json
{
  "image_id": "outputs/quarterly_report_page_1.png",
  "job_name": "quarterly_report",
  "page": 1,
  "width": 1920,
  "height": 1080
}
```

**Error** (400 Bad Request):
```json
{
  "detail": "Failed to decode/save image: Invalid base64"
}
```

---

### 3. Extract Table
```
POST /extract_table
```

**Description**: Extract structured table data from image region

**Request** (JSON):
```json
{
  "image_id": "outputs/quarterly_report_page_1.png",
  "left": 100,
  "top": 200,
  "width": 800,
  "height": 600,
  "table_csv_path": null
}
```

**Response** (200 OK):
```json
{
  "ocr_text": "Month | Q1 | Q2 | Q3 | Q4\n...",
  "raw_table_lines": [
    "Month Q1 Q2 Q3 Q4",
    "2023 100 120 150 180"
  ],
  "headers": ["Month", "Q1", "Q2", "Q3", "Q4"],
  "rows": [
    ["2023", "100", "120", "150", "180"],
    ["2024", "110", "130", "160", "190"]
  ],
  "cleaned_table": [
    ["Month", "Q1", "Q2", "Q3", "Q4"],
    ["2023", 100.0, 120.0, 150.0, 180.0],
    ["2024", 110.0, 130.0, 160.0, 190.0]
  ],
  "csv_path": null
}
```

**Errors**:
- 404: Image not found
- 400: Failed to crop image
- 500: Table extraction failed

---

### 4. Detect Elements
```
POST /detect_elements
```

**Description**: Automatically detect all extractable elements (tables, charts, text) in image region

**Request** (JSON):
```json
{
  "image_id": "outputs/report_page_1.png",
  "left": 0,
  "top": 0,
  "width": 1920,
  "height": 1080
}
```

**Response** (200 OK):
```json
{
  "tables": [],
  "charts": [
    {
      "type": "bar_chart",
      "bbox": [100, 200, 800, 500],
      "confidence": 0.92,
      "data": [
        {"label": "Q1", "value": 100.0, "confidence": 0.85},
        {"label": "Q2", "value": 120.0, "confidence": 0.87},
        {"label": "Q3", "value": 150.0, "confidence": 0.89}
      ]
    },
    {
      "type": "pie_chart",
      "bbox": [900, 200, 400, 400],
      "confidence": 0.88,
      "data": [
        {"label": "Slice_0", "percentage": 25.0, "confidence": 0.5}
      ]
    }
  ],
  "text_blocks": []
}
```

---

### 5. Validate Data
```
POST /validate_data
```

**Description**: Validate extracted data for quality, consistency, and anomalies

**Request** (JSON):
```json
{
  "table": [
    ["Month", "Revenue", "Profit"],
    ["Jan", "100000", "25000"],
    ["Feb", "120000", "30000"],
    ["Feb", "120000", "30000"],
    ["Mar", "", "35000"]
  ]
}
```

**Response** (200 OK):
```json
{
  "is_valid": false,
  "errors": [],
  "warnings": [
    {
      "type": "duplicate_rows",
      "message": "Found 1 potential duplicate rows",
      "affected_rows": [3]
    },
    {
      "type": "some_missing_values",
      "message": "Found 1 empty cells",
      "missing_cells": [[4, 1]]
    }
  ],
  "statistics": {
    "row_count": 5,
    "column_count": 3,
    "total_cells": 15
  }
}
```

---

### 6. Export Data
```
POST /export_data
```

**Description**: Export table to multiple formats (CSV, XLSX, JSON)

**Request** (JSON):
```json
{
  "table": [
    ["Month", "Q1", "Q2", "Q3"],
    ["2023", "100", "120", "150"],
    ["2024", "110", "130", "160"]
  ],
  "formats": ["csv", "xlsx", "json"],
  "include_metadata": true,
  "filename": "sales_report_2024"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "exports": {
    "csv": "exports/sales_report_2024.csv",
    "xlsx": "exports/sales_report_2024.xlsx",
    "json": "exports/sales_report_2024.json"
  },
  "row_count": 3,
  "column_count": 4
}
```

---

### 7. Generate Summary
```
POST /generate_summary
```

**Description**: Generate insights and analytics from extracted data

**Request** (JSON):
```json
{
  "table": [
    ["Category", "Q1", "Q2", "Q3", "Q4"],
    ["North", "100", "120", "150", "180"],
    ["South", "80", "90", "110", "130"],
    ["East", "120", "130", "160", "190"],
    ["West", "60", "70", "85", "100"]
  ],
  "include_trends": true,
  "include_anomalies": true
}
```

**Response** (200 OK):
```json
{
  "statistics": {
    "row_count": 5,
    "column_count": 5,
    "columns": ["Category", "Q1", "Q2", "Q3", "Q4"],
    "numeric_summary": {
      "Q1": {"min": 60.0, "max": 120.0, "mean": 90.0, "median": 80.0, "sum": 360.0},
      "Q2": {"min": 70.0, "max": 130.0, "mean": 102.0, "median": 90.0, "sum": 410.0}
    }
  },
  "top_categories": [
    {"category": "East", "count": 1},
    {"category": "North", "count": 1},
    {"category": "South", "count": 1},
    {"category": "West", "count": 1}
  ],
  "trends": {
    "x_column": "Category",
    "y_column": "Q1",
    "trend": "increasing",
    "slope": 5.2,
    "r_squared": 0.87
  },
  "data_quality": {
    "overall_score": 95.5,
    "breakdown": {
      "Completeness": 100.0,
      "Consistency": 100.0,
      "Uniqueness": 100.0
    }
  },
  "anomalies": []
}
```

---

### 8. Health Check (Monitoring)
```
GET /health
```

**Description**: Simple health check for monitoring/load balancing

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "PDF Data Extractor"
}
```

---

## Error Handling

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (invalid input)
- **404**: Not Found (image not found)
- **422**: Validation Error (invalid JSON structure)
- **500**: Server Error (processing failed)

### Error Response Format
```json
{
  "detail": "Description of what went wrong"
}
```

### Example Error Responses

**Invalid JSON (400)**:
```json
{
  "detail": "Failed to decode/save image: Invalid base64"
}
```

**Image Not Found (404)**:
```json
{
  "detail": "Image not found: outputs/nonexistent.png"
}
```

**Processing Error (500)**:
```json
{
  "detail": "Table extraction failed: OCR engine error"
}
```

---

## Rate Limiting

Currently unlimited, but can be configured with:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/extract_table")
@limiter.limit("100/minute")
async def extract_table(req: ExtractTableRequest):
    ...
```

---

## Request/Response Sizes

| Operation | Max Size | Typical Time |
|-----------|----------|-------------|
| Image (base64) | 50MB | 100-500ms |
| Table data | 10,000 rows | 50-200ms |
| Batch request | 100 images | 2-5 min |

---

## Authentication (Future)

Plan to add JWT-based authentication:

```python
# Example future request with auth
POST /extract_table
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "image_id": "...",
  ...
}
```

---

## CORS Policy

Currently allows all origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Can be restricted to specific domains:
```python
allow_origins=["http://localhost:8502", "https://myapp.com"]
```

---

## Data Models

### Chart Region
```python
{
    "type": str,           # pie_chart, bar_chart, line_chart
    "bbox": tuple,         # (x, y, width, height)
    "confidence": float,   # 0.0-1.0
    "data": list          # Chart data points
}
```

### Validation Result
```python
{
    "is_valid": bool,                    # Overall validity
    "errors": list,                      # Critical errors
    "warnings": list,                    # Non-critical issues
    "statistics": {
        "row_count": int,
        "column_count": int,
        "total_cells": int
    }
}
```

### Export Result
```python
{
    "success": bool,                     # Operation status
    "exports": dict,                     # Format → file path mapping
    "row_count": int,                    # Data statistics
    "column_count": int
}
```

---

## Usage Examples

### Python/Requests
```python
import requests
import json

BASE_URL = "http://localhost:8001"

# Upload image
response = requests.post(
    f"{BASE_URL}/upload_image",
    json={
        "image_base64": "iVBORw0KGgo...",
        "job_name": "test",
        "page": 1
    }
)
image_id = response.json()["image_id"]

# Extract table
response = requests.post(
    f"{BASE_URL}/extract_table",
    json={
        "image_id": image_id,
        "left": 0, "top": 0,
        "width": 1920, "height": 1080
    }
)
result = response.json()
```

### cURL
```bash
# Upload
curl -X POST http://localhost:8001/upload_image \
  -H "Content-Type: application/json" \
  -d @payload.json

# Extract
curl -X POST http://localhost:8001/extract_table \
  -H "Content-Type: application/json" \
  -d @extract.json

# Validate
curl -X POST http://localhost:8001/validate_data \
  -H "Content-Type: application/json" \
  -d @data.json
```

### JavaScript/Fetch
```javascript
const BASE_URL = "http://localhost:8001";

// Upload image
const uploadResponse = await fetch(`${BASE_URL}/upload_image`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        image_base64: imageB64,
        job_name: 'test',
        page: 1
    })
});
const uploadData = await uploadResponse.json();

// Extract table
const extractResponse = await fetch(`${BASE_URL}/extract_table`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        image_id: uploadData.image_id,
        left: 0, top: 0,
        width: 1920, height: 1080
    })
});
const result = await extractResponse.json();
```

---

## Troubleshooting API Issues

### Issue: 404 Image Not Found
**Cause**: Image ID incorrect or file deleted
**Solution**: Check image_id from upload response

### Issue: 500 Server Error
**Cause**: OCR failure or processing error
**Solution**: Check backend logs, ensure image quality

### Issue: 422 Validation Error
**Cause**: Invalid request JSON structure
**Solution**: Verify request matches schema

### Issue: Slow Response
**Cause**: Large image or complex chart
**Solution**: Use manual region selection, crop image first

---

## Testing API

### Using Postman
1. Create new collection
2. Add requests for each endpoint
3. Set BASE_URL variable: `{{BASE_URL}}/extract_table`
4. Use pre-request scripts for image encoding

### Using Python unittest
```python
import unittest
import requests

class TestAPI(unittest.TestCase):
    def test_upload_image(self):
        resp = requests.post(
            "http://localhost:8001/upload_image",
            json={...}
        )
        self.assertEqual(resp.status_code, 200)
```

---

**Last Updated**: Nov 21, 2024 | **Version**: 2.0
