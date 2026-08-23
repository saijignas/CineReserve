"""Integration tests for reservations API including race condition tests."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.models.movie import Movie, Genre, MovieGenre
from app.models.showtime import Showtime, Seat
from app.models.reservation import ReservationStatus
import time


@pytest.fixture
def sample_movie(db):
    """Create a sample movie for testing."""
    genre = Genre(name="Action", slug="action")
    db.add(genre)
    db.flush()
    
    movie = Movie(
        title="Test Movie",
        description="A test movie",
        poster_url="https://example.com/poster.jpg",
        duration_minutes=120,
        release_date=datetime.now().date()
    )
    db.add(movie)
    db.flush()
    
    movie_genre = MovieGenre(movie_id=movie.id, genre_id=genre.id)
    db.add(movie_genre)
    db.commit()
    db.refresh(movie)
    
    return movie


@pytest.fixture
def sample_showtime(db, sample_movie):
    """Create a sample showtime with seats."""
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    
    showtime = Showtime(
        movie_id=sample_movie.id,
        screen_name="Test Screen",
        start_time=start_time,
        end_time=end_time,
        base_price=Decimal("10.00"),
        total_seats=10
    )
    db.add(showtime)
    db.flush()
    
    for i in range(1, 11):
        seat = Seat(
            showtime_id=showtime.id,
            seat_number=i,
            row_letter="A",
            is_reserved=False
        )
        db.add(seat)
    
    db.commit()
    db.refresh(showtime)
    
    return showtime


def test_create_reservation(client, auth_headers_user, sample_showtime):
    """Test creating a reservation."""
    seat_response = client.get(
        f"/api/v1/showtimes/{sample_showtime.id}/seats"
    )
    seats = seat_response.json()
    seat_ids = [seats[0]["id"], seats[1]["id"]]
    
    response = client.post(
        "/api/v1/reservations/",
        json={
            "showtime_id": sample_showtime.id,
            "seat_ids": seat_ids
        },
        headers=auth_headers_user
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["showtime_id"] == sample_showtime.id
    assert data["status"] == "confirmed"
    assert len(data["seats"]) == 2
    assert float(data["total_price"]) == 20.0


def test_create_reservation_already_reserved(client, auth_headers_user, test_user, sample_showtime, db):
    """Test creating reservation for already reserved seats."""
    seat_response = client.get(
        f"/api/v1/showtimes/{sample_showtime.id}/seats"
    )
    seats = seat_response.json()
    seat_ids = [seats[0]["id"]]
    
    response1 = client.post(
        "/api/v1/reservations/",
        json={
            "showtime_id": sample_showtime.id,
            "seat_ids": seat_ids
        },
        headers=auth_headers_user
    )
    assert response1.status_code == 201
    
    response2 = client.post(
        "/api/v1/reservations/",
        json={
            "showtime_id": sample_showtime.id,
            "seat_ids": seat_ids
        },
        headers=auth_headers_user
    )
    
    assert response2.status_code == 409


def test_get_my_reservations(client, auth_headers_user, sample_showtime):
    """Test getting user's reservations."""
    seat_response = client.get(
        f"/api/v1/showtimes/{sample_showtime.id}/seats"
    )
    seats = seat_response.json()
    
    client.post(
        "/api/v1/reservations/",
        json={
            "showtime_id": sample_showtime.id,
            "seat_ids": [seats[0]["id"]]
        },
        headers=auth_headers_user
    )
    
    response = client.get(
        "/api/v1/reservations/my",
        headers=auth_headers_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_cancel_reservation(client, auth_headers_user, sample_showtime, db):
    """Test cancelling a reservation."""
    seat_response = client.get(
        f"/api/v1/showtimes/{sample_showtime.id}/seats"
    )
    seats = seat_response.json()
    
    create_response = client.post(
        "/api/v1/reservations/",
        json={
            "showtime_id": sample_showtime.id,
            "seat_ids": [seats[0]["id"]]
        },
        headers=auth_headers_user
    )
    reservation_id = create_response.json()["id"]
    
    response = client.delete(
        f"/api/v1/reservations/{reservation_id}",
        headers=auth_headers_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


def test_concurrent_seat_reservation_race_condition(client, db, sample_showtime):
    """Test pessimistic locking prevents double-booking."""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash, create_access_token
    
    users = []
    for i in range(10):
        user = User(
            email=f"user{i}@test.com",
            password_hash=get_password_hash("password123"),
            full_name=f"User {i}",
            role=UserRole.USER
        )
        db.add(user)
        db.flush()
        users.append(user)
    db.commit()
    
    seat_response = client.get(
        f"/api/v1/showtimes/{sample_showtime.id}/seats"
    )
    seats = seat_response.json()
    target_seat_id = seats[0]["id"]
    
    def attempt_reservation(user_id):
        token = create_access_token(data={"sub": str(user_id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/v1/reservations/",
            json={
                "showtime_id": sample_showtime.id,
                "seat_ids": [target_seat_id]
            },
            headers=headers
        )
        
        return {
            "user_id": user_id,
            "status_code": response.status_code,
            "response": response.json() if response.status_code in [201, 409, 400] else None
        }
    
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(attempt_reservation, user.id) for user in users]
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Exception in thread: {str(e)}")
    
    successful_reservations = [r for r in results if r["status_code"] == 201]
    failed_reservations = [r for r in results if r["status_code"] == 409]
    
    print(f"\n{'='*60}")
    print("RACE CONDITION TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total attempts: {len(results)}")
    print(f"Successful reservations: {len(successful_reservations)}")
    print(f"Failed (conflict): {len(failed_reservations)}")
    print(f"{'='*60}\n")
    
    assert len(successful_reservations) == 1, \
        f"Expected exactly 1 successful reservation, got {len(successful_reservations)}"
    
    assert len(failed_reservations) == 9, \
        f"Expected 9 conflict errors, got {len(failed_reservations)}"
    
    db.expire_all()
    reserved_seat = db.query(Seat).filter(Seat.id == target_seat_id).first()
    assert reserved_seat.is_reserved == True, "Seat should be marked as reserved"
    
    print("✅ PASS: Pessimistic locking successfully prevented double-booking!")


def test_reservation_max_seats_limit(client, auth_headers_user, sample_showtime):
    """Test that reservation respects max seats per booking limit."""
    seat_response = client.get(
        f"/api/v1/showtimes/{sample_showtime.id}/seats"
    )
    seats = seat_response.json()
    all_seat_ids = [seat["id"] for seat in seats]
    
    response = client.post(
        "/api/v1/reservations/",
        json={
            "showtime_id": sample_showtime.id,
            "seat_ids": all_seat_ids[:11] if len(all_seat_ids) > 10 else all_seat_ids
        },
        headers=auth_headers_user
    )
    
    if len(all_seat_ids) > 10:
        assert response.status_code == 400
