from sqlalchemy import Column, Integer, String, Enum, Text
from app.db.base_class import Base

class Ecosystem(Base):
    __tablename__ = "ecosystems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    type = Column(Enum("aquatic", "terrestrial", name="ecosystem_type_enum"), nullable=False)
    subtype = Column(String)
    description = Column(Text)
