# backend/services/export_service.py
"""
Multi-format export service for extracted data.
Supports CSV, XLSX, JSON with metadata.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class ExportService:
    """Export extracted data in multiple formats."""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(
        self,
        table: List[List[Any]],
        filename: str = None,
        include_metadata: bool = False,
    ) -> str:
        """
        Export table to CSV format.
        
        Args:
            table: List of rows
            filename: Output filename (auto-generated if None)
            include_metadata: Whether to add metadata header
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        # Convert to DataFrame
        df = pd.DataFrame(table)
        
        # Add metadata as header comments if requested
        if include_metadata:
            with open(output_path, 'w') as f:
                f.write(f"# Exported at: {datetime.now()}\n")
                f.write(f"# Rows: {len(table)}\n")
                f.write(f"# Columns: {len(table[0]) if table else 0}\n")
                df.to_csv(f, index=False)
        else:
            df.to_csv(output_path, index=False)
        
        return str(output_path)
    
    def export_to_xlsx(
        self,
        table: List[List[Any]],
        filename: str = None,
        include_metadata: bool = True,
    ) -> str:
        """
        Export table to XLSX format with formatting.
        
        Args:
            table: List of rows
            filename: Output filename (auto-generated if None)
            include_metadata: Whether to add metadata sheet
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.xlsx"
        
        output_path = self.output_dir / filename
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Data sheet
            df = pd.DataFrame(table)
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Metadata sheet
            if include_metadata:
                metadata = {
                    'Metric': [
                        'Export Date',
                        'Total Rows',
                        'Total Columns',
                        'Data Types',
                        'Missing Values',
                    ],
                    'Value': [
                        datetime.now().isoformat(),
                        len(table),
                        len(table[0]) if table else 0,
                        str(df.dtypes.to_dict()),
                        str(df.isnull().sum().to_dict()),
                    ]
                }
                metadata_df = pd.DataFrame(metadata)
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        return str(output_path)
    
    def export_to_json(
        self,
        table: List[List[Any]],
        filename: str = None,
        include_metadata: bool = True,
    ) -> str:
        """
        Export table to JSON format.
        
        Args:
            table: List of rows
            filename: Output filename (auto-generated if None)
            include_metadata: Whether to add metadata
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        # Check if first row might be headers
        if table and len(table) > 1:
            first_row = table[0]
            is_header = all(isinstance(cell, str) for cell in first_row)
            
            if is_header:
                headers = first_row
                data_rows = table[1:]
                
                # Convert to list of dicts
                json_data = []
                for row in data_rows:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        row_dict[header] = row[i] if i < len(row) else None
                    json_data.append(row_dict)
            else:
                json_data = [{"row": i, "values": row} for i, row in enumerate(table)]
        else:
            json_data = table
        
        export_obj = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "record_count": len(json_data),
            },
            "data": json_data,
        } if include_metadata else {"data": json_data}
        
        with open(output_path, 'w') as f:
            json.dump(export_obj, f, indent=2, default=str)
        
        return str(output_path)
    
    def export_to_all_formats(
        self,
        table: List[List[Any]],
        base_filename: str = None,
        include_metadata: bool = True,
    ) -> Dict[str, str]:
        """
        Export table to all supported formats.
        
        Args:
            table: List of rows
            base_filename: Base filename (without extension)
            include_metadata: Whether to include metadata
            
        Returns:
            Dict mapping format to file path
        """
        if not base_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"export_{timestamp}"
        
        results = {}
        
        results['csv'] = self.export_to_csv(
            table,
            f"{base_filename}.csv",
            include_metadata
        )
        
        results['xlsx'] = self.export_to_xlsx(
            table,
            f"{base_filename}.xlsx",
            include_metadata
        )
        
        results['json'] = self.export_to_json(
            table,
            f"{base_filename}.json",
            include_metadata
        )
        
        return results


def create_manifest(
    export_paths: Dict[str, str],
    metadata: Dict[str, Any] = None,
) -> str:
    """
    Create a manifest file listing all exports with metadata.
    
    Args:
        export_paths: Dict mapping format to file path
        metadata: Additional metadata to include
        
    Returns:
        Path to manifest file
    """
    manifest = {
        "created_at": datetime.now().isoformat(),
        "exports": export_paths,
    }
    
    if metadata:
        manifest["metadata"] = metadata
    
    manifest_path = Path("exports") / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, default=str)
    
    return str(manifest_path)
