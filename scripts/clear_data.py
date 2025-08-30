from app.db.session import SessionLocal
from app.models.climate_data import ClimateData
from app.models.wildlife_data import WildlifeData

def clear_data():
    db = SessionLocal()
    try:
        print("Clearing climate_data table...")
        db.query(ClimateData).delete()
        print("Clearing wildlife_data table...")
        db.query(WildlifeData).delete()
        db.commit()
        print("Tables cleared successfully.")
    except Exception as e:
        print(f"An error occurred while clearing the tables: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_data()
