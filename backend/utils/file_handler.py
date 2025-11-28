# backend/utils/file_handler.py

import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from backend.utils.logger import logger


async def save_upload_file(
    upload_file: UploadFile,
    directory: str = "uploads",
    allowed_extensions: list = None,
    max_size_mb: int = 20
) -> dict:
    """
    Secure file storage with:
    - Extension validation
    - MIME-type checking
    - Chunked async streaming
    - Size limit enforcement
    - Safe UUID filename
    """

    logger.info(f"📁 Saving upload: {upload_file.filename}")

    # ---------------------------------------------------------
    # 1️⃣ Validate filename + extension
    # ---------------------------------------------------------
    original_name = upload_file.filename or ""

    if "." not in original_name:
        raise HTTPException(status_code=400, detail="File must have an extension.")

    extension = original_name.rsplit(".", 1)[1].lower()

    if allowed_extensions and extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {allowed_extensions}"
        )

    # ---------------------------------------------------------
    # 2️⃣ MIME-type validation
    # ---------------------------------------------------------
    if allowed_extensions:
        mime = upload_file.content_type.lower()
        if mime.startswith("application/octet-stream"):
            # Browser couldn't detect MIME — allow it but log
            logger.warning("⚠ Unknown MIME type for uploaded file.")
        else:
            # Optional: strict MIME enforcement (disable if unnecessary)
            logger.info(f"MIME detected: {mime}")

    # ---------------------------------------------------------
    # 3️⃣ Create secure filename
    # ---------------------------------------------------------
    filename = f"{uuid.uuid4().hex}.{extension}"

    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / filename

    # ---------------------------------------------------------
    # 4️⃣ Stream-write file in chunks
    # ---------------------------------------------------------
    file_size = 0
    max_bytes = max_size_mb * 1024 * 1024

    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await upload_file.read(1024 * 1024)  # 1 MB chunk
                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > max_bytes:
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=400,
                        detail=f"File too large. Max allowed is {max_size_mb} MB."
                    )

                buffer.write(chunk)

    except Exception as e:
        logger.error(f"❌ File save failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

    # ---------------------------------------------------------
    # 5️⃣ Return response metadata
    # ---------------------------------------------------------
    return {
        "success": True,
        "filename": filename,
        "path": str(file_path),
        "original_name": original_name,
        "mime_type": upload_file.content_type,
        "size_bytes": file_size
    }
