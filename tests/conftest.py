"""Test configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User, UserRole
from app.core.security import get_password_hash, create_access_token
import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://movieuser:moviepass123@db:5432/movie_reservation_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        full_name="Test User",
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db):
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("adminpass123"),
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def user_token(test_user):
    """Generate access token for test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return token


@pytest.fixture(scope="function")
def admin_token(test_admin):
    """Generate access token for test admin."""
    token = create_access_token(data={"sub": str(test_admin.id)})
    return token


@pytest.fixture(scope="function")
def auth_headers_user(user_token):
    """Generate authorization headers for test user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="function")
def auth_headers_admin(admin_token):
    """Generate authorization headers for test admin."""
    return {"Authorization": f"Bearer {admin_token}"}
