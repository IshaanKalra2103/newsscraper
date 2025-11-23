"""Base scraper class for news sources."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from app.config import settings
from app.models.article import ArticleCreate

try:
    from patchright.sync_api import sync_playwright
    PATCHRIGHT_AVAILABLE = True
except ImportError:
    PATCHRIGHT_AVAILABLE = False
    print("Warning: Patchright not available. Install with: uv add patchright")


class BaseScraper(ABC):
    """Base class for all news scrapers."""

    def __init__(self, source_name: str):
        """
        Initialize scraper.

        Args:
            source_name: Name of the news source
        """
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })

    @abstractmethod
    def scrape_articles(
        self,
        max_articles: int = 20,
        keywords_filter: Optional[List[str]] = None
    ) -> List[ArticleCreate]:
        """
        Scrape articles from the source.

        Args:
            max_articles: Maximum number of articles to scrape
            keywords_filter: Optional list of keywords to filter by

        Returns:
            List of ArticleCreate objects
        """
        pass

    def fetch_page(self, url: str, use_stealth: bool = False) -> Optional[BeautifulSoup]:
        """
        Fetch a web page and return BeautifulSoup object.

        Args:
            url: URL to fetch
            use_stealth: If True, use Patchright for stealth scraping

        Returns:
            BeautifulSoup object or None if failed
        """
        if use_stealth and PATCHRIGHT_AVAILABLE:
            return self._fetch_with_patchright(url)

        try:
            response = self.session.get(
                url,
                timeout=settings.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Error fetching {url} with requests: {str(e)}")
            # Fallback to Patchright if available
            if PATCHRIGHT_AVAILABLE:
                print(f"Falling back to Patchright for {url}")
                return self._fetch_with_patchright(url)
            return None

    def _fetch_with_patchright(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch page using Patchright (stealth Playwright).

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=settings.USER_AGENT
                )
                page = context.new_page()

                # Navigate to the page
                page.goto(url, wait_until='domcontentloaded', timeout=settings.REQUEST_TIMEOUT * 1000)

                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)

                # Get the HTML content
                content = page.content()

                browser.close()

                return BeautifulSoup(content, 'lxml')

        except Exception as e:
            print(f"Error fetching {url} with Patchright: {str(e)}")
            return None

    def parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse date string to datetime object.

        Args:
            date_string: Date string in various formats

        Returns:
            datetime object or None if parsing fails
        """
        if not date_string:
            return None

        try:
            return date_parser.parse(date_string)
        except Exception as e:
            print(f"Error parsing date '{date_string}': {str(e)}")
            return None

    def extract_text(self, element) -> str:
        """
        Extract clean text from BeautifulSoup element.

        Args:
            element: BeautifulSoup element

        Returns:
            Cleaned text string
        """
        if not element:
            return ""

        text = element.get_text(separator=' ', strip=True)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def close(self):
        """Close the session."""
        self.session.close()
