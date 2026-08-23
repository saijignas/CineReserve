# Movie Reservation System

This is a robust implementation of a movie theater booking system, specifically addressing critical challenges such as high-concurrency seat booking and data integrity. It is designed with a clean architecture to ensure scalability, security, and maintainability.

---

## Project Highlights

This application goes beyond basic CRUD operations to tackle real-world engineering challenges in a movie theater booking system:

-   **Secure Architecture**: Implements modern JWT (JSON Web Token) authentication with a strict Role-Based Access Control (RBAC) system separating **Admins** and **Users**.
-   **Concurrency Management**: Solves the "double-booking" problem using database-level **Pessimistic Locking**, ensuring data consistency even under high load.
-   **Domain-Driven Design**: Structured using a layered Service-Repository pattern to enforce separation of concerns and improve testability.
-   **Comprehensive Testing**: Verified through an extensive suite of unit, integration, and load tests (simulating 500+ concurrent users).
-   **Containerization**: Fully Dockerized environment including the application, PostgreSQL database, and Redis cache.

---

## Technology Stack

I selected this stack to balance performance, type safety, and developer experience:

-   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+) - For high-performance, asynchronous API development.
-   **Database**: [PostgreSQL 15](https://www.postgresql.org/) - For reliable relational data storage and transaction management.
-   **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) - For robust and Pythonic database interactions.
-   **Caching**: [Redis 7](https://redis.io/) - For caching frequent data access patterns.
-   **Testing**: [Pytest](https://docs.pytest.org/) (Unit/Integration) & [Locust](https://locust.io/) (Load Testing).

---

## Quick Start

You can spin up the entire environment in minutes using Docker.

### 1. Clone and Configure
```bash
git clone <repository-url>
cd movie_reservation_system
# Initialize environment configuration
cp .env.example .env
```

### 2. Start Services
Launch the application, database, and cache containers:
```bash
docker-compose up -d
```
*The API will be available at `http://localhost:8000`*

### 3. Initialize Database
Apply schema migrations:
```bash
docker-compose exec app alembic upgrade head
```

### 4. Seed Data
Populate the database with initial reference data (movies, genres, showtimes):
```bash
docker-compose exec app python scripts/seed_data.py
```
> **Note:** This creates default credentials:
> - **Admin**: `admin@movies.com` / `admin123`
> - **User**: `user@test.com` / `password123`

---

## API Documentation

Interactive documentation is available at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

### Key Functionality

#### Authentication
-   **Sign Up**: Register new user accounts.
-   **Login**: Authenticate to receive JWT access and refresh tokens.
-   **Logout**: Invalidate tokens using Redis-based blacklisting.

#### Administration
-   **Movie Management**: Create and update movie metadata (titles, posters, descriptions).
-   **Scheduling**: Manage showtimes for specific dates and screens.
-   **Analytics**: Access revenue reports and seat capacity utilization metrics.

#### User Operations
-   **Discovery**: Browse and search movies by genre or title.
-   **Availability**: Check real-time seat availability for showtimes.
-   **Reservations**: Atomic booking of seats (concurrency-protected).
-   **Management**: View and cancel active reservations.

---

## Concurrency & Data Integrity

The core challenge in any reservation system is handling concurrent booking requests for the same resource.

**The Solution:**
I implemented **Pessimistic Locking** (`SELECT ... FOR UPDATE`) within the PostgreSQL transaction.
1.  **Lock Acquisition**: When a reservation is initiated, the specific seat rows are locked in the database.
2.  **Serialization**: Concurrent transactions attempting to book the same seats are forced to wait.
3.  **Validation & Commit**: Once the first transaction commits, the lock is released. Subsequent transactions then read the updated state (reserved), preventing the double-booking.

*Result: Zero consistency errors verified under high-concurrency load tests.*

---

## Quality Assurance

The reliability of the system is verified through multiple testing layers.

**Test Suite:**
Run unit and integration tests:
```bash
docker-compose exec app pytest -v
```

**Load Testing:**
Simulate high-traffic scenarios (500+ concurrent users) to verify performance and locking mechanisms:
```bash
docker-compose exec app python scripts/generate_load_data.py
cd tests/load
locust -f locustfile.py --host=http://localhost:8000 --users 500 --spawn-rate 10
```

---

## Architecture

The codebase follows a modular structure to support maintainability:

```
movie_reservation_system/
├── app/
│   ├── api/            # API Route Controllers (Entry points)
│   ├── services/       # Business Logic
│   ├── repositories/   # Database Queries (Data Access Layer)
│   ├── models/         # Database Tables (SQLAlchemy)
│   ├── schemas/        # Data Validation (Pydantic)
│   └── core/           # Configuration & Security
├── alembic/            # Database Migrations
├── tests/              # Unit, Integration & Load tests
└── scripts/            # Utility scripts (Seeding, Load generation)
```
