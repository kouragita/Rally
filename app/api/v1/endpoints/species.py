from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Species])
def read_species(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve multiple species."""
    species = crud.species.get_multi(db, skip=skip, limit=limit)
    return species
