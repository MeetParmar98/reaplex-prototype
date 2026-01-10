import logging
from typing import Dict, Any

import httpx
from src.worker.executor import Executor

logger = logging.getLogger(__name__)


class HtmlExecutor(Executor):
    """
    Executor for static HTML pages.

    Responsibilities:
    - Fetch HTML via HTTP
    - Validate response
    - Hand off content for further processing (later)

    This executor MUST NOT:
    - Know about Redis
    - Retry jobs
    - Handle failures beyond raising exceptions
    """

    def run(self, payload: Dict[str, Any]) -> None:
        """
        Execute a static HTML fetch job.

        Expected payload:
        {
            "url": "https://example.com"
        }
        """
        url = payload.get("url")
        if not url:
            raise ValueError("HtmlExecutor requires 'url' in payload")

        logger.info(f"HtmlExecutor: Fetching URL → {url}")

        try:
            response = httpx.get(url, timeout=30.0)
            response.raise_for_status()

            html = response.text
            size = len(html)

            logger.info(
                f"HtmlExecutor: Fetched successfully → {url} "
                f"(status={response.status_code}, bytes={size})"
            )

            # TODO:
            # - Parse HTML
            # - Extract links / data
            # - Persist results

        except httpx.HTTPError as e:
            logger.error(f"HtmlExecutor: HTTP error while fetching {url}: {e}")
            raise
