from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, models, schemas
from app.api import deps
from app.services.inflection_ai import InflectionAIService

def get_ecosystem(db: Session, target_id: int | None, target_name: str | None) -> models.Ecosystem:
    """Helper function to get an ecosystem by ID or name."""
    if target_id:
        ecosystem = crud.ecosystem.get(db, id=target_id)
    elif target_name:
        ecosystem = crud.ecosystem.get_by_name(db, name=target_name)
    else:
        raise HTTPException(status_code=400, detail="Either target_id or target_name must be provided for ecosystem analysis.")
    
    if not ecosystem:
        raise HTTPException(status_code=404, detail=f"Ecosystem not found: {target_id or target_name}")
    return ecosystem

def get_species(db: Session, target_id: int | None, target_name: str | None) -> models.Species:
    """Helper function to get a species by ID or name."""
    if target_id:
        species = crud.species.get(db, id=target_id)
    elif target_name:
        species = crud.species.get_by_scientific_name(db, scientific_name=target_name)
    else:
        raise HTTPException(status_code=400, detail="Either target_id or target_name must be provided for species analysis.")

    if not species:
        raise HTTPException(status_code=404, detail=f"Species not found: {target_id or target_name}")
    return species

router = APIRouter()

@router.post("/", response_model=schemas.AnalysisResult)
async def create_analysis(
    analysis_request: schemas.AnalysisRequest,
    db: Session = Depends(deps.get_db),
    inflection_ai_service: InflectionAIService = Depends(InflectionAIService)
):
    """
    Triggers a more efficient and targeted AI-powered analysis.
    """
    climate_data_records = []
    wildlife_data_records = []

    if analysis_request.target_type == "ecosystem":
        ecosystem = get_ecosystem(db, analysis_request.target_id, analysis_request.target_name)
        climate_data_records = crud.climate_data.get_by_ecosystem(db, ecosystem_id=ecosystem.id, limit=250)
        wildlife_data_records = crud.wildlife_data.get_by_ecosystem(db, ecosystem_id=ecosystem.id, limit=250)

    elif analysis_request.target_type == "species":
        species = get_species(db, analysis_request.target_id, analysis_request.target_name)
        wildlife_data_records = crud.wildlife_data.get_by_species(db, species_id=species.id, limit=500)
        # To get relevant climate data, we could find all ecosystems the species lives in.
        # For now, we'll fetch from the first associated ecosystem if it exists.
        if wildlife_data_records and wildlife_data_records[0].ecosystem_id:
            climate_data_records = crud.climate_data.get_by_ecosystem(db, ecosystem_id=wildlife_data_records[0].ecosystem_id, limit=500)

    # Use Pydantic schemas for serialization to avoid issues with __dict__
    climate_data_dicts = [schemas.ClimateData.from_orm(cd).dict() for cd in climate_data_records]
    wildlife_data_dicts = [schemas.WildlifeData.from_orm(wd).dict() for wd in wildlife_data_records]

    if not climate_data_dicts and not wildlife_data_dicts:
        raise HTTPException(status_code=404, detail="No climate or wildlife data found for the specified target to analyze.")

    try:
        report_create_schema = await inflection_ai_service.analyze(
            query=analysis_request.query,
            climate_data=climate_data_dicts,
            wildlife_data=wildlife_data_dicts
        )
        
        created_report = crud.report.create(db, obj_in=report_create_schema)
        return schemas.AnalysisResult(report_id=created_report.id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI analysis failed: {e}")
