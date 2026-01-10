import logging
from src.scraper.base import ScrapeResult
from src.scraper.html_scraper import HTMLScraper
from src.scraper.js_scraper import JSScraper

logger = logging.getLogger(__name__)


class ScraperRouter:
    """
    Decides which scraper to use based on configuration and response heuristics.
    Tracks 'html' vs 'js' execution.
    """

    def __init__(self):
        self.html_scraper = HTMLScraper()
        self.js_scraper = JSScraper()

    def route(self, url: str, force_js: bool = False, **kwargs) -> ScrapeResult:
        """
        Route the scrape request to the appropriate scraper.

        Strategy:
        1. If force_js is True -> JSScraper
        2. Try HTMLScraper
        3. If HTML fails or looks like it needs JS -> JSScraper
        """
        if force_js:
            logger.info(f"Router: Force JS requested for {url}")
            return self.js_scraper.fetch(url, **kwargs)

        try:
            logger.info(f"Router: Attempting HTML scrape for {url}")
            result = self.html_scraper.fetch(url, **kwargs)

            # Heuristic check: Did we get a valid page or an empty JS shell?
            if self._looks_js_heavy(result.html):
                logger.info(
                    f"Router: Detected JS-heavy content. Falling back to JS scraper for {url}"
                )
                return self.js_scraper.fetch(url, **kwargs)

            # Use the HTML result
            return result

        except Exception as e:
            # Fallback on any error (network, timeout, etc.) logic:
            # Often, HTML scrapers are blocked by WAFs that browsers can pass.
            logger.warning(
                f"Router: HTML scrape failed for {url} ({e}). Falling back to JS scraper."
            )
            return self.js_scraper.fetch(url, **kwargs)

    def _looks_js_heavy(self, html: str) -> bool:
        """
        Analyze HTML to check if it requires JavaScript to render meaningful content.
        Returns True if it looks like a JS-heavy/Single Page App shell.
        """
        if not html:
            return True

        # Common phrases indicating JS is required
        js_indicators = [
            "need to enable javascript",
            "javascript is required",
            "please enable javascript",
            "browser doesn't support javascript",
            "you need to enable javascript to run this app",
        ]

        lower_html = html.lower()

        # 1. Check for specific text indicators
        for indicator in js_indicators:
            if indicator in lower_html:
                return True

        # 2. Check for very small body content with common SPA root elements
        # (This is a rough heuristic) - If page is too small (< 2KB) and has root hook
        if len(html) < 2000:
            if (
                'id="root"' in lower_html
                or 'id="app"' in lower_html
                or 'id="__next"' in lower_html
            ):
                # If it's small and has a root div, it's likely an empty shell
                return True

        return False
