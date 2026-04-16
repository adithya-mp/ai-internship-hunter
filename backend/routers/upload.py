from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
import uuid

from schemas.user import UserResponse
from models.user import User
from utils.security import get_current_user
from services.file_parser import extract_text_from_pdf, extract_text_from_docx, parse_resume_text
from config import get_settings

settings = get_settings()
router = APIRouter()

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = uuid.uuid4().hex[:8]
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"upload_{file_id}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Extract text
    text = ""
    if file_ext == ".pdf":
        text = await extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        text = await extract_text_from_docx(file_path)

    if not text:
        raise HTTPException(status_code=500, detail="Failed to extract text from file")

    # Parse structured data
    parsed_data = await parse_resume_text(text)
    
    # We could optionally auto-update current_user.profile_data here,
    # but for now we just return the parsed data to the frontend so the user can review it.

    return {
        "filename": safe_filename,
        "parsed_data": parsed_data
    }
