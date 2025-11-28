# backend/models/user.py

from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from typing import Optional
from datetime import datetime


# ---------------------------------------------------------
# Base user model
# ---------------------------------------------------------
class UserBase(BaseModel):
    email: Optional[EmailStr] = Field(
        None, description="User email (optional, must be valid if provided)"
    )
    phone: Optional[str] = Field(
        None, pattern=r"^\+?\d{10,15}$", description="Phone number with 10-15 digits"
    )

    # Normalize fields
    @field_validator("phone")
    def normalize_phone(cls, v):
        if v:
            return v.strip()
        return v

    # Ensure at least one contact is present
    @model_validator(mode="after")
    def validate_identity(self):
        if not self.email and not self.phone:
            raise ValueError("User must have at least an email or phone.")
        return self

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# User creation model
# ---------------------------------------------------------
class UserCreate(UserBase):
    """Payload used during user creation."""
    pass


# ---------------------------------------------------------
# User model stored/returned from DB
# ---------------------------------------------------------
class User(UserBase):
    id: str = Field(..., description="MongoDB document ID as string")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

    @classmethod
    def from_mongo(cls, data: dict) -> "User":
        """Convert MongoDB document to User model"""
        if data.get("_id"):
            data["id"] = str(data["_id"])
        return cls(**data)