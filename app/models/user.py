from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timezone
import uuid
from app.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, default="Fahad Ali")
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    delivery_address = Column(String, default="Gulberg, Lahore, Pakistan")
    preferred_language = Column(String, default="roman_urdu")  # english, urdu, roman_urdu
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
