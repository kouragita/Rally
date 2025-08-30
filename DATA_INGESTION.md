# Data Ingestion Implementation Guide

## Overview

This guide shows you exactly how to download data from external sources and populate your PostgreSQL database. We'll create practical scripts for each major data source.

## Project Structure for Data Ingestion

```
climate_wildlife_backend/
├── scripts/
│   ├── data_ingestion/
│   │   ├── __init__.py
│   │   ├── base_ingester.py
│   │   ├── noaa_ingester.py
│   │   ├── nasa_ingester.py
│   │   ├── gbif_ingester.py
│   │   ├── living_planet_ingester.py
│   │   └── run_ingestion.py
│   └── database_setup.py
├── data/
│   ├── raw/           # Downloaded files
│   ├── processed/     # Cleaned data
│   └── logs/          # Ingestion logs
└── app/
    └── models/        # Your database models
```

## Step 1: Base Ingester Class

**File: `scripts/data_ingestion/base_ingester.py`**

```python
import os
import requests
import pandas as pd
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class BaseDataIngester:
    """Base class for all data ingesters"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for ingestion process"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/logs/ingestion.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def download_file(self, url: str, filepath: str, headers: Optional[Dict] = None) -> bool:
        """Download file from URL"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            response = requests.get(url, headers=headers or {}, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Downloaded: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False
    
    def save_to_database(self, data: pd.DataFrame, table_name: str, ecosystem_type: str = None):
        """Save processed data to database"""
        try:
            # Add metadata columns
            data['ingested_at'] = datetime.utcnow()
            if ecosystem_type:
                data['ecosystem_type'] = ecosystem_type
            
            # Save to database
            data.to_sql(table_name, self.engine, if_exists='append', index=False)
            
            self.logger.info(f"Saved {len(data)} records to {table_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to save to database: {e}")
            raise
```

## Step 2: NOAA Climate Data Ingester

**File: `scripts/data_ingestion/noaa_ingester.py`**

```python
import pandas as pd
from base_ingester import BaseDataIngester
from datetime import datetime, timedelta

class NOAAIngester(BaseDataIngester):
    """Ingester for NOAA climate data"""
    
    def __init__(self, database_url: str, api_key: str = None):
        super().__init__(database_url)
        self.api_key = api_key
        self.base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2"
    
    def get_climate_data(self, start_date: str, end_date: str, station_id: str = "GHCND:USW00014733"):
        """
        Download climate data from NOAA
        Example: Global temperature, precipitation data
        """
        url = f"{self.base_url}/data"
        
        params = {
            'datasetid': 'GHCND',
            'stationid': station_id,
            'startdate': start_date,
            'enddate': end_date,
            'datatypeid': 'TAVG,TMAX,TMIN,PRCP',  # Temperature and precipitation
            'limit': 1000,
            'format': 'json'
        }
        
        headers = {'token': self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            if 'results' in data:
                df = pd.DataFrame(data['results'])
                return self.process_noaa_data(df)
            else:
                self.logger.warning("No NOAA data found for specified parameters")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Failed to fetch NOAA data: {e}")
            return pd.DataFrame()
    
    def process_noaa_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw NOAA data"""
        if df.empty:
            return df
        
        # Clean and standardize data
        processed_data = []
        
        for _, row in df.iterrows():
            processed_row = {
                'source': 'NOAA',
                'station_id': row['station'],
                'date_recorded': pd.to_datetime(row['date']).date(),
                'measurement_type': row['datatype'],
                'value': row['value'],
                'unit': self.get_unit_for_datatype(row['datatype']),
                'location_lat': None,  # Will be populated if available
                'location_lon': None,
                'data_quality': row.get('qflag', 'good')
            }
            processed_data.append(processed_row)
        
        return pd.DataFrame(processed_data)
    
    def get_unit_for_datatype(self, datatype: str) -> str:
        """Get unit for NOAA data type"""
        units = {
            'TAVG': 'celsius',
            'TMAX': 'celsius', 
            'TMIN': 'celsius',
            'PRCP': 'mm'
        }
        return units.get(datatype, 'unknown')
    
    def ingest_climate_data(self, start_year: int = 2020, end_year: int = 2024):
        """Main method to ingest NOAA climate data"""
        self.logger.info(f"Starting NOAA climate data ingestion: {start_year}-{end_year}")
        
        for year in range(start_year, end_year + 1):
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            self.logger.info(f"Processing year {year}")
            
            # Get data
            climate_data = self.get_climate_data(start_date, end_date)
            
            if not climate_data.empty:
                # Classify ecosystems (simplified example)
                climate_data['ecosystem_classification'] = 'terrestrial'  # Default
                
                # Save to database
                self.save_to_database(climate_data, 'climate_data')
                
        self.logger.info("NOAA ingestion completed")
```

## Step 3: GBIF Biodiversity Data Ingester

**File: `scripts/data_ingestion/gbif_ingester.py`**

```python
import requests
import pandas as pd
import time
from base_ingester import BaseDataIngester

class GBIFIngester(BaseDataIngester):
    """Ingester for GBIF biodiversity data"""
    
    def __init__(self, database_url: str):
        super().__init__(database_url)
        self.base_url = "https://api.gbif.org/v1"
    
    def get_species_occurrences(self, species_name: str, limit: int = 10000):
        """Get species occurrence data from GBIF"""
        
        # First, get species key
        species_key = self.get_species_key(species_name)
        if not species_key:
            return pd.DataFrame()
        
        url = f"{self.base_url}/occurrence/search"
        
        params = {
            'taxonKey': species_key,
            'hasCoordinate': 'true',
            'hasGeospatialIssue': 'false',
            'limit': min(limit, 300),  # GBIF API limit per request
            'offset': 0
        }
        
        all_occurrences = []
        
        while len(all_occurrences) < limit:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'results' not in data or not data['results']:
                    break
                
                all_occurrences.extend(data['results'])
                
                # Check if we've got all available data
                if data['endOfRecords']:
                    break
                    
                # Update offset for next request
                params['offset'] += params['limit']
                
                # Rate limiting - be nice to GBIF
                time.sleep(0.1)
                
                self.logger.info(f"Fetched {len(all_occurrences)} occurrences for {species_name}")
                
            except Exception as e:
                self.logger.error(f"Error fetching GBIF data: {e}")
                break
        
        return self.process_gbif_occurrences(all_occurrences, species_name)
    
    def get_species_key(self, species_name: str) -> int:
        """Get GBIF species key for scientific name"""
        url = f"{self.base_url}/species/match"
        params = {'name': species_name}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'usageKey' in data:
                return data['usageKey']
                
        except Exception as e:
            self.logger.error(f"Failed to get species key for {species_name}: {e}")
            
        return None
    
    def process_gbif_occurrences(self, occurrences: list, species_name: str) -> pd.DataFrame:
        """Process GBIF occurrence data"""
        if not occurrences:
            return pd.DataFrame()
        
        processed_data = []
        
        for occurrence in occurrences:
            # Extract ecosystem type from habitat or location
            ecosystem_type = self.classify_ecosystem_from_occurrence(occurrence)
            
            processed_row = {
                'source': 'GBIF',
                'species_scientific_name': species_name,
                'species_common_name': occurrence.get('vernacularName', ''),
                'occurrence_id': occurrence.get('key'),
                'date_recorded': occurrence.get('eventDate', '').split('T')[0] if occurrence.get('eventDate') else None,
                'location_lat': occurrence.get('decimalLatitude'),
                'location_lon': occurrence.get('decimalLongitude'),
                'country': occurrence.get('country'),
                'habitat': occurrence.get('habitat', ''),
                'ecosystem_type': ecosystem_type,
                'occurrence_status': occurrence.get('occurrenceStatus', 'present'),
                'recorded_by': occurrence.get('recordedBy', ''),
                'institution_code': occurrence.get('institutionCode', ''),
                'collection_code': occurrence.get('collectionCode', '')
            }
            processed_data.append(processed_row)
        
        return pd.DataFrame(processed_data)
    
    def classify_ecosystem_from_occurrence(self, occurrence: dict) -> str:
        """Classify ecosystem type from occurrence data"""
        
        # Simple classification based on marine/terrestrial indicators
        habitat = occurrence.get('habitat', '').lower()
        water_body = occurrence.get('waterBody', '').lower()
        
        # Marine/Aquatic indicators
        marine_keywords = ['marine', 'ocean', 'sea', 'coral', 'reef', 'pelagic', 'benthic']
        freshwater_keywords = ['river', 'lake', 'pond', 'stream', 'freshwater']
        
        if any(keyword in habitat or keyword in water_body for keyword in marine_keywords):
            return 'aquatic_marine'
        elif any(keyword in habitat or keyword in water_body for keyword in freshwater_keywords):
            return 'aquatic_freshwater'
        else:
            return 'terrestrial'
    
    def ingest_species_list(self, species_list: list):
        """Ingest data for multiple species"""
        self.logger.info(f"Starting GBIF ingestion for {len(species_list)} species")
        
        for species in species_list:
            self.logger.info(f"Processing species: {species}")
            
            # Get occurrence data
            occurrences = self.get_species_occurrences(species)
            
            if not occurrences.empty:
                # Save to database
                self.save_to_database(occurrences, 'wildlife_occurrences')
            
            # Rate limiting between species
            time.sleep(1)
        
        self.logger.info("GBIF ingestion completed")
```

## Step 4: NASA Climate Data Ingester

**File: `scripts/data_ingestion/nasa_ingester.py`**

```python
import pandas as pd
import requests
from base_ingester import BaseDataIngester

class NASAIngester(BaseDataIngester):
    """Ingester for NASA climate data"""
    
    def __init__(self, database_url: str, api_key: str = None):
        super().__init__(database_url)
        self.api_key = api_key
        self.base_url = "https://data.giss.nasa.gov/gistemp"
    
    def download_global_temperature_data(self):
        """Download NASA GISS global temperature data"""
        
        # NASA provides CSV files for global temperature anomalies
        datasets = {
            'global_land_ocean': 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv',
            'global_land': 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts.csv',
            'northern_hemisphere': 'https://data.giss.nasa.gov/gistemp/tabledata_v4/NH.Ts+dSST.csv',
            'southern_hemisphere': 'https://data.giss.nasa.gov/gistemp/tabledata_v4/SH.Ts+dSST.csv'
        }
        
        all_data = []
        
        for dataset_name, url in datasets.items():
            self.logger.info(f"Downloading NASA dataset: {dataset_name}")
            
            try:
                # Download the CSV file
                response = requests.get(url)
                response.raise_for_status()
                
                # Save raw file
                filepath = f"data/raw/nasa_{dataset_name}.csv"
                with open(filepath, 'w') as f:
                    f.write(response.text)
                
                # Process the data
                processed_data = self.process_nasa_temperature_csv(response.text, dataset_name)
                all_data.append(processed_data)
                
            except Exception as e:
                self.logger.error(f"Failed to download NASA dataset {dataset_name}: {e}")
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            return combined_data
        
        return pd.DataFrame()
    
    def process_nasa_temperature_csv(self, csv_content: str, dataset_name: str) -> pd.DataFrame:
        """Process NASA temperature CSV data"""
        
        # NASA CSV files have a specific format with headers
        lines = csv_content.strip().split('\n')
        
        # Find the data start (usually after some header lines)
        data_start = 0
        for i, line in enumerate(lines):
            if line.startswith('Year'):
                data_start = i
                break
        
        # Read the actual data
        data_lines = lines[data_start:]
        
        # Parse into pandas DataFrame
        data_rows = []
        
        for line in data_lines[1:]:  # Skip header
            parts = line.split(',')
            if len(parts) < 13:  # Year + 12 months
                continue
            
            year = int(parts[0])
            
            # Process monthly data
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            for i, month in enumerate(months):
                if i + 1 < len(parts):
                    try:
                        temp_anomaly = float(parts[i + 1])
                        if temp_anomaly != -999.0:  # NASA uses -999 for missing data
                            data_rows.append({
                                'source': 'NASA_GISS',
                                'dataset': dataset_name,
                                'year': year,
                                'month': i + 1,
                                'date_recorded': f"{year}-{i+1:02d}-01",
                                'measurement_type': 'temperature_anomaly',
                                'value': temp_anomaly,
                                'unit': 'celsius',
                                'baseline': '1951-1980',
                                'ecosystem_classification': 'global'
                            })
                    except ValueError:
                        continue
        
        return pd.DataFrame(data_rows)
    
    def ingest_nasa_data(self):
        """Main method to ingest NASA climate data"""
        self.logger.info("Starting NASA climate data ingestion")
        
        # Download and process temperature data
        temperature_data = self.download_global_temperature_data()
        
        if not temperature_data.empty:
            # Save to database
            self.save_to_database(temperature_data, 'climate_data')
        
        self.logger.info("NASA ingestion completed")
```

## Step 5: Main Ingestion Runner

**File: `scripts/data_ingestion/run_ingestion.py`**

```python
import os
from dotenv import load_dotenv
from noaa_ingester import NOAAIngester
from gbif_ingester import GBIFIngester
from nasa_ingester import NASAIngester

# Load environment variables
load_dotenv()

def main():
    """Main function to run all data ingestion"""
    
    # Database connection
    database_url = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/climate_wildlife')
    
    # API keys
    noaa_api_key = os.getenv('NOAA_API_KEY')
    nasa_api_key = os.getenv('NASA_API_KEY')
    
    print("Starting data ingestion process...")
    
    # 1. Ingest NASA climate data
    print("\n1. Ingesting NASA climate data...")
    nasa_ingester = NASAIngester(database_url, nasa_api_key)
    nasa_ingester.ingest_nasa_data()
    
    # 2. Ingest NOAA climate data
    print("\n2. Ingesting NOAA climate data...")
    noaa_ingester = NOAAIngester(database_url, noaa_api_key)
    noaa_ingester.ingest_climate_data(start_year=2020, end_year=2024)
    
    # 3. Ingest GBIF wildlife data
    print("\n3. Ingesting GBIF wildlife data...")
    gbif_ingester = GBIFIngester(database_url)
    
    # Example species list (you can expand this)
    important_species = [
        'Ursus maritimus',      # Polar bear
        'Panthera leo',         # Lion
        'Chelonia mydas',       # Green sea turtle
        'Salmo salar',          # Atlantic salmon
        'Apis mellifera',       # Honey bee
        'Danaus plexippus',     # Monarch butterfly
        'Fratercula arctica',   # Puffin
        'Thalassarche albatrus' # Albatross
    ]
    
    gbif_ingester.ingest_species_list(important_species)
    
    print("\nData ingestion completed!")

if __name__ == "__main__":
    main()
```

## Step 6: Running the Ingestion

### Setup Commands:

```bash
# 1. Create necessary directories
mkdir -p data/{raw,processed,logs}
mkdir -p scripts/data_ingestion

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your database URL and API keys

# 3. Create database tables (run this first)
python scripts/database_setup.py

# 4. Run the ingestion
python scripts/data_ingestion/run_ingestion.py
```

### Environment Variables (.env):

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/climate_wildlife

# API Keys (optional - many sources work without keys)
NOAA_API_KEY=your_noaa_key_here
NASA_API_KEY=your_nasa_key_here

# Processing settings
BATCH_SIZE=1000
MAX_RECORDS_PER_SOURCE=50000
```

## Step 7: Monitoring Ingestion

### Check Ingestion Progress:

```python
# scripts/check_ingestion_status.py

import pandas as pd
from sqlalchemy import create_engine
import os

def check_data_status():
    """Check what data has been ingested"""
    
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Check climate data
    climate_count = pd.read_sql("SELECT COUNT(*) as count FROM climate_data", engine)
    print(f"Climate data records: {climate_count['count'].iloc[0]}")
    
    # Check wildlife data  
    wildlife_count = pd.read_sql("SELECT COUNT(*) as count FROM wildlife_occurrences", engine)
    print(f"Wildlife occurrence records: {wildlife_count['count'].iloc[0]}")
    
    # Check by source
    sources = pd.read_sql("""
        SELECT source, COUNT(*) as count 
        FROM climate_data 
        GROUP BY source
    """, engine)
    print("\nClimate data by source:")
    print(sources)
    
    # Check ecosystem classifications
    ecosystems = pd.read_sql("""
        SELECT ecosystem_type, COUNT(*) as count 
        FROM wildlife_occurrences 
        GROUP BY ecosystem_type
    """, engine)
    print("\nWildlife data by ecosystem:")
    print(ecosystems)

if __name__ == "__main__":
    check_data_status()
```

## Key Points:

1. **Start Small**: Begin with a few species and recent years, then expand
2. **Rate Limiting**: All scripts include proper delays to respect API limits
3. **Error Handling**: Each ingester logs errors and continues processing
4. **Incremental Updates**: Scripts can be run repeatedly to add new data
5. **Data Validation**: Basic validation and cleaning is included
6. **Ecosystem Classification**: Automatic classification into aquatic/terrestrial

**Run this step by step, and your database will be populated with real climate and wildlife data ready for AI analysis!**