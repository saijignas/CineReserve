"""Authentication API routes."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import AuthService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, LogoutRequest

security = HTTPBearer()
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    auth_service = AuthService(db)
    user = auth_service.register(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login and get access tokens."""
    auth_service = AuthService(db)
    tokens = auth_service.login(
        email=credentials.email,
        password=credentials.password
    )
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token."""
    auth_service = AuthService(db)
    tokens = auth_service.refresh_access_token(refresh_token)
    return tokens


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    logout_data: LogoutRequest = LogoutRequest(),
    db: Session = Depends(get_db)
):
    """Logout user by invalidating tokens."""
    auth_service = AuthService(db)
    auth_service.logout(
        access_token=credentials.credentials,
        refresh_token=logout_data.refresh_token
    )
    return None