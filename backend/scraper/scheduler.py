"""
Job Scraping Scheduler
Runs scrapers periodically and stores results in the database.
"""

import logging
import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from models.job import Job
from scraper.mock_scraper import MockScraper
from services.job_matcher import create_job_embedding

logger = logging.getLogger(__name__)


async def run_scraping_cycle():
    """
    Execute one full scraping cycle:
    1. Run all scrapers
    2. Deduplicate against existing jobs
    3. Generate embeddings
    4. Store new jobs in DB
    """
    logger.info("Starting scraping cycle...")

    # Initialize scrapers
    mock_scraper = MockScraper()

    all_jobs = []

    # Run mock scraper (always available)
    try:
        mock_jobs = await mock_scraper.scrape()
        all_jobs.extend(mock_jobs)
        logger.info(f"Mock scraper returned {len(mock_jobs)} jobs")
    except Exception as e:
        logger.error(f"Mock scraper failed: {e}")

    # Try Internshala scraper (may fail in non-browser environments)
    try:
        from scraper.internshala_scraper import IntershalaScraper
        internshala = IntershalaScraper()
        internshala_jobs = await internshala.scrape()
        all_jobs.extend(internshala_jobs)
        logger.info(f"Internshala scraper returned {len(internshala_jobs)} jobs")
    except Exception as e:
        logger.warning(f"Internshala scraper skipped: {e}")

    # Store jobs in database
    async with async_session() as session:
        stored_count = 0
        for job_data in all_jobs:
            try:
                # Check for duplicates (by title + company)
                existing = await session.execute(
                    select(Job).where(
                        Job.title == job_data["title"],
                        Job.company == job_data["company"],
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Generate embedding for the job
                try:
                    embedding = await create_job_embedding(
                        job_data["title"],
                        job_data["description"],
                        job_data.get("skills_required", []),
                    )
                except Exception:
                    embedding = None

                # Create job record
                job = Job(
                    id=uuid.uuid4(),
                    title=job_data["title"],
                    company=job_data["company"],
                    description=job_data["description"],
                    skills_required=job_data.get("skills_required", []),
                    location=job_data.get("location", ""),
                    apply_url=job_data.get("apply_url", ""),
                    source=job_data.get("source", "mock"),
                    job_type=job_data.get("job_type", "internship"),
                    stipend=job_data.get("stipend", ""),
                    duration=job_data.get("duration", ""),
                    embedding=embedding,
                    scraped_at=datetime.utcnow(),
                )
                session.add(job)
                stored_count += 1
            except Exception as e:
                logger.error(f"Error storing job: {e}")
                continue

        await session.commit()
        logger.info(f"Stored {stored_count} new jobs in database")

    return stored_count
