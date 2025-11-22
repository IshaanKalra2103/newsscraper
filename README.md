# News Scraper API

A powerful API for scraping and analyzing news articles from multiple sources with NLP-powered keyword filtering. This tool helps correlate news coverage with energy outages, financial events, and AI developments for data analysis and machine learning applications.

## Features

- 🔍 **Multi-Source Scraping**: Scrape articles from NYT, Reuters, OpenAI Blog, Google Research, and more
- 🤖 **NLP Keyword Extraction**: Automatically identify and categorize articles by topics (energy, financial, AI)
- 📅 **Date/Time Tracking**: Extract and filter articles by publication dates
- 💾 **Database Storage**: SQLite database for storing and querying articles
- 🎯 **Relevance Scoring**: Articles scored by keyword matches for easy filtering
- 🔌 **REST API**: FastAPI-powered endpoints for easy integration
- 📊 **Statistics & Analytics**: Get insights on scraped data by source, category, and date range

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd newsscraper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your preferences
```

### Running the API

Start the server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### 1. Get Available Sources

```bash
GET /api/v1/sources
```

Returns list of available news sources to scrape.

**Example Response:**
```json
{
  "sources": ["nyt", "reuters", "openai", "google_research"],
  "count": 4
}
```

### 2. Scrape News Articles

```bash
POST /api/v1/scrape
```

**Request Body:**
```json
{
  "sources": ["nyt", "reuters", "openai"],
  "max_articles": 20,
  "keywords_filter": ["energy", "AI"],
  "date_from": "2024-01-01T00:00:00",
  "date_to": "2025-12-31T23:59:59"
}
```

**Example Response:**
```json
{
  "status": "success",
  "articles_scraped": 45,
  "articles_stored": 42,
  "sources": ["nyt", "reuters", "openai"],
  "message": "Scraped 45 articles, stored 42 new articles"
}
```

### 3. Get Articles

```bash
GET /api/v1/articles?skip=0&limit=50&category=energy&min_relevance=5
```

**Query Parameters:**
- `skip` (int): Number of articles to skip (pagination)
- `limit` (int): Maximum articles to return (1-100)
- `source` (str): Filter by source name
- `category` (str): Filter by category (energy, financial, ai)
- `keyword` (str): Filter by specific keyword
- `min_relevance` (int): Minimum relevance score
- `date_from` (datetime): Filter by published date from
- `date_to` (datetime): Filter by published date to

**Example Response:**
```json
[
  {
    "id": 1,
    "title": "Solar Energy Breakthrough Could Transform Grid",
    "url": "https://example.com/article",
    "source": "New York Times",
    "content": "Article content...",
    "summary": "Brief summary...",
    "author": "John Doe",
    "published_date": "2024-11-15T10:30:00",
    "scraped_date": "2024-11-22T15:00:00",
    "keywords": ["energy", "solar", "grid", "renewable"],
    "categories": ["energy"],
    "relevance_score": 8,
    "image_url": "https://example.com/image.jpg",
    "tags": ["technology", "climate"]
  }
]
```

### 4. Get Single Article

```bash
GET /api/v1/articles/{article_id}
```

Returns detailed information for a specific article.

### 5. Get Statistics

```bash
GET /api/v1/stats
```

**Example Response:**
```json
{
  "total_articles": 150,
  "by_source": {
    "New York Times": 60,
    "Reuters": 45,
    "OpenAI Blog": 25,
    "Google Research Blog": 20
  },
  "by_category": {
    "energy": 50,
    "financial": 40,
    "ai": 60
  },
  "date_range": {
    "earliest": "2024-01-15T00:00:00",
    "latest": "2024-11-22T12:00:00"
  }
}
```

### 6. Delete Article

```bash
DELETE /api/v1/articles/{article_id}
```

## Usage Examples

### Python Client Example

```python
import requests
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

# 1. Get available sources
response = requests.get(f"{API_BASE}/sources")
print(response.json())

# 2. Scrape articles
scrape_request = {
    "sources": ["nyt", "reuters"],
    "max_articles": 20,
    "keywords_filter": ["energy", "electricity"],
    "date_from": "2024-01-01T00:00:00"
}
response = requests.post(f"{API_BASE}/scrape", json=scrape_request)
print(response.json())

# 3. Get energy-related articles
params = {
    "category": "energy",
    "min_relevance": 4,
    "limit": 10
}
response = requests.get(f"{API_BASE}/articles", params=params)
articles = response.json()

for article in articles:
    print(f"{article['title']} - {article['published_date']}")
    print(f"Categories: {article['categories']}")
    print(f"Keywords: {', '.join(article['keywords'])}")
    print("-" * 80)

# 4. Get statistics
response = requests.get(f"{API_BASE}/stats")
stats = response.json()
print(f"Total articles: {stats['total_articles']}")
print(f"By category: {stats['by_category']}")
```

### cURL Examples

**Scrape articles:**
```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["nyt", "reuters"],
    "max_articles": 10
  }'
```

**Get articles about AI:**
```bash
curl "http://localhost:8000/api/v1/articles?category=ai&limit=5"
```

**Get statistics:**
```bash
curl "http://localhost:8000/api/v1/stats"
```

## NLP Categories & Keywords

The API automatically categorizes articles into three main categories:

### Energy Keywords
- energy, electricity, power grid, blackout, outage
- renewable energy, solar, wind power, nuclear
- power plant, transmission, grid, utility, electrical

### Financial Keywords
- financial, economy, stock market, inflation, recession
- GDP, economic, finance, investment, banking
- cryptocurrency, bitcoin, trading, fiscal

### AI Keywords
- artificial intelligence, AI, machine learning, deep learning
- neural network, GPT, LLM, large language model
- ChatGPT, automation, robotics, computer vision
- data center, compute, GPU

## Configuration

Create a `.env` file to customize settings:

```env
# API Settings
API_TITLE="News Scraper API"
API_VERSION="0.1.0"

# Database
DATABASE_URL="sqlite:///./news_scraper.db"

# Scraping Settings
REQUEST_TIMEOUT=30
MAX_ARTICLES_PER_SCRAPE=50
```

## Project Structure

```
newsscraper/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py            # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── article.py       # Data models
│   ├── nlp/
│   │   ├── __init__.py
│   │   └── keyword_extractor.py  # NLP processing
│   └── scrapers/
│       ├── __init__.py
│       ├── base.py          # Base scraper class
│       ├── nyt_scraper.py   # NYT scraper
│       ├── reuters_scraper.py    # Reuters scraper
│       ├── openai_scraper.py     # OpenAI blog scraper
│       ├── google_scraper.py     # Google Research scraper
│       └── scraper_factory.py    # Scraper factory
├── requirements.txt
├── run.py                   # Server runner
├── .env.example
├── .gitignore
└── README.md
```

## Use Cases

### 1. Energy Outage Correlation Analysis
Analyze if news coverage of energy topics correlates with actual outage data:

```python
# Get energy articles during outage period
params = {
    "category": "energy",
    "date_from": "2024-07-15T00:00:00",
    "date_to": "2024-07-20T23:59:59",
    "min_relevance": 5
}
response = requests.get(f"{API_BASE}/articles", params=params)
articles = response.json()

# Analyze frequency and keywords
for article in articles:
    print(f"{article['published_date']}: {article['title']}")
    print(f"Relevance: {article['relevance_score']}")
```

### 2. AI Development Timeline Tracking
Track AI developments over time for training ML models:

```python
# Scrape AI-related content from research blogs
scrape_request = {
    "sources": ["openai", "google_research"],
    "max_articles": 50,
    "keywords_filter": ["AI", "machine learning"]
}
requests.post(f"{API_BASE}/scrape", json=scrape_request)

# Get timeline of AI articles
params = {"category": "ai", "limit": 100}
articles = requests.get(f"{API_BASE}/articles", params=params).json()

# Build timeline dataset
timeline = [
    {
        "date": a["published_date"],
        "title": a["title"],
        "keywords": a["keywords"]
    }
    for a in articles
]
```

### 3. Financial Events & Energy Correlation
Analyze financial news during energy events:

```python
# Get both financial and energy articles
energy_articles = requests.get(
    f"{API_BASE}/articles",
    params={"category": "energy", "date_from": "2024-01-01"}
).json()

financial_articles = requests.get(
    f"{API_BASE}/articles",
    params={"category": "financial", "date_from": "2024-01-01"}
).json()

# Find overlapping dates for correlation analysis
```

## Development

### Running Tests
```bash
pytest tests/
```

### Adding a New Scraper

1. Create a new scraper class in `app/scrapers/`:

```python
from app.scrapers.base import BaseScraper
from app.models.article import ArticleCreate

class MyNewsScraper(BaseScraper):
    def __init__(self):
        super().__init__("My News Source")
        self.base_url = "https://mynewssource.com"

    def scrape_articles(self, max_articles=20, keywords_filter=None):
        # Implementation here
        pass
```

2. Register it in `scraper_factory.py`:

```python
from app.scrapers.mynews_scraper import MyNewsScraper

class ScraperFactory:
    _scrapers = {
        # ... existing scrapers
        "mynews": MyNewsScraper,
    }
```

## Limitations & Notes

- Some news sites may require authentication or have rate limiting
- Web scraping is subject to websites' terms of service
- Consider using official APIs where available
- The newspaper3k library may not work perfectly for all sites
- Date extraction accuracy varies by source

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Web scraping powered by [newspaper3k](https://newspaper.readthedocs.io/)
- NLP processing with keyword matching

## Support

For questions or issues, please open a GitHub issue.
