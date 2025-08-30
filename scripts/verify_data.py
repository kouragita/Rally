import argparse
import pandas as pd
from sqlalchemy import func

# Since we are running this as a module from the root, we can use absolute imports
from app.db.session import SessionLocal
from app.db.base_class import Base
from app.models import ClimateData, WildlifeData, Species, Ecosystem, Report

def get_table_count(model):
    """Counts the number of records in a given table."""
    db = SessionLocal()
    try:
        count = db.query(model).count()
        return f"Table '{model.__tablename__}' has {count} records."
    finally:
        db.close()

def check_null_values(model, column_name):
    """Checks for NULL values in a specific column."""
    db = SessionLocal()
    try:
        count = db.query(model).filter(getattr(model, column_name) == None).count()
        return f"Found {count} NULL values in '{model.__tablename__}.{column_name}'." 
    finally:
        db.close()

def get_date_range(model, date_column_name):
    """Gets the minimum and maximum date from a column."""
    db = SessionLocal()
    try:
        min_date, max_date = db.query(
            func.min(getattr(model, date_column_name)),
            func.max(getattr(model, date_column_name))
        ).one()
        return f"Date range for '{model.__tablename__}.{date_column_name}': {min_date} to {max_date}."
    finally:
        db.close()

def get_source_counts(model, source_column_name):
    """Gets the count of records grouped by a source column."""
    db = SessionLocal()
    try:
        results = db.query(
            getattr(model, source_column_name),
            func.count(getattr(model, source_column_name))
        ).group_by(getattr(model, source_column_name)).all()
        
        summary = f"Source counts for '{model.__tablename__}':\n"
        for source, count in results:
            summary += f"  - {source}: {count}\n"
        return summary
    finally:
        db.close()


def main():
    """Main function to run data verification checks."""
    parser = argparse.ArgumentParser(description="Run data verification scripts.")
    parser.add_argument(
        '--checks',
        nargs='+',
        choices=['all', 'counts', 'nulls', 'dates', 'sources'],
        default=['all'],
        help="Specify which verification checks to run."
    )
    args = parser.parse_args()

    checks_to_run = args.checks
    if 'all' in checks_to_run:
        checks_to_run = ['counts', 'nulls', 'dates', 'sources']

    print("--- Starting Data Verification ---")

    # A map of models to the checks they support
    verification_map = {
        Ecosystem: ['counts'],
        Species: ['counts'],
        Report: ['counts'],
        ClimateData: ['counts', 'nulls', 'dates', 'sources'],
        WildlifeData: ['counts', 'nulls', 'dates']
    }

    column_map = {
        ClimateData: {
            'null_check_cols': ['value', 'date_recorded'],
            'date_col': 'date_recorded',
            'source_col': 'data_source'
        },
        WildlifeData: {
            'null_check_cols': ['population_count', 'date_recorded'],
            'date_col': 'date_recorded'
        }
    }

    for model, supported_checks in verification_map.items():
        print(f"\nVerifying table: {model.__tablename__}")
        if 'counts' in checks_to_run and 'counts' in supported_checks:
            print(get_table_count(model))
        
        if 'nulls' in checks_to_run and 'nulls' in supported_checks:
            for col in column_map[model]['null_check_cols']:
                print(check_null_values(model, col))

        if 'dates' in checks_to_run and 'dates' in supported_checks:
            print(get_date_range(model, column_map[model]['date_col']))

        if 'sources' in checks_to_run and 'sources' in supported_checks:
            print(get_source_counts(model, column_map[model]['source_col']))

    print("--- Verification Complete ---")

if __name__ == "__main__":
    # To run this script, use the command:
    # python -m scripts.verify_data --checks all
    # python -m scripts.verify_data --checks counts dates
    main()
