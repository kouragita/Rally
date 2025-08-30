from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.api import deps
from app.services.inflection_ai import InflectionAIService # Import the service class

router = APIRouter()

@router.post("/", response_model=schemas.Report)
async def create_analysis(
    analysis_request: schemas.AnalysisRequest,
    db: Session = Depends(deps.get_db),
    inflection_ai_service: InflectionAIService = Depends(InflectionAIService) # FastAPI will instantiate
):
    """
    Triggers an AI-powered analysis based on the provided query and data targets.
    """
    climate_data_records = []
    wildlife_data_records = []

    # Fetch relevant data based on target_type and target_id/name
    if analysis_request.target_type == "ecosystem":
        # For simplicity, fetch all climate and wildlife data for now.
        # In a real app, we'd filter by ecosystem_id or related data.
        climate_data_records = crud.climate_data.get_multi(db, limit=500) # Limit to avoid huge data transfer
        wildlife_data_records = crud.wildlife_data.get_multi(db, limit=500)
        
        # If a specific ecosystem is targeted, filter data further
        if analysis_request.target_id:
            # This would require more complex CRUD methods or direct queries
            # For now, we'll just pass all fetched data to the AI
            pass
        elif analysis_request.target_name:
            # Find ecosystem by name and then filter data
            # This would require a get_by_name method in crud.ecosystem
            pass

    elif analysis_request.target_type == "species":
        # Find the species first
        species_obj = None
        if analysis_request.target_id:
            species_obj = crud.species.get(db, id=analysis_request.target_id)
        elif analysis_request.target_name:
            # This would require a get_by_scientific_name method in crud.species
            species_obj = db.query(schemas.Species).filter(schemas.Species.scientific_name == analysis_request.target_name).first() # Direct query for now
        
        if not species_obj:
            raise HTTPException(status_code=404, detail=f"Target species not found: {analysis_request.target_id or analysis_request.target_name}")

        # Fetch climate data related to the species' ecosystems (complex, simplified for now)
        climate_data_records = crud.climate_data.get_multi(db, limit=500)
        # Fetch wildlife data specifically for this species
        wildlife_data_records = db.query(schemas.WildlifeData).filter(schemas.WildlifeData.species_id == species_obj.id).limit(500).all() # Direct query for now

    # Convert SQLAlchemy objects to dictionaries for the AI service
    climate_data_dicts = [cd.__dict__ for cd in climate_data_records]
    wildlife_data_dicts = [wd.__dict__ for wd in wildlife_data_records]

    try:
        # Call the AI service
        report_create_schema = await inflection_ai_service.analyze(
            query=analysis_request.query,
            climate_data=climate_data_dicts,
            wildlife_data=wildlife_data_dicts
        )
        
        # Save the report to the database
        created_report = crud.report.create(db, obj_in=report_create_schema)
        return created_report
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI analysis failed: {e}")