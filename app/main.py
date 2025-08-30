from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "docs_url": "/docs"}

app.include_router(api_router, prefix=settings.API_V1_STR)
