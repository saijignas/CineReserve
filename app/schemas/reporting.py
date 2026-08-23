"""Reporting Pydantic schemas."""
from pydantic import BaseModel
from decimal import Decimal
from typing import List
from datetime import date


class RevenueByMovieResponse(BaseModel):
    """Schema for revenue report by movie."""
    movie_id: int
    movie_title: str
    total_revenue: Decimal
    total_bookings: int
    total_seats_sold: int


class RevenueReportResponse(BaseModel):
    """Schema for revenue report response."""
    start_date: date | None
    end_date: date | None
    total_revenue: Decimal
    total_bookings: int
    total_seats_sold: int
    by_movie: List[RevenueByMovieResponse]


class CapacityReportItem(BaseModel):
    """Schema for capacity report item."""
    showtime_id: int
    movie_title: str
    screen_name: str
    start_time: str
    total_seats: int
    reserved_seats: int
    available_seats: int
    utilization_percentage: float


class CapacityReportResponse(BaseModel):
    """Schema for capacity report response."""
    items: List[CapacityReportItem]
    total_capacity: int
    total_reserved: int
    total_available: int
    overall_utilization_percentage: float
