"""Movie repository for database operations."""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Tuple
from app.models.movie import Movie, Genre, MovieGenre
from datetime import date


class MovieRepository:
    """Movie repository."""

    @staticmethod
    def get_by_id(db: Session, movie_id: int) -> Optional[Movie]:
        """Get movie by ID with genres."""
        return db.query(Movie).options(
            joinedload(Movie.movie_genres).joinedload(MovieGenre.genre)
        ).filter(Movie.id == movie_id).first()

    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 20,
        genre_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Movie], int]:
        """Get all movies with optional filters."""
        query = db.query(Movie).options(
            joinedload(Movie.movie_genres).joinedload(MovieGenre.genre)
        )
        
        if genre_id:
            query = query.join(MovieGenre).filter(MovieGenre.genre_id == genre_id)
        
        if search:
            query = query.filter(Movie.title.ilike(f"%{search}%"))
        
        total = query.count()
        
        movies = query.order_by(Movie.created_at.desc()).offset(skip).limit(limit).all()
        
        return movies, total

    @staticmethod
    def create(
        db: Session,
        title: str,
        description: Optional[str],
        poster_url: Optional[str],
        duration_minutes: int,
        release_date: date,
        genre_ids: List[int]
    ) -> Movie:
        """Create a new movie."""
        movie = Movie(
            title=title,
            description=description,
            poster_url=poster_url,
            duration_minutes=duration_minutes,
            release_date=release_date
        )
        db.add(movie)
        db.flush()
        
        for genre_id in genre_ids:
            movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre_id)
            db.add(movie_genre)
        
        db.commit()
        db.refresh(movie)
        return movie

    @staticmethod
    def update(
        db: Session,
        movie: Movie,
        title: Optional[str] = None,
        description: Optional[str] = None,
        poster_url: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        release_date: Optional[date] = None,
        genre_ids: Optional[List[int]] = None
    ) -> Movie:
        """Update movie."""
        if title is not None:
            movie.title = title
        if description is not None:
            movie.description = description
        if poster_url is not None:
            movie.poster_url = poster_url
        if duration_minutes is not None:
            movie.duration_minutes = duration_minutes
        if release_date is not None:
            movie.release_date = release_date
        
        if genre_ids is not None:
            db.query(MovieGenre).filter(MovieGenre.movie_id == movie.id).delete()
            for genre_id in genre_ids:
                movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre_id)
                db.add(movie_genre)
        
        db.commit()
        db.refresh(movie)
        return movie

    @staticmethod
    def delete(db: Session, movie: Movie) -> None:
        """Delete movie."""
        db.delete(movie)
        db.commit()


class GenreRepository:
    """Genre repository."""

    @staticmethod
    def get_by_id(db: Session, genre_id: int) -> Optional[Genre]:
        """Get genre by ID."""
        return db.query(Genre).filter(Genre.id == genre_id).first()

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Genre]:
        """Get genre by slug."""
        return db.query(Genre).filter(Genre.slug == slug).first()

    @staticmethod
    def get_all(db: Session) -> List[Genre]:
        """Get all genres."""
        return db.query(Genre).order_by(Genre.name).all()

    @staticmethod
    def create(db: Session, name: str, slug: str) -> Genre:
        """Create a new genre."""
        genre = Genre(name=name, slug=slug)
        db.add(genre)
        db.commit()
        db.refresh(genre)
        return genre

    @staticmethod
    def verify_genres_exist(db: Session, genre_ids: List[int]) -> bool:
        """Verify that all genre IDs exist."""
        count = db.query(Genre).filter(Genre.id.in_(genre_ids)).count()
        return count == len(genre_ids)
