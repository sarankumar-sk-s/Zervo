from typing import Optional, Literal
from pydantic import BaseModel, Field


class FoodExtractionRequest(BaseModel):
    description: str = Field(..., min_length=1, description="Natural-language description of food surplus")


class FoodExtractionResponse(BaseModel):
    food_name: Optional[str] = Field(None, description="Name of the food item, null if not mentioned")
    quantity: Optional[int] = Field(None, description="Extracted numerical quantity, null if not explicitly mentioned")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g. packets, meals, kg, litres, boxes, portions)")
    food_type: Literal["vegetarian", "non_vegetarian", "vegan", "unknown"] = Field(
        "unknown",
        description="Type of food classification"
    )
    prepared_time: Optional[str] = Field(None, description="Time food was prepared if mentioned, null otherwise")
    expiry_time: Optional[str] = Field(None, description="Expiry time if explicitly mentioned, null otherwise")
    description: Optional[str] = Field(None, description="Short normalized description of the donation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")

    class Config:
        json_schema_extra = {
            "example": {
                "food_name": "Veg Biryani",
                "quantity": 30,
                "unit": "packets",
                "food_type": "vegetarian",
                "prepared_time": "7 PM",
                "expiry_time": None,
                "description": "30 packets of veg biryani",
                "confidence": 0.95
            }
        }
