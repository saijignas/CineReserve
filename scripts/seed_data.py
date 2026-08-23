#!/usr/bin/env python3
"""Seed script to populate database with initial data."""
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.movie import Movie, Genre, MovieGenre
from app.models.showtime import Showtime, Seat
from app.core.security import get_password_hash
import string


def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        print("\n👤 Creating admin user...")
        admin_email = "admin@movies.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            print(f"   ℹ️  Admin user already exists: {admin_email}")
            admin = existing_admin
        else:
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"   ✅ Admin user created: {admin_email} / admin123")
        
        print("\n🎭 Creating genres...")
        genres_data = [
            {"name": "Action", "slug": "action"},
            {"name": "Comedy", "slug": "comedy"},
            {"name": "Drama", "slug": "drama"},
            {"name": "Horror", "slug": "horror"},
            {"name": "Sci-Fi", "slug": "sci-fi"},
            {"name": "Romance", "slug": "romance"},
            {"name": "Thriller", "slug": "thriller"},
            {"name": "Animation", "slug": "animation"},
        ]
        
        genres = {}
        for genre_data in genres_data:
            existing_genre = db.query(Genre).filter(Genre.slug == genre_data["slug"]).first()
            if existing_genre:
                genres[genre_data["slug"]] = existing_genre
                print(f"   ℹ️  Genre already exists: {genre_data['name']}")
            else:
                genre = Genre(**genre_data)
                db.add(genre)
                db.flush()
                genres[genre_data["slug"]] = genre
                print(f"   ✅ Genre created: {genre_data['name']}")
        
        db.commit()
        
        print("\n🎬 Creating movies...")
        movies_data = [
            {
                "title": "The Dark Knight Returns",
                "description": "An epic superhero action thriller featuring the caped crusader's return.",
                "poster_url": "https://example.com/posters/dark-knight.jpg",
                "duration_minutes": 152,
                "release_date": date(2024, 1, 15),
                "genres": ["action", "thriller"]
            },
            {
                "title": "Laugh Out Loud",
                "description": "A hilarious comedy about a group of friends trying to start a business.",
                "poster_url": "https://example.com/posters/laugh-out-loud.jpg",
                "duration_minutes": 98,
                "release_date": date(2024, 3, 20),
                "genres": ["comedy"]
            },
            {
                "title": "The Last Stand",
                "description": "A dramatic tale of survival and redemption in a post-apocalyptic world.",
                "poster_url": "https://example.com/posters/last-stand.jpg",
                "duration_minutes": 135,
                "release_date": date(2024, 2, 10),
                "genres": ["drama", "action"]
            },
            {
                "title": "Space Odyssey 2084",
                "description": "A mind-bending sci-fi adventure exploring the depths of space and time.",
                "poster_url": "https://example.com/posters/space-odyssey.jpg",
                "duration_minutes": 168,
                "release_date": date(2024, 4, 5),
                "genres": ["sci-fi", "thriller"]
            },
            {
                "title": "Love in Paris",
                "description": "A heartwarming romantic comedy set in the beautiful city of Paris.",
                "poster_url": "https://example.com/posters/love-paris.jpg",
                "duration_minutes": 110,
                "release_date": date(2024, 2, 14),
                "genres": ["romance", "comedy"]
            },
            {
                "title": "The Haunting Hour",
                "description": "A terrifying horror film that will keep you on the edge of your seat.",
                "poster_url": "https://example.com/posters/haunting-hour.jpg",
                "duration_minutes": 92,
                "release_date": date(2024, 10, 31),
                "genres": ["horror", "thriller"]
            },
            {
                "title": "Animated Adventures",
                "description": "A fun-filled animated movie for the whole family.",
                "poster_url": "https://example.com/posters/animated-adventures.jpg",
                "duration_minutes": 95,
                "release_date": date(2024, 6, 15),
                "genres": ["animation", "comedy"]
            },
        ]
        
        created_movies = []
        for movie_data in movies_data:
            existing_movie = db.query(Movie).filter(Movie.title == movie_data["title"]).first()
            if existing_movie:
                created_movies.append(existing_movie)
                print(f"   ℹ️  Movie already exists: {movie_data['title']}")
                continue
            
            genre_slugs = movie_data.pop("genres")
            movie = Movie(**movie_data)
            db.add(movie)
            db.flush()
            
            for slug in genre_slugs:
                movie_genre = MovieGenre(movie_id=movie.id, genre_id=genres[slug].id)
                db.add(movie_genre)
            
            created_movies.append(movie)
            print(f"   ✅ Movie created: {movie.title}")
        
        db.commit()
        
        print("\n🎟️  Creating showtimes for next 7 days...")
        screens = ["Screen A", "Screen B", "Screen C"]
        showtimes_created = 0
        
        for day_offset in range(7):
            show_date = datetime.now() + timedelta(days=day_offset)
            
            for screen in screens:
                morning_start = show_date.replace(hour=10, minute=0, second=0, microsecond=0)
                afternoon_start = show_date.replace(hour=14, minute=30, second=0, microsecond=0)
                evening_start = show_date.replace(hour=19, minute=0, second=0, microsecond=0)
                
                show_times = [morning_start, afternoon_start, evening_start]
                
                for idx, start_time in enumerate(show_times):
                    movie = created_movies[idx % len(created_movies)]
                    end_time = start_time + timedelta(minutes=movie.duration_minutes + 15)
                    
                    existing_showtime = db.query(Showtime).filter(
                        Showtime.screen_name == screen,
                        Showtime.start_time == start_time
                    ).first()
                    
                    if existing_showtime:
                        continue
                    
                    showtime = Showtime(
                        movie_id=movie.id,
                        screen_name=screen,
                        start_time=start_time,
                        end_time=end_time,
                        base_price=Decimal("12.99"),
                        total_seats=100
                    )
                    db.add(showtime)
                    db.flush()
                    
                    rows = string.ascii_uppercase[:10]
                    for row_letter in rows:
                        for seat_num in range(1, 11):
                            seat = Seat(
                                showtime_id=showtime.id,
                                seat_number=seat_num,
                                row_letter=row_letter,
                                is_reserved=False
                            )
                            db.add(seat)
                    
                    showtimes_created += 1
        
        db.commit()
        print(f"   ✅ Created {showtimes_created} showtimes with 100 seats each")
        
        print("\n👤 Creating test user...")
        test_email = "user@test.com"
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            print(f"   ℹ️  Test user already exists: {test_email}")
        else:
            test_user = User(
                email=test_email,
                password_hash=get_password_hash("password123"),
                full_name="Test User",
                role="user"
            )
            db.add(test_user)
            db.commit()
            print(f"   ✅ Test user created: {test_email} / password123")
        
        print("\n" + "="*60)
        print("✨ Database seeding completed successfully!")
        print("="*60)
        print("\n📝 Credentials:")
        print(f"   Admin: admin@movies.com / admin123")
        print(f"   User:  user@test.com / password123")
        print("\n📊 Summary:")
        print(f"   Genres: {len(genres_data)}")
        print(f"   Movies: {len(created_movies)}")
        print(f"   Showtimes: {showtimes_created}")
        print(f"   Total Seats: {showtimes_created * 100}")
        print("\n🚀 You can now start using the application!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
