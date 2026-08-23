"""Authentication service."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.core.redis import blacklist_token, is_token_blacklisted
from app.schemas.user import TokenResponse
from jose import JWTError


class AuthService:
    """Authentication service."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository()

    def register(self, email: str, password: str, full_name: str) -> User:
        """Register a new user."""
        existing_user = self.user_repo.get_by_email(self.db, email)
        if existing_user:
            raise BadRequestException("Email already registered")
        
        user = self.user_repo.create(
            db=self.db,
            email=email,
            password=password,
            full_name=full_name
        )
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.user_repo.get_by_email(self.db, email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user

    def login(self, email: str, password: str) -> TokenResponse:
        """Login user and generate tokens."""
        user = self.authenticate(email, password)
        if not user:
            raise UnauthorizedException("Invalid email or password")
        
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Generate new access token from refresh token."""
        try:
          
            if is_token_blacklisted(refresh_token):
                raise UnauthorizedException("Token has been revoked")
            
            payload = decode_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
            
            user_id = payload.get("sub")
            if user_id is None:
                raise UnauthorizedException("Invalid token payload")
            
            user = self.user_repo.get_by_id(self.db, int(user_id))
            if not user:
                raise UnauthorizedException("User not found")
            
            access_token = create_access_token(data={"sub": str(user.id)})
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token
            )
        except JWTError:
            raise UnauthorizedException("Invalid or expired refresh token")

    def get_current_user(self, token: str) -> User:
        """Get current user from access token."""
        try:
            
            if is_token_blacklisted(token):
                raise UnauthorizedException("Token has been revoked")
            
            payload = decode_token(token)
            
            if payload.get("type") != "access":
                raise UnauthorizedException("Invalid token type")
            
            user_id = payload.get("sub")
            if user_id is None:
                raise UnauthorizedException("Invalid token payload")
            
            user = self.user_repo.get_by_id(self.db, int(user_id))
            if not user:
                raise UnauthorizedException("User not found")
            
            return user
        except JWTError:
            raise UnauthorizedException("Invalid or expired access token")

    def logout(self, access_token: str, refresh_token: Optional[str] = None) -> None:
        """Logout user by blacklisting tokens."""
        try:
            access_payload = decode_token(access_token)
            access_exp = access_payload.get("exp", 0)
            now = datetime.now(timezone.utc).timestamp()
            access_ttl = max(0, int(access_exp - now))
            if access_ttl > 0:
                blacklist_token(access_token, access_ttl)
            
            if refresh_token:
                refresh_payload = decode_token(refresh_token)
                refresh_exp = refresh_payload.get("exp", 0)
                refresh_ttl = max(0, int(refresh_exp - now))
                if refresh_ttl > 0:
                    blacklist_token(refresh_token, refresh_ttl)
        except JWTError:
            # Token is already invalid, nothing to blacklist
            pass
