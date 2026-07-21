import os
import filetype
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_file_size(value):
    """
    Validates that the file size is not larger than 5 MB.
    """
    filesize = value.size
    
    # 5 MB limit
    if filesize > 5242880:
        raise ValidationError(_("The maximum file size that can be uploaded is 5MB"))
    return value

def validate_file_extension(value):
    """
    Validates that the file has an allowed extension.
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.webp']
    if not ext in valid_extensions:
        raise ValidationError(_("Unsupported file extension. Allowed extensions are: pdf, doc, docx, txt, jpg, jpeg, png, webp"))
    return value

def validate_file_mime_type(value):
    """
    Validates the actual MIME type of the file by reading its magic numbers.
    """
    # Read the first 2048 bytes for magic number detection
    chunk = value.read(2048)
    # Reset file pointer so it can be read later by Cloudinary
    value.seek(0)
    
    # Filetype guess
    kind = filetype.guess(chunk)
    
    valid_mime_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'image/jpeg',
        'image/png',
        'image/webp'
    ]
    
    if kind is None:
        # plain text files usually don't have magic numbers
        # fallback to checking extension if it's .txt
        ext = os.path.splitext(value.name)[1].lower()
        if ext == '.txt':
            return value
        # if it's not a text file and doesn't have a known magic number, reject
        raise ValidationError(_("Could not determine file type."))
    
    if kind.mime not in valid_mime_types:
        # Extra fallback for docx which is essentially a zip file
        if kind.mime == 'application/zip':
            ext = os.path.splitext(value.name)[1].lower()
            if ext == '.docx':
                return value
        raise ValidationError(_(f"Unsupported file type: {kind.mime}"))
        
    return value
