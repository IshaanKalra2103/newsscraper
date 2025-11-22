"""OpenAI blog scraper."""

from typing import List, Optional
from datetime import datetime
from newspaper import Article
from app.scrapers.base import BaseScraper
from app.models.article import ArticleCreate


class OpenAIScraper(BaseScraper):
    """Scraper for OpenAI blog."""

    def __init__(self):
        """Initialize OpenAI blog scraper."""
        super().__init__("OpenAI Blog")
        self.base_url = "https://openai.com"
        self.blog_url = f"{self.base_url}/blog"

    def scrape_articles(
        self,
        max_articles: int = 20,
        keywords_filter: Optional[List[str]] = None
    ) -> List[ArticleCreate]:
        """
        Scrape articles from OpenAI blog.

        Args:
            max_articles: Maximum number of articles to scrape
            keywords_filter: Optional list of keywords to filter by

        Returns:
            List of ArticleCreate objects
        """
        articles = []
        article_urls = set()

        soup = self.fetch_page(self.blog_url)
        if not soup:
            return articles

        # Find article links
        links = soup.find_all('a', href=True)
        for link in links:
            if len(articles) >= max_articles:
                break

            href = link['href']

            # OpenAI blog posts typically have /blog/ or /research/ in URL
            if '/blog/' in href or '/research/' in href:
                if not href.startswith('http'):
                    href = self.base_url + href

                if href == self.blog_url or href in article_urls:
                    continue

                article_urls.add(href)
                article_data = self._scrape_article(href)

                if article_data:
                    articles.append(article_data)

        return articles

    def _scrape_article(self, url: str) -> Optional[ArticleCreate]:
        """
        Scrape a single OpenAI blog post.

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

            # Try to extract date from meta tags if not found
            if not published_date:
                soup = self.fetch_page(url)
                if soup:
                    date_meta = soup.find('meta', property='article:published_time')
                    if date_meta and date_meta.get('content'):
                        published_date = self.parse_date(date_meta['content'])

            image_url = article.top_image if article.top_image else None

            return ArticleCreate(
                title=article.title or "Untitled",
                url=url,
                source=self.source_name,
                content=article.text or "",
                summary=article.meta_description or "",
                author=", ".join(article.authors) if article.authors else "OpenAI",
                published_date=published_date,
                image_url=image_url,
                tags=["ai", "openai"]
            )

        except Exception as e:
            print(f"Error scraping OpenAI article {url}: {str(e)}")
            return None
