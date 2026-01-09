---

# Stealth Module Usage Guide

This guide explains how to use the configurable **behavior** and **fingerprinting** modules in Python.

---

## Example 1: Single Usage (Web Scraper) – Aggressive Stealth

```python
from src.steath.behavior import get_behavior_module
from src.steath.fingerprint import get_fingerprint_module
from src.steath.stealth_config import PresetConfigs
 
class WebScraper:
    def __init__(self):
        # Full stealth configuration
        self.behavior = get_behavior_module(PresetConfigs.full_behavior())
        self.fingerprint = get_fingerprint_module(PresetConfigs.full_fingerprint())
    
    def scrape_page(self):
        # Retrieve fingerprint for this session
        fp = self.fingerprint.get_all_fingerprints()
        print(f"Using User-Agent: {fp['user_agent']}")
        
        # Apply stealth behaviors
        self.behavior.micro_wait()
        self.fingerprint.get_random_screen_size()
        self.behavior.type_like_human(lambda x: None, "search query")
        self.behavior.generate_human_scroll()
```

---

## Example 2: Different Configurations in Different Contexts

```python
from src.steath.stealth_config import BehaviorConfig

# Minimal stealth for login automation
login_behavior = get_behavior_module(BehaviorConfig(
    wait_enabled=True,
    mouse_enabled=False,
    scroll_enabled=False,
    typing_enabled=True,
    focus_enabled=False
))

# Maximum stealth for web scraping
scrape_behavior = get_behavior_module(BehaviorConfig(
    wait_enabled=True,
    mouse_enabled=True,
    scroll_enabled=True,
    typing_enabled=True,
    focus_enabled=True
))

# Login action
def do_login():
    login_behavior.type_like_human(send_key, "password123")
    login_behavior.short_wait()

# Scraping action
def do_scraping():
    scrape_behavior.generate_human_scroll()
    scrape_behavior.medium_wait()
    scrape_behavior.generate_human_path((0, 0), (500, 500))
```

---

## Example 3: Custom Mix & Match

```python
from src.steath.stealth_config import BehaviorConfig, FingerprintConfig

# Minimal behavior configuration
minimal_behavior_config = BehaviorConfig(
    wait_enabled=True,
    mouse_enabled=False,
    scroll_enabled=False,
    typing_enabled=False,
    focus_enabled=False
)

# Medium fingerprint configuration (faster, skip heavy plugins)
fp_config = FingerprintConfig(
    user_agents_enabled=True,
    screen_sizes_enabled=True,
    timezones_enabled=True,
    languages_enabled=True,
    webgl_enabled=False,
    plugins_enabled=False,
    hardware_enabled=False,
    fonts_enabled=False
)

# Create modules
minimal_behavior = get_behavior_module(minimal_behavior_config)
medium_fingerprint = get_fingerprint_module(fp_config)

# Usage
minimal_behavior.random_human_wait()        # Works
minimal_behavior.move_mouse((0, 0), (100, 100))  # Does nothing

fingerprints = medium_fingerprint.get_all_fingerprints()
# Returns: user_agent, screen_size, timezone, language
# Excludes: webgl, plugins, hardware, fonts
```

---

## Example 4: Check Enabled Features Before Use

```python
behavior = get_behavior_module(PresetConfigs.basic_behavior())
status = behavior.get_status()

print("Available modules:", status['available'])
print("Enabled in config:", status['config'])

if status['config']['typing']:
    behavior.type_like_human(send_key, "text")
else:
    print("Typing not enabled, sending text directly")
```

---

## Example 5: Modify Configuration at Runtime

```python
from src.steath.stealth_config import FingerprintConfig

config = FingerprintConfig()
fp = get_fingerprint_module(config)

# Enable WebGL
config.webgl_enabled = True
fp.get_random_webgl()  # Works

# Disable WebGL for performance
config.webgl_enabled = False
fp.get_random_webgl()  # Returns empty dict
```

---

## Key Points

1. **Configure at Import**

   * Pass the configuration when creating the module.
   * Different parts of the app can use different configs.
   * Sub-modules do not require changes.

2. **Use Factory Functions**

   * `get_behavior_module(config)` → returns `BehaviorModule`.
   * `get_fingerprint_module(config)` → returns `FingerprintModule`.
   * Makes swapping configs simple.

3. **Presets for Common Use**

   * `PresetConfigs.minimal_behavior()` – basic only.
   * `PresetConfigs.basic_behavior()` – typing + wait.
   * `PresetConfigs.full_behavior()` – full stealth.
   * Same for fingerprint configs.

4. **Custom Configurations**

   * Behavior: `BehaviorConfig(wait=True, mouse=False, ...)`
   * Fingerprint: `FingerprintConfig(user_agents=True, webgl=False, ...)`
   * Mix features as needed.

5. **Check Status**

   * `module.get_status()` shows available and enabled features.
   * Avoids unexpected behavior.

6. **Functions Respect Config**

   * Disabled features do nothing instead of raising errors.
   * Safe to call all functions regardless of config.
   * Simplifies code readability.

---
