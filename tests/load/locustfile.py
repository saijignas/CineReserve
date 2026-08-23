"""Locust load testing file for Movie Reservation System."""
from locust import HttpUser, task, between, constant_pacing
import random
import json
from datetime import datetime, timedelta


class AuthenticationUser(HttpUser):
    """User class for authentication flow testing (10% of traffic)."""
    weight = 10
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login on start."""
        self.login()
    
    def login(self):
        """Login and store token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@test.com",
                "password": "password123"
            },
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
    
    @task(5)
    def get_profile(self):
        """Get user profile."""
        if hasattr(self, 'token'):
            self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )
    
    @task(1)
    def refresh_token(self):
        """Refresh access token."""
        if hasattr(self, 'token'):
            self.client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": self.token}
            )


class MovieBrowsingUser(HttpUser):
    """User class for browsing movies and showtimes (40% of traffic)."""
    weight = 40
    wait_time = between(1, 3)
    
    @task(10)
    def list_movies(self):
        """List movies with pagination."""
        page = random.randint(1, 3)
        params = {"page": page, "page_size": 20}
        
        self.client.get(
            "/api/v1/movies/",
            params=params,
            name="/api/v1/movies/ [paginated]"
        )
    
    @task(5)
    def search_movies(self):
        """Search movies."""
        search_terms = ["Knight", "Love", "Space", "Last", "Laugh"]
        search = random.choice(search_terms)
        
        self.client.get(
            "/api/v1/movies/",
            params={"search": search},
            name="/api/v1/movies/ [search]"
        )
    
    @task(8)
    def list_showtimes(self):
        """List showtimes for a date."""
        date_offset = random.randint(0, 3)
        target_date = (datetime.now() + timedelta(days=date_offset)).date()
        
        self.client.get(
            "/api/v1/showtimes/",
            params={"date": target_date.isoformat()},
            name="/api/v1/showtimes/ [by date]"
        )
    
    @task(3)
    def get_movie_details(self):
        """Get specific movie details."""
        movie_id = random.randint(1, 7)
        
        self.client.get(
            f"/api/v1/movies/{movie_id}",
            name="/api/v1/movies/{id}"
        )
    
    @task(2)
    def get_genres(self):
        """Get all genres."""
        self.client.get("/api/v1/genres/")


class SeatReservationUser(HttpUser):
    """User class for seat reservation flow (45% of traffic)."""
    weight = 45
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login on start."""
        self.login()
    
    def login(self):
        """Login and store token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@test.com",
                "password": "password123"
            },
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
    
    @task(10)
    def view_seat_availability(self):
        """View seat availability for a showtime."""
        showtime_id = random.randint(1, 20)
        
        self.client.get(
            f"/api/v1/showtimes/{showtime_id}/seats",
            name="/api/v1/showtimes/{id}/seats"
        )
    
    @task(7)
    def reserve_seats(self):
        """Reserve seats - tests the pessimistic locking mechanism."""
        if not hasattr(self, 'token'):
            return
        
        showtime_id = random.randint(1, 20)
        
        seats_response = self.client.get(
            f"/api/v1/showtimes/{showtime_id}/seats",
            name="/api/v1/showtimes/{id}/seats [for reservation]"
        )
        
        if seats_response.status_code == 200:
            seats = seats_response.json()
            available_seats = [s for s in seats if not s.get("is_reserved", True)]
            
            if available_seats:
                num_seats = random.randint(1, min(4, len(available_seats)))
                selected_seats = random.sample(available_seats, num_seats)
                seat_ids = [s["id"] for s in selected_seats]
                
                response = self.client.post(
                    "/api/v1/reservations/",
                    json={
                        "showtime_id": showtime_id,
                        "seat_ids": seat_ids
                    },
                    headers={"Authorization": f"Bearer {self.token}"},
                    catch_response=True,
                    name="/api/v1/reservations/ [create]"
                )
                
                if response.status_code == 201:
                    response.success()
                elif response.status_code == 409:
                    response.success()
                else:
                    response.failure(f"Unexpected status: {response.status_code}")
    
    @task(5)
    def view_my_reservations(self):
        """View user's reservations."""
        if hasattr(self, 'token'):
            self.client.get(
                "/api/v1/reservations/my",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/api/v1/reservations/my"
            )
    
    @task(2)
    def cancel_reservation(self):
        """Cancel a reservation (if any exist)."""
        if not hasattr(self, 'token'):
            return
        
        reservations_response = self.client.get(
            "/api/v1/reservations/my",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/v1/reservations/my [for cancel]"
        )
        
        if reservations_response.status_code == 200:
            data = reservations_response.json()
            reservations = data.get("items", [])
            confirmed = [r for r in reservations if r["status"] == "confirmed"]
            
            if confirmed:
                reservation = random.choice(confirmed)
                
                self.client.delete(
                    f"/api/v1/reservations/{reservation['id']}",
                    headers={"Authorization": f"Bearer {self.token}"},
                    name="/api/v1/reservations/{id} [cancel]"
                )


class AdminUser(HttpUser):
    """User class for admin operations (5% of traffic)."""
    weight = 5
    wait_time = between(3, 7)
    
    def on_start(self):
        """Login as admin on start."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@movies.com",
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data["access_token"]
    
    @task(3)
    def view_revenue_report(self):
        """View revenue report."""
        if hasattr(self, 'admin_token'):
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            self.client.get(
                "/api/v1/reservations/admin/revenue",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                headers={"Authorization": f"Bearer {self.admin_token}"},
                name="/api/v1/reservations/admin/revenue"
            )
    
    @task(3)
    def view_capacity_report(self):
        """View capacity utilization report."""
        if hasattr(self, 'admin_token'):
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=3)
            
            self.client.get(
                "/api/v1/reservations/admin/capacity",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                headers={"Authorization": f"Bearer {self.admin_token}"},
                name="/api/v1/reservations/admin/capacity"
            )
    
    @task(2)
    def view_all_reservations(self):
        """View all reservations."""
        if hasattr(self, 'admin_token'):
            self.client.get(
                "/api/v1/reservations/admin/all",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                name="/api/v1/reservations/admin/all"
            )
    
    @task(1)
    def create_showtime(self):
        """Create a new showtime."""
        if hasattr(self, 'admin_token'):
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = tomorrow.replace(hour=20, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=2)
            
            movie_id = random.randint(1, 7)
            screen_name = random.choice(["Screen A", "Screen B", "Screen C"])
            
            self.client.post(
                "/api/v1/showtimes/",
                json={
                    "movie_id": movie_id,
                    "screen_name": screen_name,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "base_price": "12.99",
                    "rows": 10,
                    "seats_per_row": 10
                },
                headers={"Authorization": f"Bearer {self.admin_token}"},
                name="/api/v1/showtimes/ [create]"
            )
