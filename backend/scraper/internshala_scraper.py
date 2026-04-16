"""
Internshala Scraper
Scrapes internship listings from Internshala using Playwright.
Falls back to mock data if scraping fails.
"""

import logging
from typing import List
from scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class IntershalaScraper(BaseScraper):
    """Scrapes internship listings from Internshala."""

    BASE_URL = "https://internshala.com/internships/"

    async def scrape(self, query: str = "software development", location: str = "") -> List[dict]:
        """
        Scrape internship listings from Internshala.
        Falls back gracefully if scraping fails.
        """
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Build URL with filters
                url = self.BASE_URL
                if query:
                    slug = query.lower().replace(" ", "-")
                    url += f"{slug}-internship"

                await page.goto(url, timeout=30000)
                await page.wait_for_selector(".internship_meta", timeout=10000)

                # Extract job listings
                jobs = []
                listings = await page.query_selector_all(".individual_internship")

                for listing in listings[:20]:  # Limit to 20 per scrape
                    try:
                        title_el = await listing.query_selector(".profile a")
                        company_el = await listing.query_selector(".company_name a")
                        location_el = await listing.query_selector("#location_names span a")
                        stipend_el = await listing.query_selector(".stipend")
                        duration_el = await listing.query_selector(".item_body:nth-child(2) span")

                        title = await title_el.inner_text() if title_el else ""
                        company = await company_el.inner_text() if company_el else ""
                        loc = await location_el.inner_text() if location_el else ""
                        stipend = await stipend_el.inner_text() if stipend_el else ""
                        duration = await duration_el.inner_text() if duration_el else ""

                        link_el = await listing.query_selector(".view_detail_button")
                        link = ""
                        if link_el:
                            href = await link_el.get_attribute("href")
                            link = f"https://internshala.com{href}" if href else ""

                        if title and company:
                            jobs.append(self.normalize_job({
                                "title": title.strip(),
                                "company": company.strip(),
                                "description": f"Internship at {company.strip()} for {title.strip()} role.",
                                "skills_required": [],
                                "location": loc.strip(),
                                "apply_url": link,
                                "source": "internshala",
                                "job_type": "internship",
                                "stipend": stipend.strip(),
                                "duration": duration.strip(),
                            }))
                    except Exception as e:
                        logger.warning(f"Error parsing listing: {e}")
                        continue

                await browser.close()
                logger.info(f"Scraped {len(jobs)} jobs from Internshala")
                return jobs

        except Exception as e:
            logger.error(f"Internshala scraping failed: {e}")
            return []
