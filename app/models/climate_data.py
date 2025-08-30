from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class ClimateData(Base):
    __tablename__ = "climate_data"

    id = Column(Integer, primary_key=True, index=True)
    ecosystem_id = Column(Integer, ForeignKey("ecosystems.id"))
    data_source = Column(String)
    measurement_type = Column(String)
    value = Column(Numeric)
    unit = Column(String)
    date_recorded = Column(Date)
    location_lat = Column(Numeric)
    location_lon = Column(Numeric)

    ecosystem = relationship("Ecosystem")
