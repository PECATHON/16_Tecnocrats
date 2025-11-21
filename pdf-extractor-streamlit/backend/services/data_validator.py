# backend/services/data_validator.py
"""
Data validation and error detection for extracted data.
Detects anomalies, duplicates, missing values, and structural inconsistencies.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
import numpy as np


class DataValidator:
    """Validates extracted data for quality and consistency."""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def validate_table(self, table: List[List[Any]]) -> Dict[str, Any]:
        """
        Comprehensive validation of extracted table data.
        
        Args:
            table: List of rows, each row is a list of values
            
        Returns:
            Dict with validation results including errors, warnings, and fixes applied
        """
        self.errors = []
        self.warnings = []
        
        if not table:
            self.errors.append({"type": "empty_table", "message": "Table is empty"})
            return self._format_result(table)
        
        # Run all validation checks
        self._check_structural_integrity(table)
        self._check_for_duplicates(table)
        self._check_for_missing_values(table)
        self._check_data_types(table)
        self._check_column_consistency(table)
        
        return self._format_result(table)
    
    def _check_structural_integrity(self, table: List[List[Any]]) -> None:
        """Check for consistent row/column structure."""
        if not table:
            return
        
        col_counts = [len(row) for row in table]
        min_cols = min(col_counts)
        max_cols = max(col_counts)
        
        if min_cols != max_cols:
            self.warnings.append({
                "type": "inconsistent_columns",
                "message": f"Row column count varies: {min_cols} to {max_cols}",
                "affected_rows": [i for i, count in enumerate(col_counts) if count != max_cols],
            })
    
    def _check_for_duplicates(self, table: List[List[Any]]) -> None:
        """Detect duplicate rows."""
        if len(table) < 2:
            return
        
        seen_rows: Set[str] = set()
        duplicates = []
        
        for idx, row in enumerate(table):
            row_str = str(row)
            if row_str in seen_rows:
                duplicates.append(idx)
            seen_rows.add(row_str)
        
        if duplicates:
            self.warnings.append({
                "type": "duplicate_rows",
                "message": f"Found {len(duplicates)} potential duplicate rows",
                "affected_rows": duplicates,
            })
    
    def _check_for_missing_values(self, table: List[List[Any]]) -> None:
        """Detect missing or empty values."""
        if not table:
            return
        
        missing_cells = []
        
        for row_idx, row in enumerate(table):
            for col_idx, cell in enumerate(row):
                if cell is None or cell == "" or str(cell).strip() == "":
                    missing_cells.append((row_idx, col_idx))
        
        if missing_cells:
            missing_percentage = (len(missing_cells) / (len(table) * len(table[0]))) * 100
            
            if missing_percentage > 20:
                self.warnings.append({
                    "type": "high_missing_values",
                    "message": f"Missing values: {missing_percentage:.1f}% of cells",
                    "missing_count": len(missing_cells),
                })
            elif missing_cells:
                self.warnings.append({
                    "type": "some_missing_values",
                    "message": f"Found {len(missing_cells)} empty cells",
                    "missing_cells": missing_cells[:10],  # Show first 10
                })
    
    def _check_data_types(self, table: List[List[Any]]) -> None:
        """Detect mixed data types in columns."""
        if not table or len(table) < 2:
            return
        
        # Infer types for each column
        num_cols = len(table[0])
        col_types: Dict[int, Set[str]] = {i: set() for i in range(num_cols)}
        
        for row in table:
            for col_idx, cell in enumerate(row):
                if col_idx < len(row):
                    cell_type = self._infer_type(cell)
                    col_types[col_idx].add(cell_type)
        
        # Check for mixed types
        for col_idx, types in col_types.items():
            if len(types) > 2:  # Allow 1-2 types per column
                self.warnings.append({
                    "type": "mixed_data_types",
                    "message": f"Column {col_idx} has mixed types: {types}",
                    "column": col_idx,
                })
    
    def _check_column_consistency(self, table: List[List[Any]]) -> None:
        """Check for inconsistent column naming/header."""
        if not table or len(table) < 1:
            return
        
        # Check first row for potential headers
        first_row = table[0]
        header_score = sum(1 for cell in first_row if isinstance(cell, str) and len(str(cell)) > 2)
        
        if header_score == len(first_row):
            self.warnings.append({
                "type": "likely_header_row",
                "message": "First row appears to be headers",
            })
    
    @staticmethod
    def _infer_type(value: Any) -> str:
        """Infer the data type of a value."""
        if value is None or value == "":
            return "empty"
        
        s = str(value).strip()
        
        # Try numeric
        try:
            float(s)
            return "numeric"
        except ValueError:
            pass
        
        # Check for common patterns
        if s.lower() in ("true", "false", "yes", "no"):
            return "boolean"
        
        if len(s) <= 3 and s.upper() == s:
            return "category"
        
        return "text"
    
    def _format_result(self, table: List[List[Any]]) -> Dict[str, Any]:
        """Format validation result."""
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": {
                "row_count": len(table),
                "column_count": len(table[0]) if table else 0,
                "total_cells": sum(len(row) for row in table),
            }
        }


def compare_tables(table1: List[List[Any]], table2: List[List[Any]]) -> Dict[str, Any]:
    """
    Compare two tables for data consistency and alignment.
    
    Returns:
        Dict with comparison results
    """
    result = {
        "identical": table1 == table2,
        "row_count_match": len(table1) == len(table2),
        "column_count_match": (len(table1[0]) if table1 else 0) == (len(table2[0]) if table2 else 0),
        "differences": [],
    }
    
    if table1 == table2:
        return result
    
    # Find cell-level differences
    min_rows = min(len(table1), len(table2))
    min_cols = min(len(table1[0]) if table1 else 0, len(table2[0]) if table2 else 0)
    
    for i in range(min_rows):
        for j in range(min_cols):
            if table1[i][j] != table2[i][j]:
                result["differences"].append({
                    "row": i,
                    "col": j,
                    "value1": table1[i][j],
                    "value2": table2[i][j],
                })
    
    return result


def sanitize_table(table: List[List[Any]]) -> List[List[Any]]:
    """
    Clean and sanitize table data.
    - Remove completely empty rows
    - Trim whitespace
    - Normalize empty values
    """
    if not table:
        return []
    
    sanitized = []
    
    for row in table:
        # Remove None and empty strings
        cleaned_row = []
        for cell in row:
            if cell is None:
                cleaned_row.append(None)
            elif isinstance(cell, str):
                stripped = cell.strip()
                cleaned_row.append(stripped if stripped else None)
            else:
                cleaned_row.append(cell)
        
        # Skip completely empty rows
        if any(cell is not None for cell in cleaned_row):
            sanitized.append(cleaned_row)
    
    return sanitized


def detect_table_headers(table: List[List[Any]]) -> Tuple[bool, int]:
    """
    Detect if the table has headers and return header row index.
    
    Returns:
        (has_headers: bool, header_index: int)
    """
    if not table or len(table) < 2:
        return False, -1
    
    # Score first row as potential header
    first_row = table[0]
    text_score = sum(1 for cell in first_row if isinstance(cell, str) and len(str(cell)) > 2)
    
    if text_score >= len(first_row) * 0.7:  # 70% text content
        return True, 0
    
    return False, -1
