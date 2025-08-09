from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import and_, case, func
from fastapi import status
from typing import List, Dict
from datetime import datetime
from app.models import Forecast
from app.schema.demand_forcast_scema import ForcastData
import json
import logging
import time

logger = logging.getLogger(__name__)

def get_summary_helper(db: Session, filter_data: ForcastData) -> Dict:
    try:
        """
        Get aggregated summary of forecasts by SKU and region
        Includes business logic for transportation surcharge
        """
        logger.info(f"Received get summary request: {filter_data.dict()}")

        # Build base query
        query = db.query(
            Forecast.sku,
            Forecast.region,
            func.sum(Forecast.forecast_qty).label('total_forecast_qty'),
            func.sum(Forecast.forecast_qty * Forecast.unit_price).label('base_value'),
            func.sum(
                case(
                    (Forecast.forecast_qty > 500, Forecast.forecast_qty * Forecast.unit_price * 1.1),
                    else_=Forecast.forecast_qty * Forecast.unit_price
                )
            ).label('total_forecast_value')
        )
                
        # Apply filters
        if filter_data.start_date:
            query = query.filter(Forecast.date >= filter_data.start_date)
        if filter_data.end_date:
            query = query.filter(Forecast.date <= filter_data.end_date)
        if filter_data.sku:
            query = query.filter(Forecast.sku == filter_data.sku)
        if filter_data.region:
            query = query.filter(Forecast.region == filter_data.region)
        
        # Group by SKU and region
        query = query.group_by(Forecast.sku, Forecast.region)
        
        # Execute query and format results
        results = []
        for row in query.all():
            results.append({
                "sku": row.sku,
                "region": row.region,
                "total_forecast_qty": int(row.total_forecast_qty),
                "total_forecast_value": float(row.total_forecast_value)
            })
        
        return {
            "status": 200,
            "message": "Summary Details",
            "data": results
        }
       

    except SQLAlchemyError as e:
        logger.error(f"Database error during employee search: {str(e)}")
        db.rollback()
        return {
            "status": 500,
            "message": "Internal server error during database operation"
        }

    except Exception as e:
        logger.exception("Unexpected error occurred during employee search")
        return {
            "status": 500,
            "message": "An unexpected error occurred"
        }
