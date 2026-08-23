"""Showtime repository for database operations."""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from app.models.showtime import Showtime, Seat
from app.models.movie import Movie
import string


class ShowtimeRepository:
    """Showtime repository."""

    @staticmethod
    def get_by_id(db: Session, showtime_id: int, include_seats: bool = False) -> Optional[Showtime]:
        """Get showtime by ID."""
        query = db.query(Showtime).options(joinedload(Showtime.movie))
        
        if include_seats:
            query = query.options(joinedload(Showtime.seats))
        
        return query.filter(Showtime.id == showtime_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        movie_id: Optional[int] = None,
        date_filter: Optional[date] = None
    ) -> Tuple[List[Showtime], int]:
        """Get all showtimes with optional filters."""
        query = db.query(Showtime).options(joinedload(Showtime.movie))
        
        if movie_id:
            query = query.filter(Showtime.movie_id == movie_id)
        
        if date_filter:
            start_of_day = datetime.combine(date_filter, datetime.min.time())
            end_of_day = datetime.combine(date_filter, datetime.max.time())
            query = query.filter(
                Showtime.start_time >= start_of_day,
                Showtime.start_time <= end_of_day
            )
        
        total = query.count()
        
        showtimes = query.order_by(Showtime.start_time).offset(skip).limit(limit).all()
        
        return showtimes, total

    @staticmethod
    def create(
        db: Session,
        movie_id: int,
        screen_name: str,
        start_time: datetime,
        end_time: datetime,
        base_price: Decimal,
        rows: int,
        seats_per_row: int
    ) -> Showtime:
        """Create a new showtime with automatic seat generation."""
        total_seats = rows * seats_per_row
        
        showtime = Showtime(
            movie_id=movie_id,
            screen_name=screen_name,
            start_time=start_time,
            end_time=end_time,
            base_price=base_price,
            total_seats=total_seats
        )
        db.add(showtime)
        db.flush()
        
        letters = string.ascii_uppercase[:rows]
        for i, row_letter in enumerate(letters):
            for seat_num in range(1, seats_per_row + 1):
                seat = Seat(
                    showtime_id=showtime.id,
                    seat_number=seat_num,
                    row_letter=row_letter,
                    is_reserved=False
                )
                db.add(seat)
        
        db.commit()
        db.refresh(showtime)
        return showtime

    @staticmethod
    def update(
        db: Session,
        showtime: Showtime,
        screen_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        base_price: Optional[Decimal] = None
    ) -> Showtime:
        """Update showtime."""
        if screen_name is not None:
            showtime.screen_name = screen_name
        if start_time is not None:
            showtime.start_time = start_time
        if end_time is not None:
            showtime.end_time = end_time
        if base_price is not None:
            showtime.base_price = base_price
        
        db.commit()
        db.refresh(showtime)
        return showtime

    @staticmethod
    def delete(db: Session, showtime: Showtime) -> None:
        """Delete showtime."""
        db.delete(showtime)
        db.commit()

    @staticmethod
    def get_seats(db: Session, showtime_id: int) -> List[Seat]:
        """Get all seats for a showtime."""
        return db.query(Seat).filter(
            Seat.showtime_id == showtime_id
        ).order_by(Seat.row_letter, Seat.seat_number).all()

    @staticmethod
    def check_overlapping(
        db: Session,
        screen_name: str,
        start_time: datetime,
        end_time: datetime,
        exclude_showtime_id: Optional[int] = None
    ) -> bool:
        """Check if there's an overlapping showtime on the same screen."""
        query = db.query(Showtime).filter(
            Showtime.screen_name == screen_name,
            Showtime.start_time < end_time,
            Showtime.end_time > start_time
        )
        
        if exclude_showtime_id:
            query = query.filter(Showtime.id != exclude_showtime_id)
        
        return query.count() > 0
