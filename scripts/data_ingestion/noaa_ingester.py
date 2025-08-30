import pandas as pd
import requests
import time
from datetime import datetime
from .base_ingester import BaseDataIngester
from app.models import ClimateData
from app.core.config import settings

# Constants
NOAA_API_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
DATA_SOURCE_NAME = "NOAA_GHCND"

# A more robust mapping of NOAA datatypes to units
DATATYPE_TO_UNIT = {
    'TAVG': 'celsius',
    'TMAX': 'celsius',
    'TMIN': 'celsius',
    'PRCP': 'mm'
}

# Mapping of station IDs to ecosystem IDs
# TODO: This should be moved to a more robust location, like a database table or a config file.
STATION_TO_ECOSYSTEM = {
    "GHCND:USW00014733": 5, # NYC -> Temperate Ecosystem Complexes
    "GHCND:UK000003772": 5, # London -> Temperate Ecosystem Complexes
}

class NOAAIngester(BaseDataIngester):
    """Ingester for NOAA Global Historical Climatology Network (GHCN) data."""

    def __init__(self):
        super().__init__()
        self.api_key = settings.NOAA_API_KEY
        self.base_url = NOAA_API_URL
        if not self.api_key:
            raise ValueError("NOAA API Key is not set in the environment.")

    def get_climate_data(self, start_date: str, end_date: str, station_id: str) -> pd.DataFrame:
        """Download climate data from NOAA, handling pagination."""
        headers = {'token': self.api_key}
        params = {
            'datasetid': 'GHCND',
            'stationid': station_id,
            'startdate': start_date,
            'enddate': end_date,
            'datatypeid': list(DATATYPE_TO_UNIT.keys()),
            'limit': 1000,  # Max limit per request
            'units': 'metric',
            'offset': 0
        }
        all_results = []

        while True:
            try:
                response = requests.get(f"{self.base_url}/data", params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                results = data.get('results', [])
                if not results:
                    break
                
                all_results.extend(results)
                
                # Check if we need to paginate
                current_count = len(results)
                total_count = data.get('metadata', {}).get('resultset', {}).get('count', 0)
                params['offset'] += params['limit']
                
                if params['offset'] >= total_count:
                    break

                time.sleep(0.2) # Be nice to the API

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to fetch NOAA data for station {station_id}: {e}")
                return pd.DataFrame() # Return empty on error

        return pd.DataFrame(all_results)

    def process_data(self, df: pd.DataFrame, station_id: str, ecosystem_id: int) -> pd.DataFrame:
        """Process raw NOAA data into the format for our ClimateData model."""
        if df.empty:
            return df

        processed_rows = []
        for _, row in df.iterrows():
            try:
                date_obj = datetime.strptime(row['date'].split('T')[0], "%Y-%m-%d").date()
                datatype = row['datatype']
                processed_rows.append({
                    'data_source': f"{DATA_SOURCE_NAME}:{station_id}",
                    'measurement_type': datatype,
                    'value': row['value'],
                    'unit': DATATYPE_TO_UNIT.get(datatype, 'unknown'),
                    'date_recorded': date_obj,
                    'ecosystem_id': ecosystem_id,
                })
            except (ValueError, TypeError, KeyError) as e:
                self.logger.warning(f"Skipping row for station {station_id} due to data conversion error: {e}")
                continue
        return pd.DataFrame(processed_rows)

    def ingest(self, start_year: int, end_year: int, station_ids: list[str] = None):
        """Main method to ingest NOAA data for a list of stations and a range of years."""
        if station_ids is None:
            station_ids = list(STATION_TO_ECOSYSTEM.keys())

        self.logger.info(f"Starting NOAA climate data ingestion for stations {station_ids} from {start_year}-{end_year}")
        
        for station_id in station_ids:
            ecosystem_id = STATION_TO_ECOSYSTEM.get(station_id)
            if not ecosystem_id:
                self.logger.warning(f"No ecosystem mapping found for station {station_id}. Skipping.")
                continue

            self.logger.info(f"Processing station: {station_id} (Ecosystem: {ecosystem_id})...")
            for year in range(start_year, end_year + 1):
                self.logger.info(f"  - Processing year {year}...")
                start_date = f"{year}-01-01"
                end_date = f"{year}-12-31"
                
                raw_df = self.get_climate_data(start_date, end_date, station_id)
                if not raw_df.empty:
                    processed_df = self.process_data(raw_df, station_id, ecosystem_id)
                    if not processed_df.empty:
                        self.save_to_database(processed_df, ClimateData)
                
                time.sleep(0.2) # Be nice between years

        self.logger.info("NOAA ingestion completed.")

if __name__ == "__main__":
    current_year = datetime.now().year
    ingester = NOAAIngester()
    # Example: Ingest data for the last 2 full years for a list of stations
    ingester.ingest(
        start_year=current_year - 3,
        end_year=current_year - 1,
        station_ids=["GHCND:USW00014733", "GHCND:UK000003772"] # NYC and London
    )
