"""
Browser Fingerprinting Module

Config-aware wrapper around fingerprinting utilities located in the
`browser-fingerprinting` directory (hyphenated, non-importable package).

Provides safe fallbacks, per-feature enable/disable via FingerprintConfig,
and a stable interface for browser fingerprint generation.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from stealth_config import FingerprintConfig

# ---------------------------------------------------------------------------
# Import path setup
# ---------------------------------------------------------------------------

_FINGERPRINTING_DIR = os.path.join(os.path.dirname(__file__), "browser-fingerprinting")
if _FINGERPRINTING_DIR not in sys.path:
    sys.path.insert(0, _FINGERPRINTING_DIR)

# ---------------------------------------------------------------------------
# Module availability tracking
# ---------------------------------------------------------------------------

_MODULES_AVAILABLE: dict[str, bool] = {}

# ---------------------------------------------------------------------------
# User agent
# ---------------------------------------------------------------------------

try:
    from user_agents import get_random_user_agent, USER_AGENTS
    _MODULES_AVAILABLE["user_agents"] = True
except ImportError:
    _MODULES_AVAILABLE["user_agents"] = False

    def get_random_user_agent() -> str:
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.5993.90 Safari/537.36"
        )

    USER_AGENTS = [get_random_user_agent()]

# ---------------------------------------------------------------------------
# Screen size
# ---------------------------------------------------------------------------

try:
    from screen_sizes import get_random_screen_size
    _MODULES_AVAILABLE["screen_sizes"] = True
except ImportError:
    _MODULES_AVAILABLE["screen_sizes"] = False

    def get_random_screen_size() -> Dict[str, int]:
        return {"width": 1920, "height": 1080}

# ---------------------------------------------------------------------------
# Timezone
# ---------------------------------------------------------------------------

try:
    from timezones import get_random_timezone
    _MODULES_AVAILABLE["timezones"] = True
except ImportError:
    _MODULES_AVAILABLE["timezones"] = False

    def get_random_timezone() -> str:
        return "America/New_York"

# ---------------------------------------------------------------------------
# Language
# ---------------------------------------------------------------------------

try:
    from languages import get_random_language
    _MODULES_AVAILABLE["languages"] = True
except ImportError:
    _MODULES_AVAILABLE["languages"] = False

    def get_random_language() -> str:
        return "en-US"

# ---------------------------------------------------------------------------
# WebGL
# ---------------------------------------------------------------------------

try:
    from webgl_canvas import get_random_webgl, get_webgl_fingerprint
    _MODULES_AVAILABLE["webgl"] = True
except ImportError:
    _MODULES_AVAILABLE["webgl"] = False

    def get_random_webgl() -> Dict:
        return {"vendor": "Google", "renderer": "ANGLE"}

    def get_webgl_fingerprint() -> str:
        return "ANGLE (Intel)"

# ---------------------------------------------------------------------------
# Plugins
# ---------------------------------------------------------------------------

try:
    from plugins import get_random_plugins
    _MODULES_AVAILABLE["plugins"] = True
except ImportError:
    _MODULES_AVAILABLE["plugins"] = False

    def get_random_plugins() -> list:
        return [{"name": "Chrome PDF Plugin"}]

# ---------------------------------------------------------------------------
# Hardware concurrency
# ---------------------------------------------------------------------------

try:
    from hardware_concurrency import get_hardware_concurrency
    _MODULES_AVAILABLE["hardware"] = True
except ImportError:
    _MODULES_AVAILABLE["hardware"] = False

    def get_hardware_concurrency() -> int:
        return 4

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

try:
    from fonts import get_random_fonts
    _MODULES_AVAILABLE["fonts"] = True
except ImportError:
    _MODULES_AVAILABLE["fonts"] = False

    def get_random_fonts() -> list:
        return ["Arial", "Times New Roman", "Courier New"]

# ---------------------------------------------------------------------------
# Fingerprint module (config-aware facade)
# ---------------------------------------------------------------------------

class FingerprintModule:
    """
    Facade providing fingerprint generation gated by FingerprintConfig.
    """

    def __init__(self, config: "FingerprintConfig | None" = None):
        if config is None:
            from stealth_config import DEFAULT_FINGERPRINT_CONFIG
            config = DEFAULT_FINGERPRINT_CONFIG
        self.config = config

    # --- Individual fingerprints -----------------------------------------

    def get_random_user_agent(self) -> str:
        return get_random_user_agent() if self.config.user_agents_enabled else "Mozilla/5.0"

    def get_random_screen_size(self) -> Dict[str, int]:
        return (
            get_random_screen_size()
            if self.config.screen_sizes_enabled
            else {"width": 1920, "height": 1080}
        )

    def get_random_timezone(self) -> str:
        return get_random_timezone() if self.config.timezones_enabled else "UTC"

    def get_random_language(self) -> str:
        return get_random_language() if self.config.languages_enabled else "en-US"

    def get_random_webgl(self) -> Dict:
        return get_random_webgl() if self.config.webgl_enabled else {}

    def get_webgl_fingerprint(self) -> str:
        return get_webgl_fingerprint() if self.config.webgl_enabled else ""

    def get_random_plugins(self) -> list:
        return get_random_plugins() if self.config.plugins_enabled else []

    def get_hardware_concurrency(self) -> int:
        return get_hardware_concurrency() if self.config.hardware_enabled else 4

    def get_random_fonts(self) -> list:
        return get_random_fonts() if self.config.fonts_enabled else []

    # --- Aggregate --------------------------------------------------------

    def get_all_fingerprints(self) -> Dict:
        """
        Return all enabled fingerprint components as a single dictionary.
        """
        fingerprints: Dict[str, object] = {}

        if self.config.user_agents_enabled:
            fingerprints["user_agent"] = self.get_random_user_agent()
        if self.config.screen_sizes_enabled:
            fingerprints["screen_size"] = self.get_random_screen_size()
        if self.config.timezones_enabled:
            fingerprints["timezone"] = self.get_random_timezone()
        if self.config.languages_enabled:
            fingerprints["language"] = self.get_random_language()
        if self.config.webgl_enabled:
            fingerprints["webgl"] = self.get_random_webgl()
        if self.config.plugins_enabled:
            fingerprints["plugins"] = self.get_random_plugins()
        if self.config.hardware_enabled:
            fingerprints["hardware_concurrency"] = self.get_hardware_concurrency()
        if self.config.fonts_enabled:
            fingerprints["fonts"] = self.get_random_fonts()

        return fingerprints

    # --- Introspection ----------------------------------------------------

    def get_status(self) -> dict:
        """Return module availability and active configuration."""
        return {
            "available": dict(_MODULES_AVAILABLE),
            "enabled": {
                "user_agents": self.config.user_agents_enabled,
                "screen_sizes": self.config.screen_sizes_enabled,
                "timezones": self.config.timezones_enabled,
                "languages": self.config.languages_enabled,
                "webgl": self.config.webgl_enabled,
                "plugins": self.config.plugins_enabled,
                "hardware": self.config.hardware_enabled,
                "fonts": self.config.fonts_enabled,
            },
        }

# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_fingerprint_module(
    config: "FingerprintConfig | None" = None,
) -> FingerprintModule:
    """Create a FingerprintModule using the provided configuration."""
    return FingerprintModule(config)

# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "get_fingerprint_module",
    "FingerprintModule",
    "get_random_user_agent",
    "USER_AGENTS",
    "get_random_screen_size",
    "get_random_timezone",
    "get_random_language",
    "get_random_webgl",
    "get_webgl_fingerprint",
    "get_random_plugins",
    "get_hardware_concurrency",
    "get_random_fonts",
]
