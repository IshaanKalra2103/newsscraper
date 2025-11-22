"""Configuration settings for the News Scraper API."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_TITLE: str = "News Scraper API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "API to scrape news articles with NLP keyword filtering"

    # Database
    DATABASE_URL: str = "sqlite:///./news_scraper.db"

    # NLP Keywords
    ENERGY_KEYWORDS: List[str] = [
        "energy", "electricity", "power grid", "blackout", "outage",
        "renewable energy", "solar", "wind power", "nuclear", "fossil fuel",
        "power plant", "transmission", "grid", "utility", "electrical"
    ]

    FINANCIAL_KEYWORDS: List[str] = [
        "financial", "economy", "stock market", "inflation", "recession",
        "GDP", "economic", "finance", "investment", "banking", "market",
        "cryptocurrency", "bitcoin", "trading", "fiscal"
    ]

    AI_KEYWORDS: List[str] = [
        "artificial intelligence", "AI", "machine learning", "deep learning",
        "neural network", "GPT", "LLM", "large language model", "OpenAI",
        "ChatGPT", "automation", "robotics", "computer vision", "NLP",
        "natural language processing", "data center", "compute", "GPU"
    ]

    # Scraping Settings
    REQUEST_TIMEOUT: int = 30
    MAX_ARTICLES_PER_SCRAPE: int = 50
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
