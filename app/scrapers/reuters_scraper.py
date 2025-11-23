"""Reuters scraper."""

from typing import List, Optional
from datetime import datetime
from newspaper import Article
from app.scrapers.base import BaseScraper
from app.models.article import ArticleCreate


class ReutersScraper(BaseScraper):
    """Scraper for Reuters articles."""

    def __init__(self):
        """Initialize Reuters scraper."""
        super().__init__("Reuters")
        self.base_url = "https://www.reuters.com"
        self.section_urls = {
            "technology": f"{self.base_url}/technology/",
            "business": f"{self.base_url}/business/",
            "energy": f"{self.base_url}/business/energy/",
            "sustainability": f"{self.base_url}/sustainability/"
        }

    def scrape_articles(
        self,
        max_articles: int = 20,
        keywords_filter: Optional[List[str]] = None
    ) -> List[ArticleCreate]:
        """
        Scrape articles from Reuters.

        Args:
            max_articles: Maximum number of articles to scrape
            keywords_filter: Optional list of keywords to filter by

        Returns:
            List of ArticleCreate objects
        """
        articles = []
        article_urls = set()

        for section_name, section_url in self.section_urls.items():
            if len(articles) >= max_articles:
                break

            # Use stealth mode for Reuters (they block regular scrapers)
            soup = self.fetch_page(section_url, use_stealth=True)
            if not soup:
                continue

            # Find article links
            links = soup.find_all('a', href=True)
            for link in links:
                if len(articles) >= max_articles:
                    break

                href = link['href']

                # Reuters article URLs typically contain specific patterns
                if '/article/' in href or '/world/' in href or '/technology/' in href:
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
        Scrape a single Reuters article.

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
            print(f"Error scraping Reuters article {url}: {str(e)}")
            return None
