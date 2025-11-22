"""Factory for creating scrapers."""

from typing import Dict, Type
from app.scrapers.base import BaseScraper
from app.scrapers.nyt_scraper import NYTScraper
from app.scrapers.reuters_scraper import ReutersScraper
from app.scrapers.openai_scraper import OpenAIScraper
from app.scrapers.google_scraper import GoogleResearchScraper


class ScraperFactory:
    """Factory to create scraper instances."""

    _scrapers: Dict[str, Type[BaseScraper]] = {
        "nyt": NYTScraper,
        "new_york_times": NYTScraper,
        "reuters": ReutersScraper,
        "openai": OpenAIScraper,
        "openai_blog": OpenAIScraper,
        "google": GoogleResearchScraper,
        "google_research": GoogleResearchScraper,
    }

    @classmethod
    def create_scraper(cls, source: str) -> BaseScraper:
        """
        Create a scraper instance for the given source.

        Args:
            source: Source name (e.g., 'nyt', 'reuters')

        Returns:
            Scraper instance

        Raises:
            ValueError: If source is not supported
        """
        source_key = source.lower().replace(" ", "_")

        if source_key not in cls._scrapers:
            available = ", ".join(sorted(set(cls._scrapers.keys())))
            raise ValueError(
                f"Unsupported source: {source}. Available sources: {available}"
            )

        return cls._scrapers[source_key]()

    @classmethod
    def get_available_sources(cls) -> list:
        """Get list of available source names."""
        return sorted(set(cls._scrapers.keys()))
