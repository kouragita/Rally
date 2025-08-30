from sqlalchemy.orm import Session
from typing import List

from .base import CRUDBase
from app.models.wildlife_data import WildlifeData
from app.schemas.wildlife_data import WildlifeDataCreate, WildlifeDataUpdate

class CRUDWildlifeData(CRUDBase[WildlifeData, WildlifeDataCreate, WildlifeDataUpdate]):
    def get_by_ecosystem(self, db: Session, *, ecosystem_id: int, limit: int = 100) -> List[WildlifeData]:
        return db.query(WildlifeData).filter(WildlifeData.ecosystem_id == ecosystem_id).limit(limit).all()

    def get_by_species(self, db: Session, *, species_id: int, limit: int = 100) -> List[WildlifeData]:
        return db.query(WildlifeData).filter(WildlifeData.species_id == species_id).limit(limit).all()

wildlife_data = CRUDWildlifeData(WildlifeData)
