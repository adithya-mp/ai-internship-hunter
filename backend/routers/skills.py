from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models.skill import Skill
from models.user import User
from models.job import Job
from schemas.skill import SkillCreate, SkillResponse, SkillAnalyzeRequest, SkillGapAnalysis
from utils.security import get_current_user
from services.skill_analyzer import analyze_skill_gap

router = APIRouter()

@router.post("", response_model=SkillResponse)
async def add_skill(skill_data: SkillCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    skill = Skill(
        user_id=current_user.id,
        name=skill_data.name,
        proficiency=skill_data.proficiency,
        category=skill_data.category
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill

@router.get("", response_model=List[SkillResponse])
async def list_skills(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Skill).where(Skill.user_id == current_user.id))
    return result.scalars().all()

@router.post("/analyze", response_model=SkillGapAnalysis)
async def analyze_skills(
    request: SkillAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job_result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    skills_result = await db.execute(select(Skill).where(Skill.user_id == current_user.id))
    user_skills = [s.name for s in skills_result.scalars().all()]

    analysis = await analyze_skill_gap(user_skills, job.skills_required or [], job.title)
    return analysis
