import pandas as pd
import requests
from datetime import datetime
from .base_ingester import BaseDataIngester
from app.models import ClimateData
from app.core.config import settings

class NASAIngester(BaseDataIngester):
    """Ingester for NASA GISS global temperature data"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://data.giss.nasa.gov/gistemp"

    def download_global_temperature_data(self):
        """Download and process NASA GISS global temperature data"""
        datasets = {
            'global_land_ocean': 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv',
        }
        all_data = []
        for dataset_name, url in datasets.items():
            self.logger.info(f"Downloading NASA dataset: {dataset_name}")
            try:
                response = requests.get(url)
                response.raise_for_status()
                filepath = f"data/raw/nasa_{dataset_name}.csv" # Adjusted path
                import os
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write(response.text)
                processed_data = self.process_nasa_temperature_csv(response.text, dataset_name)
                all_data.append(processed_data)
            except Exception as e:
                self.logger.error(f"Failed to process NASA dataset {dataset_name}: {e}")
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()

    def process_nasa_temperature_csv(self, csv_content: str, dataset_name: str) -> pd.DataFrame:
        """Process NASA temperature CSV data"""
        lines = csv_content.strip().split('\n')
        data_start = 0
        for i, line in enumerate(lines):
            if line.startswith('Year'):
                data_start = i
                break
        data_lines = lines[data_start+1:]
        data_rows = []
        for line in data_lines:
            parts = line.split(',')
            if len(parts) < 13: continue
            year = int(parts[0])
            for i, month_name in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                if i + 1 < len(parts) and parts[i+1] != '***':
                    try:
                        temp_anomaly = float(parts[i + 1]) / 100.0
                        date_str = f"{year}-{i+1:02d}-01"
                        data_rows.append({
                            'data_source': 'NASA_GISS',
                            'measurement_type': 'temperature_anomaly',
                            'value': temp_anomaly,
                            'unit': 'celsius',
                            'date_recorded': datetime.strptime(date_str, "%Y-%m-%d").date(),
                        })
                    except ValueError:
                        continue
        return pd.DataFrame(data_rows)

    def ingest(self):
        """Main method to ingest NASA climate data"""
        self.logger.info("Starting NASA climate data ingestion")
        temperature_data = self.download_global_temperature_data()
        if not temperature_data.empty:
            self.save_to_database(temperature_data, ClimateData)
        self.logger.info("NASA ingestion completed")

if __name__ == "__main__":
    ingester = NASAIngester()
    ingester.ingest()
