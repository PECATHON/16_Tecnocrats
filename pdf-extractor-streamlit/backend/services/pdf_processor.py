# backend/services/pdf_processor.py
"""
Multi-page PDF processing and batch handling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import numpy as np
from PIL import Image
import io


class PDFProcessor:
    """Process multi-page PDFs and extract content per page."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        self.doc = fitz.open(str(self.pdf_path))
        self.page_count = len(self.doc)
    
    def get_page_count(self) -> int:
        """Get total number of pages in PDF."""
        return self.page_count
    
    def extract_page_image(
        self,
        page_num: int,
        zoom: float = 2.0,
        output_format: str = "PIL",
    ) -> Image.Image | np.ndarray | str:
        """
        Extract a specific page as an image.
        
        Args:
            page_num: 0-indexed page number
            zoom: Zoom factor for rendering
            output_format: 'PIL', 'numpy', or 'base64'
            
        Returns:
            Image in requested format
        """
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Invalid page number: {page_num}")
        
        page = self.doc[page_num]
        
        # Render page to image
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        if output_format == "PIL":
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            return img.convert("RGB")
        
        elif output_format == "numpy":
            import numpy as np
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            return np.array(img)
        
        elif output_format == "base64":
            import base64
            buf = io.BytesIO()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("utf-8")
        
        return None
    
    def extract_text_from_page(self, page_num: int) -> str:
        """Extract text from a specific page."""
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Invalid page number: {page_num}")
        
        page = self.doc[page_num]
        return page.get_text()
    
    def extract_all_pages_as_images(
        self,
        zoom: float = 2.0,
        output_dir: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract all pages as images.
        
        Args:
            zoom: Zoom factor for rendering
            output_dir: Optional directory to save images
            
        Returns:
            List of dicts with page info and file paths
        """
        results = []
        
        for page_num in range(self.page_count):
            try:
                img = self.extract_page_image(page_num, zoom, "PIL")
                
                page_info = {
                    "page_num": page_num,
                    "width": img.width,
                    "height": img.height,
                    "image": img,
                }
                
                if output_dir:
                    output_path = Path(output_dir) / f"page_{page_num:04d}.png"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    img.save(output_path)
                    page_info["file_path"] = str(output_path)
                
                results.append(page_info)
            
            except Exception as e:
                results.append({
                    "page_num": page_num,
                    "error": str(e),
                })
        
        return results
    
    def get_page_metadata(self, page_num: int) -> Dict[str, Any]:
        """Get metadata for a specific page."""
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Invalid page number: {page_num}")
        
        page = self.doc[page_num]
        
        return {
            "page_num": page_num,
            "width": page.rect.width,
            "height": page.rect.height,
            "is_landscape": page.rect.width > page.rect.height,
            "text_count": len(page.get_text()),
            "image_count": len(page.get_images()),
        }
    
    def close(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()


def process_batch_pdfs(
    pdf_paths: List[str],
    processing_func,
    output_dir: str = "batch_output",
) -> Dict[str, Any]:
    """
    Process multiple PDFs with a given function.
    
    Args:
        pdf_paths: List of PDF file paths
        processing_func: Function to call for each PDF
        output_dir: Directory to save results
        
    Returns:
        Results summary
    """
    results = {
        "total_pdfs": len(pdf_paths),
        "processed": 0,
        "failed": 0,
        "details": [],
    }
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for pdf_path in pdf_paths:
        try:
            processor = PDFProcessor(pdf_path)
            
            result = processing_func(processor)
            
            results["processed"] += 1
            results["details"].append({
                "pdf": pdf_path,
                "status": "success",
                "result": result,
            })
            
            processor.close()
        
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "pdf": pdf_path,
                "status": "error",
                "error": str(e),
            })
    
    return results
