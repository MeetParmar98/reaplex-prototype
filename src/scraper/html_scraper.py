import logging
import time
from typing import Optional, Dict, Any

from src.scraper.base import BaseScraper, ScrapeResult
from src.stealth.network.tls_client import get_ja4_client

logger = logging.getLogger(__name__)


class HTMLScraper(BaseScraper):
    """
    Scraper implementation using stealth HTTP client (TLS/JA4 fingerprinting).
    Fetches raw HTML without executing JavaScript.
    """

    def fetch(self, url: str, **kwargs) -> ScrapeResult:
        """
        Fetch URL using JA4Client.

        Args:
            url: Target URL
            **kwargs:
                - timeout: int (default 30)
                - headers: dict (ignored to preserve stealth fingerprint)
        """
        client = get_ja4_client()
        timeout = kwargs.get("timeout", 30)

        # Note: We knowingly ignore 'headers' from kwargs here because JA4Client
        # tightly controls headers to maintain the specific Chrome fingerprint.
        # Injecting random headers would likely break the stealth.

        logger.info(f"HTMLScraper: Fetching {url}")
        start_time = time.time()

        try:
            # client.get() handles the stealth headers and impersonation
            response = client.get(url, timeout=timeout)

            # Calculate duration
            duration = time.time() - start_time

            # Note: We rely on the caller/Router to decide if a 403/404 is a 'failure'
            # to be retried with JS, but generally we return what we got.
            # However, network exceptions (connection error, timeout) will raise.

            return ScrapeResult(
                url=url,
                html=response.text,
                status=response.status_code,
                scraper_type="html",
                response_time=duration,
            )

        except Exception as e:
            logger.warning(f"HTMLScraper failed for {url}: {e}")
            raise e
