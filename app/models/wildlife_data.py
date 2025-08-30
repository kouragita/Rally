from sqlalchemy import Column, Integer, Date, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class WildlifeData(Base):
    __tablename__ = "wildlife_data"

    id = Column(Integer, primary_key=True, index=True)
    species_id = Column(Integer, ForeignKey("species.id"))
    ecosystem_id = Column(Integer, ForeignKey("ecosystems.id"))
    population_count = Column(Integer)
    habitat_quality_score = Column(Numeric)
    migration_pattern = Column(JSON)
    date_recorded = Column(Date)
    location_lat = Column(Numeric)
    location_lon = Column(Numeric)

    species = relationship("Species")
    ecosystem = relationship("Ecosystem")
