from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Species])
def read_species(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Retrieve multiple species."""
    species = crud.species.get_multi(db, skip=skip, limit=limit)
    return species

@router.post("/", response_model=schemas.Species, status_code=201)
def create_species(
    *, # force keyword arguments
    db: Session = Depends(deps.get_db),
    species_in: schemas.SpeciesCreate,
) -> Any:
    """Create new species."""
    species = crud.species.get_by_scientific_name(db, scientific_name=species_in.scientific_name)
    if species:
        raise HTTPException(
            status_code=400,
            detail="The species with this scientific name already exists in the system.",
        )
    species = crud.species.create(db, obj_in=species_in)
    return species

@router.put("/{id}", response_model=schemas.Species)
def update_species(
    *, # force keyword arguments
    db: Session = Depends(deps.get_db),
    id: int,
    species_in: schemas.SpeciesUpdate,
) -> Any:
    """Update a species."""
    species = crud.species.get(db, id=id)
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    species = crud.species.update(db, db_obj=species, obj_in=species_in)
    return species

@router.delete("/{id}", response_model=schemas.Species)
def delete_species(
    *, # force keyword arguments
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """Delete a species."""
    species = crud.species.get(db, id=id)
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    species = crud.species.remove(db, id=id)
    return species
