from __future__ import annotations

from typing import List, Dict, Any, Optional
import csv
import io
import re

from PIL import Image
import cv2
import numpy as np

from .ocr import run_ocr
from .io import save_table_csv


def _has_digit(s: str) -> bool:
    return any(ch.isdigit() for ch in s)


def _select_table_block(lines: List[str]) -> List[str]:
    """
    Heuristic to find table content:
    - More lenient: collect any lines with mixed alphanumeric content
    - Tries to find header row and data rows
    - Returns non-empty blocks with structure
    """
    cleaned = [ln.strip() for ln in lines if ln.strip()]
    
    if not cleaned:
        return []
    
    # Remove lines that are clearly not table content
    filtered = []
    for ln in cleaned:
        lower = ln.lower()
        # Skip obvious non-table lines
        if lower.startswith(("page", "source:", "note:", "©", "™")):
            continue
        # Skip lines that are too short (likely headers or noise)
        if len(ln) < 2:
            continue
        filtered.append(ln)
    
    if not filtered:
        return []
    
    # Look for the start of table data
    # Prefer lines with multiple words/tokens (likely headers or first rows)
    table_start = 0
    for i, ln in enumerate(filtered):
        tokens = ln.split()
        if len(tokens) >= 2:  # At least 2 tokens suggests structured data
            table_start = i
            break
    
    # Collect consecutive lines that look like table rows
    # (have similar token structure or contain digits/numbers)
    block = []
    if table_start < len(filtered):
        baseline_tokens = len(filtered[table_start].split())
        
        for ln in filtered[table_start:]:
            tokens = ln.split()
            if not tokens:
                continue
            
            # Accept lines that:
            # 1. Have similar number of tokens as baseline (±2)
            # 2. OR contain any digits (likely data rows)
            # 3. OR are short but have numbers (data values)
            token_match = abs(len(tokens) - baseline_tokens) <= 2
            has_numbers = any(c.isdigit() for c in ln)
            
            if token_match or has_numbers or len(tokens) >= 2:
                block.append(ln)
            elif block:  # Stop if we hit a non-matching line after collecting some rows
                if len(block) > 1:  # Only break if we have multiple rows
                    break
    
    return block if len(block) >= 1 else []


def _split_tokens(line: str) -> List[str]:
    """
    Split a line into tokens on whitespace.
    """
    return line.split()


def _parse_table_from_block(block: List[str]) -> Dict[str, Any]:
    """
    Generic parser:
    - first line -> header (skip first token if it's a year like '1999')
    - remaining lines -> rows
    - More tolerant: accept rows with varying numbers of columns
    """

    if not block:
        return {
            "raw_table_lines": [],
            "headers": [],
            "rows": [],
            "cleaned_table": [],
        }

    header_line = block[0]
    header_tokens = _split_tokens(header_line)

    # If first token is mostly digits (e.g. '1999'), drop it
    if header_tokens and header_tokens[0].isdigit():
        header_tokens = header_tokens[1:]

    # If still empty, use generic column names
    if not header_tokens:
        header_tokens = [f"Column_{i+1}" for i in range(5)]  # Default 5 columns
    
    headers = header_tokens

    data_rows: List[List[str]] = []
    for ln in block[1:]:
        tokens = _split_tokens(ln)
        if len(tokens) < 1:  # Accept even single-token rows
            continue

        row_label = tokens[0]
        values = tokens[1:] if len(tokens) > 1 else []

        # More lenient: accept ANY row with at least a label
        # (don't require numeric values)
        data_rows.append([row_label] + values)

    # Build cleaned table as list of dicts
    cleaned: List[Dict[str, Any]] = []
    for row in data_rows:
        row_label = row[0]
        values = row[1:]
        row_dict: Dict[str, Any] = {"Label": row_label}

        for i, v in enumerate(values):
            col_name = headers[i] if i < len(headers) else f"Col{i+1}"
            # try to normalize numbers
            num = _maybe_number(v)
            row_dict[col_name] = num

        cleaned.append(row_dict)

    return {
        "raw_table_lines": block,
        "headers": headers,
        "rows": data_rows,
        "cleaned_table": cleaned,
    }


def _maybe_number(s: str):
    s = s.replace(",", "")
    # sometimes OCR merges decimals: treat things like "42" that should be "4.2" manually later
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def extract_table_from_image(
    image: Image.Image,
    table_csv_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main public function:
    - run OCR with fallback
    - detect table block with multiple strategies
    - parse rows
    - optionally write CSV
    """
    # Step 1: Run OCR
    ocr_text = run_ocr(image)
    
    # Step 2: If OCR returns empty or very short text, try image-based detection
    lines = ocr_text.splitlines()
    block = _select_table_block(lines)
    
    # If no block found from OCR, try image-based detection
    if not block and ocr_text.strip():
        # OCR returned text but couldn't find table structure
        # Use all non-empty lines as potential table content
        block = [ln.strip() for ln in lines if ln.strip() and len(ln.strip()) > 3]
    
    if not block:
        # Last resort: return empty but valid response
        return {
            "ocr_text": ocr_text,
            "raw_table_lines": [],
            "headers": [],
            "rows": [],
            "cleaned_table": [],
            "csv_path": None,
            "detection_status": "no_table_found",
        }
    
    # Step 3: Parse the detected block
    parsed = _parse_table_from_block(block)
    
    result: Dict[str, Any] = {
        "ocr_text": ocr_text,
        "raw_table_lines": parsed["raw_table_lines"],
        "headers": parsed["headers"],
        "rows": parsed["rows"],
        "cleaned_table": parsed["cleaned_table"],
        "csv_path": None,
        "detection_status": "table_found" if parsed["cleaned_table"] else "no_valid_rows",
    }

    # Optional CSV saving
    if table_csv_path and parsed["cleaned_table"]:
        csv_buffer = io.StringIO()
        fieldnames = ["Label"] + parsed["headers"]
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        for row in parsed["cleaned_table"]:
            writer.writerow(row)
        csv_content = csv_buffer.getvalue()

        saved_path = save_table_csv(csv_content, table_csv_path)
        result["csv_path"] = saved_path

    return result
