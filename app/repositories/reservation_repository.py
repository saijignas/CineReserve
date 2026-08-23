"""Reservation repository for database operations."""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional, Tuple
from decimal import Decimal
from app.models.reservation import Reservation, ReservationStatus, ReservationSeat
from app.models.showtime import Seat, Showtime
from app.core.exceptions import ConflictException, BadRequestException
import logging

logger = logging.getLogger(__name__)


class ReservationRepository:
    """Reservation repository with pessimistic locking for seat reservation."""

    @staticmethod
    def get_by_id(db: Session, reservation_id: int) -> Optional[Reservation]:
        """Get reservation by ID with relationships."""
        return db.query(Reservation).options(
            joinedload(Reservation.showtime).joinedload(Showtime.movie),
            joinedload(Reservation.reservation_seats).joinedload(ReservationSeat.seat)
        ).filter(Reservation.id == reservation_id).first()

    @staticmethod
    def get_user_reservations(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[ReservationStatus] = None
    ) -> Tuple[List[Reservation], int]:
        """Get reservations for a specific user."""
        query = db.query(Reservation).options(
            joinedload(Reservation.showtime).joinedload(Showtime.movie),
            joinedload(Reservation.reservation_seats).joinedload(ReservationSeat.seat)
        ).filter(Reservation.user_id == user_id)
        
        if status:
            query = query.filter(Reservation.status == status)
        
        total = query.count()
        reservations = query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()
        
        return reservations, total

    @staticmethod
    def get_all_reservations(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[ReservationStatus] = None
    ) -> Tuple[List[Reservation], int]:
        """Get all reservations (admin)."""
        query = db.query(Reservation).options(
            joinedload(Reservation.showtime).joinedload(Showtime.movie),
            joinedload(Reservation.reservation_seats).joinedload(ReservationSeat.seat),
            joinedload(Reservation.user)
        )
        
        if status:
            query = query.filter(Reservation.status == status)
        
        total = query.count()
        reservations = query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()
        
        return reservations, total

    @staticmethod
    def reserve_seats_atomic(
        db: Session,
        user_id: int,
        showtime_id: int,
        seat_ids: List[int]
    ) -> Reservation:
        """Reserve seats atomically using pessimistic locking (SELECT FOR UPDATE)."""
        try:
            logger.info(f"Starting atomic seat reservation for user {user_id}, showtime {showtime_id}")
            
            seats = db.query(Seat).filter(
                and_(
                    Seat.id.in_(seat_ids),
                    Seat.showtime_id == showtime_id
                )
            ).with_for_update().all()
            
            logger.info(f"Acquired locks on {len(seats)} seats")
            
            if len(seats) != len(seat_ids):
                found_ids = {seat.id for seat in seats}
                missing_ids = set(seat_ids) - found_ids
                raise BadRequestException(
                    f"Some seats not found or don't belong to this showtime: {missing_ids}"
                )
            
            reserved_seats = [seat for seat in seats if seat.is_reserved]
            if reserved_seats:
                reserved_ids = [seat.id for seat in reserved_seats]
                raise ConflictException(
                    f"Seats already reserved: {reserved_ids}",
                    details={"reserved_seat_ids": reserved_ids}
                )
            
            showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
            if not showtime:
                raise BadRequestException("Showtime not found")
            
            total_price = Decimal(str(showtime.base_price)) * len(seats)
            
            reservation = Reservation(
                user_id=user_id,
                showtime_id=showtime_id,
                total_price=total_price,
                status=ReservationStatus.CONFIRMED
            )
            db.add(reservation)
            db.flush()
            
            logger.info(f"Created reservation {reservation.id}")
            
            for seat in seats:
                seat.is_reserved = True
                seat.version += 1
                
                reservation_seat = ReservationSeat(
                    reservation_id=reservation.id,
                    seat_id=seat.id
                )
                db.add(reservation_seat)
            
            db.commit()
            
            logger.info(f"Successfully reserved {len(seats)} seats for reservation {reservation.id}")
            
            db.refresh(reservation)
            return reservation
            
        except (ConflictException, BadRequestException):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error during seat reservation: {str(e)}")
            raise BadRequestException(f"Failed to reserve seats: {str(e)}")

    @staticmethod
    def cancel_reservation(db: Session, reservation: Reservation) -> Reservation:
        """Cancel a reservation and release seats."""
        try:
            seat_ids = [rs.seat_id for rs in reservation.reservation_seats]
            seats = db.query(Seat).filter(
                Seat.id.in_(seat_ids)
            ).with_for_update().all()
            
            for seat in seats:
                seat.is_reserved = False
                seat.version += 1
            
            reservation.status = ReservationStatus.CANCELLED
            
            db.commit()
            db.refresh(reservation)
            return reservation
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cancelling reservation: {str(e)}")
            raise BadRequestException(f"Failed to cancel reservation: {str(e)}")
