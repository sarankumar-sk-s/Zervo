import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True, default="")
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=True, default="")
    points = Column(Integer, default=0)
    deliveries = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
