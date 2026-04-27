"""
Job Scraping Scheduler — Resume-Aware Multi-Platform Scraper
============================================================
This is the heart of the "scan platforms based on my resume" feature.

Flow:
1. Load all user profiles + their skill embeddings
2. For each unique skill cluster, run targeted searches on:
   - LinkedIn
   - Internshala
   - Unstop
3. Deduplicate, generate embeddings, store new jobs
4. Run every SCRAPE_INTERVAL_HOURS (default: 6)
"""

import logging
import uuid
from datetime import datetime
from collections import Counter
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from models.job import Job
from models.user import User
from models.skill import Skill
from scraper.mock_scraper import MockScraper
from services.job_matcher import create_job_embedding

logger = logging.getLogger(__name__)

# ─── Platform Scrapers ───────────────────────────────────────────────────────

def _get_scrapers():
    """
    Lazily import scrapers so app starts even if Playwright isn't installed.
    Returns a list of (scraper_name, scraper_instance) tuples.
    """
    scrapers = []

    try:
        from scraper.linkedin_scraper import LinkedInScraper
        scrapers.append(("LinkedIn", LinkedInScraper()))
    except Exception as e:
        logger.warning(f"LinkedIn scraper unavailable: {e}")

    try:
        from scraper.unstop_scraper import UnstopScraper
        scrapers.append(("Unstop", UnstopScraper()))
    except Exception as e:
        logger.warning(f"Unstop scraper unavailable: {e}")

    try:
        from scraper.internshala_scraper import IntershalaScraper
        scrapers.append(("Internshala", IntershalaScraper()))
    except Exception as e:
        logger.warning(f"Internshala scraper unavailable: {e}")

    # Mock scraper always available (for development / demo)
    scrapers.append(("Mock", MockScraper()))

    return scrapers


# ─── Skill → Search Query Mapping ────────────────────────────────────────────

# Maps individual skills to effective job search queries.
# When a user has these skills, we search for these terms.
SKILL_TO_QUERY_MAP = {
    # Frontend
    "react": "React Frontend Developer Intern",
    "vue.js": "Vue.js Frontend Intern",
    "angular": "Angular Developer Intern",
    "next.js": "Next.js React Developer Intern",
    "typescript": "TypeScript Frontend Developer Intern",
    "javascript": "JavaScript Web Developer Intern",
    "html": "Web Developer Intern",
    "css": "Frontend Developer Intern",
    "figma": "UI UX Designer Intern",
    "tailwind": "Frontend Developer Intern",

    # Backend
    "python": "Python Developer Intern",
    "fastapi": "Python Backend Developer Intern",
    "django": "Django Python Developer Intern",
    "flask": "Python Flask Backend Intern",
    "node.js": "Node.js Backend Developer Intern",
    "express": "Node.js Express Backend Intern",
    "java": "Java Developer Intern",
    "spring boot": "Java Spring Boot Backend Intern",
    "go": "Golang Backend Developer Intern",
    "rust": "Systems Developer Intern",
    "c++": "C++ Software Engineer Intern",
    "c#": "C# .NET Developer Intern",
    "ruby": "Ruby on Rails Developer Intern",
    "php": "PHP Web Developer Intern",

    # Data / ML / AI
    "machine learning": "Machine Learning Engineer Intern",
    "deep learning": "Deep Learning AI Research Intern",
    "tensorflow": "Machine Learning TensorFlow Intern",
    "pytorch": "Deep Learning PyTorch Research Intern",
    "data science": "Data Science Analytics Intern",
    "pandas": "Data Analyst Python Intern",
    "numpy": "Data Science Python Intern",
    "nlp": "Natural Language Processing AI Intern",
    "computer vision": "Computer Vision AI Intern",
    "data engineering": "Data Engineering Intern",
    "apache spark": "Big Data Spark Engineer Intern",
    "kafka": "Data Infrastructure Engineer Intern",
    "sql": "Data Analyst SQL Intern",
    "postgresql": "Backend Database Developer Intern",
    "mongodb": "Full Stack MongoDB Developer Intern",

    # Cloud / DevOps
    "aws": "AWS Cloud Engineer Intern",
    "azure": "Azure Cloud Developer Intern",
    "gcp": "Google Cloud Engineer Intern",
    "docker": "DevOps Engineer Intern",
    "kubernetes": "Cloud DevOps Kubernetes Intern",
    "terraform": "Infrastructure DevOps Intern",
    "ci/cd": "DevOps Platform Engineer Intern",
    "linux": "Systems Engineer DevOps Intern",

    # Mobile
    "flutter": "Flutter Mobile Developer Intern",
    "react native": "React Native Mobile Developer Intern",
    "android": "Android App Developer Intern",
    "ios": "iOS Swift Developer Intern",
    "swift": "iOS App Developer Intern",
    "kotlin": "Android Kotlin Developer Intern",
    "dart": "Flutter Mobile App Intern",

    # Blockchain / Web3
    "solidity": "Blockchain Solidity Developer Intern",
    "web3": "Web3 Blockchain Developer Intern",
    "ethereum": "Blockchain Smart Contract Intern",

    # Cybersecurity
    "network security": "Cybersecurity Engineer Intern",
    "penetration testing": "Security Analyst Pen Test Intern",
    "owasp": "Application Security Engineer Intern",

    # Game Dev
    "unity": "Unity Game Developer Intern",
    "unreal": "Unreal Engine Game Developer Intern",

    # General
    "product management": "Product Manager Intern",
    "agile": "Software Developer Intern",
    "git": "Software Developer Intern",
    "graphql": "Full Stack API Developer Intern",
    "rest": "Backend API Developer Intern",
    "microservices": "Backend Microservices Engineer Intern",
}

DEFAULT_QUERIES = [
    "software developer intern",
    "full stack developer intern",
    "data science intern",
    "machine learning intern",
    "frontend developer intern",
]


# ─── Core Functions ───────────────────────────────────────────────────────────

async def _get_search_queries_from_users(db: AsyncSession) -> List[str]:
    """
    Analyze all user skills in the database and derive targeted search queries.
    Uses skill frequency to prioritize the most common skill interests.
    """
    # Fetch all skills across all users
    result = await db.execute(select(Skill.name))
    skill_names = [row[0].lower() for row in result.fetchall()]

    if not skill_names:
        logger.info("No user skills found — using default search queries")
        return DEFAULT_QUERIES

    # Count skill frequency
    skill_counts = Counter(skill_names)
    top_skills = [skill for skill, _ in skill_counts.most_common(10)]

    # Map skills → search queries, deduplicate
    queries = []
    seen = set()
    for skill in top_skills:
        # Try exact match first, then partial match
        query = SKILL_TO_QUERY_MAP.get(skill)
        if not query:
            for key, val in SKILL_TO_QUERY_MAP.items():
                if key in skill or skill in key:
                    query = val
                    break
        if query and query not in seen:
            queries.append(query)
            seen.add(query)

    # Also add queries from user profile_data skills
    profile_result = await db.execute(select(User.profile_data))
    for (profile_data,) in profile_result.fetchall():
        if not profile_data:
            continue
        for skill in profile_data.get("skills", []):
            skill_lower = skill.lower()
            query = SKILL_TO_QUERY_MAP.get(skill_lower)
            if query and query not in seen:
                queries.append(query)
                seen.add(query)

    # Ensure we always have some queries
    if not queries:
        queries = DEFAULT_QUERIES[:5]

    logger.info(f"Generated {len(queries)} search queries from user skills: {queries[:5]}...")
    return queries[:8]  # Cap at 8 queries per cycle to avoid being rate-limited


async def _store_jobs(session: AsyncSession, all_jobs: List[dict]) -> int:
    """
    Deduplicate and store new jobs in the database.
    Returns number of new jobs stored.
    """
    stored_count = 0

    for job_data in all_jobs:
        try:
            # Deduplicate by title + company (case-insensitive)
            existing = await session.execute(
                select(Job).where(
                    Job.title.ilike(job_data["title"]),
                    Job.company.ilike(job_data["company"]),
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip duplicate

            # Generate embedding for AI matching
            try:
                embedding = await create_job_embedding(
                    job_data["title"],
                    job_data["description"],
                    job_data.get("skills_required", []),
                )
            except Exception as emb_err:
                logger.warning(f"Embedding failed for '{job_data['title']}': {emb_err}")
                embedding = None

            job = Job(
                id=uuid.uuid4(),
                title=job_data["title"],
                company=job_data["company"],
                description=job_data["description"],
                skills_required=job_data.get("skills_required", []),
                location=job_data.get("location", ""),
                apply_url=job_data.get("apply_url", ""),
                source=job_data.get("source", "unknown"),
                job_type=job_data.get("job_type", "internship"),
                stipend=job_data.get("stipend", ""),
                duration=job_data.get("duration", ""),
                embedding=embedding,
                scraped_at=datetime.utcnow(),
            )
            session.add(job)
            stored_count += 1

        except Exception as e:
            logger.error(f"Error storing job '{job_data.get('title', '?')}': {e}")
            continue

    await session.commit()
    return stored_count


# ─── Main Scraping Cycle ──────────────────────────────────────────────────────

async def run_scraping_cycle() -> int:
    """
    Full scraping cycle:
    1. Analyze user skills → generate targeted search queries
    2. Run all scrapers in parallel per query
    3. Store new unique jobs with embeddings

    Returns total number of new jobs stored.
    """
    logger.info("=" * 60)
    logger.info("ApplyIQ Scraping Cycle Started")
    logger.info("=" * 60)

    all_jobs: List[dict] = []
    scrapers = _get_scrapers()

    async with async_session() as db:
        # Step 1: Get personalized queries from user profiles
        queries = await _get_search_queries_from_users(db)

        # Step 2: Run each scraper for each query
        for query in queries:
            for scraper_name, scraper in scrapers:
                try:
                    logger.info(f"[{scraper_name}] Searching: '{query}'")
                    jobs = await scraper.scrape(query=query)
                    all_jobs.extend(jobs)
                    logger.info(f"[{scraper_name}] Found {len(jobs)} results")
                except Exception as e:
                    logger.error(f"[{scraper_name}] Failed for query '{query}': {e}")

        logger.info(f"Total raw results: {len(all_jobs)} jobs across all platforms")

        # Step 3: Deduplicate and store
        stored = await _store_jobs(db, all_jobs)

    logger.info(f"Scraping cycle complete — {stored} new jobs stored")
    logger.info("=" * 60)
    return stored


# ─── APScheduler Setup ───────────────────────────────────────────────────────

def setup_scheduler(app, interval_hours: int = 6):
    """
    Attach APScheduler to the FastAPI app.
    Runs run_scraping_cycle() every `interval_hours` hours.

    Call this from main.py lifespan:
        setup_scheduler(app, settings.SCRAPE_INTERVAL_HOURS)
    """
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scraping_cycle,
        trigger="interval",
        hours=interval_hours,
        id="scraping_cycle",
        name="Multi-Platform Job Scraper",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )
    scheduler.start()
    logger.info(f"Scheduler started — scraping every {interval_hours} hours")
    return scheduler
