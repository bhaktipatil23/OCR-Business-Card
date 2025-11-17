from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # User name from popup
    team = Column(String(255), nullable=False)  # Team name from popup
    batch_id = Column(String(255), unique=True, nullable=False, index=True)  # Batch ID as foreign key
    event = Column(String(255), nullable=False)  # Event name from popup
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    business_cards = relationship("BusinessCard", back_populates="event")

class BusinessCard(Base):
    __tablename__ = "business_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(255), ForeignKey("events.batch_id"), nullable=False, index=True)
    
    # Extracted OCR data
    name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    designation = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    event = relationship("Event", back_populates="business_cards")