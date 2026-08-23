"""Showtimes API routes."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.db.session import get_db
from app.services.showtime_service import ShowtimeService
from app.services.movie_service import MovieService
from app.schemas.showtime import (
    ShowtimeCreate, ShowtimeUpdate, ShowtimeResponse, 
    ShowtimeWithSeatsResponse, ShowtimeListResponse, SeatResponse
)
from app.api.deps import get_current_admin
from app.models.user import User
import math

router = APIRouter()


@router.get("/", response_model=ShowtimeListResponse)
def list_showtimes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    movie_id: Optional[int] = Query(None),
    date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get paginated list of showtimes."""
    showtime_service = ShowtimeService(db)
    showtimes, total = showtime_service.get_showtimes(
        page=page,
        page_size=page_size,
        movie_id=movie_id,
        date_filter=date
    )
    
    movie_service = MovieService(db)
    showtime_responses = []
    for showtime in showtimes:
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
        
        showtime_responses.append(ShowtimeResponse(
            id=showtime.id,
            movie_id=showtime.movie_id,
            screen_name=showtime.screen_name,
            start_time=showtime.start_time,
            end_time=showtime.end_time,
            base_price=showtime.base_price,
            total_seats=showtime.total_seats,
            movie=movie_dict
        ))
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return ShowtimeListResponse(
        items=showtime_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{showtime_id}", response_model=ShowtimeResponse)
def get_showtime(
    showtime_id: int,
    db: Session = Depends(get_db)
):
    """Get showtime by ID."""
    showtime_service = ShowtimeService(db)
    showtime = showtime_service.get_showtime(showtime_id)
    
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
    
    return ShowtimeResponse(
        id=showtime.id,
        movie_id=showtime.movie_id,
        screen_name=showtime.screen_name,
        start_time=showtime.start_time,
        end_time=showtime.end_time,
        base_price=showtime.base_price,
        total_seats=showtime.total_seats,
        movie=movie_dict
    )


@router.get("/{showtime_id}/seats", response_model=List[SeatResponse])
def get_showtime_seats(
    showtime_id: int,
    db: Session = Depends(get_db)
):
    """Get seat availability map for a showtime."""
    showtime_service = ShowtimeService(db)
    seats = showtime_service.get_showtime_seats(showtime_id)
    return seats


@router.post("/", response_model=ShowtimeResponse, status_code=status.HTTP_201_CREATED)
def create_showtime(
    showtime_data: ShowtimeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Create a new showtime with automatic seat generation (Admin only)."""
    showtime_service = ShowtimeService(db)
    showtime = showtime_service.create_showtime(
        movie_id=showtime_data.movie_id,
        screen_name=showtime_data.screen_name,
        start_time=showtime_data.start_time,
        end_time=showtime_data.end_time,
        base_price=showtime_data.base_price,
        rows=showtime_data.rows,
        seats_per_row=showtime_data.seats_per_row
    )
    
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
    
    return ShowtimeResponse(
        id=showtime.id,
        movie_id=showtime.movie_id,
        screen_name=showtime.screen_name,
        start_time=showtime.start_time,
        end_time=showtime.end_time,
        base_price=showtime.base_price,
        total_seats=showtime.total_seats,
        movie=movie_dict
    )


@router.put("/{showtime_id}", response_model=ShowtimeResponse)
def update_showtime(
    showtime_id: int,
    showtime_data: ShowtimeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Update a showtime (Admin only)."""
    showtime_service = ShowtimeService(db)
    showtime = showtime_service.update_showtime(
        showtime_id=showtime_id,
        screen_name=showtime_data.screen_name,
        start_time=showtime_data.start_time,
        end_time=showtime_data.end_time,
        base_price=showtime_data.base_price
    )
    
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
    
    return ShowtimeResponse(
        id=showtime.id,
        movie_id=showtime.movie_id,
        screen_name=showtime.screen_name,
        start_time=showtime.start_time,
        end_time=showtime.end_time,
        base_price=showtime.base_price,
        total_seats=showtime.total_seats,
        movie=movie_dict
    )


@router.delete("/{showtime_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_showtime(
    showtime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a showtime (Admin only)."""
    showtime_service = ShowtimeService(db)
    showtime_service.delete_showtime(showtime_id)
