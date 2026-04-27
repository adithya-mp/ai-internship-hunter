import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from sqlalchemy import select
from database import async_session
from models.user import User
from models.job import Job
from services.resume_generator import generate_resume

async def test():
    async with async_session() as db:
        # Get first user
        res = await db.execute(select(User).limit(1))
        user = res.scalar_one_or_none()
        if not user:
            print("No users found")
            return

        # Get the specific job
        res = await db.execute(select(Job).where(Job.id == '4403461234'))
        job = res.scalar_one_or_none()
        if not job:
            print("Job 4403461234 not found")
            return

        print(f"Generating for: {job.title} at {job.company}")
        
        # Prepare profile
        profile = user.profile_data or {}
        profile['full_name'] = user.full_name
        profile['bio'] = user.bio
        
        # Call generator
        content = await generate_resume(
            job_title=job.title,
            company=job.company,
            job_description=job.description,
            required_skills=job.skills_required or [],
            user_profile=profile
        )
        
        print("SUCCESS")
        print("-" * 20)
        print("Summary Preview:")
        print(content.get('summary', 'No summary')[:200] + "...")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(test())
