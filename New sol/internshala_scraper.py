"""
Internshala Scraper (Improved)
Uses Internshala's public JSON API endpoint — much more reliable than scraping HTML.
Falls back to Playwright-based scraping if API is unavailable.
"""

import logging
import httpx
from typing import List
from bs4 import BeautifulSoup
from scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class IntershalaScraper(BaseScraper):
    """
    Scrapes internship listings from Internshala.
    Primary method: JSON API (fast, reliable).
    Fallback: Playwright browser scraping.
    """

    # Internshala's internal search API (observable via browser DevTools)
    API_URL = "https://internshala.com/internships/ajax"
    BASE_URL = "https://internshala.com"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://internshala.com/internships/",
    }

    async def scrape(self, query: str = "software development", location: str = "") -> List[dict]:
        """
        Fetch internship listings from Internshala.
        Tries JSON API first, falls back to Playwright.
        """
        jobs = await self._scrape_via_api(query, location)

        if not jobs:
            logger.info("Internshala API failed, trying Playwright fallback...")
            jobs = await self._scrape_via_playwright(query, location)

        logger.info(f"Internshala: scraped {len(jobs)} jobs for '{query}'")
        return jobs

    async def _scrape_via_api(self, query: str, location: str) -> List[dict]:
        """Attempt to scrape via Internshala's AJAX API."""
        jobs = []
        try:
            async with httpx.AsyncClient(
                headers=self.HEADERS,
                follow_redirects=True,
                timeout=20.0,
            ) as client:
                # Build category slug from query
                category_slug = query.lower().replace(" ", "-")

                # Internshala AJAX internship search
                params = {
                    "search_po": "1",
                    "sort_by": "recently_added",
                }
                if location:
                    params["location_ids"] = location

                url = f"{self.API_URL}/{category_slug}-internship"
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                # Internshala wraps listings in "internships_meta" or "internships"
                internships = (
                    data.get("internships_meta", {})
                    or data.get("internships", {})
                    or {}
                )

                for intern_id, intern_data in internships.items():
                    try:
                        parsed = self._parse_internship(intern_id, intern_data)
                        if parsed:
                            jobs.append(self.normalize_job(parsed))
                    except Exception as e:
                        logger.warning(f"Internshala parse error: {e}")

        except Exception as e:
            logger.debug(f"Internshala API attempt failed: {e}")

        return jobs

    def _parse_internship(self, intern_id: str, data: dict) -> dict | None:
        """Parse Internshala internship JSON object."""
        try:
            title = data.get("profile_name", "").strip()
            company = data.get("company_name", "").strip()

            if not title or not company:
                return None

            # Skills
            skills = [s.strip() for s in data.get("skill_criteria", "").split(",") if s.strip()]

            # Location
            locations = data.get("location_names", [])
            location = ", ".join(locations) if locations else "India"

            # Stipend
            stipend = data.get("stipend", {})
            if isinstance(stipend, dict):
                stipend_str = stipend.get("salary", "Unpaid")
            else:
                stipend_str = str(stipend) if stipend else "Unpaid"

            # Duration
            duration = data.get("duration", "")

            # Description — build from available fields
            about = data.get("about_company", "")
            desc = f"{title} internship at {company}. {about}".strip()

            apply_url = f"https://internshala.com/internship/detail/{intern_id}"

            return {
                "title": title,
                "company": company,
                "description": desc[:3000],
                "skills_required": skills[:15],
                "location": location,
                "apply_url": apply_url,
                "source": "internshala",
                "job_type": "internship",
                "stipend": stipend_str,
                "duration": duration,
            }
        except Exception:
            return None

    async def _scrape_via_playwright(self, query: str, location: str) -> List[dict]:
        """Playwright fallback scraper for Internshala."""
        jobs = []
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                )
                page = await context.new_page()

                slug = query.lower().replace(" ", "-")
                url = f"https://internshala.com/internships/{slug}-internship/"
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                # Wait for job cards
                await page.wait_for_selector(".individual_internship", timeout=10000)

                listings = await page.query_selector_all(".individual_internship")
                for listing in listings[:20]:
                    try:
                        title_el = await listing.query_selector(".profile a, h3 a")
                        company_el = await listing.query_selector(".company_name a, .company_name")
                        location_el = await listing.query_selector("#location_names span a, .location_link")
                        stipend_el = await listing.query_selector(".stipend")
                        duration_el = await listing.query_selector(".item_body:nth-child(2) span")

                        title = (await title_el.inner_text()).strip() if title_el else ""
                        company = (await company_el.inner_text()).strip() if company_el else ""
                        loc = (await location_el.inner_text()).strip() if location_el else ""
                        stipend = (await stipend_el.inner_text()).strip() if stipend_el else ""
                        duration = (await duration_el.inner_text()).strip() if duration_el else ""

                        # Get apply link
                        link_el = await listing.query_selector(".view_detail_button")
                        href = await link_el.get_attribute("href") if link_el else ""
                        apply_url = f"https://internshala.com{href}" if href else ""

                        if title and company:
                            jobs.append(self.normalize_job({
                                "title": title,
                                "company": company,
                                "description": f"{title} internship at {company}. Location: {loc}.",
                                "skills_required": [],
                                "location": loc,
                                "apply_url": apply_url,
                                "source": "internshala",
                                "job_type": "internship",
                                "stipend": stipend,
                                "duration": duration,
                            }))
                    except Exception as e:
                        logger.warning(f"Playwright listing parse error: {e}")

                await browser.close()

        except Exception as e:
            logger.error(f"Internshala Playwright scrape failed: {e}")

        return jobs
