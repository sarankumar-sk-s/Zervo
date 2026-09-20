import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float
from app.database.session import Base


class FoodListing(Base):
    __tablename__ = "food_listings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    donor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    donor_name = Column(String(255), nullable=False)
    organisation = Column(String(255), nullable=True, default="")
    food_type = Column(String(50), nullable=False)
    quantity = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    pickup_address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    cooked_time = Column(String(100), nullable=True, default="")
    pickup_time = Column(String(100), nullable=True, default="")
    contact = Column(String(100), nullable=False)
    status = Column(String(50), default="available")  # available, claimed, completed
    photo = Column(Text, nullable=True)
    claimed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FoodRequest(Base):
    __tablename__ = "food_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    receiver_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    organisation = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    contact = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")  # pending, accepted, fulfilled
    created_at = Column(DateTime, default=datetime.utcnow)
