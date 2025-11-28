# backend/core/security.py

"""
Security utilities for validating uploaded files.
Stronger, safer, and production-ready.
"""

import os
import re
from fastapi import HTTPException, status, UploadFile


# ---------------------------------------------------------
# Filename Sanitization
# ---------------------------------------------------------
def sanitize_filename(filename: str) -> str:
    """
    Remove dangerous characters from filenames and prevent path traversal.
    Converts spaces to underscores and strips problematic symbols.
    """

    # Prevent ../ path traversal
    safe_name = os.path.basename(filename)

    # Allow only alphanumeric + dash + underscore + dot
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", safe_name)

    return safe_name


# ---------------------------------------------------------
# File Extension Validation
# ---------------------------------------------------------
def validate_file_type(filename: str, allowed_extensions: list):
    """
    Validate file extension safely.
    - Case-insensitive
    - Prevents double-extension attacks (file.pdf.exe)
    - Ensures extension exists
    """
    safe_name = sanitize_filename(filename)

    if "." not in safe_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have an extension (e.g. .pdf, .jpg)."
        )

    # Extract last extension only
    ext = safe_name.rsplit(".", 1)[1].lower()

    allowed = [e.lower() for e in allowed_extensions]

    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed. Allowed: {allowed_extensions}"
        )

    return True


# ---------------------------------------------------------
# File Size Validation
# ---------------------------------------------------------
def validate_file_size(upload_file: UploadFile, max_size_mb: int = 5):
    """
    Limit file upload size (default 5MB).
    Uses file.seek to compute size.
    """
    upload_file.file.seek(0, os.SEEK_END)
    size_bytes = upload_file.file.tell()
    upload_file.file.seek(0)

    max_bytes = max_size_mb * 1024 * 1024

    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum allowed size is {max_size_mb}MB."
        )

    return True


# ---------------------------------------------------------
# Combined Validator
# ---------------------------------------------------------
def validate_upload(upload_file: UploadFile, allowed_extensions: list, max_size_mb: int = 5):
    """
    Combined file validation:
    - Safe filename
    - Allowed extension
    - Max size
    """
    validate_file_type(upload_file.filename, allowed_extensions)
    validate_file_size(upload_file, max_size_mb)

    return True
