import os
from django.core.exceptions import ValidationError

def validate_evidence_file(file):
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file.size > max_size:
        raise ValidationError("File size cannot exceed 10MB.")

    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.mp4']
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file format '{ext}'. Allowed formats: JPG, JPEG, PNG, MP4."
        )
