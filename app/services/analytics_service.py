from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import and_, case, desc, func
from fastapi import status
from typing import Any, List, Dict, Optional
from datetime import date, datetime
from app.models import Forecast
from app.schema.demand_forcast_scema import ForcastData
import json
import logging
import time

logger = logging.getLogger(__name__)

def get_analytics_helper(db: Session, filter_data: ForcastData) -> Dict:
    try:
        """
        Get advanced analytics by region:
        - top_sku_by_value: SKU with highest total forecast value
        - avg_forecast_qty: Average daily forecast quantity
        - total_skus: Count of unique SKUs
        """
        logger.info(f"Received get anaytics request: {filter_data.dict()}")
        regions = ["North", "South", "East", "West"]
        analytics_data = {}
        start_date,end_date=None,None
        if filter_data.start_date:
             start_date = filter_data.start_date
        if filter_data.end_date:
             end_date = filter_data.end_date

        for region in regions:
            analytics_data[region] = get_region_analytics(db, region, start_date, end_date)
        

        return {
            "status": 200,
            "message": "Advance Analytics",
            "data": analytics_data
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




def get_region_analytics(db: Session,region: str,start_date: Optional[date] = None,end_date: Optional[date] = None) -> Dict[str, Any]:
        """Get analytics for a specific region"""
        
        # Base query for the region
        base_query = db.query(Forecast).filter(Forecast.region == region)
        
        # Apply date filters
        if start_date:
            base_query = base_query.filter(Forecast.date >= start_date)
        if end_date:
            base_query = base_query.filter(Forecast.date <= end_date)
        
        # Get top SKU by value (with business logic)
        top_sku_query = base_query.with_entities(
            Forecast.sku,
            func.sum(
                case(
                    (Forecast.forecast_qty > 500, Forecast.forecast_qty * Forecast.unit_price * 1.1),
                    else_=Forecast.forecast_qty * Forecast.unit_price
                )
            ).label('total_value')
        ).group_by(Forecast.sku).order_by(desc('total_value')).first()
        
        top_sku_by_value = top_sku_query.sku if top_sku_query else None
        
        # Get average forecast quantity
        avg_qty_query = base_query.with_entities(
            func.avg(Forecast.forecast_qty).label('avg_qty')
        ).first()
        
        avg_forecast_qty = float(avg_qty_query.avg_qty) if avg_qty_query.avg_qty else 0.0
        
        # Get total unique SKUs
        total_skus_query = base_query.with_entities(
            func.count(func.distinct(Forecast.sku)).label('total_skus')
        ).first()
        
        total_skus = int(total_skus_query.total_skus) if total_skus_query.total_skus else 0
        
        return {
            "top_sku_by_value": top_sku_by_value,
            "avg_forecast_qty": round(avg_forecast_qty, 2),
            "total_skus": total_skus
        }