"""
LinkedIn Scraper
Uses LinkedIn's public job search (no auth required for basic listings).
Falls back gracefully if blocked. Respects rate limits.
"""

import logging
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List
from scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """
    Scrapes LinkedIn public job listings.
    Uses the public /jobs/search endpoint — no login required.
    LinkedIn's public search is accessible without auth for basic listings.
    """

    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    JOB_DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    async def scrape(self, query: str = "software developer intern", location: str = "India") -> List[dict]:
        """
        Scrape LinkedIn job listings via the guest API.
        Returns list of normalized job dicts.
        """
        jobs = []

        try:
            async with httpx.AsyncClient(
                headers=self.HEADERS,
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                # LinkedIn guest job search — returns HTML fragments
                params = {
                    "keywords": query,
                    "location": location,
                    "f_JT": "I",       # I = Internship job type
                    "f_TPR": "r604800", # Past week
                    "start": 0,
                    "count": 25,
                }

                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("li")

                for card in job_cards:
                    try:
                        job_data = self._parse_job_card(card)
                        if job_data:
                            # Fetch job details for description + skills
                            detail = await self._fetch_job_detail(client, job_data.get("job_id", ""))
                            if detail:
                                job_data.update(detail)
                            jobs.append(self.normalize_job(job_data))
                            await asyncio.sleep(0.5)  # Be polite — avoid rate limits
                    except Exception as e:
                        logger.warning(f"LinkedIn card parse error: {e}")
                        continue

        except httpx.HTTPStatusError as e:
            logger.error(f"LinkedIn HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"LinkedIn scrape failed: {e}")

        logger.info(f"LinkedIn: scraped {len(jobs)} jobs for '{query}' in '{location}'")
        return jobs

    def _parse_job_card(self, card) -> dict | None:
        """Parse a LinkedIn job card HTML fragment."""
        try:
            # Job ID from data attribute or link
            job_link = card.find("a", class_="base-card__full-link")
            if not job_link:
                return None

            href = job_link.get("href", "")
            # Extract job ID from URL like /jobs/view/1234567890
            job_id = ""
            if "/view/" in href:
                job_id = href.split("/view/")[1].split("?")[0].strip("/")

            title_el = card.find("h3", class_="base-search-card__title")
            company_el = card.find("h4", class_="base-search-card__subtitle")
            location_el = card.find("span", class_="job-search-card__location")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            location = location_el.get_text(strip=True) if location_el else ""

            if not title or not company:
                return None

            return {
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "apply_url": f"https://www.linkedin.com/jobs/view/{job_id}" if job_id else href,
                "source": "linkedin",
                "job_type": "internship",
                "description": f"Internship position: {title} at {company}",  # Default until detail fetch
                "skills_required": [],
                "stipend": "",
                "duration": "",
            }
        except Exception:
            return None

    async def _fetch_job_detail(self, client: httpx.AsyncClient, job_id: str) -> dict | None:
        """Fetch full job description from LinkedIn job detail API."""
        if not job_id:
            return None
        try:
            url = self.JOB_DETAIL_URL.format(job_id=job_id)
            response = await client.get(url, timeout=15.0)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Description
            desc_el = soup.find("div", class_="description__text")
            description = desc_el.get_text(separator="\n", strip=True)[:3000] if desc_el else ""

            # Skills (LinkedIn lists them in criteria section)
            skills = []
            criteria = soup.find_all("li", class_="description__job-criteria-item")
            for c in criteria:
                header = c.find("h3")
                value = c.find("span")
                if header and value:
                    if "skill" in header.get_text(strip=True).lower():
                        skills.append(value.get_text(strip=True))

            # Also try to extract skills from description text
            skills += self._extract_skills_from_text(description)

            return {
                "description": description or "No description available.",
                "skills_required": list(set(skills))[:15],  # Deduplicate, cap at 15
            }
        except Exception as e:
            logger.debug(f"LinkedIn detail fetch failed for {job_id}: {e}")
            return None

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Basic keyword extraction for common tech skills from job description."""
        common_skills = [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "Java",
            "C++", "C#", "Go", "Rust", "SQL", "PostgreSQL", "MongoDB",
            "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Git",
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "FastAPI", "Django", "Flask", "Next.js", "Vue.js", "Angular",
            "Redis", "Kafka", "GraphQL", "REST", "Figma", "Linux",
            "Data Science", "NLP", "Computer Vision", "Solidity", "Flutter",
        ]
        text_lower = text.lower()
        return [s for s in common_skills if s.lower() in text_lower]
