from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Report])
def read_reports(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """Retrieve multiple reports."""
    reports = crud.report.get_multi(db, skip=skip, limit=limit)
    return reports

@router.get("/{report_id}", response_model=schemas.Report)
def read_report_by_id(
    report_id: int,
    db: Session = Depends(deps.get_db)
):
    """Retrieve a single report by ID."""
    report = crud.report.get(db, id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report