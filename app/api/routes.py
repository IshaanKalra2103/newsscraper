"""API routes for the News Scraper API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.db import get_db
from app.models.article import (
    Article,
    ArticleCreate,
    ArticleDB,
    ScrapeRequest,
    ScrapeResponse
)
from app.scrapers.scraper_factory import ScraperFactory
from app.nlp.keyword_extractor import KeywordExtractor

router = APIRouter()
keyword_extractor = KeywordExtractor()


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "News Scraper API",
        "version": "0.1.0",
        "endpoints": {
            "scrape": "/scrape",
            "articles": "/articles",
            "sources": "/sources",
            "stats": "/stats"
        }
    }


@router.get("/sources")
async def get_sources():
    """Get list of available news sources."""
    return {
        "sources": ScraperFactory.get_available_sources(),
        "count": len(ScraperFactory.get_available_sources())
    }


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_news(
    request: ScrapeRequest,
    db: Session = Depends(get_db)
):
    """
    Scrape news articles from specified sources.

    Args:
        request: Scrape request with sources and filters
        db: Database session

    Returns:
        ScrapeResponse with scraping results
    """
    articles_scraped = 0
    articles_stored = 0
    errors = []

    for source in request.sources:
        try:
            # Create scraper
            scraper = ScraperFactory.create_scraper(source)

            # Scrape articles
            articles = scraper.scrape_articles(
                max_articles=request.max_articles or 20,
                keywords_filter=request.keywords_filter
            )

            articles_scraped += len(articles)

            # Process and store articles
            for article_data in articles:
                # Apply NLP keyword extraction
                nlp_result = keyword_extractor.extract_keywords(
                    article_data.content or "",
                    article_data.title
                )

                # Update article with NLP data
                article_data.keywords = nlp_result["keywords"]
                article_data.categories = nlp_result["categories"]
                article_data.relevance_score = nlp_result["relevance_score"]

                # Filter by date if specified
                if request.date_from and article_data.published_date:
                    if article_data.published_date < request.date_from:
                        continue

                if request.date_to and article_data.published_date:
                    if article_data.published_date > request.date_to:
                        continue

                # Check if article already exists
                existing = db.query(ArticleDB).filter(
                    ArticleDB.url == article_data.url
                ).first()

                if not existing:
                    # Create new article
                    db_article = ArticleDB(**article_data.model_dump())
                    db.add(db_article)
                    articles_stored += 1

            db.commit()
            scraper.close()

        except ValueError as e:
            errors.append(f"{source}: {str(e)}")
        except Exception as e:
            errors.append(f"{source}: Unexpected error - {str(e)}")

    message = f"Scraped {articles_scraped} articles, stored {articles_stored} new articles"
    if errors:
        message += f". Errors: {'; '.join(errors)}"

    return ScrapeResponse(
        status="success" if articles_stored > 0 else "partial",
        articles_scraped=articles_scraped,
        articles_stored=articles_stored,
        sources=request.sources,
        message=message
    )


@router.get("/articles", response_model=List[Article])
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    min_relevance: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get articles with optional filtering.

    Args:
        skip: Number of articles to skip
        limit: Maximum number of articles to return
        source: Filter by source name
        category: Filter by category (energy, financial, ai)
        keyword: Filter by keyword
        min_relevance: Minimum relevance score
        date_from: Filter by published date from
        date_to: Filter by published date to
        db: Database session

    Returns:
        List of articles
    """
    query = db.query(ArticleDB)

    # Apply filters
    if source:
        query = query.filter(ArticleDB.source.ilike(f"%{source}%"))

    if category:
        query = query.filter(ArticleDB.categories.contains(category.lower()))

    if keyword:
        query = query.filter(ArticleDB.keywords.contains(keyword.lower()))

    if min_relevance is not None:
        query = query.filter(ArticleDB.relevance_score >= min_relevance)

    if date_from:
        query = query.filter(ArticleDB.published_date >= date_from)

    if date_to:
        query = query.filter(ArticleDB.published_date <= date_to)

    # Order by published date (most recent first)
    query = query.order_by(ArticleDB.published_date.desc())

    # Apply pagination
    articles = query.offset(skip).limit(limit).all()

    return articles


@router.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Get a specific article by ID.

    Args:
        article_id: Article ID
        db: Database session

    Returns:
        Article object
    """
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about scraped articles.

    Args:
        db: Database session

    Returns:
        Statistics dictionary
    """
    total_articles = db.query(ArticleDB).count()

    # Count by source
    sources = db.query(ArticleDB.source).distinct().all()
    source_counts = {}
    for (source,) in sources:
        count = db.query(ArticleDB).filter(ArticleDB.source == source).count()
        source_counts[source] = count

    # Count by category
    category_counts = {
        "energy": db.query(ArticleDB).filter(
            ArticleDB.categories.contains("energy")
        ).count(),
        "financial": db.query(ArticleDB).filter(
            ArticleDB.categories.contains("financial")
        ).count(),
        "ai": db.query(ArticleDB).filter(
            ArticleDB.categories.contains("ai")
        ).count(),
    }

    # Get date range
    earliest = db.query(ArticleDB).order_by(
        ArticleDB.published_date.asc()
    ).first()
    latest = db.query(ArticleDB).order_by(
        ArticleDB.published_date.desc()
    ).first()

    return {
        "total_articles": total_articles,
        "by_source": source_counts,
        "by_category": category_counts,
        "date_range": {
            "earliest": earliest.published_date if earliest else None,
            "latest": latest.published_date if latest else None
        }
    }


@router.delete("/articles/{article_id}")
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """
    Delete an article by ID.

    Args:
        article_id: Article ID
        db: Database session

    Returns:
        Success message
    """
    article = db.query(ArticleDB).filter(ArticleDB.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()

    return {"message": f"Article {article_id} deleted successfully"}
