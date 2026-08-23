"""Movies API routes."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services.movie_service import MovieService
from app.schemas.movie import MovieCreate, MovieUpdate, MovieResponse, MovieListResponse
from app.api.deps import get_current_admin, get_current_user
from app.models.user import User
import math

router = APIRouter()


@router.get("/", response_model=MovieListResponse)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    genre_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get paginated list of movies."""
    movie_service = MovieService(db)
    movies, total = movie_service.get_movies(
        page=page,
        page_size=page_size,
        genre_id=genre_id,
        search=search
    )
    
    movie_responses = []
    for movie in movies:
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
        movie_responses.append(movie_dict)
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return MovieListResponse(
        items=movie_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    """Get movie by ID."""
    movie_service = MovieService(db)
    movie = movie_service.get_movie(movie_id)
    
    genres = [mg.genre for mg in movie.movie_genres]
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        poster_url=movie.poster_url,
        duration_minutes=movie.duration_minutes,
        release_date=movie.release_date,
        created_at=movie.created_at,
        genres=genres
    )


@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Create a new movie (Admin only)."""
    movie_service = MovieService(db)
    movie = movie_service.create_movie(
        title=movie_data.title,
        description=movie_data.description,
        poster_url=movie_data.poster_url,
        duration_minutes=movie_data.duration_minutes,
        release_date=movie_data.release_date,
        genre_ids=movie_data.genre_ids
    )
    
    genres = [mg.genre for mg in movie.movie_genres]
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        poster_url=movie.poster_url,
        duration_minutes=movie.duration_minutes,
        release_date=movie.release_date,
        created_at=movie.created_at,
        genres=genres
    )


@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Update a movie (Admin only)."""
    movie_service = MovieService(db)
    movie = movie_service.update_movie(
        movie_id=movie_id,
        title=movie_data.title,
        description=movie_data.description,
        poster_url=movie_data.poster_url,
        duration_minutes=movie_data.duration_minutes,
        release_date=movie_data.release_date,
        genre_ids=movie_data.genre_ids
    )
    
    genres = [mg.genre for mg in movie.movie_genres]
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        poster_url=movie.poster_url,
        duration_minutes=movie.duration_minutes,
        release_date=movie.release_date,
        created_at=movie.created_at,
        genres=genres
    )


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a movie (Admin only)."""
    movie_service = MovieService(db)
    movie_service.delete_movie(movie_id)
