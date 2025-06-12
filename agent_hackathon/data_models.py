# data_models.py
"""
Pydantic models for the ElectroStore data structures.
These models provide type safety and validation for our customer support system.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import date
from decimal import Decimal


class OrderItem(BaseModel):
    """Represents an item within an order"""
    product_id: str
    quantity: int = Field(gt=0)  # Quantity must be positive
    price: Decimal = Field(decimal_places=2)


class Order(BaseModel):
    """Order model with all relevant details"""
    order_id: str
    customer_id: str
    status: str
    total_amount: Decimal = Field(decimal_places=2)
    order_date: date
    tracking_number: Optional[str] = None
    items: List[OrderItem]

class Customer(BaseModel):
    """Customer model with contact and account information"""
    customer_id: str
    name: str
    email: str
    phone: str
    address: str

class Product(BaseModel):
    """Product model with specifications"""
    product_id: str
    name: str
    category: str
    price: Decimal = Field(decimal_places=2)
    stock_count: int = Field(ge=0)  # Stock must be non-negative
    description: str

class SearchResult(BaseModel):
    """Search results containing matching products"""
    query: str
    products: List[Product]
    results_count: int