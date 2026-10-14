"""
Image handling, validation, and storage utility.
Ensures uploaded files are legitimate images, prevents path traversal, and enforces size limits.
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io
from backend.app.config import settings


def validate_and_save_image(file: UploadFile, subfolder: str = "") -> str:
    """
    Validate uploaded image file and save it to the uploads directory.
    Returns the relative URL path for accessing the image via web.
    """
    # 1. Validate content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type '{file.content_type}'. Allowed types: JPEG, PNG, WebP."
        )

    # 2. Read bytes and validate file size
    file_bytes = file.file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image file size ({len(file_bytes) / 1024 / 1024:.1f} MB) exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    # 3. Verify image integrity with Pillow
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify() # Verify file is a valid image
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid or readable image."
        )

    # 4. Generate unique, safe filename
    original_ext = Path(file.filename or "image.jpg").suffix.lower()
    if original_ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        original_ext = ".jpg"
    
    unique_filename = f"{uuid.uuid4().hex[:12]}_{int(uuid.uuid1().time)}{original_ext}"
    
    target_dir = settings.UPLOADS_DIR
    if subfolder:
        target_dir = target_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)
        
    destination_path = target_dir / unique_filename

    # 5. Write file safely to disk
    with open(destination_path, "wb") as f:
        f.write(file_bytes)

    # Return web-accessible URL path
    if subfolder:
        return f"/uploads/{subfolder}/{unique_filename}"
    return f"/uploads/{unique_filename}"
