"""Genres API routes."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.movie_service import GenreService
from app.schemas.movie import GenreCreate, GenreResponse
from app.api.deps import get_current_admin

router = APIRouter()


@router.get("/", response_model=List[GenreResponse])
def list_genres(db: Session = Depends(get_db)):
    """Get all genres."""
    genre_service = GenreService(db)
    genres = genre_service.get_all_genres()
    return genres


@router.post("/", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
def create_genre(
    genre_data: GenreCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Create a new genre (Admin only)."""
    genre_service = GenreService(db)
    genre = genre_service.create_genre(
        name=genre_data.name,
        slug=genre_data.slug
    )
    return genre
