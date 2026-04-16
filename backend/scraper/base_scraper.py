"""
Base Scraper
Abstract base class for all job scrapers.
"""

from abc import ABC, abstractmethod
from typing import List


class BaseScraper(ABC):
    """Abstract base class for job scrapers."""

    @abstractmethod
    async def scrape(self, query: str = "", location: str = "") -> List[dict]:
        """
        Scrape job listings.
        Returns list of dicts with keys:
        - title, company, description, skills_required, location,
          apply_url, source, job_type, stipend, duration
        """
        pass

    def normalize_job(self, raw: dict) -> dict:
        """Normalize scraped job data to standard format."""
        return {
            "title": raw.get("title", "").strip(),
            "company": raw.get("company", "").strip(),
            "description": raw.get("description", "").strip(),
            "skills_required": raw.get("skills_required", []),
            "location": raw.get("location", "").strip(),
            "apply_url": raw.get("apply_url", ""),
            "source": raw.get("source", "unknown"),
            "job_type": raw.get("job_type", "internship"),
            "stipend": raw.get("stipend", ""),
            "duration": raw.get("duration", ""),
        }
