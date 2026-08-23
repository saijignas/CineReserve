#!/usr/bin/env python3
"""Generate large dataset for load testing."""
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.movie import Movie, Genre, MovieGenre
from app.models.showtime import Showtime, Seat
import string


def generate_load_data():
    """Generate large dataset for load testing."""
    db = SessionLocal()
    
    try:
        print("🚀 Generating load testing data...")
        
        genres = db.query(Genre).all()
        if not genres:
            print("❌ No genres found. Please run seed_data.py first.")
            return
        
        print("\n🎬 Creating 100 movies...")
        movie_titles = [
            "Action Hero", "Comedy Night", "Drama Queen", "Horror Show",
            "Sci-Fi Adventure", "Romance Story", "Thriller Chase", "Mystery Box",
            "Fantasy Land", "Documentary Life"
        ]
        
        movies = []
        for i in range(100):
            title_base = random.choice(movie_titles)
            movie = Movie(
                title=f"{title_base} {i+1}",
                description=f"An exciting movie about {title_base.lower()}",
                poster_url=f"https://example.com/poster{i+1}.jpg",
                duration_minutes=random.randint(90, 180),
                release_date=date(2024, random.randint(1, 12), random.randint(1, 28))
            )
            db.add(movie)
            db.flush()
            
            num_genres = random.randint(1, 3)
            selected_genres = random.sample(genres, num_genres)
            for genre in selected_genres:
                movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre.id)
                db.add(movie_genre)
            
            movies.append(movie)
            
            if (i + 1) % 20 == 0:
                print(f"   Created {i+1} movies...")
        
        db.commit()
        print(f"   ✅ Created {len(movies)} movies")
        
        print("\n🎟️  Creating 1000 showtimes with seats...")
        screens = ["Screen A", "Screen B", "Screen C", "Screen D", "Screen E"]
        showtimes_created = 0
        seats_created = 0
        
        for day_offset in range(14):
            show_date = datetime.now() + timedelta(days=day_offset)
            
            for screen in screens:
                for hour in [10, 13, 16, 19, 22]:
                    start_time = show_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    movie = random.choice(movies)
                    end_time = start_time + timedelta(minutes=movie.duration_minutes + 15)
                    
                    showtime = Showtime(
                        movie_id=movie.id,
                        screen_name=screen,
                        start_time=start_time,
                        end_time=end_time,
                        base_price=Decimal(str(random.choice(["9.99", "12.99", "15.99"]))),
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
                            seats_created += 1
                    
                    showtimes_created += 1
                    
                    if showtimes_created % 100 == 0:
                        db.commit()
                        print(f"   Created {showtimes_created} showtimes, {seats_created} seats...")
                    
                    if showtimes_created >= 1000:
                        break
                
                if showtimes_created >= 1000:
                    break
            
            if showtimes_created >= 1000:
                break
        
        db.commit()
        
        print("\n" + "="*60)
        print("✨ Load testing data generated successfully!")
        print("="*60)
        print(f"   Movies: {len(movies)}")
        print(f"   Showtimes: {showtimes_created}")
        print(f"   Seats: {seats_created}")
        print("\n🧪 Ready for load testing with 500 concurrent users!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error generating data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_load_data()
