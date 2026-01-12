# tls_client.py
# TLS / JA4 Fingerprinting Client
#
# Purpose:
#   Perform HTTP/HTTPS requests using Chrome’s exact TLS fingerprint
#   (BoringSSL via curl_cffi) to evade JA4-based bot detection.
#
# Key Idea:
#   JA4 fingerprinting detects TLS handshakes.
#   Python's default OpenSSL fingerprints as a bot.
#   curl_cffi impersonation reproduces Chrome's real TLS stack.

from typing import Dict, Optional

from curl_cffi import requests as cffi_requests
from stealth import fingerprint


class JA4Client:
    """
    JA4-compliant HTTP client.

    Uses curl_cffi impersonation to reproduce Chrome's exact TLS handshake,
    making requests indistinguishable from a real Chrome browser.
    """

    # User-Agent selection delegated to the project's fingerprint module

    def __init__(self) -> None:
        self.session = cffi_requests
        self.impersonate = "chrome124"  # Chrome + BoringSSL

    # ------------------------------------------------------------------
    # Headers
    # ------------------------------------------------------------------

    def _build_headers(self) -> Dict[str, str]:
        """Generate Chrome-realistic HTTP headers."""
        return {
            "User-Agent": fingerprint.get_random_user_agent(),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

    # ------------------------------------------------------------------
    # HTTP Methods
    # ------------------------------------------------------------------

    def get(self, url: str, timeout: int = 30, **kwargs):
        """
        Perform a JA4-compliant GET request.

        Args:
            url: Target URL
            timeout: Request timeout in seconds
            **kwargs: Additional curl_cffi parameters

        Returns:
            curl_cffi response object
        """
        try:
            return self.session.get(
                url,
                headers=self._build_headers(),
                impersonate=self.impersonate,
                timeout=timeout,
                **kwargs,
            )
        except Exception as e:
            raise RuntimeError(f"JA4 GET request failed: {url}") from e

    def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        timeout: int = 30,
        **kwargs,
    ):
        """
        Perform a JA4-compliant POST request.

        Args:
            url: Target URL
            data: JSON payload
            timeout: Request timeout in seconds
            **kwargs: Additional curl_cffi parameters

        Returns:
            curl_cffi response object
        """
        try:
            return self.session.post(
                url,
                json=data,
                headers=self._build_headers(),
                impersonate=self.impersonate,
                timeout=timeout,
                **kwargs,
            )
        except Exception as e:
            raise RuntimeError(f"JA4 POST request failed: {url}") from e


# ----------------------------------------------------------------------
# Singleton Accessor
# ----------------------------------------------------------------------

_ja4_client: Optional[JA4Client] = None


def get_ja4_client() -> JA4Client:
    """
    Return a singleton JA4Client instance.
    """
    global _ja4_client
    if _ja4_client is None:
        _ja4_client = JA4Client()
    return _ja4_client
