from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.job import Job
from models.user import User
from schemas.skill import EmailRequest, EmailResponse
from utils.security import get_current_user
from services.email_writer import generate_email

router = APIRouter()

@router.post("/generate", response_model=EmailResponse)
async def create_email(
    request: EmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile_data = current_user.profile_data or {}
    profile_data["full_name"] = current_user.full_name

    email_content = await generate_email(
        job_title=job.title,
        company=job.company,
        email_type=request.email_type,
        user_profile=profile_data,
        custom_instructions=request.custom_instructions or ""
    )

    # Simplified response assuming the AI engine returned text that might include Subject:
    subject = f"Interest in {job.title} position"
    body = email_content
    
    if "Subject:" in email_content:
        parts = email_content.split("\n", 1)
        subject = parts[0].replace("Subject:", "").strip()
        body = parts[1].strip() if len(parts)>1 else email_content

    return {
        "subject": subject,
        "body": body,
        "job_title": job.title,
        "company": job.company
    }
