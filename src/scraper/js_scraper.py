import asyncio
import logging
import time
from typing import Optional

from src.scraper.base import BaseScraper, ScrapeResult
from src.stealth.browser.nodriver_session import create_session

logger = logging.getLogger(__name__)


class JSScraper(BaseScraper):
    """
    Scraper implementation using a headless browser (nodriver).
    Executes JavaScript and retrieves the rendered DOM.
    """

    def fetch(self, url: str, **kwargs) -> ScrapeResult:
        """
        Fetch URL using asyncio-managed browser session.
        Wraps async logic in a synchronous call.
        """
        try:
            # We use a new event loop or the existing one?
            # Since this is likely called from a sync Worker context, asyncio.run is appropriate.
            # However, if the broader app is async, this might nest loops.
            # For this 'Worker' design which is thread-based/sync, asyncio.run is correct.
            return asyncio.run(self._fetch_async(url, **kwargs))
        except Exception as e:
            logger.error(f"JSScraper execution failed: {e}")
            raise e

    async def _fetch_async(self, url: str, **kwargs) -> ScrapeResult:
        """
        Internal async fetch logic.
        """
        timeout = kwargs.get("timeout", 60)
        start_time = time.time()
        session = None

        try:
            logger.info(f"JSScraper: Launching browser for {url}")
            session = await create_session(headless=True)

            logger.info(f"JSScraper: Navigating to {url}")
            # Note: The underlying goto handles timeout
            await session.goto(url, timeout=timeout)

            # Wait for DOM to stabilize
            logger.info("JSScraper: Waiting for DOM ready")
            await session.wait_for_load(timeout=timeout)

            html = await session.get_page_content()
            duration = time.time() - start_time
            timestamp = time.time()

            logger.info(f"JSScraper: Navigation successful ({len(html)} bytes)")

            # Note: Browsers hard to get exact HTTP status code without network interception.
            # If we got content, assume 200 OK.
            return ScrapeResult(
                url=url,
                html=html,
                status=200,
                scraper_type="js",
                response_time=duration,
                timestamp=timestamp,
            )

        except Exception as e:
            logger.error(f"JSScraper async error: {e}")
            raise e

        finally:
            if session:
                logger.debug("JSScraper: Closing browser session")
                await session.close()
