from datetime import datetime
from enum import Enum
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    discontinued = "discontinued"


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(default=None, min_length=2, max_length=100)
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    status: Optional[ProductStatus] = None


class ProductResponse(ProductBase):
    id: int
    status: ProductStatus
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