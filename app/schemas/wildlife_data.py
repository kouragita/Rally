from pydantic import BaseModel, Json, ConfigDict # Import ConfigDict from pydantic
from datetime import date
from typing import Any, Optional

class WildlifeDataBase(BaseModel):
    species_id: int | None = None
    ecosystem_id: int | None = None
    population_count: int | None = None
    habitat_quality_score: float | None = None
    migration_pattern: Json[Any] | None = None
    date_recorded: date | None = None
    location_lat: float | None = None
    location_lon: float | None = None

class WildlifeDataCreate(WildlifeDataBase):
    pass

class WildlifeDataUpdate(BaseModel):
    species_id: Optional[int] = None
    ecosystem_id: Optional[int] = None
    population_count: Optional[int] = None
    habitat_quality_score: Optional[float] = None
    migration_pattern: Optional[Json[Any]] = None
    date_recorded: Optional[date] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None

class WildlifeData(WildlifeDataBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Use model_config instead of Config