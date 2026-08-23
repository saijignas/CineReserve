"""Movie and Genre models."""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Genre(Base):
    """Genre model."""
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    movie_genres = relationship("MovieGenre", back_populates="genre", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Movie(Base):
    """Movie model."""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    poster_url = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    release_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    showtimes = relationship("Showtime", back_populates="movie", cascade="all, delete-orphan")
    movie_genres = relationship("MovieGenre", back_populates="movie", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"


class MovieGenre(Base):
    """MovieGenre junction table for many-to-many relationship."""
    __tablename__ = "movie_genres"

    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)
    
    movie = relationship("Movie", back_populates="movie_genres")
    genre = relationship("Genre", back_populates="movie_genres")
    
    def __repr__(self):
        return f"<MovieGenre(movie_id={self.movie_id}, genre_id={self.genre_id})>"
