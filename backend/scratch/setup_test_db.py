import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from database import engine, Base, async_session
from models.job import Job
from models.user import User

async def setup():
    print("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Injecting test job 4403461234...")
    async with async_session() as db:
        # Create the job
        test_job = Job(
            id="4403461234",
            title="Full Stack Developer",
            company="LinkedIn Tech",
            description="Verified AI test job. Focus on Python, React, and Backend optimization.",
            location="Remote",
            source="linkedin",
            scraped_at=datetime.utcnow()
        )
        db.add(test_job)
        
        # Create a test user for easy login
        hashed_pwd = "pbkdf2:sha256:600000$mock_hash" # This is just a placeholder, but we will register properly in the UI
        test_user = User(
            email="tester@example.com",
            password_hash=hashed_pwd,
            full_name="Test Runner",
            bio="Automated test account for UI verification."
        )
        db.add(test_user)
        
        await db.commit()
    print("Database setup complete.")

if __name__ == "__main__":
    asyncio.run(setup())
