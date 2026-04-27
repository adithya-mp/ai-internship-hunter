"""
ApplyIQ — FastAPI Application Entry Point
Updated to wire in the multi-platform scraper scheduler.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from config import get_settings
from database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("ApplyIQ Backend Starting...")

    # Initialize database tables
    await init_db()
    print("✓ Database tables created")

    # Seed mock jobs on first run (development convenience)
    from scraper.mock_scraper import seed_mock_jobs
    await seed_mock_jobs()
    print("✓ Mock jobs seeded (skipped if already exist)")

    # Start the multi-platform job scraper scheduler
    from scraper.scheduler import setup_scheduler
    scheduler = setup_scheduler(app, interval_hours=settings.SCRAPE_INTERVAL_HOURS)
    print(f"✓ Job scraper scheduled every {settings.SCRAPE_INTERVAL_HOURS} hours")

    # Run one immediate scraping cycle in background (non-blocking)
    import asyncio
    from scraper.scheduler import run_scraping_cycle
    asyncio.create_task(run_scraping_cycle())
    print("✓ Initial scraping cycle triggered (running in background)")

    yield

    # Shutdown
    if scheduler.running:
        scheduler.shutdown(wait=False)
    print("ApplyIQ Backend Shutting Down...")


app = FastAPI(
    title="ApplyIQ API",
    description="AI-Powered Internship Automation Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static files for uploads ───
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ─── Register Routers ───
from routers import auth, jobs, resume, cover_letter, skills, chatbot, email_assistant, upload, applications

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(cover_letter.router, prefix="/api/cover-letter", tags=["Cover Letter"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(chatbot.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(email_assistant.router, prefix="/api/email", tags=["Email Assistant"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": "ApplyIQ", "version": "1.0.0"}


@app.post("/api/scrape/trigger", tags=["Admin"])
async def trigger_scrape():
    """Manually trigger a scraping cycle (useful for testing)."""
    import asyncio
    from scraper.scheduler import run_scraping_cycle
    asyncio.create_task(run_scraping_cycle())
    return {"status": "scraping cycle triggered", "message": "Check logs for progress"}
