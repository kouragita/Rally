import os
import requests
import pandas as pd
import logging
from typing import Optional, Dict, Any, Type
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.inspection import inspect

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
        log_dir = "scripts/logs"
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'ingestion.log')),
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

    def save_to_database(self, data: pd.DataFrame, model: Type[Base], db: Optional[Session] = None):
        """
        Save processed data to the database.
        If a db session is provided, it uses it; otherwise, it creates a new one.
        """
        if db:
            self._save_with_session(data, model, db)
        else:
            db_session = self.SessionLocal()
            try:
                self._save_with_session(data, model, db_session)
                db_session.commit()
            except Exception as e:
                self.logger.error(f"Failed to save to database for {model.__tablename__}: {e}")
                db_session.rollback()
                raise
            finally:
                db_session.close()

    def _save_with_session(self, data: pd.DataFrame, model: Type[Base], db: Session):
        """Helper method to save data using a provided session."""
        mapper = inspect(model)
        model_columns = {c.key for c in mapper.attrs}
        df_columns = set(data.columns)

        if not df_columns.issubset(model_columns):
            extra_cols = df_columns - model_columns
            self.logger.error(
                f"DataFrame columns do not match {model.__tablename__} model. "
                f"Extra columns in DataFrame: {extra_cols}"
            )
            raise ValueError(f"DataFrame contains columns not present in the {model.__tablename__} model: {extra_cols}")

        records = data.to_dict(orient='records')
        db.bulk_insert_mappings(model, records)
        self.logger.info(f"Staged {len(records)} records for {model.__tablename__} table.")
