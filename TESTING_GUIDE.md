# Backend API Testing Guide and Architectural Deep Dive

This document serves as a comprehensive guide for testing the backend API endpoints and provides an in-depth explanation of the system's architecture, data flow, and unique capabilities.

## 1. Prerequisites

Before you begin testing, ensure the following:

*   **Backend Server is Running:** The FastAPI application must be active.
    ```bash
    # From the project root directory
    uvicorn app.main:app --reload
    ```
*   **Database is Populated:** The database should contain climate, wildlife, and ecosystem data.
    *   If not, first ensure your `.env` is configured (especially `DATABASE_URL` and `NOAA_API_KEY`).
    *   Then, run the data ingestion scripts:
        ```bash
        # Clear existing data (optional, but recommended for a clean test)
        python -m scripts.clear_data
        # Run all ingesters
        python -m scripts.run_ingestion all
        ```

## 2. Core API Endpoints for Testing

We will focus on the primary endpoints designed for frontend interaction and AI-powered analysis.

*   `GET /api/v1/ecosystems/`: Retrieve a list of all defined ecosystems.
*   `GET /api/v1/species/`: Retrieve a list of all tracked species.
*   `POST /api/v1/analysis/`: Trigger an AI-powered analysis for a specific ecosystem or species.
*   `GET /api/v1/reports/{report_id}`: Fetch a previously generated AI analysis report.

## 3. Detailed Test Cases

Use `curl` commands to interact with the API. Replace `http://127.0.0.1:8000` with your server's address if different.

### Test Case 3.1: Retrieve Ecosystems

**Purpose:** Verify that the ecosystem data is accessible.

**Command:**
```bash
curl "http://127.0.0.1:8000/api/v1/ecosystems/"
```

**Expected Output:** A JSON array of ecosystem objects, including the ones we created (e.g., "Pelagic Marine Systems", "Arctic Terrestrial Systems").

### Test Case 3.2: Retrieve Species

**Purpose:** Verify that the species data is accessible.

**Command:**
```bash
curl "http://127.0.0.1:8000/api/v1/species/"
```

**Expected Output:** A JSON array of species objects (e.g., "Ursus maritimus", "Panthera leo").

### Test Case 3.3: Ecosystem Analysis (AI-Powered)

**Purpose:** Test the core AI analysis functionality for an ecosystem. This will trigger a call to Inflection AI.

**Command:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analysis/" \
     -H "Content-Type: application/json" \
     -d \
'{
  "query": "What are the main threats to Arctic Terrestrial Systems and how can we mitigate them?",
  "target_type": "ecosystem",
  "target_name": "Arctic Terrestrial Systems"
}'
```

**Expected Output:** A JSON object containing a `report_id` and a success message. Example: `{"report_id":1,"message":"Analysis complete and report generated."}`

### Test Case 3.4: Species Analysis (AI-Powered)

**Purpose:** Test the core AI analysis functionality for a specific species. This will also trigger a call to Inflection AI.

**Command:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analysis/" \
     -H "Content-Type: application/json" \
     -d \
'{
  "query": "Assess the current endangerment level of the Polar Bear.",
  "target_type": "species",
  "target_name": "Ursus maritimus"
}'
```

**Expected Output:** A JSON object containing a `report_id` and a success message. Example: `{"report_id":2,"message":"Analysis complete and report generated."}`

### Test Case 3.5: Fetch Generated Report

**Purpose:** Retrieve the full AI-generated report using its ID.

**Command:** (Replace `[REPORT_ID]` with an ID obtained from Test Case 3.3 or 3.4)
```bash
curl "http://127.0.0.1:8000/api/v1/reports/[REPORT_ID]"
```

**Expected Output:** A large JSON object containing the `report_type`, `query_parameters`, `analysis_results` (including `raw_text` from AI), `predictions`, `citations`, `confidence_scores`, and `ai_model_version`.

## 4. Architectural Deep Dive: The Brains Behind the Operation

Our backend service is a sophisticated system designed to provide AI-powered insights into climate change impacts on wildlife. It's built with a modular, scalable architecture that ensures data integrity, efficient processing, and actionable intelligence.

### 4.1. Unique Data Acquisition and Integration

What makes our project unique is its ability to seamlessly integrate diverse, real-world scientific data sources:

*   **NASA GISS (Global Land-Ocean Temperature Data):** Provides historical temperature anomalies, crucial for understanding long-term climate trends. Our `NASAIngester` processes this global data and intelligently associates it with *all* defined ecosystems, ensuring every ecosystem benefits from this foundational climate context.
*   **NOAA GHCN (Global Historical Climatology Network Daily):** Offers granular daily climate data (temperature, precipitation) from specific weather stations. Our `NOAAIngester` fetches this data and maps it to specific ecosystems based on predefined station-to-ecosystem relationships, providing localized climate context.
*   **GBIF (Global Biodiversity Information Facility):** Supplies vast amounts of species occurrence data (sightings, locations). Our `GBIFIngester` processes this, creates/updates species records, and crucially, uses a simplified geospatial bounding box logic to assign each wildlife sighting to its most probable ecosystem, ensuring wildlife data is contextually relevant.

This multi-source ingestion pipeline ensures a rich, varied dataset for the AI to analyze, providing a holistic view of climate and wildlife interactions.

### 4.2. The Intelligent Data Flow

Data doesn't just sit in our database; it flows through a carefully orchestrated pipeline:

1.  **Ingestion (`scripts/data_ingestion/`):** Raw data is fetched from external APIs, processed (cleaned, standardized), and then intelligently linked to `Ecosystem` and `Species` records before being stored in our PostgreSQL database.
2.  **API Gateway (`app/api/v1/endpoints/`):** The frontend interacts primarily with the `POST /api/v1/analysis/` endpoint. This endpoint acts as the orchestrator for AI analysis requests.
3.  **Targeted Data Retrieval (`app/crud/`):** Based on the frontend's `target_type` (ecosystem or species) and `target_name`/`id`, the `analysis` endpoint uses highly optimized CRUD operations to fetch *only the most relevant* climate and wildlife data from the database. This prevents overwhelming the AI with unnecessary information and improves efficiency.
4.  **AI Processing (`app/services/inflection_ai.py`):** The retrieved, targeted data is passed to the `InflectionAIService`. This service employs a unique **two-step AI interaction process**:
    *   **Step 1 (Analysis):** The AI is prompted to perform a deep, natural language analysis of the data, identifying trends, impacts, and recommendations.
    *   **Step 2 (Extraction):** The natural language output from Step 1 is then fed back to the AI with a strict Pydantic schema. The AI's task here is to extract specific, structured information (summary, predictions, citations, confidence scores) into a clean JSON object. This ensures the frontend receives reliable, parseable data.
5.  **Report Generation & Storage (`app/models/report.py`, `app/crud/crud_report.py`):** The structured JSON output from the AI is used to create a `Report` record, which is then saved back into the database. This allows for historical tracking of analyses and asynchronous retrieval by the frontend.

### 4.3. Architectural Uniqueness and Robustness

*   **Modular Design:** The project is structured into clear layers (models, schemas, CRUD, services, API endpoints, scripts), promoting maintainability and scalability.
*   **FastAPI & Pydantic:** Leveraging FastAPI provides high performance and automatic data validation/serialization via Pydantic, ensuring data integrity from API request to database storage.
*   **Intelligent AI Orchestration:** The two-step AI process is a key differentiator, ensuring that complex natural language analysis can be reliably converted into structured, actionable data for the frontend.
*   **Targeted Data Context:** By fetching only relevant data for the AI, we optimize API calls to Inflection AI, reduce costs, and improve the accuracy of the AI's analysis.
*   **Comprehensive Data Management:** Full CRUD operations for core entities (Ecosystems, Species) provide a complete backend solution.

This architecture ensures that our system is not just a data repository, but an intelligent analytical engine capable of transforming raw environmental data into meaningful, actionable insights for conservation efforts.
