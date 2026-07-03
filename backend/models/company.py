from sqlalchemy import Column, String, Integer, Text, TIMESTAMP
from sqlalchemy.sql import func
from core.database import Base


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String, primary_key=True)  # UUID stored as string
    name = Column(String(255), nullable=False)
    website = Column(String(255))
    domain = Column(String(255))
    industry = Column(String(100))
    size = Column(String(50))
    revenue_range = Column(String(50))
    location = Column(String(255))
    country = Column(String(100))
    employee_count = Column(Integer)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
