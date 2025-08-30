from sqlalchemy.orm import Session
from typing import Optional

from .base import CRUDBase
from app.models.species import Species
from app.schemas.species import SpeciesCreate, SpeciesUpdate

class CRUDSpecies(CRUDBase[Species, SpeciesCreate, SpeciesUpdate]):
    def get_by_scientific_name(self, db: Session, *, scientific_name: str) -> Optional[Species]:
        return db.query(Species).filter(Species.scientific_name == scientific_name).first()

species = CRUDSpecies(Species)
