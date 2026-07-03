from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from core.database import Base


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(String, primary_key=True)  # UUID stored as string
    company_id = Column(String, ForeignKey("companies.id", ondelete="SET NULL"))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50))
    mobile = Column(String(50))
    title = Column(String(100))
    department = Column(String(100))
    linkedin_url = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
