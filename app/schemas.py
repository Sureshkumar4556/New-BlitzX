import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------- Auth ----------

class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Orders ----------

ALLOWED_SERVICES = {"Website Development", "SEO Optimization", "Digital Marketing", "E-Commerce"}
ALLOWED_BUDGETS = {"Under ₹20,000", "₹20,000 – ₹50,000", "₹50,000 – ₹1,50,000", "₹1,50,000+"}
ALLOWED_TIMELINES = {"ASAP (1–2 weeks)", "1 month", "2–3 months", "Flexible"}
ALLOWED_ORDER_STATUSES = {"pending", "confirmed", "in_progress", "completed", "cancelled"}


class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ALLOWED_ORDER_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(ALLOWED_ORDER_STATUSES))}")
        return v


class OrderCreate(BaseModel):
    service: str
    details: str = Field(min_length=10, max_length=4000)
    budget: str
    timeline: str
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)

    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str) -> str:
        if v not in ALLOWED_SERVICES:
            raise ValueError("Invalid service selected")
        return v

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: str) -> str:
        if v not in ALLOWED_BUDGETS:
            raise ValueError("Invalid budget selected")
        return v

    @field_validator("timeline")
    @classmethod
    def validate_timeline(cls, v: str) -> str:
        if v not in ALLOWED_TIMELINES:
            raise ValueError("Invalid timeline selected")
        return v


class OrderOut(BaseModel):
    id: uuid.UUID
    service: str
    details: str
    budget: str
    timeline: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Leads / Contact ----------

class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    service: str = Field(max_length=120)
    message: str = Field(min_length=10, max_length=4000)
    company: Optional[str] = Field(default="", max_length=200)  # honeypot


class LeadOut(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    service: str
    created_at: datetime

    class Config:
        from_attributes = True
