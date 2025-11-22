#!/usr/bin/env python3
"""
Example usage of the News Scraper API.

This script demonstrates how to:
1. Scrape articles from multiple sources
2. Filter by categories and keywords
3. Retrieve and analyze articles
4. Get statistics
"""

import requests
from datetime import datetime, timedelta
import time

API_BASE = "http://localhost:8000/api/v1"


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ API is running\n")
            return True
        else:
            print("✗ API is not responding correctly\n")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running (python run.py)\n")
        return False


def get_available_sources():
    """Get and display available news sources."""
    print("=" * 80)
    print("STEP 1: Getting available sources")
    print("=" * 80)

    response = requests.get(f"{API_BASE}/sources")
    data = response.json()

    print(f"Available sources ({data['count']}):")
    for source in data['sources']:
        print(f"  - {source}")
    print()

    return data['sources']


def scrape_articles():
    """Scrape articles from multiple sources."""
    print("=" * 80)
    print("STEP 2: Scraping articles")
    print("=" * 80)

    scrape_request = {
        "sources": ["nyt", "reuters"],
        "max_articles": 10,  # Small number for testing
    }

    print(f"Scraping from sources: {', '.join(scrape_request['sources'])}")
    print(f"Max articles per source: {scrape_request['max_articles']}")
    print("This may take a few moments...\n")

    response = requests.post(f"{API_BASE}/scrape", json=scrape_request)
    data = response.json()

    print(f"Status: {data['status']}")
    print(f"Articles scraped: {data['articles_scraped']}")
    print(f"Articles stored: {data['articles_stored']}")
    print(f"Message: {data['message']}\n")

    return data


def get_energy_articles():
    """Get and display energy-related articles."""
    print("=" * 80)
    print("STEP 3: Retrieving energy-related articles")
    print("=" * 80)

    params = {
        "category": "energy",
        "min_relevance": 2,
        "limit": 5
    }

    response = requests.get(f"{API_BASE}/articles", params=params)
    articles = response.json()

    print(f"Found {len(articles)} energy-related articles:\n")

    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Published: {article['published_date']}")
        print(f"   Categories: {', '.join(article['categories']) if article['categories'] else 'N/A'}")
        print(f"   Relevance Score: {article['relevance_score']}")
        print(f"   Keywords: {', '.join(article['keywords'][:5]) if article['keywords'] else 'N/A'}")
        print(f"   URL: {article['url']}")
        print()

    return articles


def get_ai_articles():
    """Get and display AI-related articles."""
    print("=" * 80)
    print("STEP 4: Retrieving AI-related articles")
    print("=" * 80)

    params = {
        "category": "ai",
        "min_relevance": 2,
        "limit": 5
    }

    response = requests.get(f"{API_BASE}/articles", params=params)
    articles = response.json()

    print(f"Found {len(articles)} AI-related articles:\n")

    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Relevance Score: {article['relevance_score']}")
        print(f"   Top Keywords: {', '.join(article['keywords'][:3]) if article['keywords'] else 'N/A'}")
        print()

    return articles


def get_statistics():
    """Get and display statistics."""
    print("=" * 80)
    print("STEP 5: Getting statistics")
    print("=" * 80)

    response = requests.get(f"{API_BASE}/stats")
    stats = response.json()

    print(f"Total articles in database: {stats['total_articles']}\n")

    print("Articles by source:")
    for source, count in stats['by_source'].items():
        print(f"  - {source}: {count}")
    print()

    print("Articles by category:")
    for category, count in stats['by_category'].items():
        print(f"  - {category.upper()}: {count}")
    print()

    if stats['date_range']['earliest'] and stats['date_range']['latest']:
        print("Date range:")
        print(f"  Earliest: {stats['date_range']['earliest']}")
        print(f"  Latest: {stats['date_range']['latest']}")
    else:
        print("Date range: No articles with dates yet")
    print()

    return stats


def search_by_keyword():
    """Search articles by specific keyword."""
    print("=" * 80)
    print("STEP 6: Searching by keyword")
    print("=" * 80)

    keyword = "electricity"
    params = {
        "keyword": keyword,
        "limit": 3
    }

    response = requests.get(f"{API_BASE}/articles", params=params)
    articles = response.json()

    print(f"Articles containing keyword '{keyword}': {len(articles)}\n")

    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Keywords: {', '.join(article['keywords']) if article['keywords'] else 'N/A'}")
        print()


def get_recent_articles():
    """Get articles from the last 30 days."""
    print("=" * 80)
    print("STEP 7: Getting recent articles (last 30 days)")
    print("=" * 80)

    date_from = (datetime.now() - timedelta(days=30)).isoformat()

    params = {
        "date_from": date_from,
        "limit": 10
    }

    response = requests.get(f"{API_BASE}/articles", params=params)
    articles = response.json()

    print(f"Found {len(articles)} articles from the last 30 days\n")

    for article in articles:
        if article['published_date']:
            print(f"- {article['title']}")
            print(f"  Date: {article['published_date']}")
            print()


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("NEWS SCRAPER API - EXAMPLE USAGE")
    print("=" * 80 + "\n")

    # Check if API is running
    if not check_api_health():
        print("Please start the API server first:")
        print("  python run.py")
        return

    try:
        # 1. Get available sources
        sources = get_available_sources()

        # 2. Scrape articles
        scrape_result = scrape_articles()

        # Wait a moment for processing
        time.sleep(1)

        # 3. Get energy articles
        energy_articles = get_energy_articles()

        # 4. Get AI articles
        ai_articles = get_ai_articles()

        # 5. Get statistics
        stats = get_statistics()

        # 6. Search by keyword
        search_by_keyword()

        # 7. Get recent articles
        get_recent_articles()

        print("=" * 80)
        print("EXAMPLE COMPLETE!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/docs for interactive API documentation")
        print("2. Try scraping from different sources: openai, google_research")
        print("3. Experiment with different filters and date ranges")
        print("4. Build your own correlation analysis using the scraped data")
        print()

    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error communicating with API: {e}")
        print("Make sure the server is running and try again.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
