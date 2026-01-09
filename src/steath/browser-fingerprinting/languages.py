# languages.py

import random

# Common browser languages
LANGUAGES = [
    "en-US",
    "en-GB",
    "en-AU",
    "en-CA",  # English variants
    "fr-FR",
    "fr-CA",  # French
    "de-DE",
    "de-AT",
    "de-CH",  # German
    "es-ES",
    "es-MX",
    "es-AR",  # Spanish
    "it-IT",
    "it-CH",  # Italian
    "pt-BR",
    "pt-PT",  # Portuguese
    "ja-JP",  # Japanese
    "ko-KR",  # Korean
    "zh-CN",
    "zh-TW",
    "zh-HK",  # Chinese
    "ru-RU",  # Russian
    "ar-SA",
    "ar-EG",  # Arabic
    "hi-IN",  # Hindi
    "nl-NL",
    "nl-BE",  # Dutch
    "sv-SE",
    "no-NO",
    "fi-FI",  # Nordic languages
]


def get_random_language():
    """
    Returns a random browser language code.
    """
    return random.choice(LANGUAGES)
