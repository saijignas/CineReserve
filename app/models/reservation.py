"""Reservation and ReservationSeat models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class ReservationStatus(str, enum.Enum):
    """Reservation status enum."""
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Reservation(Base):
    """Reservation model."""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    showtime_id = Column(Integer, ForeignKey("showtimes.id", ondelete="CASCADE"), nullable=False, index=True)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(ReservationStatus, values_callable=lambda x: [e.value for e in x]), default=ReservationStatus.CONFIRMED, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="reservations")
    showtime = relationship("Showtime", back_populates="reservations")
    reservation_seats = relationship("ReservationSeat", back_populates="reservation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class ReservationSeat(Base):
    """ReservationSeat junction table for many-to-many relationship."""
    __tablename__ = "reservation_seats"

    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="CASCADE"), primary_key=True)
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), primary_key=True)
    
    reservation = relationship("Reservation", back_populates="reservation_seats")
    seat = relationship("Seat", back_populates="reservation_seats")
    
    def __repr__(self):
        return f"<ReservationSeat(reservation_id={self.reservation_id}, seat_id={self.seat_id})>"
