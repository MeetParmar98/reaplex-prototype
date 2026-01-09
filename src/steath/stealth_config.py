"""
Stealth Module Configuration

Defines configuration objects that control which behavior and fingerprint
sub-modules are enabled when importing behavior.py or fingerprint.py.

These configs are intentionally simple, explicit, and composable.
"""

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Behavior configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BehaviorConfig:
    """
    Configure which human-behavior sub-modules are active.
    """
    wait_enabled: bool = True      # human_wait.py
    mouse_enabled: bool = True     # human_mouse.py
    scroll_enabled: bool = True    # human_scroll.py
    typing_enabled: bool = True    # human_typing.py
    focus_enabled: bool = False    # human_focus.py (optional)


# ---------------------------------------------------------------------------
# Fingerprint configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FingerprintConfig:
    """
    Configure which browser fingerprinting sub-modules are active.
    """
    user_agents_enabled: bool = True
    screen_sizes_enabled: bool = True
    timezones_enabled: bool = True
    languages_enabled: bool = True
    webgl_enabled: bool = False
    plugins_enabled: bool = False
    hardware_enabled: bool = False
    fonts_enabled: bool = False


# ---------------------------------------------------------------------------
# Default configurations
# ---------------------------------------------------------------------------

DEFAULT_BEHAVIOR_CONFIG = BehaviorConfig()
DEFAULT_FINGERPRINT_CONFIG = FingerprintConfig()


# ---------------------------------------------------------------------------
# Preset configurations
# ---------------------------------------------------------------------------

class PresetConfigs:
    """
    Predefined configurations for common stealth scenarios.
    """

    # --- Behavior presets --------------------------------------------------

    @staticmethod
    def minimal_behavior() -> BehaviorConfig:
        """
        Minimal interaction:
        - Randomized wait timing only
        """
        return BehaviorConfig(
            wait_enabled=True,
            mouse_enabled=False,
            scroll_enabled=False,
            typing_enabled=False,
            focus_enabled=False,
        )

    @staticmethod
    def basic_behavior() -> BehaviorConfig:
        """
        Basic form interaction:
        - Wait timing
        - Human-like typing
        """
        return BehaviorConfig(
            wait_enabled=True,
            mouse_enabled=False,
            scroll_enabled=False,
            typing_enabled=True,
            focus_enabled=False,
        )

    @staticmethod
    def full_behavior() -> BehaviorConfig:
        """
        Full interaction simulation:
        - Mouse movement
        - Scrolling
        - Typing
        - Focus drift
        """
        return BehaviorConfig(
            wait_enabled=True,
            mouse_enabled=True,
            scroll_enabled=True,
            typing_enabled=True,
            focus_enabled=True,
        )

    # --- Fingerprint presets ----------------------------------------------

    @staticmethod
    def minimal_fingerprint() -> FingerprintConfig:
        """
        Minimal browser identity:
        - User agent
        - Screen size
        """
        return FingerprintConfig(
            user_agents_enabled=True,
            screen_sizes_enabled=True,
            timezones_enabled=False,
            languages_enabled=False,
            webgl_enabled=False,
            plugins_enabled=False,
            hardware_enabled=False,
            fonts_enabled=False,
        )

    @staticmethod
    def full_fingerprint() -> FingerprintConfig:
        """
        Full browser fingerprint:
        - All supported fingerprint surfaces enabled
        """
        return FingerprintConfig(
            user_agents_enabled=True,
            screen_sizes_enabled=True,
            timezones_enabled=True,
            languages_enabled=True,
            webgl_enabled=True,
            plugins_enabled=True,
            hardware_enabled=True,
            fonts_enabled=True,
        )
