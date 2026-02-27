"""Data validation - ensures input/output is correct format."""
from pydantic import BaseModel, Field
from typing import List

# INPUT - What user sends us
class CategoryGeneratorRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255)
    product_description: str = Field(..., min_length=10)
    product_price: float = Field(..., gt=0)

# OUTPUT - What we send back
class SustainabilityFilter(BaseModel):
    name: str
    confidence: float = Field(..., ge=0, le=1)

class CategoryGeneratorResponse(BaseModel):
    product_id: int
    primary_category: str
    sub_category: str
    seo_tags: List[str] = Field(..., min_items=5, max_items=10)
    sustainability_filters: List[SustainabilityFilter]
