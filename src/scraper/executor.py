import logging
from typing import Dict, Any

from src.worker.executor import Executor
from src.scraper.router import ScraperRouter

logger = logging.getLogger(__name__)


class ScraperExecutor(Executor):
    """
    Executor that runs the scraping workflow via the Router.
    Connects the Worker to the Scraper system.
    """

    def __init__(self):
        self.router = ScraperRouter()

    def run(self, payload: Dict[str, Any]) -> None:
        """
        Execute a scrape job.

        Payload:
            url (str): Required.
            force_js (bool | None): Optional.
            timeout (int | None): Optional.
            headers (dict | None): Optional.

        Raises:
            ValueError: If url is missing.
            Exception: If scraping completely fails.
        """
        url = payload.get("url")
        if not url:
            raise ValueError("Payload missing required field: 'url'")

        # Parse optional fields
        force_js = payload.get("force_js")
        if force_js is None:
            force_js = False

        timeout = payload.get("timeout")
        headers = payload.get("headers")

        # Construct kwargs for the router/fetcher
        start_kwargs = {}
        if timeout is not None:
            start_kwargs["timeout"] = timeout
        if headers is not None:
            start_kwargs["headers"] = headers

        try:
            # Delegate to Router
            result = self.router.route(url, force_js=force_js, **start_kwargs)

            # Log result metadata (as per requirement)
            logger.info(
                f"ScraperExecutor: Scrape Success → {url} | "
                f"Type: {result.scraper_type} | "
                f"Status: {result.status} | "
                f"Time: {result.response_time:.2f}s | "
                f"Size: {len(result.html)} bytes"
            )

            # Returns NOTHING (implicit None)

        except Exception as e:
            logger.error(f"ScraperExecutor: Scrape Failed → {url} | Error: {e}")
            raise e
