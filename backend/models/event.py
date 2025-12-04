from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    """Base model with common event fields"""
    title: str = Field(..., min_length=1, description="Event title (non-empty)")
    description: str = Field(..., description="Event description")
    date: str = Field(..., description="Event date in YYYY-MM-DD format")
    location: str = Field(..., min_length=1, description="Event location (non-empty)")
    capacity: int = Field(..., ge=0, description="Event capacity (non-negative)")
    organizer: str = Field(..., min_length=1, description="Event organizer (non-empty)")
    status: str = Field(..., min_length=1, description="Event status (non-empty)")

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate that date is in YYYY-MM-DD format"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class CreateEventRequest(EventBase):
    """Request model for creating a new event"""
    eventId: Optional[str] = Field(None, description="Optional event ID (generated if not provided)")


class UpdateEventRequest(BaseModel):
    """Request model for updating an event (all fields optional for partial updates)"""
    title: Optional[str] = Field(None, min_length=1, description="Event title (non-empty)")
    description: Optional[str] = None
    date: Optional[str] = Field(None, description="Event date in YYYY-MM-DD format")
    location: Optional[str] = Field(None, min_length=1, description="Event location (non-empty)")
    capacity: Optional[int] = Field(None, ge=0, description="Event capacity (non-negative)")
    organizer: Optional[str] = Field(None, min_length=1, description="Event organizer (non-empty)")
    status: Optional[str] = Field(None, min_length=1, description="Event status (non-empty)")

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate that date is in YYYY-MM-DD format if provided"""
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class Event(EventBase):
    """Complete event model with eventId"""
    eventId: str = Field(..., description="Unique event identifier")

    model_config = ConfigDict(from_attributes=True)
