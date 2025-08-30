import pandas as pd
import requests
import time
from datetime import datetime
from sqlalchemy.orm import Session
from .base_ingester import BaseDataIngester
from app.models import Species, WildlifeData

class GBIFIngester(BaseDataIngester):
    """Ingester for GBIF biodiversity data"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.gbif.org/v1"

    def get_or_create_species(self, db: Session, scientific_name: str) -> Species:
        """Gets a species from the DB or creates it if it doesn't exist."""
        species = db.query(Species).filter(Species.scientific_name == scientific_name).first()
        if species:
            self.logger.info(f"Found existing species: {scientific_name}")
            return species
        else:
            self.logger.info(f"Creating new species: {scientific_name}")
            new_species = Species(scientific_name=scientific_name)
            db.add(new_species)
            db.commit()
            db.refresh(new_species)
            return new_species

    def get_species_key(self, species_name: str) -> int | None:
        """Get GBIF's internal key for a species."""
        url = f"{self.base_url}/species/match"
        params = {'name': species_name, 'strict': 'true'}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if 'usageKey' in data:
                return data['usageKey']
            self.logger.warning(f"No usageKey found for {species_name}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get species key for {species_name}: {e}")
            return None

    def get_species_occurrences(self, species_key: int, limit: int = 200) -> pd.DataFrame:
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
        except Exception as e:
            self.logger.error(f"Error fetching GBIF occurrences: {e}")
        return pd.DataFrame()

    def process_occurrences(self, df: pd.DataFrame, species_id: int) -> pd.DataFrame:
        """Process raw GBIF occurrence data into the format for our WildlifeData model."""
        if df.empty:
            return df

        processed_rows = []
        for _, row in df.iterrows():
            try:
                if 'eventDate' not in row or not row['eventDate'] or pd.isna(row['eventDate']):
                    continue
                
                date_str = row['eventDate'].split('T')[0]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

                pop_count = row.get('individualCount')
                
                processed_rows.append({
                    'species_id': species_id,
                    'population_count': int(pop_count) if pd.notna(pop_count) else 1,
                    'date_recorded': date_obj,
                    'location_lat': row.get('decimalLatitude'),
                    'location_lon': row.get('decimalLongitude'),
                })
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Skipping row due to data conversion error: {e} - Data: {row}")
                continue
        
        return pd.DataFrame(processed_rows)

    def ingest(self, species_list: list[str]):
        """Main method to ingest GBIF data for a list of species."""
        self.logger.info(f"Starting GBIF ingestion for {len(species_list)} species")
        db = self.SessionLocal()
        try:
            for name in species_list:
                self.logger.info(f"--- Processing: {name} ---")
                species_record = self.get_or_create_species(db, name)
                species_key = self.get_species_key(name)

                if not species_key:
                    continue

                occurrences_df = self.get_species_occurrences(species_key)
                if occurrences_df.empty:
                    self.logger.info(f"No occurrences found for {name}")
                    continue

                processed_df = self.process_occurrences(occurrences_df, species_record.id)
                if processed_df.empty:
                    self.logger.info(f"No processable occurrences found for {name}")
                    continue
                
                self.save_to_database(processed_df, WildlifeData)
                
                time.sleep(1) # Be nice to the API
        except Exception as e:
            self.logger.error(f"An error occurred during ingestion: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()
        self.logger.info("GBIF ingestion completed")

if __name__ == "__main__":
    species_to_ingest = [
        'Ursus maritimus',      # Polar Bear
        'Panthera leo',         # Lion
        'Chelonia mydas',       # Green Sea Turtle
        'Salmo salar',          # Atlantic Salmon
        'Danaus plexippus',     # Monarch Butterfly
    ]
    ingester = GBIFIngester()
    ingester.ingest(species_to_ingest)
