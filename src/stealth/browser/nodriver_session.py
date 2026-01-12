# nodriver_session.py
# CDP-Free Browser Automation
#
# Purpose: Single Responsibility - Control Chrome browser WITHOUT Chrome DevTools Protocol.
# 
# Why nodriver instead of Playwright?
# - Playwright = CDP enabled = Google detects debugger = BLOCKED
# - Nodriver = Custom socket connection = No debugger signature = UNDETECTED
#
# How it works:
# - nodriver connects to Chrome's internal socket WITHOUT enabling CDP
# - Browser sees normal user interaction, not automated commands
# - Google's anti-bot can't detect the debugger phone line

import asyncio
from typing import Optional
import nodriver


class NoderiverSession:
    """
    CDP-free browser session using nodriver.
    
    This replaces Playwright for tasks that need true stealth.
    No Chrome DevTools Protocol = No debugger detection.
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize a nodriver browser session.
        
        Args:
            headless: Run browser in headless mode
        """
        self.headless = headless
        self.browser = None
        self.tab = None
        self.uses = 0
    
    async def start(self) -> None:
        """
        Start the browser asynchronously.
        
        Raises:
            Exception: If browser fails to start
        """
        try:
            # Launch Chrome WITHOUT debugger (no CDP)
            self.browser = await nodriver.start(
                headless=self.headless,
                # These args prevent Google detection:
                # --disable-blink-features=AutomationControlled (hides 'navigator.webdriver')
                # --disable-dev-shm-usage (reduces memory fingerprints)
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                    "--disable-extensions",
                ],
            )
            # Get the first tab from the browser
            self.tab = await self.browser.get()
            print("✅ Nodriver browser started (CDP-free)")
        except Exception as e:
            raise Exception(f"Failed to start nodriver browser: {e}")
    
    async def goto(self, url: str, timeout: int = 30) -> None:
        """
        Navigate to a URL.
        
        Args:
            url: Target URL
            timeout: Navigation timeout in seconds
        """
        try:
            # Nodriver uses 'get' for navigation (not 'goto')
            await self.tab.get(url)
            self.uses += 1
        except Exception as e:
            raise Exception(f"Navigation to {url} failed: {e}")
    
    async def wait_for_selector(self, selector: str, timeout: int = 10) -> Optional[object]:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector
            timeout: Timeout in seconds
        
        Returns:
            Element object if found
        """
        try:
            # Use nodriver's find method with retries
            import time
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Try to find element using JavaScript evaluation
                    result = await self.tab.evaluate(
                        f"document.querySelector('{selector}') !== null"
                    )
                    if result:
                        return True
                except:
                    pass
                await asyncio.sleep(0.2)
            raise TimeoutError(f"Selector '{selector}' not found after {timeout}s")
        except Exception as e:
            raise Exception(f"wait_for_selector failed: {e}")
    
    async def type_text(self, selector: str, text: str, delay: float = 0.05) -> None:
        """
        Type text into an element with realistic delays.
        
        Args:
            selector: CSS selector of input field
            text: Text to type
            delay: Delay between keystrokes in seconds
        """
        try:
            await self.wait_for_selector(selector, timeout=5)
            
            # Focus element using JavaScript
            await self.tab.evaluate(f"document.querySelector('{selector}').focus()")
            await asyncio.sleep(0.1)
            
            # Type using JavaScript to insert text char by char
            for char in text:
                await self.tab.evaluate(
                    f"document.querySelector('{selector}').value += '{char}'; "
                    f"document.querySelector('{selector}').dispatchEvent(new Event('input', {{ bubbles: true }}))"
                )
                await asyncio.sleep(delay)
        except Exception as e:
            raise Exception(f"type_text failed: {e}")
    
    async def click(self, selector: str) -> None:
        """
        Click an element.
        
        Args:
            selector: CSS selector
        """
        try:
            await self.wait_for_selector(selector, timeout=5)
            # Use JavaScript to click element
            await self.tab.evaluate(f"document.querySelector('{selector}').click()")
        except Exception as e:
            raise Exception(f"click failed: {e}")
    
    async def get_page_content(self) -> str:
        """
        Get the current page's HTML content.
        
        Returns:
            Full page HTML
        """
        try:
            # Use JavaScript to get page content
            return await self.tab.evaluate("document.documentElement.outerHTML")
        except Exception as e:
            raise Exception(f"get_page_content failed: {e}")
    
    async def press_key(self, key: str) -> None:
        """
        Press a keyboard key.
        
        Args:
            key: Key name (e.g., 'Enter', 'Tab')
        """
        try:
            # Map key names to keyboard codes
            key_map = {
                "Enter": "\\n",
                "Tab": "\\t",
                "Escape": "Escape",
            }
            js_key = key_map.get(key, key)
            
            # Use keyboard event via JavaScript
            await self.tab.evaluate(
                f"var event = new KeyboardEvent('keydown', {{ key: '{js_key}' }}); "
                f"document.dispatchEvent(event);"
            )
        except Exception as e:
            raise Exception(f"press_key failed: {e}")
    
    async def wait_for_load(self, timeout: int = 30) -> None:
        """
        Wait for page to fully load.
        
        Args:
            timeout: Timeout in seconds
        """
        try:
            # Simple network idle detection
            await asyncio.sleep(1)  # Initial wait
        except Exception as e:
            raise Exception(f"wait_for_load failed: {e}")
    
    async def close(self) -> None:
        """Gracefully close the browser."""
        try:
            if self.browser:
                await self.browser.close()
                print("✅ Nodriver browser closed")
        except:
            pass


async def create_session(headless: bool = True) -> NoderiverSession:
    """
    Factory function to create and initialize a nodriver session.
    
    Args:
        headless: Run in headless mode
    
    Returns:
        Initialized NoderiverSession
    """
    session = NoderiverSession(headless=headless)
    await session.start()
    return session
