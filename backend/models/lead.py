from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, DECIMAL, Date, Boolean
from sqlalchemy.sql import func
from core.database import Base


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(String, primary_key=True)  # UUID stored as string
    contact_id = Column(String, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id", ondelete="SET NULL"))
    source = Column(String(50), nullable=False)
    status = Column(String(50), default="new")
    score = Column(Integer, default=0)
    tier = Column(String(20))
    assigned_to = Column(String(100))
    estimated_value = Column(DECIMAL(15, 2))
    probability = Column(Integer, default=0)
    expected_close_date = Column(Date)
    custom_fields = Column(String)  # JSONB stored as string
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_contacted_at = Column(TIMESTAMP(timezone=True))
    next_followup_at = Column(TIMESTAMP(timezone=True))
    interaction_count = Column(Integer, default=0)
    notified_hot = Column(Boolean, default=False)
    notified_at = Column(TIMESTAMP(timezone=True))
