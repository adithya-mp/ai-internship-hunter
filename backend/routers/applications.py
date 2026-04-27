from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List


from database import get_db
from models.application import Application
from models.user import User
from models.job import Job
from schemas.job import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from utils.security import get_current_user

router = APIRouter()

@router.post("", response_model=ApplicationResponse)
async def create_application(
    app_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # check job exists
    result = await db.execute(select(Job).where(Job.id == app_data.job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")
        
    app = Application(
        user_id=current_user.id,
        job_id=app_data.job_id,
        resume_id=app_data.resume_id,
        notes=app_data.notes,
        status="applied"
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    
    # fetch application with job relationship populated manually for response
    result_with_job = await db.execute(select(Application).where(Application.id == app.id))
    ret_app = result_with_job.scalar_one()
    ret_app.job = (await db.execute(select(Job).where(Job.id == ret_app.job_id))).scalar_one()
    return ret_app

@router.get("", response_model=List[ApplicationResponse])
async def list_applications(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.user_id == current_user.id).order_by(Application.applied_at.desc()))
    apps = result.scalars().all()
    
    # Hydrate jobs manually to avoid complex joins for schemas if lazy loaded
    for app in apps:
        app.job = (await db.execute(select(Job).where(Job.id == app.job_id))).scalar_one()
    return apps

@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    app_update: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Application).where(Application.id == app_id, Application.user_id == current_user.id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    app.status = app_update.status
    if app_update.notes is not None:
        app.notes = app_update.notes
        
    await db.commit()
    await db.refresh(app)
    
    app.job = (await db.execute(select(Job).where(Job.id == app.job_id))).scalar_one()
    return app
