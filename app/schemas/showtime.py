"""Showtime and Seat Pydantic schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from app.schemas.movie import MovieResponse


class SeatBase(BaseModel):
    """Base seat schema."""
    seat_number: int
    row_letter: str
    is_reserved: bool


class SeatResponse(SeatBase):
    """Schema for seat response."""
    id: int

    class Config:
        from_attributes = True


class ShowtimeBase(BaseModel):
    """Base showtime schema."""
    movie_id: int
    screen_name: str = Field(..., min_length=1, max_length=100)
    start_time: datetime
    end_time: datetime
    base_price: Decimal = Field(..., gt=0)


class ShowtimeCreate(ShowtimeBase):
    """Schema for showtime creation."""
    rows: int = Field(default=10, ge=1, le=26)
    seats_per_row: int = Field(default=10, ge=1, le=50)


class ShowtimeUpdate(BaseModel):
    """Schema for showtime update."""
    screen_name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    base_price: Optional[Decimal] = Field(None, gt=0)


class ShowtimeResponse(ShowtimeBase):
    """Schema for showtime response."""
    id: int
    total_seats: int
    movie: Optional[MovieResponse] = None

    class Config:
        from_attributes = True


class ShowtimeWithSeatsResponse(ShowtimeResponse):
    """Schema for showtime response with seats."""
    seats: List[SeatResponse] = []


class ShowtimeListResponse(BaseModel):
    """Schema for showtime list response."""
    items: List[ShowtimeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
