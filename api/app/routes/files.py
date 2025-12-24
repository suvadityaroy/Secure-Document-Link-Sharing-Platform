"""File upload and sharing routes."""
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Request
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import (
    FileUploadResponse,
    CreateShareRequest,
    ShareResponse
)
from app.services.file_share_service import FileShareService
from app.services.file_service_client import FileServiceClient
from app.routes.dependencies import get_current_user_id

router = APIRouter(prefix="/api/files", tags=["files"])

# Configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msword",
    "application/vnd.ms-excel",
    "image/jpeg",
    "image/png",
    "image/gif"
}


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Upload a file to the platform.
    
    - **file**: File to upload (max 100MB)
    
    Supports: PDF, images, documents (Word, Excel), text files.
    """
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{file.content_type}' is not supported"
        )
    
    # Upload to Java service
    upload_result = await FileServiceClient.upload_file(
        file_content,
        file.filename
    )
    
    if not upload_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage service"
        )
    
    return FileUploadResponse(**upload_result)


@router.post("/share", response_model=ShareResponse)
def create_share(
    share_request: CreateShareRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a shareable link for an uploaded file.
    
    - **file_id**: ID returned from file upload
    - **file_name**: Original filename
    - **file_size**: File size in bytes
    - **file_hash**: SHA-256 hash from upload response
    - **one_time_access**: If true, link can only be used once
    - **expires_in_hours**: Optional expiry time in hours (null = no expiry)
    """
    try:
        return FileShareService.create_share(db, user_id, share_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/shares", response_model=List[ShareResponse])
def list_user_shares(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all share links created by the current user."""
    return FileShareService.get_user_shares(db, user_id)


@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_share(
    share_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Disable/revoke a share link.
    Only the user who created the share can disable it.
    """
    success = FileShareService.disable_share(db, share_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found or access denied"
        )
    
    return None


@router.get("/download/{share_token}")
async def download_via_share(
    share_token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Download a file using a share token (no authentication required).
    
    This endpoint is public - anyone with a valid share token can access it.
    """
    
    # Validate share token
    share_info = FileShareService.validate_share_token(db, share_token)
    if not share_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or deactivated share token"
        )
    
    # Download file from Java service
    file_data = await FileServiceClient.download_file(share_info["file_id"])
    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file"
        )
    
    file_content, file_name = file_data
    
    # Record access in database and update download count
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        FileShareService.record_access(
            db,
            share_info["share_id"],
            ip_address,
            user_agent
        )
    except Exception as e:
        print(f"Error recording access: {e}")
    
    # Stream file to client
    return {
        "content": file_content,
        "media_type": "application/octet-stream",
        "headers": {
            "Content-Disposition": f"attachment; filename={file_name}"
        }
    }
