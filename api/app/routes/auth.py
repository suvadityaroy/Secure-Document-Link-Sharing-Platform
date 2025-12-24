"""Authentication routes (register, login, profile)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse
)
from app.services.auth_service import AuthService
from app.routes.dependencies import get_current_user_id

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **username**: Username (3-255 characters, unique)
    - **email**: Email address (must be unique)
    - **password**: Password (minimum 8 characters, must contain uppercase letter and digit)
    """
    try:
        return AuthService.register_user(db, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login and receive JWT access token.
    
    - **username**: Username
    - **password**: Password
    
    Returns access token valid for 30 minutes.
    """
    token = AuthService.login_user(db, login_data)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return token


@router.get("/me", response_model=UserResponse)
def get_profile(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current user's profile."""
    user = AuthService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
