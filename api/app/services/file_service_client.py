"""External service for file operations (Java File Service)."""
from typing import Optional
import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FileServiceClient:
    """Client for interacting with Java file service."""
    
    BASE_URL = settings.FILE_SERVICE_URL
    TIMEOUT = 30.0
    
    @classmethod
    async def upload_file(
        cls,
        file_content: bytes,
        file_name: str
    ) -> Optional[dict]:
        """Upload file to Java service."""
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                files = {"file": (file_name, file_content)}
                response = await client.post(
                    f"{cls.BASE_URL}/api/files/upload",
                    files=files
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(
                        f"File upload failed: {response.status_code} - "
                        f"{response.text}"
                    )
                    return None
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None
    
    @classmethod
    async def download_file(
        cls,
        file_id: str
    ) -> Optional[tuple]:
        """
        Download file from Java service.
        Returns (file_content, file_name) or None on error.
        """
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/api/files/download/{file_id}",
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    file_name = response.headers.get(
                        "content-disposition",
                        "attachment"
                    )
                    # Extract filename from content-disposition if present
                    if "filename=" in file_name:
                        file_name = file_name.split("filename=")[1].strip('"')
                    
                    return (response.content, file_name)
                else:
                    logger.error(
                        f"File download failed: {response.status_code} - "
                        f"{response.text}"
                    )
                    return None
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return None
    
    @classmethod
    async def delete_file(cls, file_id: str) -> bool:
        """Delete file from Java service."""
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.delete(
                    f"{cls.BASE_URL}/api/files/delete/{file_id}"
                )
                
                if response.status_code in [200, 204]:
                    return True
                else:
                    logger.error(
                        f"File deletion failed: {response.status_code} - "
                        f"{response.text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    @classmethod
    async def verify_file(cls, file_id: str, file_hash: str) -> bool:
        """Verify file integrity using hash."""
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.post(
                    f"{cls.BASE_URL}/api/files/verify/{file_id}",
                    json={"expected_hash": file_hash}
                )
                
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error verifying file: {str(e)}")
            return False
