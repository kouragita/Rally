from .base import CRUDBase
from app.models.wildlife_data import WildlifeData
from app.schemas.wildlife_data import WildlifeDataCreate, WildlifeDataUpdate

class CRUDWildlifeData(CRUDBase[WildlifeData, WildlifeDataCreate, WildlifeDataUpdate]):
    pass

wildlife_data = CRUDWildlifeData(WildlifeData)
