from pydantic import BaseModel, ConfigDict # Import ConfigDict from pydantic
from datetime import date
from typing import Optional

class ClimateDataBase(BaseModel):
    ecosystem_id: int | None = None
    data_source: str | None = None
    measurement_type: str | None = None
    value: float | None = None
    unit: str | None = None
    date_recorded: date | None = None
    location_lat: float | None = None
    location_lon: float | None = None

class ClimateDataCreate(ClimateDataBase):
    pass

class ClimateDataUpdate(BaseModel):
    ecosystem_id: Optional[int] = None
    data_source: Optional[str] = None
    measurement_type: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    date_recorded: Optional[date] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None

class ClimateData(ClimateDataBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Use model_config instead of Config