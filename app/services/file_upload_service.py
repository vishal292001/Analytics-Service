from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import File, HTTPException, UploadFile, status
from typing import List, Dict
from datetime import datetime
import json
import logging
import time
import pandas as pd
from app.models import Forecast, Upload
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)

async def file_upload_helper(db: Session, file: UploadFile = File(...)):
    try:
        # Validate file Type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed"
            )
        
        # Create upload record
        upload_record = Upload(
            filename=file.filename,
            upload_time=datetime.utcnow(),
            status="processing"
        )
        db.add(upload_record)
        db.flush()  # Get the ID without committing
           

        content = await file.read()
        df = pd.read_csv(pd.io.common.StringIO(content.decode('utf-8')))
        print(df)

        validation_service = ValidationService()
        validation_errors = validation_service.validate_csv_data(df)  

        print("this is validation errors", validation_errors)   

        if validation_errors:
            upload_record.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Validation failed",
                    "errors": validation_errors
                }
            )
        records_processed = 0
        for _, row in df.iterrows():
            forecast = Forecast(
                sku=str(row['sku']),
                date=datetime.strptime(str(row['date']), '%Y-%m-%d').date(),
                forecast_qty=int(float(row['forecast_qty'])),
                unit_price=float(row['unit_price']),
                region=str(row['region']),
                upload_id=upload_record.id
            )
            db.add(forecast)
            records_processed += 1
        
        # Update upload status
        upload_record.status = "completed"
        db.commit()
        
        logger.info(f"Successfully processed {records_processed} records from {file.filename}")
        
        return {
            "upload_id": upload_record.id,
            "records_processed": records_processed
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


