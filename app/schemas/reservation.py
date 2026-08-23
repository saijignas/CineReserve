"""Reservation Pydantic schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from decimal import Decimal
from app.models.reservation import ReservationStatus
from app.schemas.showtime import ShowtimeResponse, SeatResponse


class ReservationCreate(BaseModel):
    """Schema for reservation creation."""
    showtime_id: int
    seat_ids: List[int] = Field(..., min_items=1, max_items=10)


class ReservationResponse(BaseModel):
    """Schema for reservation response."""
    id: int
    user_id: int
    showtime_id: int
    total_price: Decimal
    status: ReservationStatus
    created_at: datetime
    showtime: ShowtimeResponse | None = None
    seats: List[SeatResponse] = []

    class Config:
        from_attributes = True


class ReservationListResponse(BaseModel):
    """Schema for reservation list response."""
    items: List[ReservationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
