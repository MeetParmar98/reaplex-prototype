# plugins.py
import random

# Realistic browser plugin sets
PLUGIN_SETS = {
    "chrome": ["Chrome PDF Plugin", "Chrome PDF Viewer", "Native Client"],
    "edge": ["Chrome PDF Plugin", "Chrome PDF Viewer", "Native Client"],
    "firefox": ["PDF.js"],
    "safari": ["Apple PDF Plugin"],
}


def get_plugins(browser="chrome"):
    """
    Returns a realistic list of browser plugins.

    browser: chrome, edge, firefox, safari
    """
    return PLUGIN_SETS.get(browser, PLUGIN_SETS["chrome"]).copy()
