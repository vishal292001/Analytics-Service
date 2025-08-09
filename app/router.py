from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.schema.demand_forcast_scema import ForcastData
from app.services.analytics_service import get_analytics_helper
from app.services.file_upload_service import file_upload_helper
from app.services.summary_service import get_summary_helper
from app.utils.api_request_handler import handle_api_request

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status_code": 200,
        "message": "Server is up and Running!"
    }


@router.post("/api/upload-forecast")
async def upload_forecast(request: Request,db: Session = Depends(get_db)):
    """
    Upload CSV file with demand forecasts
    Expected columns: sku, date, forecast_qty, unit_price, region
    """
    return await handle_api_request(
        request=request,
        db=db,
        query_schema=None,
        helper_function=file_upload_helper
    )

@router.get("/api/summary")
async def get_summary(request: Request, db: Session = Depends(get_db)):
    return await handle_api_request(
        request=request,
        db=db,
        query_schema=ForcastData,
        helper_function=get_summary_helper,
    )


@router.get("/api/analytics")
async def get_analytics(request: Request, db: Session = Depends(get_db)):
    return await handle_api_request(
        request=request,
        db=db,
        query_schema=ForcastData,
        helper_function=get_analytics_helper,
    )

