from pydantic import BaseModel, ConfigDict # Import ConfigDict from pydantic
from typing import Literal, Optional

class EcosystemBase(BaseModel):
    name: str
    type: Literal["aquatic", "terrestrial"]
    subtype: str | None = None
    description: str | None = None

class EcosystemCreate(EcosystemBase):
    pass

class EcosystemUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Literal["aquatic", "terrestrial"]] = None
    subtype: Optional[str] = None
    description: Optional[str] = None

class Ecosystem(EcosystemBase):
    id: int

    model_config = ConfigDict(from_attributes=True) # Use model_config instead of Config