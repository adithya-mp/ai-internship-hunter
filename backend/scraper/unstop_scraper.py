"""
Unstop (formerly Dare2Compete) Scraper
Uses Unstop's public listing API — returns JSON directly, much more reliable than HTML scraping.
"""

import logging
import httpx
from typing import List
from scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class UnstopScraper(BaseScraper):
    """
    Scrapes internship listings from Unstop.
    Unstop provides a public JSON API for opportunities — no auth required.
    """

    # Unstop's public opportunities API
    API_URL = "https://unstop.com/api/public/opportunity/search-result"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://unstop.com",
        "Referer": "https://unstop.com/internships",
    }

    async def scrape(self, query: str = "software", location: str = "") -> List[dict]:
        """
        Fetch internship listings from Unstop's public API.
        Returns list of normalized job dicts.
        """
        jobs = []

        try:
            async with httpx.AsyncClient(
                headers=self.HEADERS,
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                params = {
                    "opportunity": "internships",    # Filter for internships only
                    "search": query,
                    "page": 1,
                    "per_page": 25,
                    "sort": "recent",                # Most recent first
                }
                if location:
                    params["city[]"] = location

                response = await client.get(self.API_URL, params=params)
                response.raise_for_status()

                data = response.json()

                # Unstop returns data under "data" -> "data" (list of opportunities)
                opportunities = (
                    data.get("data", {}).get("data", [])
                    or data.get("data", [])
                    or []
                )

                for opp in opportunities:
                    try:
                        parsed = self._parse_opportunity(opp)
                        if parsed:
                            jobs.append(self.normalize_job(parsed))
                    except Exception as e:
                        logger.warning(f"Unstop parse error: {e}")
                        continue

        except httpx.HTTPStatusError as e:
            logger.error(f"Unstop HTTP {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Unstop scrape failed: {e}")

        logger.info(f"Unstop: scraped {len(jobs)} internships for '{query}'")
        return jobs

    def _parse_opportunity(self, opp: dict) -> dict | None:
        """
        Parse a single Unstop opportunity object into standard format.
        Unstop API response structure varies — we handle the common patterns.
        """
        try:
            # Title / Role
            title = (
                opp.get("title")
                or opp.get("job_title")
                or opp.get("opportunity_title", "")
            ).strip()

            if not title:
                return None

            # Company / Organisation
            org = opp.get("organisation", {}) or {}
            company = (
                org.get("name")
                or opp.get("organisation_name")
                or opp.get("company_name", "Unknown Company")
            ).strip()

            # Description
            description = (
                opp.get("description")
                or opp.get("about", "")
                or f"Internship opportunity: {title} at {company}"
            )
            if isinstance(description, str):
                # Strip HTML tags if present
                from bs4 import BeautifulSoup
                description = BeautifulSoup(description, "html.parser").get_text(separator=" ", strip=True)[:3000]

            # Skills — Unstop often has a skills array
            skills_raw = opp.get("skills", []) or opp.get("required_skills", []) or []
            skills = []
            for s in skills_raw:
                if isinstance(s, dict):
                    skills.append(s.get("name", s.get("skill_name", "")))
                elif isinstance(s, str):
                    skills.append(s)
            skills = [s for s in skills if s]  # Remove empty

            # Location
            location_parts = []
            for loc_field in ["city", "location", "state"]:
                val = opp.get(loc_field, "")
                if isinstance(val, list):
                    location_parts.extend([v.get("name", str(v)) if isinstance(v, dict) else str(v) for v in val])
                elif val:
                    location_parts.append(str(val))
            location = ", ".join(location_parts) if location_parts else "India"

            # Stipend
            stipend = ""
            stipend_data = opp.get("stipend") or opp.get("compensation", {})
            if isinstance(stipend_data, dict):
                amount = stipend_data.get("amount") or stipend_data.get("max", "")
                currency = stipend_data.get("currency", "INR")
                if amount:
                    stipend = f"{currency} {amount}/month"
            elif isinstance(stipend_data, str):
                stipend = stipend_data

            # Duration
            duration = str(opp.get("duration", "")) or opp.get("internship_duration", "")
            if duration and not any(unit in duration.lower() for unit in ["month", "week", "day"]):
                duration = f"{duration} months"

            # Application URL
            opp_id = opp.get("id") or opp.get("opportunity_id", "")
            slug = opp.get("slug") or opp.get("seo_url", "")
            apply_url = (
                f"https://unstop.com/{slug}"
                if slug
                else f"https://unstop.com/internships/{opp_id}"
            )

            return {
                "title": title,
                "company": company,
                "description": description,
                "skills_required": skills[:15],
                "location": location,
                "apply_url": apply_url,
                "source": "unstop",
                "job_type": "internship",
                "stipend": stipend,
                "duration": duration,
            }

        except Exception as e:
            logger.warning(f"Unstop opportunity parse failed: {e}")
            return None
