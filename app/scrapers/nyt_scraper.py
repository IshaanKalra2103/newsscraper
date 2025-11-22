"""New York Times scraper."""

from typing import List, Optional
from datetime import datetime
from newspaper import Article
from app.scrapers.base import BaseScraper
from app.models.article import ArticleCreate


class NYTScraper(BaseScraper):
    """Scraper for New York Times articles."""

    def __init__(self):
        """Initialize NYT scraper."""
        super().__init__("New York Times")
        self.base_url = "https://www.nytimes.com"
        self.section_urls = {
            "business": f"{self.base_url}/section/business",
            "technology": f"{self.base_url}/section/technology",
            "climate": f"{self.base_url}/section/climate",
            "science": f"{self.base_url}/section/science"
        }

    def scrape_articles(
        self,
        max_articles: int = 20,
        keywords_filter: Optional[List[str]] = None
    ) -> List[ArticleCreate]:
        """
        Scrape articles from NYT.

        Args:
            max_articles: Maximum number of articles to scrape
            keywords_filter: Optional list of keywords to filter by

        Returns:
            List of ArticleCreate objects
        """
        articles = []
        article_urls = set()

        # Scrape from multiple sections
        for section_name, section_url in self.section_urls.items():
            if len(articles) >= max_articles:
                break

            soup = self.fetch_page(section_url)
            if not soup:
                continue

            # Find article links
            links = soup.find_all('a', href=True)
            for link in links:
                if len(articles) >= max_articles:
                    break

                href = link['href']
                # NYT article URLs typically contain /YYYY/MM/DD/
                if '/2024/' in href or '/2025/' in href:
                    if not href.startswith('http'):
                        href = self.base_url + href

                    if href in article_urls:
                        continue

                    article_urls.add(href)
                    article_data = self._scrape_article(href)

                    if article_data:
                        articles.append(article_data)

        return articles

    def _scrape_article(self, url: str) -> Optional[ArticleCreate]:
        """
        Scrape a single NYT article.

        Args:
            url: Article URL

        Returns:
            ArticleCreate object or None
        """
        try:
            article = Article(url)
            article.download()
            article.parse()

            # Extract publish date
            published_date = None
            if article.publish_date:
                published_date = article.publish_date

            # Get top image
            image_url = article.top_image if article.top_image else None

            return ArticleCreate(
                title=article.title or "Untitled",
                url=url,
                source=self.source_name,
                content=article.text or "",
                summary=article.meta_description or "",
                author=", ".join(article.authors) if article.authors else None,
                published_date=published_date,
                image_url=image_url,
                tags=article.tags if article.tags else None
            )

        except Exception as e:
            print(f"Error scraping NYT article {url}: {str(e)}")
            return None
