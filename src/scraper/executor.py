import logging
import json
import uuid
import os
from pathlib import Path
from typing import Dict, Any

from src.worker.executor import Executor
from src.scraper.router import ScraperRouter

logger = logging.getLogger(__name__)


class ScraperExecutor(Executor):
    """
    Executor that runs the scraping workflow via the Router.
    Connects the Worker to the Scraper system and handles storage.
    """

    def __init__(self):
        self.router = ScraperRouter()

        # Setup data directories
        self.base_dir = Path("data")
        self.raw_dir = self.base_dir / "raw"
        self.structured_dir = self.base_dir / "structured"

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.structured_dir.mkdir(parents=True, exist_ok=True)

    def run(self, payload: Dict[str, Any]) -> None:
        """
        Execute a scrape job.

        Payload:
            url (str): Required.
            force_js (bool | None): Optional.
            timeout (int | None): Optional.
            headers (dict | None): Optional.
            job_id (str | None): Optional. Used for file naming.

        Raises:
            ValueError: If url is missing.
            Exception: If scraping completely fails.
        """
        url = payload.get("url")
        if not url:
            raise ValueError("Payload missing required field: 'url'")

        # Determine Job ID for storage
        job_id = payload.get("job_id") or payload.get("id")
        if not job_id:
            # Fallback if no ID provided in payload
            job_id = str(uuid.uuid4())
            logger.debug(
                f"ScraperExecutor: No job_id found in payload, generated: {job_id}"
            )

        # Parse optional fields
        force_js = payload.get("force_js") or False
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

            # Log result metadata
            logger.info(
                f"ScraperExecutor: Scrape Success → {url} | "
                f"Type: {result.scraper_type} | "
                f"Status: {result.status} | "
                f"Time: {result.response_time:.2f}s | "
                f"Size: {len(result.html)} bytes"
            )

            # ---------------------------
            # Storage
            # ---------------------------

            # 1. Save Raw HTML
            raw_path = self.raw_dir / f"{job_id}.html"
            raw_path.write_text(result.html, encoding="utf-8")

            # 2. Save Structured JSON (Metadata)
            structured_data = {
                "id": job_id,
                "url": result.url,
                "scraper_type": result.scraper_type,
                "status": result.status,
                "response_time": result.response_time,
                "timestamp": result.timestamp,
                "raw_file": str(raw_path),
            }

            structured_path = self.structured_dir / f"{job_id}.json"
            structured_path.write_text(
                json.dumps(structured_data, indent=2), encoding="utf-8"
            )

            logger.info(f"ScraperExecutor: Data saved to {structured_path}")

        except Exception as e:
            logger.error(f"ScraperExecutor: Scrape Failed → {url} | Error: {e}")
            raise e
