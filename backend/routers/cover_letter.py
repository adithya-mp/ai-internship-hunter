from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import os

from database import get_db
from models.resume import Resume
from models.user import User
from models.job import Job
from schemas.resume import CoverLetterRequest, CoverLetterResponse
from utils.security import get_current_user
from services.cover_letter_gen import generate_cover_letter
from utils.pdf_builder import generate_cover_letter_pdf

router = APIRouter()

@router.post("/generate", response_model=CoverLetterResponse)
async def create_cover_letter(
    request: CoverLetterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile_data = current_user.profile_data or {}
    profile_data["full_name"] = current_user.full_name
    profile_data["bio"] = current_user.bio

    content = await generate_cover_letter(
        job_title=job.title,
        company=job.company,
        job_description=job.description,
        required_skills=job.skills_required or [],
        user_profile=profile_data,
        custom_instructions=request.custom_instructions or ""
    )

    pdf_path = generate_cover_letter_pdf(content, current_user.full_name, job.company, job.title)

    # Save to db using the Resume model but type cover_letter
    cl = Resume(
        user_id=current_user.id,
        target_job_id=job.id,
        cover_letter=content,
        content={"text": content}, # dummy struct
        cover_letter_pdf_path=pdf_path,
        doc_type="cover_letter"
    )
    db.add(cl)
    await db.commit()
    await db.refresh(cl)

    return {
        "id": cl.id,
        "content": content,
        "job_title": job.title,
        "company": job.company,
        "pdf_path": pdf_path,
        "created_at": cl.created_at
    }

@router.get("/{id}/download")
async def download_cover_letter(id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == id, Resume.user_id == current_user.id, Resume.doc_type == "cover_letter"))
    cl = result.scalar_one_or_none()
    if not cl or not cl.cover_letter_pdf_path or not os.path.exists(cl.cover_letter_pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
        
    return FileResponse(cl.cover_letter_pdf_path, media_type="application/pdf", filename=f"CoverLetter_{current_user.full_name.replace(' ', '_')}.pdf")
