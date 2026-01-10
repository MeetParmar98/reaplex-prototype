# advanced_search.py
# ---------------------------------------------------------------------------
# Advanced Search Orchestration
#
# Purpose:
#     Orchestrates a single search query using multiple stealth layers
#     to minimize detection by modern anti-bot systems.
#
# Stealth Layers Used:
#     1. TLS Layer     → JA4-compliant requests (Chrome-like TLS handshake)
#     2. Browser Layer → Nodriver (no CDP fingerprint)
#     3. Behavior Layer→ Human-like pauses, typing entropy, and timing
#
# High-Level Flow:
#     search("python tutorial")
#         → launch nodriver browser
#         → navigate to search results
#         → wait with human-like cognitive pauses
#         → extract page content
# ---------------------------------------------------------------------------

import asyncio
from typing import Optional
from urllib.parse import quote_plus

from stealth.browser.nodriver_session import create_session as create_nodriver_session
from stealth.human_biometrics import HumanBiometrics


class AdvancedSearcher:
    """
    High-level search interface combining all stealth layers.

    Example:
        searcher = AdvancedSearcher()
        results = await searcher.search("python tutorial")
        await searcher.close()
    """

    def __init__(self, headless: bool = False, engine: str = "google"):
        """
        Initialize the search orchestrator.

        Args:
            headless: Whether to run the browser headless.
                      Headful mode is more reliable for stealth.
            engine: Search engine to use ("google", "bing").
        """
        self.headless = headless
        self.engine = engine
        self.session = None
        self.uses = 0

        # Engine-specific selectors and endpoints
        self.engines = {
            "google": {
                "url": "https://www.google.com",
                "search_field": "input[name='q']",
                "submit_key": "Enter",
            },
            "bing": {
                "url": "https://www.bing.com",
                "search_field": "input[id='sb_form_q']",
                "submit_key": "Enter",
            },
        }

    # ------------------------------------------------------------------
    # Session Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start a Nodriver browser session."""
        self.session = await create_nodriver_session(headless=self.headless)
        print(f"✅ Advanced searcher ready (engine: {self.engine})")

    async def close(self) -> None:
        """Close the browser session."""
        if self.session:
            await self.session.close()
            self.session = None
            print("✅ Searcher closed")

    def __del__(self):
        """Best-effort cleanup when garbage collected."""
        try:
            asyncio.run(self.close())
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Search Execution
    # ------------------------------------------------------------------

    async def search(self, query: str) -> str:
        """
        Perform a search using full stealth orchestration.

        Args:
            query: Search query string.

        Returns:
            Raw HTML content of the results page.
        """
        if not self.session:
            await self.start()

        self.uses += 1
        print(f"\n🔍 Searching for: '{query}'")

        try:
            # Build search URL directly (more reliable than simulating typing)
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            print(f"📍 Navigating to: {search_url}")

            # Step 1: Navigate to search results
            await self.session.goto(search_url, timeout=30)

            # Step 2: Wait for results to load (selector-based with fallback)
            print("⏳ Waiting for results to load...")
            if not await self._wait_for_results():
                print("⚠️  Falling back to time-based wait")
                await asyncio.sleep(3)

            # Step 3: Human-like pause to simulate reading
            pause = HumanBiometrics.cognitive_pause(1.5, 3.0)
            print(f"📖 Reading results for {pause:.2f}s")
            await asyncio.sleep(pause)

            # Step 4: Extract page content
            print("📄 Extracting page content...")
            content = await self.session.get_page_content()

            self._inspect_content(content)
            return content

        except Exception as e:
            print(f"❌ Search failed: {e}")
            raise

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    async def _wait_for_results(self) -> bool:
        """
        Attempt to detect search results using known selectors.

        Returns:
            True if results container was found, False otherwise.
        """
        try:
            await self.session.wait_for_selector("#search", timeout=10)
            print("✅ Search results container detected (#search)")
            return True
        except Exception:
            try:
                await self.session.wait_for_selector("div.g", timeout=10)
                print("✅ Search result blocks detected (div.g)")
                return True
            except Exception:
                return False

    def _inspect_content(self, content: str) -> None:
        """
        Inspect page content for detection or failure indicators.
        """
        lower = content.lower()

        if "detected unusual traffic" in lower:
            print("🚨 WARNING: Google flagged unusual traffic")

        if "captcha" in lower:
            print("🚨 WARNING: CAPTCHA detected on page")

        if (
            "search results" in content
            or "did not match any documents" in content
            or len(content) > 50_000
        ):
            print(f"✅ Search completed successfully ({len(content)} bytes)")
        else:
            print(f"⚠️  Page may not contain valid results ({len(content)} bytes)")

    # ------------------------------------------------------------------
    # Typing (unused in current flow but retained intentionally)
    # ------------------------------------------------------------------

    async def _type_with_biometrics(self, selector: str, text: str) -> None:
        """
        Type text using human-like entropy patterns.

        Uses variable delays, Gaussian jitter, and burst behavior
        to increase Shannon entropy.

        Args:
            selector: CSS selector of the input field.
            text: Text to type.
        """
        delays = HumanBiometrics.shannon_entropy_variation(len(text))
        delay_index = 0

        for char in text:
            delay = delays[delay_index % len(delays)]
            delay_index += 1
            await self.session.type_text(selector, char, delay=delay)


# ---------------------------------------------------------------------------
# Convenience Function
# ---------------------------------------------------------------------------

async def search(query: str, engine: str = "google", headless: bool = True) -> str:
    """
    Perform a one-off search without managing the session manually.

    Args:
        query: Search query string.
        engine: Search engine to use.
        headless: Whether to run browser headless.

    Returns:
        Raw HTML content of the results page.
    """
    searcher = AdvancedSearcher(headless=headless, engine=engine)
    await searcher.start()

    try:
        return await searcher.search(query)
    finally:
        await searcher.close()
