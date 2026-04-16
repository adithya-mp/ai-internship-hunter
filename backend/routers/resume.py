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
from schemas.resume import ResumeGenerateRequest, ResumeResponse, CoverLetterRequest, CoverLetterResponse
from utils.security import get_current_user
from services.resume_generator import generate_resume
from utils.pdf_builder import generate_resume_pdf

router = APIRouter()

@router.post("/generate", response_model=ResumeResponse)
async def create_resume(
    request: ResumeGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch job details
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile_data = current_user.profile_data or {}
    profile_data["full_name"] = current_user.full_name
    profile_data["bio"] = current_user.bio

    # AI generation
    content = await generate_resume(
        job_title=job.title,
        company=job.company,
        job_description=job.description,
        required_skills=job.skills_required or [],
        user_profile=profile_data,
        custom_instructions=request.custom_instructions or ""
    )

    # Generate PDF
    pdf_path = generate_resume_pdf(content, current_user.full_name, current_user.email)

    # Save to db
    resume = Resume(
        user_id=current_user.id,
        target_job_id=job.id,
        content=content,
        pdf_path=pdf_path,
        doc_type="resume"
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return resume

@router.get("", response_model=list[ResumeResponse])
async def list_resumes(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.user_id == current_user.id, Resume.doc_type == "resume").order_by(Resume.created_at.desc()))
    return result.scalars().all()

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@router.get("/{resume_id}/download")
async def download_resume(resume_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    resume = result.scalar_one_or_none()
    if not resume or not resume.pdf_path or not os.path.exists(resume.pdf_path):
        raise HTTPException(status_code=404, detail="PDF not generated or found")
    
    return FileResponse(resume.pdf_path, media_type="application/pdf", filename=f"Resume_{current_user.full_name.replace(' ', '_')}.pdf")
