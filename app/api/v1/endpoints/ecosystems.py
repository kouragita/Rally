from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Ecosystem])
def read_ecosystems(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve multiple ecosystems."""
    ecosystems = crud.ecosystem.get_multi(db, skip=skip, limit=limit)
    return ecosystems
