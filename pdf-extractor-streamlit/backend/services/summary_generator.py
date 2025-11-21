# backend/services/summary_generator.py
"""
Generate summaries and insights from extracted data.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Generate insights and summaries from extracted data."""
    
    def __init__(self, table: List[List[Any]]):
        self.table = table
        self.df = self._table_to_dataframe(table)
    
    @staticmethod
    def _table_to_dataframe(table: List[List[Any]]) -> pd.DataFrame:
        """Convert table to DataFrame.
        
        Handles both formats:
        - List[Dict]: List of dictionaries with column names as keys
        - List[List]: Raw 2D lists
        """
        if not table:
            return pd.DataFrame()
        
        try:
            # If first element is a dictionary, convert from dict format
            if isinstance(table[0], dict):
                return pd.DataFrame(table)
            
            # Check if first row is headers (all strings)
            if len(table) > 1 and all(isinstance(cell, str) for cell in table[0]):
                headers = table[0]
                data = table[1:]
                return pd.DataFrame(data, columns=headers)
            else:
                return pd.DataFrame(table)
        except Exception as e:
            # Fallback: try creating DataFrame directly
            try:
                return pd.DataFrame(table)
            except:
                return pd.DataFrame()
    
    def get_basic_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the data."""
        if self.df.empty:
            logger.warning("Empty dataframe for statistics")
            return {"row_count": 0, "column_count": 0, "columns": []}
        
        try:
            stats = {
                "row_count": len(self.df),
                "column_count": len(self.df.columns),
                "columns": [str(c) for c in self.df.columns],
            }
            
            # Numeric statistics
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                stats["numeric_summary"] = {}
                for col in numeric_cols:
                    try:
                        col_data = pd.to_numeric(self.df[col], errors='coerce')
                        stats["numeric_summary"][str(col)] = {
                            "min": float(col_data.min()),
                            "max": float(col_data.max()),
                            "mean": float(col_data.mean()),
                            "median": float(col_data.median()),
                            "sum": float(col_data.sum()),
                        }
                    except Exception as e:
                        logger.warning(f"Could not compute stats for column {col}: {e}")
            
            return stats
        except Exception as e:
            logger.error(f"Error computing statistics: {e}")
            return {"row_count": 0, "column_count": 0, "columns": []}
    
    def get_top_categories(
        self,
        column: str = None,
        n: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Get top N categories from a column.
        
        Args:
            column: Column name (auto-detect if None)
            n: Number of top items to return
            
        Returns:
            List of dicts with category and count
        """
        if self.df.empty:
            return []
        
        try:
            # Auto-detect categorical column if not specified
            if column is None:
                non_numeric_cols = self.df.select_dtypes(exclude=[np.number]).columns
                if len(non_numeric_cols) == 0:
                    # No non-numeric columns, try first column
                    if len(self.df.columns) > 0:
                        column = self.df.columns[0]
                    else:
                        return []
                else:
                    column = non_numeric_cols[0]
            
            if column not in self.df.columns:
                logger.warning(f"Column '{column}' not found")
                return []
            
            top_categories = self.df[column].value_counts().head(n)
            
            if len(top_categories) == 0:
                return []
            
            return [
                {"category": str(cat), "count": int(count)}
                for cat, count in top_categories.items()
            ]
        except Exception as e:
            logger.error(f"Error getting top categories: {e}")
            return []
    
    def get_trends(
        self,
        x_column: str = None,
        y_column: str = None,
    ) -> Dict[str, Any]:
        """
        Identify trends in the data.
        
        Args:
            x_column: X-axis column (auto-detect if None)
            y_column: Y-axis column (auto-detect if None)
            
        Returns:
            Dict with trend information
        """
        if self.df.empty:
            return {}
        
        try:
            # Auto-detect columns
            if y_column is None:
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    logger.warning("No numeric columns found for trend analysis")
                    return {}
                y_column = numeric_cols[0]
            
            if x_column is None and len(self.df.columns) > 1:
                non_y_cols = [c for c in self.df.columns if c != y_column]
                x_column = non_y_cols[0]
            
            if x_column not in self.df.columns or y_column not in self.df.columns:
                logger.warning(f"Columns not found: x={x_column}, y={y_column}")
                return {}
            
            # Calculate trend
            y_values = pd.to_numeric(self.df[y_column], errors='coerce')
            
            if y_values.isna().all():
                logger.warning(f"All values in {y_column} are NaN")
                return {}
            
            # Simple linear trend
            x_values = np.arange(len(y_values))
            valid_idx = ~y_values.isna()
            
            if valid_idx.sum() < 2:
                logger.warning("Not enough valid data points for trend")
                return {}
            
            x_clean = x_values[valid_idx]
            y_clean = y_values[valid_idx].values
            
            coeffs = np.polyfit(x_clean, y_clean, 1)
            slope, intercept = coeffs
            
            trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat"
            
            return {
                "x_column": str(x_column),
                "y_column": str(y_column),
                "trend": trend_direction,
                "slope": float(slope),
                "r_squared": float(self._calculate_r_squared(x_clean, y_clean, slope, intercept)),
            }
        
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {}
    
    @staticmethod
    def _calculate_r_squared(x, y, slope, intercept):
        """Calculate R-squared value."""
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    def get_data_quality_score(self) -> Dict[str, Any]:
        """
        Calculate overall data quality score (0-100).
        
        Returns:
            Score and breakdown
        """
        if self.df.empty:
            return {"score": 0, "reason": "Empty dataset"}
        
        scores = []
        
        # Completeness: % of non-null cells
        completeness = (1 - self.df.isna().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        scores.append(("Completeness", completeness))
        
        # Consistency: % of columns with single data type
        consistency = 0
        for col in self.df.columns:
            non_null = self.df[col].dropna()
            if len(non_null) > 0:
                types = set(type(x).__name__ for x in non_null)
                if len(types) == 1:
                    consistency += 1
        consistency = (consistency / len(self.df.columns)) * 100 if len(self.df.columns) > 0 else 0
        scores.append(("Consistency", consistency))
        
        # Uniqueness: % of unique values (avoid duplicates)
        total_rows = len(self.df)
        unique_rows = len(self.df.drop_duplicates())
        uniqueness = (unique_rows / total_rows) * 100 if total_rows > 0 else 0
        scores.append(("Uniqueness", uniqueness))
        
        # Overall score
        overall = np.mean([s[1] for s in scores])
        
        return {
            "overall_score": round(overall, 1),
            "breakdown": {s[0]: round(s[1], 1) for s in scores},
        }
    
    def get_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect anomalies and outliers in the data.
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            try:
                # Use IQR method for outlier detection
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_indices = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)].index
                
                if len(outlier_indices) > 0:
                    anomalies.append({
                        "type": "outlier",
                        "column": col,
                        "count": len(outlier_indices),
                        "values": self.df.loc[outlier_indices, col].tolist(),
                        "indices": outlier_indices.tolist(),
                    })
            
            except Exception:
                pass
        
        return anomalies
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive data report."""
        return {
            "statistics": self.get_basic_statistics(),
            "top_categories": self.get_top_categories(),
            "trends": self.get_trends(),
            "data_quality": self.get_data_quality_score(),
            "anomalies": self.get_anomalies(),
        }
