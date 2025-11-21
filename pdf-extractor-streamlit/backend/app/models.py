from __future__ import annotations

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class UploadImageRequest(BaseModel):
    image_base64: str
    job_name: str
    page: int


class UploadImageResponse(BaseModel):
    image_id: str
    job_name: str
    page: int
    width: int
    height: int


class ExtractTableRequest(BaseModel):
    image_id: str
    left: int
    top: int
    width: int
    height: int
    table_csv_path: Optional[str] = None


class TableExtractionResult(BaseModel):
    ocr_text: str
    raw_table_lines: List[str]
    headers: List[str]
    rows: List[List[str]]
    cleaned_table: List[Dict[str, Any]]
    csv_path: Optional[str] = None


class ChartRegion(BaseModel):
    type: str  # pie_chart, bar_chart, line_chart, etc.
    bbox: tuple
    confidence: float
    data: List[Dict[str, Any]]


class DetectionResult(BaseModel):
    """Result of element detection (tables, charts, etc.)"""
    tables: List[Dict[str, Any]]
    charts: List[ChartRegion]
    text_blocks: List[Dict[str, Any]]


class DataValidationResult(BaseModel):
    """Data validation and quality check result"""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    statistics: Dict[str, Any]


class ExportRequest(BaseModel):
    """Request to export extracted data"""
    table: List[List[Any]]
    formats: List[str]  # csv, xlsx, json
    include_metadata: bool = True
    filename: Optional[str] = None


class BatchProcessRequest(BaseModel):
    """Request to batch process multiple PDFs"""
    pdf_urls: List[str]
    operations: List[str]  # extract_tables, extract_charts, etc.


class SummaryRequest(BaseModel):
    """Request to generate data summary"""
    table: List[List[Any]]
    include_trends: bool = True
    include_anomalies: bool = True
