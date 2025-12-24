"""Authentication service for user management."""
from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.models.database import User
from app.models.schemas import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse
)


class AuthService:
    """Service for user authentication operations."""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> UserResponse:
        """Register a new user."""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise ValueError("Username or email already registered")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse.model_validate(db_user)
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> Optional[Token]:
        """Authenticate user and return token."""
        query = db.query(User)

        if login_data.email:
            user = query.filter(User.email == login_data.email).first()
        else:
            user = query.filter(User.username == login_data.username).first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username},
            expires_delta=timedelta(minutes=30)
        )
        
        return Token(
            access_token=access_token,
            expires_in=1800  # 30 minutes in seconds
        )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return UserResponse.model_validate(user)
        return None
