"""File sharing service for managing share links."""
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.core.redis_client import cache_set, cache_get, cache_delete
from app.core.security import generate_share_token
from app.models.database import FileShare, AccessLog
from app.models.schemas import CreateShareRequest, ShareResponse


class FileShareService:
    """Service for file sharing operations."""
    
    @staticmethod
    def create_share(
        db: Session,
        user_id: int,
        share_request: CreateShareRequest
    ) -> ShareResponse:
        """Create a new share link for a file."""
        
        # Calculate expiry time if specified
        expires_at = None
        if share_request.expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(
                hours=share_request.expires_in_hours
            )
        
        # Generate share token
        share_token = generate_share_token()
        
        # Create database record
        db_share = FileShare(
            user_id=user_id,
            file_id=share_request.file_id,
            file_name=share_request.file_name,
            file_size=share_request.file_size,
            file_hash=share_request.file_hash,
            share_token=share_token,
            one_time_access=share_request.one_time_access,
            expires_at=expires_at
        )
        
        db.add(db_share)
        db.commit()
        db.refresh(db_share)
        
        # Cache share token for fast validation (1 hour TTL)
        cache_set(
            f"share_token:{share_token}",
            {
                "share_id": db_share.id,
                "file_id": share_request.file_id,
                "user_id": user_id,
                "one_time_access": share_request.one_time_access,
                "is_active": True
            },
            expire=3600
        )
        
        return ShareResponse.model_validate(db_share)
    
    @staticmethod
    def get_share_by_token(
        db: Session,
        share_token: str
    ) -> Optional[ShareResponse]:
        """Get share details by token."""
        share = db.query(FileShare).filter(
            FileShare.share_token == share_token
        ).first()
        
        if not share:
            return None
        
        # Check if share is still valid
        if not share.is_active:
            return None
        
        if share.expires_at and datetime.utcnow() > share.expires_at:
            # Disable expired share
            share.is_active = False
            db.commit()
            return None
        
        return ShareResponse.model_validate(share)
    
    @staticmethod
    def validate_share_token(
        db: Session,
        share_token: str
    ) -> Optional[dict]:
        """Validate share token and return share info from cache or DB."""
        
        # Try cache first
        cached_share = cache_get(f"share_token:{share_token}")
        if cached_share:
            return cached_share
        
        # Fall back to database
        share = db.query(FileShare).filter(
            FileShare.share_token == share_token,
            FileShare.is_active == True
        ).first()
        
        if not share:
            return None
        
        # Check expiry
        if share.expires_at and datetime.utcnow() > share.expires_at:
            share.is_active = False
            db.commit()
            return None
        
        # Cache for future requests
        share_info = {
            "share_id": share.id,
            "file_id": share.file_id,
            "user_id": share.user_id,
            "one_time_access": share.one_time_access,
            "is_active": True
        }
        cache_set(f"share_token:{share_token}", share_info, expire=3600)
        
        return share_info
    
    @staticmethod
    def record_access(
        db: Session,
        share_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Record file access in log and update download count."""
        
        # Update download count
        share = db.query(FileShare).filter(FileShare.id == share_id).first()
        if share:
            share.download_count += 1
            
            # If one-time access, disable after first download
            if share.one_time_access:
                share.is_active = False
                # Clear from cache
                cache_delete(f"share_token:{share.share_token}")
            
            db.commit()
        
        # Create access log
        access_log = AccessLog(
            file_share_id=share_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        
        db.add(access_log)
        db.commit()
    
    @staticmethod
    def disable_share(db: Session, share_id: int, user_id: int) -> bool:
        """Disable a share link (user can only disable their own shares)."""
        share = db.query(FileShare).filter(
            FileShare.id == share_id,
            FileShare.user_id == user_id
        ).first()
        
        if not share:
            return False
        
        share.is_active = False
        db.commit()
        
        # Clear from cache
        cache_delete(f"share_token:{share.share_token}")
        
        return True
    
    @staticmethod
    def get_user_shares(
        db: Session,
        user_id: int
    ) -> List[ShareResponse]:
        """Get all shares created by a user."""
        shares = db.query(FileShare).filter(
            FileShare.user_id == user_id
        ).order_by(FileShare.created_at.desc()).all()
        
        return [ShareResponse.model_validate(share) for share in shares]
