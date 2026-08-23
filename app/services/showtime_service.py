"""Showtime service."""
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from app.models.showtime import Showtime, Seat
from app.repositories.showtime_repository import ShowtimeRepository
from app.repositories.movie_repository import MovieRepository
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import get_settings

settings = get_settings()


class ShowtimeService:
    """Showtime service."""

    def __init__(self, db: Session):
        self.db = db
        self.showtime_repo = ShowtimeRepository()
        self.movie_repo = MovieRepository()

    def get_showtime(self, showtime_id: int, include_seats: bool = False) -> Showtime:
        """Get showtime by ID."""
        showtime = self.showtime_repo.get_by_id(self.db, showtime_id, include_seats)
        if not showtime:
            raise NotFoundException(f"Showtime with ID {showtime_id} not found")
        return showtime

    def get_showtimes(
        self,
        page: int = 1,
        page_size: int = None,
        movie_id: Optional[int] = None,
        date_filter: Optional[date] = None
    ) -> Tuple[List[Showtime], int]:
        """Get paginated list of showtimes."""
        if page_size is None:
            page_size = settings.DEFAULT_PAGE_SIZE
        
        if page < 1:
            page = 1
        if page_size > settings.MAX_PAGE_SIZE:
            page_size = settings.MAX_PAGE_SIZE
        
        skip = (page - 1) * page_size
        
        return self.showtime_repo.get_all(
            self.db,
            skip=skip,
            limit=page_size,
            movie_id=movie_id,
            date_filter=date_filter
        )

    def create_showtime(
        self,
        movie_id: int,
        screen_name: str,
        start_time: datetime,
        end_time: datetime,
        base_price: Decimal,
        rows: int,
        seats_per_row: int
    ) -> Showtime:
        """Create a new showtime with automatic seat generation."""
        movie = self.movie_repo.get_by_id(self.db, movie_id)
        if not movie:
            raise NotFoundException(f"Movie with ID {movie_id} not found")
        
        if end_time <= start_time:
            raise BadRequestException("End time must be after start time")
        
        if self.showtime_repo.check_overlapping(self.db, screen_name, start_time, end_time):
            raise BadRequestException(
                f"Showtime overlaps with existing showtime on screen '{screen_name}'"
            )
        
        showtime = self.showtime_repo.create(
            db=self.db,
            movie_id=movie_id,
            screen_name=screen_name,
            start_time=start_time,
            end_time=end_time,
            base_price=base_price,
            rows=rows,
            seats_per_row=seats_per_row
        )
        return showtime

    def update_showtime(
        self,
        showtime_id: int,
        screen_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        base_price: Optional[Decimal] = None
    ) -> Showtime:
        """Update a showtime."""
        showtime = self.get_showtime(showtime_id)
        
        final_start = start_time if start_time is not None else showtime.start_time
        final_end = end_time if end_time is not None else showtime.end_time
        final_screen = screen_name if screen_name is not None else showtime.screen_name
        
        if final_end <= final_start:
            raise BadRequestException("End time must be after start time")
        
        if self.showtime_repo.check_overlapping(
            self.db, final_screen, final_start, final_end, exclude_showtime_id=showtime_id
        ):
            raise BadRequestException(
                f"Showtime overlaps with existing showtime on screen '{final_screen}'"
            )
        
        showtime = self.showtime_repo.update(
            db=self.db,
            showtime=showtime,
            screen_name=screen_name,
            start_time=start_time,
            end_time=end_time,
            base_price=base_price
        )
        return showtime

    def delete_showtime(self, showtime_id: int) -> None:
        """Delete a showtime."""
        showtime = self.get_showtime(showtime_id)
        self.showtime_repo.delete(self.db, showtime)

    def get_showtime_seats(self, showtime_id: int) -> List[Seat]:
        """Get all seats for a showtime."""
        self.get_showtime(showtime_id)
        
        return self.showtime_repo.get_seats(self.db, showtime_id)
