from sqlalchemy.orm import Session
from typing import Optional

from .base import CRUDBase
from app.models.ecosystem import Ecosystem
from app.schemas.ecosystem import EcosystemCreate, EcosystemUpdate

class CRUDEcosystem(CRUDBase[Ecosystem, EcosystemCreate, EcosystemUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Ecosystem]:
        return db.query(Ecosystem).filter(Ecosystem.name == name).first()

ecosystem = CRUDEcosystem(Ecosystem)
