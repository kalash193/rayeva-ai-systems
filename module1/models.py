"""Database models - define what data looks like."""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    """Product table in database."""
    __tablename__ = "products"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    price = Column(Float, nullable=False)
    
    # AI-generated data
    primary_category = Column(String(100))
    sub_category = Column(String(100))
    seo_tags = Column(JSON, default=list)
    sustainability_filters = Column(JSON, default=list)
    
    # Metadata
    ai_processed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AILog(Base):
    """Log all AI requests for debugging."""
    __tablename__ = "ai_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String(100), nullable=False)
    input_data = Column(JSON, nullable=False)
    prompt = Column(String(2000), nullable=False)
    ai_response = Column(JSON, nullable=False)
    tokens_used = Column(Integer)
    processing_time_ms = Column(Integer)
    status = Column(String(50), default="success")
    error_message = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)