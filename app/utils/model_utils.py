import datetime
from sqlalchemy.orm import class_mapper
from enum import Enum



def model_to_dict(model, exclude_fields=None):
    """Convert SQLAlchemy model instance to dictionary, with option to exclude certain fields."""
    if exclude_fields is None:
        exclude_fields = []

    data = {}
    for c in class_mapper(model.__class__).mapped_table.c:
        if c.key in exclude_fields:  # Skip excluded fields
            continue

        value = getattr(model, c.key)
        if isinstance(value, Enum):  # Convert Enum to string
            data[c.key] = value.name
        elif isinstance(value, datetime.datetime):  # Convert datetime to ISO format string
            data[c.key] = value.isoformat()
        else:
            data[c.key] = value
    return data


