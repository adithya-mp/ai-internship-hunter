"""
Jobs Router — Updated with scrape-trigger and resume-based matching endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from database import get_db
from models.job import Job, SavedJob
from models.user import User
from schemas.job import JobResponse, JobMatchResponse, ApplicationCreate, ApplicationUpdate, ApplicationResponse
from utils.security import get_current_user
from services.job_matcher import match_jobs

router = APIRouter()


@router.get("", response_model=dict)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: str = Query(None),
    source: str = Query(None, description="Filter by source: linkedin, internshala, unstop, mock"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all scraped jobs with optional text search and source filter.
    Source filter lets users see only LinkedIn jobs, only Unstop, etc.
    """
    offset = (page - 1) * per_page

    stmt = select(Job)
    if q:
        stmt = stmt.where(
            Job.title.ilike(f"%{q}%") | Job.company.ilike(f"%{q}%") | Job.description.ilike(f"%{q}%")
        )
    if source:
        stmt = stmt.where(Job.source == source)

    total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_result.scalar_one()

    stmt = stmt.order_by(Job.scraped_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return {"items": jobs, "total": total, "page": page, "per_page": per_page}


@router.get("/matched", response_model=list[JobMatchResponse])
async def get_matched_jobs(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return jobs ranked by cosine similarity against the user's profile embedding.
    This is the core "jobs matching MY resume" feature.

    If the user has no embedding yet (hasn't updated profile),
    we fall back to returning the most recent jobs.
    """
    if not current_user.embedding:
        # Fallback: return recent jobs with a neutral score
        result = await db.execute(
            select(Job).order_by(Job.scraped_at.desc()).limit(limit)
        )
        jobs = result.scalars().all()
        return [
            {
                "job": j,
                "match_score": 0.0,
                "match_reason": "Update your profile to get personalized match scores.",
            }
            for j in jobs
        ]

    # Fetch jobs that have embeddings (required for matching)
    result = await db.execute(
        select(Job).where(Job.embedding.isnot(None)).limit(300)
    )
    jobs = result.scalars().all()

    if not jobs:
        # No embeddings yet — fall back to recency
        result = await db.execute(select(Job).order_by(Job.scraped_at.desc()).limit(limit))
        return [{"job": j, "match_score": 0.0, "match_reason": "Embeddings being generated..."} for j in result.scalars().all()]

    jobs_list = [
        {
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
            "embedding": j.embedding,
        }
        for j in jobs
    ]

    matched = await match_jobs(current_user.embedding, jobs_list)
    return matched[:limit]


@router.post("/scrape", status_code=202)
async def trigger_scrape_for_user(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """
    Trigger an immediate scraping cycle based on the current user's skills.
    Runs in the background — returns immediately.
    This is what the "Scan Platforms" button in the UI should call.
    """
    from scraper.scheduler import run_scraping_cycle
    background_tasks.add_task(run_scraping_cycle)
    return {
        "status": "accepted",
        "message": "Scanning LinkedIn, Internshala, and Unstop for internships matching your profile. Refresh in 30-60 seconds.",
    }


@router.get("/sources", response_model=dict)
async def get_job_sources(db: AsyncSession = Depends(get_db)):
    """Return a count of jobs per source platform."""
    result = await db.execute(
        select(Job.source, func.count(Job.id).label("count"))
        .group_by(Job.source)
        .order_by(func.count(Job.id).desc())
    )
    sources = {row.source: row.count for row in result.fetchall()}
    return {"sources": sources}


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/save")
async def save_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")

    existing = await db.execute(
        select(SavedJob).where(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id)
    )
    if existing.scalar_one_or_none():
        return {"status": "already_saved"}

    db.add(SavedJob(user_id=current_user.id, job_id=job_id))
    await db.commit()
    return {"status": "saved"}


@router.delete("/{job_id}/save")
async def unsave_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SavedJob).where(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id)
    )
    saved = result.scalar_one_or_none()
    if saved:
        await db.delete(saved)
        await db.commit()
    return {"status": "unsaved"}


@router.get("/user/saved", response_model=list[JobResponse])
async def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job).join(SavedJob).where(SavedJob.user_id == current_user.id)
    )
    return result.scalars().all()
