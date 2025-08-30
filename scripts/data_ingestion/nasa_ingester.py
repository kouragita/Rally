import pandas as pd
import requests
import os
from datetime import datetime
from .base_ingester import BaseDataIngester
from app.models import ClimateData, Ecosystem
from app.db.session import SessionLocal

# Constants
DATA_SOURCE = "NASA_GISS"
MEASUREMENT_TYPE = "temperature_anomaly"
UNIT = "celsius"
RAW_DATA_DIR = "data/raw"

class NASAIngester(BaseDataIngester):
    """Ingester for NASA GISS global temperature data"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://data.giss.nasa.gov/gistemp"

    def download_global_temperature_data(self) -> pd.DataFrame:
        """Download and process NASA GISS global temperature data"""
        datasets = {
            'global_land_ocean': 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv',
        }
        all_data = []
        os.makedirs(RAW_DATA_DIR, exist_ok=True)

        for dataset_name, url in datasets.items():
            self.logger.info(f"Downloading NASA dataset: {dataset_name}")
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                filepath = os.path.join(RAW_DATA_DIR, f"nasa_{dataset_name}.csv")
                with open(filepath, 'w') as f:
                    f.write(response.text)

                processed_data = self.process_nasa_temperature_csv(response.text, dataset_name)
                all_data.append(processed_data)
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to download NASA dataset {dataset_name}: {e}")
            except Exception as e:
                self.logger.error(f"Failed to process NASA dataset {dataset_name}: {e}")

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()

    def process_nasa_temperature_csv(self, csv_content: str, dataset_name: str) -> pd.DataFrame:
        """Process NASA temperature CSV data"""
        lines = csv_content.strip().split('\n')
        
        try:
            header_index = [i for i, line in enumerate(lines) if line.startswith('Year')][0]
        except IndexError:
            self.logger.error("Could not find header row in NASA CSV data.")
            return pd.DataFrame()

        data_lines = lines[header_index + 1:]
        data_rows = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for line in data_lines:
            parts = line.split(',')
            if len(parts) < 13: continue
            
            year_str = parts[0]
            try:
                year = int(year_str)
            except ValueError:
                self.logger.warning(f"Skipping invalid year: {year_str}")
                continue

            for i, month_name in enumerate(months):
                if i + 1 < len(parts) and parts[i+1] not in ['***', '****']:
                    try:
                        # NASA data is in hundredths of a degree Celsius
                        temp_anomaly = float(parts[i + 1]) / 100.0
                        date_str = f"{year}-{i+1:02d}-01"
                        data_rows.append({
                            'data_source': DATA_SOURCE,
                            'measurement_type': MEASUREMENT_TYPE,
                            'value': temp_anomaly,
                            'unit': UNIT,
                            'date_recorded': datetime.strptime(date_str, "%Y-%m-%d").date(),
                        })
                    except ValueError:
                        self.logger.warning(f"Could not parse temperature value '{parts[i+1]}' for {month_name} {year}. Skipping.")
                        continue
        return pd.DataFrame(data_rows)

    def ingest(self):
        """Main method to ingest NASA climate data and associate with all ecosystems."""
        self.logger.info("Starting NASA climate data ingestion")
        temperature_data = self.download_global_temperature_data()
        if temperature_data.empty:
            self.logger.info("No NASA temperature data downloaded. Skipping.")
            return

        db = SessionLocal()
        try:
            ecosystems = db.query(Ecosystem).all()
            if not ecosystems:
                self.logger.warning("No ecosystems found in the database. Cannot associate NASA data.")
                return

            # Create a new DataFrame with ecosystem_id for each ecosystem
            all_ecosystem_data = []
            for ecosystem in ecosystems:
                eco_data = temperature_data.copy()
                eco_data['ecosystem_id'] = ecosystem.id
                all_ecosystem_data.append(eco_data)
            
            if all_ecosystem_data:
                full_df = pd.concat(all_ecosystem_data, ignore_index=True)
                self.save_to_database(full_df, ClimateData, db)
                db.commit()
            
        except Exception as e:
            self.logger.error(f"An error occurred during NASA ingestion: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

        self.logger.info("NASA ingestion completed")

if __name__ == "__main__":
    ingester = NASAIngester()
    ingester.ingest()

