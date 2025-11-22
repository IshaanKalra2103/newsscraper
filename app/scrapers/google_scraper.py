"""Google Research blog scraper."""

from typing import List, Optional
from datetime import datetime
from newspaper import Article
from app.scrapers.base import BaseScraper
from app.models.article import ArticleCreate


class GoogleResearchScraper(BaseScraper):
    """Scraper for Google Research blog."""

    def __init__(self):
        """Initialize Google Research blog scraper."""
        super().__init__("Google Research Blog")
        self.base_url = "https://blog.research.google"

    def scrape_articles(
        self,
        max_articles: int = 20,
        keywords_filter: Optional[List[str]] = None
    ) -> List[ArticleCreate]:
        """
        Scrape articles from Google Research blog.

        Args:
            max_articles: Maximum number of articles to scrape
            keywords_filter: Optional list of keywords to filter by

        Returns:
            List of ArticleCreate objects
        """
        articles = []
        article_urls = set()

        soup = self.fetch_page(self.base_url)
        if not soup:
            return articles

        # Find article links - Google blog uses specific classes
        article_elements = soup.find_all('article')

        for article_elem in article_elements:
            if len(articles) >= max_articles:
                break

            link = article_elem.find('a', href=True)
            if not link:
                continue

            href = link['href']
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
        Scrape a single Google Research blog post.

        Args:
            url: Article URL

        Returns:
            ArticleCreate object or None
        """
        try:
            article = Article(url)
            article.download()
            article.parse()

            published_date = None
            if article.publish_date:
                published_date = article.publish_date

            # Try to extract date from page
            if not published_date:
                soup = self.fetch_page(url)
                if soup:
                    # Look for date in various meta tags
                    date_meta = (
                        soup.find('meta', property='article:published_time') or
                        soup.find('meta', attrs={'name': 'publish_date'}) or
                        soup.find('time', class_='published')
                    )
                    if date_meta:
                        date_str = date_meta.get('content') or date_meta.get('datetime')
                        if date_str:
                            published_date = self.parse_date(date_str)

            image_url = article.top_image if article.top_image else None

            return ArticleCreate(
                title=article.title or "Untitled",
                url=url,
                source=self.source_name,
                content=article.text or "",
                summary=article.meta_description or "",
                author=", ".join(article.authors) if article.authors else "Google Research",
                published_date=published_date,
                image_url=image_url,
                tags=["ai", "research", "google"]
            )

        except Exception as e:
            print(f"Error scraping Google Research article {url}: {str(e)}")
            return None
