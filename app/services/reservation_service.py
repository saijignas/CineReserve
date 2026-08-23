"""Reservation service."""
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from datetime import datetime, timedelta, timezone
from app.models.reservation import Reservation, ReservationStatus
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.showtime_repository import ShowtimeRepository
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from app.config import get_settings

settings = get_settings()


class ReservationService:
    """Reservation service."""

    def __init__(self, db: Session):
        self.db = db
        self.reservation_repo = ReservationRepository()
        self.showtime_repo = ShowtimeRepository()

    def create_reservation(
        self,
        user_id: int,
        showtime_id: int,
        seat_ids: List[int]
    ) -> Reservation:
        """Create a new reservation with pessimistic locking."""
        if len(seat_ids) > settings.MAX_SEATS_PER_BOOKING:
            raise BadRequestException(
                f"Cannot reserve more than {settings.MAX_SEATS_PER_BOOKING} seats per booking"
            )
        
        showtime = self.showtime_repo.get_by_id(self.db, showtime_id)
        if not showtime:
            raise NotFoundException(f"Showtime with ID {showtime_id} not found")
        
        current_time = datetime.now(timezone.utc)
        if showtime.start_time <= current_time:
            raise BadRequestException("Cannot reserve seats for a showtime that has already started")
        
        reservation = self.reservation_repo.reserve_seats_atomic(
            db=self.db,
            user_id=user_id,
            showtime_id=showtime_id,
            seat_ids=seat_ids
        )
        
        return reservation

    def get_reservation(self, reservation_id: int, user_id: Optional[int] = None) -> Reservation:
        """Get reservation by ID."""
        reservation = self.reservation_repo.get_by_id(self.db, reservation_id)
        if not reservation:
            raise NotFoundException(f"Reservation with ID {reservation_id} not found")
        
        if user_id is not None and reservation.user_id != user_id:
            raise ForbiddenException("You don't have permission to view this reservation")
        
        return reservation

    def get_user_reservations(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = None,
        status: Optional[ReservationStatus] = None
    ) -> Tuple[List[Reservation], int]:
        """Get user's reservations."""
        if page_size is None:
            page_size = settings.DEFAULT_PAGE_SIZE
        
        if page < 1:
            page = 1
        if page_size > settings.MAX_PAGE_SIZE:
            page_size = settings.MAX_PAGE_SIZE
        
        skip = (page - 1) * page_size
        
        return self.reservation_repo.get_user_reservations(
            db=self.db,
            user_id=user_id,
            skip=skip,
            limit=page_size,
            status=status
        )

    def get_all_reservations(
        self,
        page: int = 1,
        page_size: int = None,
        status: Optional[ReservationStatus] = None
    ) -> Tuple[List[Reservation], int]:
        """Get all reservations (admin only)."""
        if page_size is None:
            page_size = settings.DEFAULT_PAGE_SIZE
        
        if page < 1:
            page = 1
        if page_size > settings.MAX_PAGE_SIZE:
            page_size = settings.MAX_PAGE_SIZE
        
        skip = (page - 1) * page_size
        
        return self.reservation_repo.get_all_reservations(
            db=self.db,
            skip=skip,
            limit=page_size,
            status=status
        )

    def cancel_reservation(self, reservation_id: int, user_id: int) -> Reservation:
        """Cancel a reservation."""
        reservation = self.get_reservation(reservation_id, user_id)
        
        if reservation.status == ReservationStatus.CANCELLED:
            raise BadRequestException("Reservation is already cancelled")
        
        min_cancellation_time = reservation.showtime.start_time - timedelta(
            hours=settings.MIN_CANCELLATION_HOURS
        )
        
        current_time = datetime.now(timezone.utc)
        if current_time >= min_cancellation_time:
            raise BadRequestException(
                f"Cannot cancel reservation less than {settings.MIN_CANCELLATION_HOURS} "
                f"hours before showtime"
            )
        
        reservation = self.reservation_repo.cancel_reservation(self.db, reservation)
        return reservation
