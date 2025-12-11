# brandguard/backend/app/services/data_collectors/reviews_collector.py
import asyncio
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.sentiment import Review
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
from bs4 import BeautifulSoup
import time


class ReviewsCollector:
    """
    Collect public reviews from various platforms
    """

    PLATFORMS = [
        {
            "name": "Google Reviews",
            "base_url": "https://www.google.com/search",
            "requires_scraping": True,
        },
        {
            "name": "Trustpilot",
            "base_url": "https://www.trustpilot.com",
            "requires_api": False,
        },
    ]

    def __init__(self):
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome driver for scraping (where allowed)"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    async def collect_google_reviews(
        self, company_name: str, location: str = None
    ) -> List[Dict]:
        """Collect Google Reviews (where available publicly)"""
        reviews = []

        search_query = f"{company_name} reviews"
        if location:
            search_query += f" {location}"

        try:
            self.driver.get(f"https://www.google.com/search?q={search_query}")
            time.sleep(2)

            # Find review elements
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            review_elements = soup.find_all("div", {"data-review-id": True})

            for element in review_elements:
                review = self._parse_google_review(element, company_name)
                if review:
                    reviews.append(review)

        except Exception as e:
            logger.error(f"Google Reviews collection error: {str(e)}")

        return reviews

    def _parse_google_review(self, element, company: Company) -> Dict:
        """Parse individual Google review"""
        try:
            rating_stars = element.find("span", class_="NyDUv") or element.find(
                "div", {"role": "img"}
            )
            text_element = element.find("span", {"data-expandable-section": True})

            if rating_stars and text_element:
                return {
                    "platform": "Google Reviews",
                    "reviewer_id": None,  # Not available publicly
                    "rating": self._extract_rating_from_stars(rating_stars),
                    "content": text_element.text.strip(),
                    "review_date": self._parse_relative_date(date_element),
                    "verified": True,  # Assume verified for collected reviews
                    "helpful_count": 0,
                }

        except Exception as e:
            logger.error(f"Failed to parse Google review: {str(e)}")

        return None

    def _extract_rating_from_stars(self, stars_element) -> int:
        """Convert star rating to 1-5 scale"""
        # Extract from aria-label or other attributes
        rating_text = stars_element.get("aria-label", "")
        if "star" in rating_text:
            rating_match = re.search(r"(\d)", rating_text)
            if rating_match:
                return int(rating_match.group(1))
        return 3  # Default

    def _parse_relative_date(self, date_element) -> datetime:
        """Convert relative date strings to datetime"""
        date_text = date_element.text

        relative_patterns = {
            r"(\d+)\s+hour": lambda x: timedelta(hours=int(x)),
            r"(\d+)\s+day": lambda x: timedelta(days=int(x)),
            r"(\d+)\s+week": lambda x: timedelta(weeks=int(x)),
            r"(\d+)\s+month": lambda x: timedelta(days=int(x) * 30),
        }

        for pattern, delta_func in relative_patterns.items():
            match = re.search(pattern, date_text)
            if match:
                return datetime.utcnow() - delta_func(match.group(1))

        return datetime.utcnow() - timedelta(days=1)  # Default
