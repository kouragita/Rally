from sqlalchemy import Column, Integer, String, Numeric, JSON
from app.db.base_class import Base

class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True, index=True)
    scientific_name = Column(String, unique=True, index=True, nullable=False)
    common_name = Column(String)
    conservation_status = Column(String)
    ecosystem_dependencies = Column(JSON)
    climate_sensitivity = Column(Numeric)
