# fonts.py

import random

# Common fonts across operating systems
FONTS = [
    # Windows Fonts
    "Arial",
    "Verdana",
    "Tahoma",
    "Trebuchet MS",
    "Times New Roman",
    "Georgia",
    "Courier New",
    "Lucida Console",
    "Impact",
    "Comic Sans MS",
    # macOS Fonts
    "Helvetica",
    "Geneva",
    "Menlo",
    "Monaco",
    "Avenir",
    "Futura",
    "Gill Sans",
    # Linux Fonts
    "Ubuntu",
    "DejaVu Sans",
    "DejaVu Serif",
    "Liberation Sans",
    "Liberation Serif",
    # Generic / Web Fonts
    "sans-serif",
    "serif",
    "monospace",
    "cursive",
    "fantasy",
    # Mobile common fonts
    "SF Pro Text",
    "SF Pro Display",
    "Roboto",
    "Noto Sans",
    "PingFang SC",
    "Apple Color Emoji",
]


def get_random_fonts(n=5):
    """
    Returns a list of n randomly selected fonts from the list.
    Defaults to 5 fonts to simulate a realistic system font list.
    """
    return random.sample(FONTS, n)
