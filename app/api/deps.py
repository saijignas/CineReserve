"""API dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.core.exceptions import UnauthorizedException, ForbiddenException

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token."""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_current_user(credentials.credentials)
        return user
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require current user to be an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_security),
    db: Session = Depends(get_db)
) -> User | None:
    """Get current user if token is provided, None otherwise."""
    if not credentials:
        return None
    
    try:
        auth_service = AuthService(db)
        user = auth_service.get_current_user(credentials.credentials)
        return user
    except UnauthorizedException:
        return None