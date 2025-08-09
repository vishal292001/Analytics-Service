from datetime import date
from typing import Optional
from pydantic.v1 import BaseModel, constr, EmailStr, validator
import re
from pydantic import BaseModel, Field
from typing import Optional




class ForcastData(BaseModel):
    start_date: Optional[date] = Field(None, description="Start date filter (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date filter (YYYY-MM-DD)")
    sku: Optional[str] = Field(None, description="SKU filter")
    region: Optional[str] = Field(None, description="Region filter")