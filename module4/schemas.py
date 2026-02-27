"""Data validation - ensures input/output is correct format."""
from pydantic import BaseModel, Field
from typing import List, Optional

# ── Module 1 ──────────────────────────────────────────────
class CategoryGeneratorRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255)
    product_description: str = Field(..., min_length=10)
    product_price: float = Field(..., gt=0)

class SustainabilityFilter(BaseModel):
    name: str
    confidence: float = Field(..., ge=0, le=1)

class CategoryGeneratorResponse(BaseModel):
    product_id: int
    primary_category: str
    sub_category: str
    seo_tags: List[str] = Field(..., min_length=5, max_length=10)
    sustainability_filters: List[SustainabilityFilter]


# ── Module 4 ──────────────────────────────────────────────
class WhatsAppMessageRequest(BaseModel):
    customer_phone: str = Field(..., min_length=7, max_length=20)
    message: str = Field(..., min_length=1, max_length=1000)

class WhatsAppMessageResponse(BaseModel):
    customer_phone: str
    customer_message: str
    bot_response: str
    intent: str
    escalated: bool
    confidence: float
    processing_time_ms: int
