from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import Column, Enum as SqlEnum, String

Base = declarative_base()

class Upload(Base):
    __tablename__ = "uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), default="completed", nullable=False)
    
    # Relationship to forecasts
    forecasts = relationship("Forecast", back_populates="upload")



class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    forecast_qty = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    region = Column(String(20), nullable=False, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to upload
    upload = relationship("Upload", back_populates="forecasts")
