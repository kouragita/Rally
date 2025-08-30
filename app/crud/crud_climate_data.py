from .base import CRUDBase
from app.models.climate_data import ClimateData
from app.schemas.climate_data import ClimateDataCreate, ClimateDataUpdate

class CRUDClimateData(CRUDBase[ClimateData, ClimateDataCreate, ClimateDataUpdate]):
    pass

climate_data = CRUDClimateData(ClimateData)
