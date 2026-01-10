from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScrapeResult:
    """
    Standardized result object for all scrapers.
    """

    url: str
    html: str
    status: int
    scraper_type: str  # "html" | "js"
    response_time: float
    timestamp: float  # Unix timestamp of when the scrape finished


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    """

    @abstractmethod
    def fetch(self, url: str, **kwargs) -> ScrapeResult:
        """
        Fetch the URL and return a ScrapeResult.

        Args:
            url (str): The URL to scrape.
            **kwargs: Additional arguments (timeout, headers, etc.)

        Returns:
            ScrapeResult: The scraping result.
        """
        pass
