"""
Human Behavior Module

Config-aware wrapper around behavior utilities located in the
`human-behavior` directory (hyphenated, non-importable package).

This module provides:
- Safe fallbacks when optional behavior modules are unavailable
- Runtime enable/disable via BehaviorConfig
- A single, stable interface for human-like behavior simulation
"""

from __future__ import annotations

import os
import sys
import random
import time
from typing import Iterable, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from stealth_config import BehaviorConfig

# ---------------------------------------------------------------------------
# Import path setup
# ---------------------------------------------------------------------------

_BEHAVIOR_DIR = os.path.join(os.path.dirname(__file__), "human-behavior")
if _BEHAVIOR_DIR not in sys.path:
    sys.path.insert(0, _BEHAVIOR_DIR)

# ---------------------------------------------------------------------------
# Module availability tracking
# ---------------------------------------------------------------------------

_MODULES_AVAILABLE: dict[str, bool] = {}

# ---------------------------------------------------------------------------
# Wait behavior
# ---------------------------------------------------------------------------

try:
    from human_wait import (
        random_human_wait,
        short_wait,
        micro_wait,
        medium_wait,
        long_wait,
    )
    _MODULES_AVAILABLE["wait"] = True
except ImportError:
    _MODULES_AVAILABLE["wait"] = False

    def random_human_wait() -> None:
        time.sleep(random.uniform(0.1, 0.5))

    def short_wait() -> None:
        time.sleep(random.uniform(0.1, 0.3))

    def micro_wait() -> None:
        time.sleep(random.uniform(0.01, 0.05))

    def medium_wait() -> None:
        time.sleep(random.uniform(0.5, 1.5))

    def long_wait() -> None:
        time.sleep(random.uniform(2.0, 5.0))

# ---------------------------------------------------------------------------
# Mouse behavior
# ---------------------------------------------------------------------------

try:
    from human_mouse import generate_human_path, human_delay
    _MODULES_AVAILABLE["mouse"] = True
except ImportError:
    _MODULES_AVAILABLE["mouse"] = False

    def generate_human_path(
        start: Tuple[int, int],
        target: Tuple[int, int],
        screen_size: Tuple[int, int] = (1920, 1080),
    ) -> List[Tuple[int, int]]:
        return [start, target]

    def human_delay() -> None:
        time.sleep(random.uniform(0.001, 0.01))

# ---------------------------------------------------------------------------
# Scroll behavior
# ---------------------------------------------------------------------------

try:
    from human_scroll import (
        generate_human_scroll,
        generate_natural_scroll,
        generate_search_scroll,
    )
    _MODULES_AVAILABLE["scroll"] = True
except ImportError:
    _MODULES_AVAILABLE["scroll"] = False

    def generate_human_scroll(
        target_distance: int | None = None,
        direction: str = "down",
    ) -> List[Tuple[int, float]]:
        return [(100, 0.5)]

    def generate_natural_scroll(pages: int = 1) -> List[Tuple[int, float]]:
        return [(100, 0.5)]

    def generate_search_scroll() -> List[Tuple[int, float]]:
        return [(100, 0.5)]

# ---------------------------------------------------------------------------
# Typing behavior
# ---------------------------------------------------------------------------

try:
    from human_typing import type_like_human, human_typing_sequence
    _MODULES_AVAILABLE["typing"] = True
except ImportError:
    _MODULES_AVAILABLE["typing"] = False

    def type_like_human(send_key_func, text: str) -> None:
        for char in text:
            send_key_func(char)

    def human_typing_sequence(
        text: str,
        base_delay: Tuple[float, float] = (0.04, 0.18),
        fast_burst_chance: float = 0.25,
        pause_chance: float = 0.12,
        mistake_chance: float = 0.06,
        correction_chance: float = 0.85,
    ) -> Iterable[str]:
        yield from text

# ---------------------------------------------------------------------------
# Focus behavior
# ---------------------------------------------------------------------------

try:
    from human_focus import simulate_focus_drift, focus_on_element
    _MODULES_AVAILABLE["focus"] = True
except ImportError:
    _MODULES_AVAILABLE["focus"] = False

    def simulate_focus_drift() -> None:
        return None

    def focus_on_element(element) -> None:
        return None

# ---------------------------------------------------------------------------
# Behavior module (config-aware facade)
# ---------------------------------------------------------------------------

class BehaviorModule:
    """
    Facade providing human-like behavior functions gated by BehaviorConfig.
    """

    def __init__(self, config: "BehaviorConfig | None" = None):
        if config is None:
            from stealth_config import DEFAULT_BEHAVIOR_CONFIG
            config = DEFAULT_BEHAVIOR_CONFIG
        self.config = config

    # --- Wait --------------------------------------------------------------

    def random_human_wait(self) -> None:
        if self.config.wait_enabled:
            random_human_wait()

    def short_wait(self) -> None:
        if self.config.wait_enabled:
            short_wait()

    def micro_wait(self) -> None:
        if self.config.wait_enabled:
            micro_wait()

    def medium_wait(self) -> None:
        if self.config.wait_enabled:
            medium_wait()

    def long_wait(self) -> None:
        if self.config.wait_enabled:
            long_wait()

    # --- Mouse -------------------------------------------------------------

    def generate_human_path(
        self,
        start: Tuple[int, int],
        target: Tuple[int, int],
        screen_size: Tuple[int, int] = (1920, 1080),
    ) -> List[Tuple[int, int]]:
        return (
            generate_human_path(start, target, screen_size)
            if self.config.mouse_enabled
            else [start, target]
        )

    def human_delay(self) -> None:
        if self.config.mouse_enabled:
            human_delay()

    # --- Scroll ------------------------------------------------------------

    def generate_human_scroll(
        self,
        target_distance: int | None = None,
        direction: str = "down",
    ) -> List[Tuple[int, float]]:
        return (
            generate_human_scroll(target_distance, direction)
            if self.config.scroll_enabled
            else [(100, 0.5)]
        )

    def generate_natural_scroll(self, pages: int = 1) -> List[Tuple[int, float]]:
        return (
            generate_natural_scroll(pages)
            if self.config.scroll_enabled
            else [(100, 0.5)]
        )

    def generate_search_scroll(self) -> List[Tuple[int, float]]:
        return (
            generate_search_scroll()
            if self.config.scroll_enabled
            else [(100, 0.5)]
        )

    # --- Typing ------------------------------------------------------------

    def type_like_human(self, send_key_func, text: str) -> None:
        if self.config.typing_enabled:
            type_like_human(send_key_func, text)

    def human_typing_sequence(
        self,
        text: str,
        base_delay: Tuple[float, float] = (0.04, 0.18),
        fast_burst_chance: float = 0.25,
        pause_chance: float = 0.12,
        mistake_chance: float = 0.06,
        correction_chance: float = 0.85,
    ) -> Iterable[str]:
        return (
            human_typing_sequence(
                text,
                base_delay,
                fast_burst_chance,
                pause_chance,
                mistake_chance,
                correction_chance,
            )
            if self.config.typing_enabled
            else iter(text)
        )

    # --- Focus -------------------------------------------------------------

    def simulate_focus_drift(self) -> None:
        if self.config.focus_enabled:
            simulate_focus_drift()

    def focus_on_element(self, element) -> None:
        if self.config.focus_enabled:
            focus_on_element(element)

    # --- Introspection -----------------------------------------------------

    def get_status(self) -> dict:
        """Return module availability and active configuration."""
        return {
            "available": dict(_MODULES_AVAILABLE),
            "enabled": {
                "wait": self.config.wait_enabled,
                "mouse": self.config.mouse_enabled,
                "scroll": self.config.scroll_enabled,
                "typing": self.config.typing_enabled,
                "focus": self.config.focus_enabled,
            },
        }

# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_behavior_module(
    config: "BehaviorConfig | None" = None,
) -> BehaviorModule:
    """Create a BehaviorModule using the provided configuration."""
    return BehaviorModule(config)

# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "get_behavior_module",
    "BehaviorModule",
    "random_human_wait",
    "short_wait",
    "micro_wait",
    "medium_wait",
    "long_wait",
    "generate_human_path",
    "human_delay",
    "generate_human_scroll",
    "generate_natural_scroll",
    "generate_search_scroll",
    "type_like_human",
    "human_typing_sequence",
    "simulate_focus_drift",
    "focus_on_element",
]
