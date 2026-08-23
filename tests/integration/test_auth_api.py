"""Integration tests for authentication API."""
import pytest

def test_signup(client):
    """Test user signup."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@test.com",
            "password": "password123",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "user"
    assert "id" in data

def test_login(client, test_user):
    """Test user login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401

def test_get_current_user(client, auth_headers_user, test_user):
    """Test getting current user info."""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id

def test_get_current_user_unauthorized(client):
    """Test getting current user without token."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 403
