from __future__ import annotations

from PIL import Image
import pytesseract
import logging

logger = logging.getLogger(__name__)


def run_ocr(img: Image.Image) -> str:
    """
    Run OCR on a PIL image and return raw text.
    Handles errors gracefully and logs issues.
    """
    try:
        # Ensure image is in RGB mode
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        text = pytesseract.image_to_string(img)
        
        if not text or not text.strip():
            logger.warning("OCR returned empty text")
            return ""
        
        return text
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract not found. Please install it and ensure it's in PATH.")
        raise Exception("Tesseract OCR not found. Please ensure Tesseract is installed.")
    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise Exception(f"OCR processing failed: {e}")

