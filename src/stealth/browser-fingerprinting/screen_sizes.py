# screen_sizes.py

import random

# Common screen sizes for desktops, laptops, tablets, and mobile devices
SCREEN_SIZES = [
    # Desktop
    (1920, 1080),  # Full HD
    (2560, 1440),  # 2K
    (3840, 2160),  # 4K
    (1680, 1050),
    (1600, 900),
    (1440, 900),
    (1366, 768),
    (1280, 1024),
    # Laptop
    (1440, 900),
    (1536, 864),
    (1366, 768),
    (1280, 800),
    (1280, 720),
    # Tablet
    (1280, 800),
    (1024, 768),
    (800, 1280),
    (768, 1024),
    # Mobile
    (1080, 2340),  # Modern Android phones
    (1170, 2532),  # iPhone 13/14/15
    (1125, 2436),  # iPhone X/XS
    (1242, 2688),  # iPhone 11 Pro Max
    (750, 1334),  # iPhone 6/7/8
    (720, 1600),  # Mid-range Android
    (1080, 1920),
]


def get_random_screen_size():
    """
    Returns a random screen size as a (width, height) tuple.
    """
    return random.choice(SCREEN_SIZES)
