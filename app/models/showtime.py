"""Showtime and Seat models."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.base import Base


class Showtime(Base):
    """Showtime model."""
    __tablename__ = "showtimes"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    screen_name = Column(String(100), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    total_seats = Column(Integer, nullable=False)
    
    movie = relationship("Movie", back_populates="showtimes")
    seats = relationship("Seat", back_populates="showtime", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="showtime", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Showtime(id={self.id}, movie_id={self.movie_id}, start_time='{self.start_time}')>"


class Seat(Base):
    """Seat model."""
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    showtime_id = Column(Integer, ForeignKey("showtimes.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_number = Column(Integer, nullable=False)
    row_letter = Column(String(2), nullable=False)
    is_reserved = Column(Boolean, default=False, nullable=False, index=True)
    version = Column(Integer, default=0, nullable=False)
    
    showtime = relationship("Showtime", back_populates="seats")
    reservation_seats = relationship("ReservationSeat", back_populates="seat", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Seat(id={self.id}, row='{self.row_letter}', number={self.seat_number}, reserved={self.is_reserved})>"
