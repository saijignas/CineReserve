"""User repository for database operations."""
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User, UserRole
from app.core.security import get_password_hash


class UserRepository:
    """User repository."""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, email: str, password: str, full_name: str, role: UserRole = UserRole.USER) -> User:
        """Create a new user."""
        password_hash = get_password_hash(password)
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: User, **kwargs) -> User:
        """Update user."""
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> None:
        """Delete user."""
        db.delete(user)
        db.commit()

    @staticmethod
    def promote_to_admin(db: Session, user: User) -> User:
        """Promote user to admin."""
        user.role = UserRole.ADMIN
        db.commit()
        db.refresh(user)
        return user
