"""Reporting repository for analytics queries."""
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.reservation import Reservation, ReservationStatus, ReservationSeat
from app.models.showtime import Showtime, Seat
from app.models.movie import Movie


class ReportingRepository:
    """Reporting repository for admin analytics."""

    @staticmethod
    def get_revenue_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        movie_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get revenue report with aggregated data."""
        query = db.query(
            Movie.id.label('movie_id'),
            Movie.title.label('movie_title'),
            func.sum(Reservation.total_price).label('total_revenue'),
            func.count(Reservation.id).label('total_bookings'),
            func.count(ReservationSeat.seat_id).label('total_seats_sold')
        ).join(
            Showtime, Reservation.showtime_id == Showtime.id
        ).join(
            Movie, Showtime.movie_id == Movie.id
        ).outerjoin(
            ReservationSeat, Reservation.id == ReservationSeat.reservation_id
        ).filter(
            Reservation.status == ReservationStatus.CONFIRMED
        )
        
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(Showtime.start_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(Showtime.start_time <= end_datetime)
        
        if movie_id:
            query = query.filter(Movie.id == movie_id)
        
        query = query.group_by(Movie.id, Movie.title)
        
        results = query.all()
        
        total_revenue = sum(r.total_revenue or Decimal('0') for r in results)
        total_bookings = sum(r.total_bookings or 0 for r in results)
        total_seats_sold = sum(r.total_seats_sold or 0 for r in results)
        
        by_movie = [
            {
                'movie_id': r.movie_id,
                'movie_title': r.movie_title,
                'total_revenue': r.total_revenue or Decimal('0'),
                'total_bookings': r.total_bookings or 0,
                'total_seats_sold': r.total_seats_sold or 0
            }
            for r in results
        ]
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'total_seats_sold': total_seats_sold,
            'by_movie': by_movie
        }

    @staticmethod
    def get_capacity_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        movie_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get capacity utilization report."""
        query = db.query(
            Showtime.id.label('showtime_id'),
            Movie.title.label('movie_title'),
            Showtime.screen_name,
            Showtime.start_time,
            Showtime.total_seats,
            func.count(
                case((Seat.is_reserved == True, 1))
            ).label('reserved_seats')
        ).join(
            Movie, Showtime.movie_id == Movie.id
        ).outerjoin(
            Seat, Showtime.id == Seat.showtime_id
        )
        
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(Showtime.start_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(Showtime.start_time <= end_datetime)
        
        if movie_id:
            query = query.filter(Movie.id == movie_id)
        
        query = query.group_by(
            Showtime.id,
            Movie.title,
            Showtime.screen_name,
            Showtime.start_time,
            Showtime.total_seats
        ).order_by(Showtime.start_time)
        
        results = query.all()
        
        total_capacity = sum(r.total_seats for r in results)
        total_reserved = sum(r.reserved_seats for r in results)
        total_available = total_capacity - total_reserved
        overall_utilization = (total_reserved / total_capacity * 100) if total_capacity > 0 else 0
        
        items = []
        for r in results:
            available_seats = r.total_seats - r.reserved_seats
            utilization = (r.reserved_seats / r.total_seats * 100) if r.total_seats > 0 else 0
            
            items.append({
                'showtime_id': r.showtime_id,
                'movie_title': r.movie_title,
                'screen_name': r.screen_name,
                'start_time': r.start_time.isoformat(),
                'total_seats': r.total_seats,
                'reserved_seats': r.reserved_seats,
                'available_seats': available_seats,
                'utilization_percentage': round(utilization, 2)
            })
        
        return {
            'items': items,
            'total_capacity': total_capacity,
            'total_reserved': total_reserved,
            'total_available': total_available,
            'overall_utilization_percentage': round(overall_utilization, 2)
        }
