"""Article database and Pydantic models."""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel
from app.database.db import Base


def get_time_period(published_date: Optional[datetime]) -> Optional[str]:
    """
    Determine the time period for an article based on publication date.

    Periods:
    - "2002-2018": Early period (2002 to end of 2018)
    - "2018-2022": Middle period (2019 to end of 2022)
    - "2023-2024": Recent period (2023 onwards)

    Args:
        published_date: The publication date of the article

    Returns:
        Time period string or None if date is outside range or None
    """
    if not published_date:
        return None

    year = published_date.year

    if 2002 <= year <= 2018:
        return "2002-2018"
    elif 2019 <= year <= 2022:
        return "2018-2022"
    elif 2023 <= year <= 2024:
        return "2023-2024"
    else:
        return None


class ArticleDB(Base):
    """Database model for articles."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    author = Column(String(200), nullable=True)
    published_date = Column(DateTime, nullable=True, index=True)
    scraped_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # NLP Analysis
    keywords = Column(JSON, nullable=True)  # List of extracted keywords
    categories = Column(JSON, nullable=True)  # List of categories (energy, financial, AI)
    relevance_score = Column(Integer, default=0)  # How relevant based on keywords

    # Time Period (2002-2018, 2018-2022, 2023-2024)
    time_period = Column(String(20), nullable=True, index=True)

    # Metadata
    image_url = Column(String(1000), nullable=True)
    tags = Column(JSON, nullable=True)


class ArticleCreate(BaseModel):
    """Schema for creating an article."""

    title: str
    url: str
    source: str
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    keywords: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    relevance_score: Optional[int] = 0
    time_period: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class Article(BaseModel):
    """Schema for article response."""

    id: int
    title: str
    url: str
    source: str
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    scraped_date: datetime
    keywords: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    relevance_score: int = 0
    time_period: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

    class Config:
        from_attributes = True


class ScrapeRequest(BaseModel):
    """Request model for scraping."""

    sources: List[str]  # e.g., ["nyt", "reuters"]
    max_articles: Optional[int] = 20
    keywords_filter: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ScrapeResponse(BaseModel):
    """Response model for scraping."""

    status: str
    articles_scraped: int
    articles_stored: int
    sources: List[str]
    message: str
