import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings
import uuid

# Auto-configure cloudinary if settings are available, else it will use CLOUDINARY_URL
# Currently we assume CLOUDINARY_URL is present in the environment for the MVP.

class CloudinaryUploadService:
    """
    A generic upload service for B10 CRM attachments.
    """

    @staticmethod
    def upload_file(file_obj, folder: str) -> dict:
        """
        Uploads a file to Cloudinary.
        
        Args:
            file_obj: The in-memory file object from the request.
            folder: The destination folder string, e.g., 'b10/website-leads/uuid'
            
        Returns:
            A dictionary containing Cloudinary response data (secure_url, public_id, etc.)
        """
        try:
            # We use a unique filename to prevent overwrites, but keep the original extension
            original_name = file_obj.name
            extension = original_name.split('.')[-1] if '.' in original_name else ''
            
            # resource_type 'auto' allows raw files (PDFs, docs) and images
            response = cloudinary.uploader.upload(
                file_obj,
                folder=folder,
                resource_type='auto',
                use_filename=True,
                unique_filename=True
            )
            return response
        except Exception as e:
            # Re-raise or handle. We let the caller handle the exception for atomic rollbacks
            raise e

    @staticmethod
    def delete_file(public_id: str, resource_type: str = 'auto') -> bool:
        """
        Deletes a file from Cloudinary by its public_id.
        """
        try:
            response = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return response.get('result') == 'ok'
        except Exception as e:
            return False

    @staticmethod
    def get_public_url(public_id: str, resource_type: str = 'auto') -> str:
        """
        Returns the public URL for a given public_id.
        """
        try:
            url, options = cloudinary.utils.cloudinary_url(public_id, resource_type=resource_type, secure=True)
            return url
        except Exception:
            return ""
