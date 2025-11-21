# Utility functions for the Streamlit app
# utils.py
import fitz
from PIL import Image
import io
import os
import pytesseract
import pandas as pd
from datetime import datetime
import json

# If Tesseract is installed in non-standard path (Windows), set it here:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def render_pdf_pages(pdf_bytes):
    """Render PDF bytes to a list of PIL Images using PyMuPDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        mat = fitz.Matrix(2, 2)  # zoom factor (higher -> better resolution)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(img)
    return pages

def crop_image(pil_img, rect):
    """Crop a PIL image using rectangle dict: left, top, width, height."""
    left = max(0, rect["left"])
    top = max(0, rect["top"])
    right = left + rect["width"]
    bottom = top + rect["height"]
    return pil_img.crop((left, top, right, bottom))

def run_local_ocr(pil_img, lang="eng"):
    """Run pytesseract on a PIL image and return extracted text."""
    # convert to RGB if necessary
    img = pil_img.convert("RGB")
    text = pytesseract.image_to_string(img, lang=lang)
    return text.strip()

def save_outputs(job_name, df, results, base_dir="../outputs"):
    """Save CSV/XLSX/JSON and save cropped images to an outputs folder; return output dir."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    odir = os.path.join(base_dir, f"{job_name}_{timestamp}")
    os.makedirs(odir, exist_ok=True)

    # Save DataFrame
    csv_path = os.path.join(odir, "extracted.csv")
    xlsx_path = os.path.join(odir, "extracted.xlsx")
    json_path = os.path.join(odir, "extracted.json")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    # Save JSON that includes images as base64 plus metadata
    payload = []
    for r in results:
        img_b64 = None
        if "image_bytes" in r:
            img_b64 = base64_encode_bytes(r["image_bytes"])
        payload.append({
            "page": r["page"],
            "region_id": r["region_id"],
            "coords": r["coords"],
            "ocr_text": r.get("ocr_text", ""),
            "image_base64": img_b64
        })
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Save each cropped image
    for r in results:
        if "image_bytes" in r:
            fname = os.path.join(odir, f"page_{r['page']}_region_{r['region_id']}.png")
            with open(fname, "wb") as f:
                f.write(r["image_bytes"])

    return os.path.abspath(odir)

def base64_encode_bytes(b: bytes) -> str:
    import base64
    return base64.b64encode(b).decode("utf-8")
