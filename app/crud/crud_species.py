from .base import CRUDBase
from app.models.species import Species
from app.schemas.species import SpeciesCreate, SpeciesUpdate

class CRUDSpecies(CRUDBase[Species, SpeciesCreate, SpeciesUpdate]):
    pass

species = CRUDSpecies(Species)
