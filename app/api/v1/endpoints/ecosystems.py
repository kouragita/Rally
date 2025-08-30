from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Ecosystem])
def read_ecosystems(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve ecosystems."""
    ecosystems = crud.ecosystem.get_multi(db, skip=skip, limit=limit)
    return ecosystems

@router.post("/", response_model=schemas.Ecosystem, status_code=201)
def create_ecosystem(
    *, # force keyword arguments
    db: Session = Depends(deps.get_db),
    ecosystem_in: schemas.EcosystemCreate,
) -> Any:
    """Create new ecosystem."""
    ecosystem = crud.ecosystem.get_by_name(db, name=ecosystem_in.name)
    if ecosystem:
        raise HTTPException(
            status_code=400,
            detail="The ecosystem with this name already exists in the system.",
        )
    ecosystem = crud.ecosystem.create(db, obj_in=ecosystem_in)
    return ecosystem

@router.put("/{id}", response_model=schemas.Ecosystem)
def update_ecosystem(
    *, # force keyword arguments
    db: Session = Depends(deps.get_db),
    id: int,
    ecosystem_in: schemas.EcosystemUpdate,
) -> Any:
    """Update an ecosystem."""
    ecosystem = crud.ecosystem.get(db, id=id)
    if not ecosystem:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    ecosystem = crud.ecosystem.update(db, db_obj=ecosystem, obj_in=ecosystem_in)
    return ecosystem

@router.delete("/{id}", response_model=schemas.Ecosystem)
def delete_ecosystem(
    *, # force keyword arguments
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """Delete an ecosystem."""
    ecosystem = crud.ecosystem.get(db, id=id)
    if not ecosystem:
        raise HTTPException(status_code=404, detail="Ecosystem not found")
    ecosystem = crud.ecosystem.remove(db, id=id)
    return ecosystem

