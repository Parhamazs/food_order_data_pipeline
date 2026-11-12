from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class OrderItems(BaseModel):
    item_id: int
    name: str
    quantity: int = Field(gt=0, description="must be at least 1 or greater can't be negative")
    unit_price: float = Field(gt=0, description="price must be positive")

class OrderCreateRequest(BaseModel):
    idempotency_key: str = Field(..., description="کلید یکتایی که کلاینت تولید می‌کند تا سفارش دوبار ثبت نشود")
    customer_id: str
    restaurant_id: str
    items: List[OrderItems]
    total_amount: float = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OrderResponse(BaseModel):
    status: str
    message: str
    idempotency_key: str