from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models.skill import Skill
from models.user import User
from models.job import Job
from schemas.skill import SkillCreate, SkillUpdate, SkillResponse, SkillAnalyzeRequest, SkillGapAnalysis
from utils.security import get_current_user
from services.skill_analyzer import analyze_skill_gap, recommend_skills_for_role

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

@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: str,
    skill_data: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id, Skill.user_id == current_user.id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    if skill_data.proficiency is not None:
        skill.proficiency = skill_data.proficiency
    if skill_data.category is not None:
        skill.category = skill_data.category
        
    await db.commit()
    await db.refresh(skill)
    return skill

@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id, Skill.user_id == current_user.id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    await db.delete(skill)
    await db.commit()
    return {"detail": "Skill deleted successfully"}

@router.get("/recommendations")
async def get_skill_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    skills_result = await db.execute(select(Skill).where(Skill.user_id == current_user.id))
    user_skills = [s.name for s in skills_result.scalars().all()]
    
    target_role = ""
    if current_user.profile_data:
        target_role = current_user.profile_data.get("target_role", "")
        
    recommendations = await recommend_skills_for_role(user_skills, target_role)
    return recommendations
