from typing import Optional
from pydantic import BaseModel, Field


class FoodListingCreate(BaseModel):
    organisation: Optional[str] = ""
    donorName: Optional[str] = ""
    foodType: str
    quantity: str
    location: str
    pickup_address: Optional[str] = Field(None, alias="pickupAddress")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Valid latitude between -90 and 90")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Valid longitude between -180 and 180")
    cookedTime: Optional[str] = ""
    pickupTime: Optional[str] = ""
    contact: str
    photo: Optional[str] = None

    class Config:
        populate_by_name = True


class FoodListingResponse(BaseModel):
    id: str
    donorId: Optional[str] = None
    donorName: str
    organisation: Optional[str] = ""
    foodType: str
    quantity: str
    location: str
    pickup_address: Optional[str] = None
    pickupAddress: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cookedTime: Optional[str] = ""
    pickupTime: Optional[str] = ""
    contact: str
    status: str
    photo: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class FoodRequestCreate(BaseModel):
    organisation: str
    address: str
    contact: str


class FoodRequestResponse(BaseModel):
    id: str
    receiverId: Optional[str] = None
    organisation: str
    address: str
    contact: str
    status: str

    class Config:
        from_attributes = True
