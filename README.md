# AI Backend Service: Implementation Strategy

## 1. Overview

This document outlines a refined and actionable implementation strategy for the Climate Wildlife AI Backend System.

The goal is to build a robust, scalable, and maintainable backend service that can:
- Ingest and manage climate and wildlife data.
- Leverage the Inflection AI API for advanced data analysis, pattern recognition, and report generation.
- Expose a clean, well-documented RESTful API for a frontend client.

This strategy modernizes the proposed technology stack and provides a clear roadmap for development.

## 2. Technology Stack

We will use a modern Python stack designed for performance, developer efficiency, and scalability.

- **Web Framework**: **FastAPI** - A high-performance framework for building APIs with Python 3.8+ based on standard Python type hints. It provides automatic data validation, interactive API documentation, and supports asynchronous operations.
- **Database ORM**: **SQLAlchemy** - The de-facto standard for Python database toolkits. We will use its ORM capabilities to map our data models to database tables.
- **Database Migrations**: **Alembic** - A lightweight database migration tool for SQLAlchemy. It allows us to manage and version our database schema over time.
- **Data Validation**: **Pydantic** - FastAPI is built on Pydantic, which we will use to define clear, type-hinted data models for our API requests and responses.
- **Database**: **SQLite** (for development) and **PostgreSQL** (for production) - As originally planned.
- **Configuration**: Environment variables using `python-dotenv`.
- **Testing**: `pytest` for writing and running tests.

## 3. Refined Project Structure

This structure promotes modularity and separation of concerns.

```
backend/
├── alembic/                  # Alembic migration scripts
│   ├── versions/
│   └── env.py
├── app/
│   ├── __init__.py
│   ├── api/                  # API endpoint definitions (routers)
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── analysis.py
│   │       │   └── reports.py
│   │       └── api.py        # Main v1 API router
│   ├── core/                 # Core logic and configuration
│   │   ├── __init__.py
│   │   └── config.py         # Configuration management
│   ├── crud/                 # Reusable functions to interact with the data in the database.
│   │   ├── __init__.py
│   │   ├── crud_ecosystem.py
│   │   └── crud_report.py
│   ├── models/               # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── ecosystem.py
│   │   └── report.py
│   ├── schemas/              # Pydantic models for API validation
│   │   ├── __init__.py
│   │   ├── ecosystem.py
│   │   └── report.py
│   ├── services/             # Business logic and external service integrations
│   │   ├── __init__.py
│   │   └── inflection_ai.py  # Service for Inflection AI API
│   └── main.py               # Main FastAPI application instance
├── scripts/                  # Data ingestion and other utility scripts
│   └── ...
├── tests/                    # Application tests
│   └── ...
├── .env                      # Environment variables (gitignored)
├── .gitignore
├── alembic.ini               # Alembic configuration
├── requirements.txt
└── README.md
```

## 4. Data Layer Implementation

### 4.1. SQLAlchemy Models (`app/models/`)

We will define our database tables as Python classes using SQLAlchemy\'s ORM.

**Example: `app/models/ecosystem.py`**
```python
from sqlalchemy import Column, Integer, String, Enum
from app.db.base_class import Base

class Ecosystem(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(Enum("aquatic", "terrestrial", name="ecosystem_type"))
    description = Column(String)
```

### 4.2. Pydantic Schemas (`app/schemas/`)

These models define the shape of the data for our API.

**Example: `app/schemas/ecosystem.py`**
```python
from pydantic import BaseModel
from typing import Literal

class EcosystemBase(BaseModel):
    name: str
    type: Literal["aquatic", "terrestrial"]
    description: str | None = None

class EcosystemCreate(EcosystemBase):
    pass

class Ecosystem(EcosystemBase):
    id: int

    class Config:
        orm_mode = True
```

## 5. API Design with FastAPI

We will structure our API with versioning (`/api/v1/...`). FastAPI routers will be used to organize endpoints.

### 5.1. Analysis Endpoint

**File**: `app/api/v1/endpoints/analysis.py`

This endpoint will take details about an ecosystem and data, send it to the Inflection AI service for analysis, and return the results.

**Endpoint Definition:**
```python
from fastapi import APIRouter, Depends
from app import schemas
from app.services import inflection_ai

router = APIRouter()

@router.post("/analyze", response_model=schemas.AnalysisResult)
async def analyze_ecosystem(
    analysis_request: schemas.AnalysisRequest,
    inflection_service: inflection_ai.InflectionAIService = Depends()
):
    """
    Run analysis on ecosystem data using Inflection AI.
    """
    analysis_result = await inflection_service.analyze(
        prompt=analysis_request.prompt,
        data=analysis_request.data
    )
    # Here you would store the result and return it
    return analysis_result
```

### 5.2. Pydantic Schemas for the Endpoint

**File**: `app/schemas/analysis.py`
```python
from pydantic import BaseModel
from typing import List, Dict, Any

class AnalysisRequest(BaseModel):
    prompt: str
    data: List[Dict[str, Any]]

class AnalysisResult(BaseModel):
    summary: str
    key_findings: List[str]
    confidence_score: float
    raw_response: Dict[str, Any]
```

## 6. Inflection AI Service Integration

We will create a dedicated service to handle all communication with the Inflection AI API. This encapsulates the logic and makes it easy to manage the API key and endpoint details.

**File**: `app/services/inflection_ai.py`
```python
import httpx
from fastapi import Depends
from app.core.config import get_settings, Settings

class InflectionAIService:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.api_key = settings.INFLECTION_AI_API_KEY
        self.api_url = f"{settings.INFLECTION_AI_BASE_URL}/v1/chat/completions"

    async def analyze(self, prompt: str, data: list) -> dict:
        """
        Calls the Inflection AI chat completions endpoint for analysis.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Convert the structured data into a string format for the prompt
        data_string = "\n".join([str(item) for item in data])

        messages = [
            {"role": "system", "content": "You are a scientific assistant specializing in climate change and wildlife biology. Analyze the following data to identify key patterns, risks, and insights."},
            {"role": "user", "content": f"{prompt}\n\nData:\n{data_string}"}
        ]

        payload = {
            "model": "Pi-3.1", # Or another suitable model
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.5,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            # Here, you would parse the response into a structured format
            # (e.g., the AnalysisResult schema)
            return response.json()

```

## 7. Development and Setup Plan

### Step 1: Initial Setup

1.  **Create Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    Create a `requirements.txt` with the new stack and install it.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Create a `.env` file from `.env.example` and add your `DATABASE_URL` and `INFLECTION_AI_API_KEY`.

### Step 2: Database Initialization

1.  **Configure Alembic**:
    Edit `alembic.ini` to point to your database URL.

2.  **Create Initial Migration**:
    ```bash
    alembic revision --autogenerate -m "Initial migration"
    ```

3.  **Apply Migration**:
    ```bash
    alembic upgrade head
    ```

### Step 3: Running the Application

-   **Run the dev server**:
    ```bash
    uvicorn app.main:app --reload
    ```
-   **Access Interactive Docs**:
    Navigate to `http://127.0.0.1:8000/docs` to see the auto-generated Swagger UI for your API.

## 8. Next Steps

1.  **Implement the Project Structure**: Create the directories and files as outlined above.
2.  **Define Models and Schemas**: Flesh out the SQLAlchemy models and Pydantic schemas for all data entities (ClimateData, WildlifeData, Reports, etc.).
3.  **Build CRUD Operations**: Create the CRUD (Create, Read, Update, Delete) functions for each model.
4.  **Develop API Endpoints**: Implement the FastAPI routers and endpoints for each resource.
5.  **Write Tests**: Create unit and integration tests for services and API endpoints.
6.  **Refine Data Ingestion Scripts**: Adapt the existing data ingestion scripts to use the new SQLAlchemy models.
