from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)

    @field_validator('price')
    @classmethod
    def validate_price_decimal(cls, v: Decimal) -> Decimal:
        """Validate price has at most 2 decimal places"""
        if v.as_tuple().exponent < -2:
            raise ValueError('Price must have at most 2 decimal places')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(default=None, min_length=2, max_length=100)
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)

    @field_validator('price')
    @classmethod
    def validate_price_decimal(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate price has at most 2 decimal places"""
        if v is not None and v.as_tuple().exponent < -2:
            raise ValueError('Price must have at most 2 decimal places')
        return v


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockCheckRequest(BaseModel):
    quantity: int = Field(..., gt=0)


class StockCheckResponse(BaseModel):
    product_id: int
    requested_quantity: int
    available_quantity: int
    is_available: bool