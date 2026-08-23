"""Unit tests for authentication service."""
import pytest
from app.services.auth_service import AuthService
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.models.user import UserRole


def test_register_user(db):
    """Test user registration."""
    auth_service = AuthService(db)
    
    user = auth_service.register(
        email="newuser@test.com",
        password="password123",
        full_name="New User"
    )
    
    assert user.id is not None
    assert user.email == "newuser@test.com"
    assert user.full_name == "New User"
    assert user.role == UserRole.USER
    assert user.password_hash != "password123"


def test_register_duplicate_email(db, test_user):
    """Test registration with duplicate email."""
    auth_service = AuthService(db)
    
    with pytest.raises(BadRequestException) as exc_info:
        auth_service.register(
            email=test_user.email,
            password="password123",
            full_name="Duplicate User"
        )
    
    assert "already registered" in str(exc_info.value.message).lower()


def test_authenticate_success(db, test_user):
    """Test successful authentication."""
    auth_service = AuthService(db)
    
    user = auth_service.authenticate(
        email=test_user.email,
        password="testpass123"
    )
    
    assert user is not None
    assert user.id == test_user.id


def test_authenticate_wrong_password(db, test_user):
    """Test authentication with wrong password."""
    auth_service = AuthService(db)
    
    user = auth_service.authenticate(
        email=test_user.email,
        password="wrongpassword"
    )
    
    assert user is None


def test_authenticate_nonexistent_user(db):
    """Test authentication with non-existent user."""
    auth_service = AuthService(db)
    
    user = auth_service.authenticate(
        email="nonexistent@test.com",
        password="password123"
    )
    
    assert user is None


def test_login_success(db, test_user):
    """Test successful login."""
    auth_service = AuthService(db)
    
    tokens = auth_service.login(
        email=test_user.email,
        password="testpass123"
    )
    
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"


def test_login_invalid_credentials(db, test_user):
    """Test login with invalid credentials."""
    auth_service = AuthService(db)
    
    with pytest.raises(UnauthorizedException):
        auth_service.login(
            email=test_user.email,
            password="wrongpassword"
        )


def test_get_current_user(db, test_user, user_token):
    """Test getting current user from token."""
    auth_service = AuthService(db)
    
    user = auth_service.get_current_user(user_token)
    
    assert user.id == test_user.id
    assert user.email == test_user.email


def test_get_current_user_invalid_token(db):
    """Test getting current user with invalid token."""
    auth_service = AuthService(db)
    
    with pytest.raises(UnauthorizedException):
        auth_service.get_current_user("invalid_token")
