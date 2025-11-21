from __future__ import annotations

import base64
import io
import os
from pathlib import Path
from typing import Tuple

from PIL import Image


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_base64_image(image_base64: str, job_name: str, page: int) -> Tuple[str, Image.Image]:
    """
    Decode a base64 image and save it to data/uploads/.
    Returns (image_path_str, PIL.Image).
    """
    if "," in image_base64:
        _, image_base64 = image_base64.split(",", 1)

    img_bytes = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    filename = f"{job_name}_page_{page}.png"
    image_path = UPLOAD_DIR / filename
    img.save(image_path)

    return str(image_path), img


def load_image_from_path(image_path: str) -> Image.Image:
    """
    Load an image from a given path (relative or absolute).
    """
    p = Path(image_path)
    if not p.is_absolute():
        p = BASE_DIR / image_path

    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")

    return Image.open(p).convert("RGB")


def crop_image(img: Image.Image, left: int, top: int, width: int, height: int) -> Image.Image:
    """
    Crop the image using a bounding box.
    """
    right = left + width
    bottom = top + height
    return img.crop((left, top, right, bottom))


def save_table_csv(csv_content: str, filename: str) -> str:
    """
    Save CSV text to data/outputs/ and return the path.
    """
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    return str(path)
