"""Keyword extraction and categorization for articles."""

from typing import List, Dict, Tuple, Optional
import re
from app.config import settings


class KeywordExtractor:
    """Extract and categorize keywords from article text."""

    def __init__(self):
        """Initialize keyword extractor with predefined keywords."""
        self.energy_keywords = [kw.lower() for kw in settings.ENERGY_KEYWORDS]
        self.financial_keywords = [kw.lower() for kw in settings.FINANCIAL_KEYWORDS]
        self.ai_keywords = [kw.lower() for kw in settings.AI_KEYWORDS]

    def extract_keywords(
        self,
        text: str,
        title: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Extract keywords and categorize the article.

        Args:
            text: Article content
            title: Article title (optional, weighted more heavily)

        Returns:
            Dictionary containing keywords, categories, and relevance score
        """
        if not text:
            return {
                "keywords": [],
                "categories": [],
                "relevance_score": 0
            }

        # Combine title and text, give title more weight
        full_text = text.lower()
        if title:
            full_text = (title.lower() + " " + title.lower() + " " + full_text)

        # Find matching keywords
        found_keywords = []
        categories = set()
        relevance_score = 0

        # Check energy keywords
        energy_matches = self._find_keyword_matches(full_text, self.energy_keywords)
        if energy_matches:
            found_keywords.extend(energy_matches)
            categories.add("energy")
            relevance_score += len(energy_matches) * 2

        # Check financial keywords
        financial_matches = self._find_keyword_matches(full_text, self.financial_keywords)
        if financial_matches:
            found_keywords.extend(financial_matches)
            categories.add("financial")
            relevance_score += len(financial_matches) * 2

        # Check AI keywords
        ai_matches = self._find_keyword_matches(full_text, self.ai_keywords)
        if ai_matches:
            found_keywords.extend(ai_matches)
            categories.add("ai")
            relevance_score += len(ai_matches) * 2

        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for kw in found_keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return {
            "keywords": unique_keywords,
            "categories": sorted(list(categories)),
            "relevance_score": relevance_score
        }

    def _find_keyword_matches(self, text: str, keywords: List[str]) -> List[str]:
        """
        Find matching keywords in text.

        Args:
            text: Text to search
            keywords: List of keywords to find

        Returns:
            List of found keywords
        """
        matches = []
        for keyword in keywords:
            # Use word boundaries for more accurate matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(keyword)

        return matches

    def is_relevant(self, text: str, title: Optional[str] = None, min_score: int = 2) -> bool:
        """
        Check if article is relevant based on keyword matching.

        Args:
            text: Article content
            title: Article title
            min_score: Minimum relevance score

        Returns:
            True if article is relevant, False otherwise
        """
        result = self.extract_keywords(text, title)
        return result["relevance_score"] >= min_score

    def filter_by_keywords(
        self,
        text: str,
        title: Optional[str] = None,
        required_keywords: Optional[List[str]] = None
    ) -> bool:
        """
        Filter article by specific keywords.

        Args:
            text: Article content
            title: Article title
            required_keywords: List of keywords that must be present

        Returns:
            True if article contains required keywords, False otherwise
        """
        if not required_keywords:
            return True

        full_text = text.lower()
        if title:
            full_text = title.lower() + " " + full_text

        for keyword in required_keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, full_text, re.IGNORECASE):
                return True

        return False
