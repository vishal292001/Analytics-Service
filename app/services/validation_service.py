import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException

class ValidationService:
    
    VALID_REGIONS = ["North", "South", "East", "West"]
    REQUIRED_COLUMNS = ["sku", "date", "forecast_qty", "unit_price", "region"]
    
    def validate_csv_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate CSV data and return list of errors"""
        errors = []
        
        # Check required columns
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Validate each row
        for index, row in df.iterrows():
            row_errors = self._validate_row(row, index + 1)
            errors.extend(row_errors)
        
        return errors
    
    def _validate_row(self, row: pd.Series, row_number: int) -> List[Dict[str, Any]]:
        """Validate a single row"""
        errors = []
        
        # Check for missing values
        for col in self.REQUIRED_COLUMNS:
            if pd.isna(row[col]) or row[col] == '':
                errors.append({
                    "row": row_number,
                    "column": col,
                    "value": row[col],
                    "error": "Missing value"
                })
                continue
        
        # Validate SKU (alphanumeric with - or _ allowed)
        if not pd.isna(row['sku']) and not re.match(r'^[a-zA-Z0-9_-]+$', str(row['sku'])):
            errors.append({
                "row": row_number,
                "column": "sku",
                "value": row['sku'],
                "error": "SKU must be alphanumeric with - or _ allowed"
            })
        
        # Validate date format
        if not pd.isna(row['date']):
            try:
                datetime.strptime(str(row['date']), '%Y-%m-%d')
            except ValueError:
                errors.append({
                    "row": row_number,
                    "column": "date",
                    "value": row['date'],
                    "error": "Date must be in YYYY-MM-DD format"
                })
        
        # Validate forecast_qty (positive integer)
        if not pd.isna(row['forecast_qty']):
            try:
                qty = int(float(row['forecast_qty']))
                if qty <= 0:
                    errors.append({
                        "row": row_number,
                        "column": "forecast_qty",
                        "value": row['forecast_qty'],
                        "error": "Forecast quantity must be a positive integer"
                    })
            except (ValueError, TypeError):
                errors.append({
                    "row": row_number,
                    "column": "forecast_qty",
                    "value": row['forecast_qty'],
                    "error": "Forecast quantity must be a positive integer"
                })
        
        # Validate unit_price (positive float)
        if not pd.isna(row['unit_price']):
            try:
                price = float(row['unit_price'])
                if price <= 0:
                    errors.append({
                        "row": row_number,
                        "column": "unit_price",
                        "value": row['unit_price'],
                        "error": "Unit price must be a positive number"
                    })
            except (ValueError, TypeError):
                errors.append({
                    "row": row_number,
                    "column": "unit_price",
                    "value": row['unit_price'],
                    "error": "Unit price must be a positive number"
                })
        
        # Validate region
        if not pd.isna(row['region']) and row['region'] not in self.VALID_REGIONS:
            errors.append({
                "row": row_number,
                "column": "region",
                "value": row['region'],
                "error": f"Region must be one of: {', '.join(self.VALID_REGIONS)}"
            })
        
        return errors

