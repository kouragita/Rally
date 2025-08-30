import pandas as pd
import requests
import time
from datetime import datetime
from sqlalchemy.orm import Session
from .base_ingester import BaseDataIngester
from app.models import Species, WildlifeData

# Constants
GBIF_API_URL = "https://api.gbif.org/v1"
DEFAULT_OCCURRENCE_LIMIT = 200

# Bounding boxes for ecosystem mapping
# TODO: This is a simplified approach. A more robust solution would use a geospatial library.
ECOSYSTEM_BOUNDING_BOXES = {
    # Arctic Terrestrial Systems (simplified to a box around the arctic circle)
    3: {"min_lat": 66.5, "max_lat": 90, "min_lon": -180, "max_lon": 180},
    # Temperate Ecosystem Complexes (simplified to a box around Europe)
    5: {"min_lat": 35, "max_lat": 60, "min_lon": -10, "max_lon": 40},
    # Arid and Semi-Arid Systems (simplified to a box around the Sahara)
    6: {"min_lat": 15, "max_lat": 35, "min_lon": -15, "max_lon": 35},
}

class GBIFIngester(BaseDataIngester):
    """Ingester for GBIF biodiversity data"""

    def __init__(self):
        super().__init__()
        self.base_url = GBIF_API_URL

    def get_ecosystem_by_location(self, lat: float, lon: float) -> int | None:
        """Get ecosystem ID by location using bounding boxes."""
        for eco_id, bbox in ECOSYSTEM_BOUNDING_BOXES.items():
            if bbox["min_lat"] <= lat <= bbox["max_lat"] and bbox["min_lon"] <= lon <= bbox["max_lon"]:
                return eco_id
        return None # Return None if no ecosystem is found

    def get_or_create_species(self, db: Session, scientific_name: str) -> Species:
        """Gets a species from the DB or creates it if it doesn't exist within the same transaction."""
        species = db.query(Species).filter(Species.scientific_name == scientific_name).first()
        if species:
            return species
        
        self.logger.info(f"Creating new species: {scientific_name}")
        new_species = Species(scientific_name=scientific_name)
        db.add(new_species)
        # The commit is handled by the main ingest method
        return new_species

    def get_species_key(self, species_name: str) -> int | None:
        """Get GBIF's internal key for a species."""
        url = f"{self.base_url}/species/match"
        params = {'name': species_name, 'strict': 'true'}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('usageKey'):
                return data['usageKey']
            self.logger.warning(f"No usageKey found for {species_name} in GBIF match.")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API error getting species key for {species_name}: {e}")
            return None

    def get_species_occurrences(self, species_key: int, limit: int) -> pd.DataFrame:
        """Get species occurrence data from GBIF."""
        url = f"{self.base_url}/occurrence/search"
        params = {
            'taxonKey': species_key,
            'hasCoordinate': 'true',
            'hasGeospatialIssue': 'false',
            'limit': limit,
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if 'results' in data and data['results']:
                return pd.DataFrame(data['results'])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching GBIF occurrences for key {species_key}: {e}")
        return pd.DataFrame()

    def process_occurrences(self, df: pd.DataFrame, species_id: int) -> pd.DataFrame:
        """Process raw GBIF occurrence data into the format for our WildlifeData model."""
        if df.empty:
            return df

        processed_rows = []
        skipped_rows = 0
        for _, row in df.iterrows():
            try:
                if pd.isna(row.get('eventDate')) or pd.isna(row.get('decimalLatitude')) or pd.isna(row.get('decimalLongitude')):
                    skipped_rows += 1
                    continue
                
                lat = row['decimalLatitude']
                lon = row['decimalLongitude']
                ecosystem_id = self.get_ecosystem_by_location(lat, lon)

                if not ecosystem_id:
                    skipped_rows += 1
                    continue

                date_str = str(row['eventDate']).split('T')[0]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

                pop_count = row.get('individualCount')
                
                processed_rows.append({
                    'species_id': species_id,
                    'ecosystem_id': ecosystem_id,
                    # Default to 1 individual if count is not provided, as this is an occurrence record.
                    'population_count': int(pop_count) if pd.notna(pop_count) and pop_count > 0 else 1,
                    'date_recorded': date_obj,
                    'location_lat': lat,
                    'location_lon': lon,
                })
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Skipping row due to data conversion error: {e} - Data: {row.get('eventDate')}")
                skipped_rows += 1
                continue
        
        if skipped_rows > 0:
            self.logger.info(f"Skipped {skipped_rows} rows for species ID {species_id} due to missing or invalid data.")

        return pd.DataFrame(processed_rows)

    def ingest(self, species_list: list[str], limit_per_species: int = DEFAULT_OCCURRENCE_LIMIT):
        """Main method to ingest GBIF data for a list of species using a single DB session."""
        self.logger.info(f"Starting GBIF ingestion for {len(species_list)} species.")
        db = self.SessionLocal()
        try:
            for name in species_list:
                self.logger.info(f"--- Processing: {name} ---")
                
                # Get or create the species record
                species_record = self.get_or_create_species(db, name)
                db.flush() # Flush to get the ID of a newly created species

                species_key = self.get_species_key(name)
                if not species_key:
                    self.logger.warning(f"Could not find species key for {name}. Skipping.")
                    continue

                occurrences_df = self.get_species_occurrences(species_key, limit_per_species)
                if occurrences_df.empty:
                    self.logger.info(f"No occurrences found for {name}.")
                    continue

                processed_df = self.process_occurrences(occurrences_df, species_record.id)
                if processed_df.empty:
                    self.logger.info(f"No processable occurrences found for {name}.")
                    continue
                
                # Save data using the existing session
                self.save_to_database(processed_df, WildlifeData, db)
            
            self.logger.info("Committing all changes to the database.")
            db.commit()

        except Exception as e:
            self.logger.error(f"An error occurred during GBIF ingestion. Rolling back changes.", exc_info=True)
            db.rollback()
        finally:
            db.close()
        self.logger.info("GBIF ingestion completed.")

if __name__ == "__main__":
    species_to_ingest = [
        'Ursus maritimus',      # Polar Bear
        'Panthera leo',         # Lion
        'Chelonia mydas',       # Green Sea Turtle
        'Salmo salar',          # Atlantic Salmon
        'Danaus plexippus',     # Monarch Butterfly
    ]
    ingester = GBIFIngester()
    ingester.ingest(species_to_ingest, limit_per_species=500)
