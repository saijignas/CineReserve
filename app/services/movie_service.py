"""Movie service."""
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import date
from app.models.movie import Movie, Genre
from app.repositories.movie_repository import MovieRepository, GenreRepository
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import get_settings

settings = get_settings()


class MovieService:
    """Movie service."""

    def __init__(self, db: Session):
        self.db = db
        self.movie_repo = MovieRepository()
        self.genre_repo = GenreRepository()

    def get_movie(self, movie_id: int) -> Movie:
        """Get movie by ID."""
        movie = self.movie_repo.get_by_id(self.db, movie_id)
        if not movie:
            raise NotFoundException(f"Movie with ID {movie_id} not found")
        return movie

    def get_movies(
        self,
        page: int = 1,
        page_size: int = None,
        genre_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Movie], int]:
        """Get paginated list of movies."""
        if page_size is None:
            page_size = settings.DEFAULT_PAGE_SIZE
        
        if page < 1:
            page = 1
        if page_size > settings.MAX_PAGE_SIZE:
            page_size = settings.MAX_PAGE_SIZE
        
        skip = (page - 1) * page_size
        
        return self.movie_repo.get_all(
            self.db,
            skip=skip,
            limit=page_size,
            genre_id=genre_id,
            search=search
        )

    def create_movie(
        self,
        title: str,
        description: Optional[str],
        poster_url: Optional[str],
        duration_minutes: int,
        release_date: date,
        genre_ids: List[int]
    ) -> Movie:
        """Create a new movie."""
        if not self.genre_repo.verify_genres_exist(self.db, genre_ids):
            raise BadRequestException("One or more genre IDs are invalid")
        
        movie = self.movie_repo.create(
            db=self.db,
            title=title,
            description=description,
            poster_url=poster_url,
            duration_minutes=duration_minutes,
            release_date=release_date,
            genre_ids=genre_ids
        )
        return movie

    def update_movie(
        self,
        movie_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        poster_url: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        release_date: Optional[date] = None,
        genre_ids: Optional[List[int]] = None
    ) -> Movie:
        """Update a movie."""
        movie = self.get_movie(movie_id)
        
        if genre_ids is not None and not self.genre_repo.verify_genres_exist(self.db, genre_ids):
            raise BadRequestException("One or more genre IDs are invalid")
        
        movie = self.movie_repo.update(
            db=self.db,
            movie=movie,
            title=title,
            description=description,
            poster_url=poster_url,
            duration_minutes=duration_minutes,
            release_date=release_date,
            genre_ids=genre_ids
        )
        return movie

    def delete_movie(self, movie_id: int) -> None:
        """Delete a movie."""
        movie = self.get_movie(movie_id)
        self.movie_repo.delete(self.db, movie)


class GenreService:
    """Genre service."""

    def __init__(self, db: Session):
        self.db = db
        self.genre_repo = GenreRepository()

    def get_all_genres(self) -> List[Genre]:
        """Get all genres."""
        return self.genre_repo.get_all(self.db)

    def get_genre(self, genre_id: int) -> Genre:
        """Get genre by ID."""
        genre = self.genre_repo.get_by_id(self.db, genre_id)
        if not genre:
            raise NotFoundException(f"Genre with ID {genre_id} not found")
        return genre

    def create_genre(self, name: str, slug: str) -> Genre:
        """Create a new genre."""
        existing = self.genre_repo.get_by_slug(self.db, slug)
        if existing:
            raise BadRequestException(f"Genre with slug '{slug}' already exists")
        
        return self.genre_repo.create(self.db, name, slug)
