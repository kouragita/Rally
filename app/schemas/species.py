from pydantic import BaseModel, Json, ConfigDict # Import ConfigDict from pydantic
from typing import Any, Optional

class SpeciesBase(BaseModel):
    scientific_name: str
    common_name: str | None = None
    conservation_status: str | None = None
    climate_sensitivity: float | None = None
    ecosystem_dependencies: Json[Any] | None = None

class SpeciesCreate(SpeciesBase):
    pass

class SpeciesUpdate(BaseModel):
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    conservation_status: Optional[str] = None
    climate_sensitivity: Optional[float] = None
    ecosystem_dependencies: Optional[Json[Any]] = None

class Species(SpeciesBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Use model_config instead of Config