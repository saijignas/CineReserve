"""Reservations API routes."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.services.reservation_service import ReservationService
from app.services.reporting_service import ReportingService
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationListResponse
from app.schemas.reporting import RevenueReportResponse, CapacityReportResponse
from app.schemas.showtime import SeatResponse
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.models.reservation import ReservationStatus
import math

router = APIRouter()


@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation_data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reserve seats for a showtime."""
    reservation_service = ReservationService(db)
    reservation = reservation_service.create_reservation(
        user_id=current_user.id,
        showtime_id=reservation_data.showtime_id,
        seat_ids=reservation_data.seat_ids
    )
    
    return _transform_reservation(reservation)


@router.get("/my", response_model=ReservationListResponse)
def get_my_reservations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ReservationStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's reservations."""
    reservation_service = ReservationService(db)
    reservations, total = reservation_service.get_user_reservations(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status
    )
    
    reservation_responses = [_transform_reservation(r) for r in reservations]
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return ReservationListResponse(
        items=reservation_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/admin/all", response_model=ReservationListResponse)
def get_all_reservations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ReservationStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get all reservations (Admin only)."""
    reservation_service = ReservationService(db)
    reservations, total = reservation_service.get_all_reservations(
        page=page,
        page_size=page_size,
        status=status
    )
    
    reservation_responses = [_transform_reservation(r) for r in reservations]
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return ReservationListResponse(
        items=reservation_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reservation by ID."""
    reservation_service = ReservationService(db)
    reservation = reservation_service.get_reservation(
        reservation_id=reservation_id,
        user_id=current_user.id
    )
    
    return _transform_reservation(reservation)


@router.delete("/{reservation_id}", status_code=status.HTTP_200_OK, response_model=ReservationResponse)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a reservation."""
    reservation_service = ReservationService(db)
    reservation = reservation_service.cancel_reservation(
        reservation_id=reservation_id,
        user_id=current_user.id
    )
    
    return _transform_reservation(reservation)


@router.get("/admin/revenue", response_model=RevenueReportResponse)
def get_revenue_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    movie_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get revenue report (Admin only)."""
    reporting_service = ReportingService(db)
    report = reporting_service.get_revenue_report(
        start_date=start_date,
        end_date=end_date,
        movie_id=movie_id
    )
    return report


@router.get("/admin/capacity", response_model=CapacityReportResponse)
def get_capacity_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    movie_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get capacity utilization report (Admin only)."""
    reporting_service = ReportingService(db)
    report = reporting_service.get_capacity_report(
        start_date=start_date,
        end_date=end_date,
        movie_id=movie_id
    )
    return report


def _transform_reservation(reservation) -> dict:
    """Transform reservation for response."""
    showtime = reservation.showtime
    if showtime:
        movie = showtime.movie
        if movie:
            genres = [mg.genre for mg in movie.movie_genres]
            movie_dict = {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "poster_url": movie.poster_url,
                "duration_minutes": movie.duration_minutes,
                "release_date": movie.release_date,
                "created_at": movie.created_at,
                "genres": genres
            }
        else:
            movie_dict = None
        
        showtime_dict = {
            "id": showtime.id,
            "movie_id": showtime.movie_id,
            "screen_name": showtime.screen_name,
            "start_time": showtime.start_time,
            "end_time": showtime.end_time,
            "base_price": showtime.base_price,
            "total_seats": showtime.total_seats,
            "movie": movie_dict
        }
    else:
        showtime_dict = None
    
    seats = [SeatResponse(
        id=rs.seat.id,
        seat_number=rs.seat.seat_number,
        row_letter=rs.seat.row_letter,
        is_reserved=rs.seat.is_reserved
    ) for rs in reservation.reservation_seats]
    
    return ReservationResponse(
        id=reservation.id,
        user_id=reservation.user_id,
        showtime_id=reservation.showtime_id,
        total_price=reservation.total_price,
        status=reservation.status,
        created_at=reservation.created_at,
        showtime=showtime_dict,
        seats=seats
    )
