# Project Setup and Execution Guide

This guide provides step-by-step instructions on how to set up the virtual environment, install the required dependencies, and run the backend application.

## 1. Environment Setup

It is highly recommended to use a virtual environment to manage the project's dependencies.

**From the project root directory (`/home/code_sensei/dev/Rally`), follow these steps:**

### a. Create a Virtual Environment

If you don't have a virtual environment set up yet, create one:

```bash
python -m venv env
```

This will create a directory named `env` in the project root.

### b. Activate the Virtual Environment

Before you can install dependencies or run the application, you need to activate the virtual environment:

```bash
source env/bin/activate
```

Your shell prompt should now be prefixed with `(env)`, indicating that the virtual environment is active.

## 2. Install Dependencies

Once the virtual environment is active, install all the required packages from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This will install all the necessary libraries, such as FastAPI, Uvicorn, SQLAlchemy, etc.

## 3. Database Setup

This project uses Alembic to manage database migrations.

### a. Configure the Database URL

Make sure your `.env` file has the correct `DATABASE_URL` for your PostgreSQL database. For development, you can use the default SQLite database.

### b. Apply Migrations

To create all the necessary tables in the database, run the following command:

```bash
alembic upgrade head
```

## 4. Running the Application

The application is run using the Uvicorn ASGI server.

### a. Start the Server

To start the backend server, run the following command from the project root directory:

```bash
uvicorn app.main:app --reload
```

*   `--reload`: This flag enables auto-reloading, so the server will automatically restart when you make changes to the code.

### b. Access the API

The API will be running at `http://127.0.0.1:8000`.

You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## 5. Running Data Ingestion

The data ingestion scripts can be run from the command line.

### a. Run All Ingesters

To run all data ingesters, use the following command:

```bash
python -m scripts.run_ingestion all
```

### b. Run Specific Ingesters

You can also run specific ingesters and provide custom parameters. For example:

```bash
# Run only the GBIF ingester with custom species
python -m scripts.run_ingestion gbif --species "Ursus maritimus" "Panthera leo"

# Run only the NOAA ingester with a custom date range and stations
python -m scripts.run_ingestion noaa --start_year 2020 --end_year 2022 --stations "GHCND:USW00014733"
```

## 6. Verifying Data

You can verify the data in the database using the `verify_data.py` script:

```bash
python -m scripts.verify_data --checks all
```
