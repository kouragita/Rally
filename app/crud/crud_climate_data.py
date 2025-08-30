from sqlalchemy.orm import Session
from typing import List

from .base import CRUDBase
from app.models.climate_data import ClimateData
from app.schemas.climate_data import ClimateDataCreate, ClimateDataUpdate

class CRUDClimateData(CRUDBase[ClimateData, ClimateDataCreate, ClimateDataUpdate]):
    def get_by_ecosystem(self, db: Session, *, ecosystem_id: int, limit: int = 100) -> List[ClimateData]:
        return db.query(ClimateData).filter(ClimateData.ecosystem_id == ecosystem_id).limit(limit).all()

climate_data = CRUDClimateData(ClimateData)
