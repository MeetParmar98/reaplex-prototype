# timezones.py

import random

# List of common timezones
TIMEZONES = [
    # North America
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Phoenix",
    "America/Toronto",
    "America/Vancouver",
    # Europe
    "Europe/London",
    "Europe/Berlin",
    "Europe/Paris",
    "Europe/Madrid",
    "Europe/Rome",
    "Europe/Moscow",
    # Asia
    "Asia/Tokyo",
    "Asia/Seoul",
    "Asia/Shanghai",
    "Asia/Singapore",
    "Asia/Kolkata",
    "Asia/Dubai",
    # Australia
    "Australia/Sydney",
    "Australia/Melbourne",
    "Australia/Brisbane",
    "Australia/Perth",
    # South America
    "America/Sao_Paulo",
    "America/Argentina/Buenos_Aires",
    "America/Bogota",
    # Africa
    "Africa/Johannesburg",
    "Africa/Cairo",
    "Africa/Lagos",
]


def get_random_timezone():
    """
    Returns a random timezone string.
    """
    return random.choice(TIMEZONES)
