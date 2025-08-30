import os
import requests
import pandas as pd
import logging
from typing import Optional, Dict, Any, Type
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path to allow importing from app
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1])) # Adjusted parents index

from app.core.config import settings
from app.db.base_class import Base

class BaseDataIngester:
    """Base class for all data ingesters"""

    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for ingestion process"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scripts/ingestion.log'), # Adjusted path
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

    def save_to_database(self, data: pd.DataFrame, model: Type[Base]):
        """Save processed data to database by mapping DataFrame rows to the SQLAlchemy model."""
        db = self.SessionLocal()
        try:
            records = data.to_dict(orient='records')
            db.bulk_insert_mappings(model, records)
            db.commit()
            self.logger.info(f"Saved {len(records)} records to {model.__tablename__} table.")
        except Exception as e:
            self.logger.error(f"Failed to save to database: {e}")
            db.rollback()
            raise
        finally:
            db.close()
