from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from database import get_db
from models.job import Job, SavedJob
from models.user import User
from schemas.job import JobResponse, JobMatchResponse, SaveJobRequest
from utils.security import get_current_user
from services.job_matcher import match_jobs

router = APIRouter()

@router.get("", response_model=dict)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: str = None,
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page
    
    stmt = select(Job)
    if q:
        stmt = stmt.where(Job.title.ilike(f"%{q}%") | Job.company.ilike(f"%{q}%"))
        
    total_query = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    stmt = stmt.order_by(Job.scraped_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return {
        "items": jobs,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/matched", response_model=list[JobMatchResponse])
async def get_matched_jobs(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not current_user.embedding:
        return []

    result = await db.execute(select(Job).limit(200)) # get recent jobs to match
    jobs = result.scalars().all()
    
    jobs_list = []
    for j in jobs:
        jobs_list.append({
            "id": str(j.id),
            "title": j.title,
            "company": j.company,
            "description": j.description,
            "skills_required": j.skills_required,
            "location": j.location,
            "apply_url": j.apply_url,
            "source": j.source,
            "job_type": j.job_type,
            "stipend": j.stipend,
            "duration": j.duration,
            "scraped_at": j.scraped_at,
            "embedding": j.embedding
        })

    matched = await match_jobs(current_user.embedding, jobs_list)
    return matched[:20]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/save")
async def save_job(job_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    s_result = await db.execute(select(SavedJob).where(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id))
    if s_result.scalar_one_or_none():
        return {"status": "already_saved"}

    saved_job = SavedJob(user_id=current_user.id, job_id=job_id)
    db.add(saved_job)
    await db.commit()
    return {"status": "saved"}

@router.delete("/{job_id}/save")
async def unsave_job(job_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SavedJob).where(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id))
    saved_job = result.scalar_one_or_none()
    if saved_job:
        await db.delete(saved_job)
        await db.commit()
    return {"status": "unsaved"}

@router.get("/user/saved", response_model=list[JobResponse])
async def get_saved_jobs(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).join(SavedJob).where(SavedJob.user_id == current_user.id))
    return result.scalars().all()
