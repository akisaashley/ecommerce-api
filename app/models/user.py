from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    full_name: str = Field(..., min_length=2, max_length=255)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Basic email validation"""
        if v is not None:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
            return v.lower()
        return v


class UserResponse(UserBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)