from fastapi import APIRouter
from app.api.v1.endpoints import analysis, species, climate_data, wildlife_data, ecosystems, reports

api_router = APIRouter()
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(species.router, prefix="/species", tags=["species"])
api_router.include_router(climate_data.router, prefix="/climate_data", tags=["climate_data"])
api_router.include_router(wildlife_data.router, prefix="/wildlife_data", tags=["wildlife_data"])
api_router.include_router(ecosystems.router, prefix="/ecosystems", tags=["ecosystems"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
