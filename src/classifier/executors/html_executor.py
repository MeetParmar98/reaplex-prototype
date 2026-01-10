import logging
import httpx
from typing import Dict, Any
from src.worker.executor import Executor

logger = logging.getLogger(__name__)


class HtmlExecutor(Executor):
    """
    Executor implementation for fetching static HTML content.
    Uses httpx to perform HTTP GET requests.
    """

    def run(self, payload: Dict[str, Any]) -> None:
        """
        Executes the HTML fetch job.

        Args:
            payload (Dict[str, Any]): Job payload containing 'url'.

        Raises:
            ValueError: If 'url' is missing.
            httpx.HTTPError: If the HTTP request fails.
        """
        url = payload.get("url")
        if not url:
            logger.error("Job payload missing 'url'")
            raise ValueError("Job payload missing 'url' field")

        logger.info(f"HtmlExecutor: Starting fetch for {url}")

        try:
            # Using a context manager for the client is best practice,
            # though for single requests httpx.get is fine.
            # We use a client to control timeouts/headers if needed.
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()

                content_len = len(response.content)
                logger.info(
                    f"HtmlExecutor: Successfully fetched {url}. Status: {response.status_code}, Length: {content_len} bytes"
                )

                # In a real app, we might save the content here

        except httpx.RequestError as e:
            logger.error(f"HtmlExecutor: Network error fetching {url}: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HtmlExecutor: HTTP error fetching {url}: {e.response.status_code}"
            )
            raise
        except Exception as e:
            logger.error(f"HtmlExecutor: Unexpected error: {e}")
            raise
