# backend/app/services/pdf_loader.py
import fitz  # PyMuPDF
from PIL import Image
import io

def render_pdf_pages(pdf_bytes: bytes, zoom: float = 2.0):
    """
    Return list of PIL Images for each page
    zoom: scaling factor for higher-res rasterization
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    mat = fitz.Matrix(zoom, zoom)
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(img)
    return pages
