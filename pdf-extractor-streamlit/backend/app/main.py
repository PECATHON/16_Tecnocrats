from __future__ import annotations

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    UploadImageRequest,
    UploadImageResponse,
    ExtractTableRequest,
    TableExtractionResult,
    DataValidationResult,
    ExportRequest,
    SummaryRequest,
)
from services.io import save_base64_image, load_image_from_path, crop_image
from services.table_extractor import extract_table_from_image
from services.preprocessor import preprocess_for_table
from services.chart_extractor import (
    detect_chart_regions,
    extract_bar_chart_data,
    extract_pie_chart_data,
    extract_line_chart_data,
)
from services.data_validator import DataValidator, sanitize_table
from services.export_service import ExportService
from services.summary_generator import SummaryGenerator


app = FastAPI(title="Intelligent PDF/Image Data Extractor")

# Allow all origins for now (you can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Intelligent PDF/Image Data Extractor running",
        "version": "2.0",
        "features": [
            "Table extraction from images",
            "Chart detection and data extraction (bar, pie, line)",
            "Data validation and quality checking",
            "Multi-format export (CSV, XLSX, JSON)",
            "Data summary and insights generation",
            "Batch PDF processing",
        ]
    }


@app.post("/upload_image", response_model=UploadImageResponse)
def upload_image(req: UploadImageRequest):
    """
    Accept base64-encoded page image, save it, and return an image_id.
    """
    try:
        image_id, img = save_base64_image(
            image_base64=req.image_base64,
            job_name=req.job_name,
            page=req.page,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode/save image: {e}")

    return UploadImageResponse(
        image_id=image_id,
        job_name=req.job_name,
        page=req.page,
        width=img.width,
        height=img.height,
    )


@app.post("/extract_table", response_model=TableExtractionResult)
async def extract_table(req: ExtractTableRequest):
    """
    Given an image_id and a bounding box, crop the image, run OCR,
    extract a table, and return structured data.
    """
    try:
        img = load_image_from_path(req.image_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Image not found: {req.image_id}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load image: {e}")

    try:
        crop = crop_image(img, req.left, req.top, req.width, req.height)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to crop image: {e}")

    try:
        # Preprocess image for better OCR
        img_cv2 = np.array(crop.convert("RGB"))
        img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_RGB2BGR)
        preprocessed = preprocess_for_table(img_cv2)
        
        # Convert back to PIL for OCR
        crop_enhanced = crop  # Original for OCR as backup
        
        # Run extraction
        result_dict = extract_table_from_image(
            crop_enhanced,
            table_csv_path=req.table_csv_path,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Table extraction failed: {e}")

    return TableExtractionResult(**result_dict)



@app.post("/detect_elements")
async def detect_elements(req: ExtractTableRequest):
    """
    Detect all extractable elements (tables, charts, text blocks) in an image region.
    """
    try:
        img = load_image_from_path(req.image_id)
        img_cv2 = np.array(img.convert("RGB"))
        img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_RGB2BGR)
        
        crop = crop_image(img, req.left, req.top, req.width, req.height)
        crop_cv2 = np.array(crop.convert("RGB"))
        crop_cv2 = cv2.cvtColor(crop_cv2, cv2.COLOR_RGB2BGR)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load/crop image: {e}")

    try:
        # Detect chart regions
        charts = detect_chart_regions(crop_cv2)
        
        # Extract data from each chart
        chart_results = []
        for chart in charts:
            chart_type = chart["type"]
            region = chart["region_img"]
            
            if chart_type == "bar_chart":
                data = extract_bar_chart_data(region)
            elif chart_type == "pie_chart":
                data = extract_pie_chart_data(region)
            elif chart_type == "line_chart":
                data = extract_line_chart_data(region)
            else:
                data = []
            
            chart_results.append({
                "type": chart_type,
                "bbox": chart["bbox"],
                "confidence": chart["confidence"],
                "data": data,
            })
        
        return {
            "tables": [],  # Could add table detection here
            "charts": chart_results,
            "text_blocks": [],  # Could add text block detection
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Element detection failed: {e}")


@app.post("/validate_data")
async def validate_data(payload: dict):
    """
    Validate extracted data for quality, consistency, and anomalies.
    """
    try:
        table = payload.get("table", [])
        
        validator = DataValidator()
        validation_result = validator.validate_table(table)
        
        return validation_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {e}")


@app.post("/export_data")
async def export_data(req: ExportRequest):
    """
    Export extracted data in multiple formats (CSV, XLSX, JSON).
    """
    try:
        sanitized_table = sanitize_table(req.table)
        
        exporter = ExportService()
        
        results = {}
        if "csv" in req.formats:
            results["csv"] = exporter.export_to_csv(
                sanitized_table,
                filename=req.filename and f"{req.filename}.csv",
                include_metadata=req.include_metadata,
            )
        
        if "xlsx" in req.formats:
            results["xlsx"] = exporter.export_to_xlsx(
                sanitized_table,
                filename=req.filename and f"{req.filename}.xlsx",
                include_metadata=req.include_metadata,
            )
        
        if "json" in req.formats:
            results["json"] = exporter.export_to_json(
                sanitized_table,
                filename=req.filename and f"{req.filename}.json",
                include_metadata=req.include_metadata,
            )
        
        return {
            "success": True,
            "exports": results,
            "row_count": len(sanitized_table),
            "column_count": len(sanitized_table[0]) if sanitized_table else 0,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")


@app.post("/generate_summary")
async def generate_summary(req: SummaryRequest):
    """
    Generate data insights and summary (trends, top categories, anomalies, quality score).
    """
    try:
        generator = SummaryGenerator(req.table)
        
        summary = {
            "statistics": generator.get_basic_statistics(),
            "top_categories": generator.get_top_categories(n=5),
        }
        
        if req.include_trends:
            summary["trends"] = generator.get_trends()
        
        if req.include_anomalies:
            summary["anomalies"] = generator.get_anomalies()
        
        summary["data_quality"] = generator.get_data_quality_score()
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {e}")


@app.post("/debug_table_detection")
async def debug_table_detection(req: ExtractTableRequest):
    """
    Debug endpoint to show OCR output and table detection steps.
    Useful for troubleshooting table detection issues.
    """
    try:
        img = load_image_from_path(req.image_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Image not found: {req.image_id}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load image: {e}")

    try:
        crop = crop_image(img, req.left, req.top, req.width, req.height)
        
        # Import OCR for debugging
        from services.ocr import run_ocr
        
        ocr_text = run_ocr(crop)
        lines = ocr_text.splitlines()
        
        return {
            "ocr_successful": bool(ocr_text and ocr_text.strip()),
            "total_characters": len(ocr_text),
            "total_lines": len(lines),
            "ocr_text": ocr_text,
            "lines": lines[:20],  # First 20 lines
            "message": "Use this to debug table detection. Check if OCR is working and what text is being extracted."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug failed: {e}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "PDF Data Extractor"}
