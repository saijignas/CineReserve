"""Movie and Genre Pydantic schemas."""
from pydantic import BaseModel, Field, HttpUrl
from datetime import date, datetime
from typing import List, Optional


class GenreBase(BaseModel):
    """Base genre schema."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)


class GenreCreate(GenreBase):
    """Schema for genre creation."""
    pass


class GenreResponse(GenreBase):
    """Schema for genre response."""
    id: int

    class Config:
        from_attributes = True


class MovieBase(BaseModel):
    """Base movie schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    poster_url: Optional[str] = Field(None, max_length=500)
    duration_minutes: int = Field(..., gt=0)
    release_date: date


class MovieCreate(MovieBase):
    """Schema for movie creation."""
    genre_ids: List[int] = Field(..., min_items=1)


class MovieUpdate(BaseModel):
    """Schema for movie update."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    poster_url: Optional[str] = Field(None, max_length=500)
    duration_minutes: Optional[int] = Field(None, gt=0)
    release_date: Optional[date] = None
    genre_ids: Optional[List[int]] = None


class MovieResponse(MovieBase):
    """Schema for movie response."""
    id: int
    created_at: datetime
    genres: List[GenreResponse] = []

    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    """Schema for movie list response."""
    items: List[MovieResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
