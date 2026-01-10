# human_scroll.py
# Clean, realistic human-like scrolling generator
# Public API:
#   - generate_human_scroll(...)
#   - generate_natural_scroll(...)
#   - generate_search_scroll(...)

import random
import time
from typing import List, Tuple

ScrollStep = Tuple[int, float]  # (delta_px, pause_seconds)


# ============================================================
# Public APIs
# ============================================================


def generate_human_scroll(
    target_distance: int | None = None, direction: str = "down"
) -> List[ScrollStep]:
    if target_distance is None:
        target_distance = random.randint(300, 2000)

    if direction == "random":
        direction = random.choice(("down", "up"))

    multiplier = 1 if direction == "down" else -1

    scrolls: List[ScrollStep] = []
    scrolled = 0

    while scrolled < target_distance:
        pattern = _choose_pattern()
        step, pause, micro_chance = _pattern_params(pattern)

        if random.random() < micro_chance:
            step = random.randint(3, 18)

        remaining = target_distance - scrolled
        step = min(step, remaining)

        scrolls.append((step * multiplier, pause))
        scrolled += step

        if random.random() < 0.18 and scrolled < target_distance:
            back = random.randint(5, 35)
            scrolls.append((-back * multiplier, random.uniform(0.03, 0.12)))
            scrolled = max(0, scrolled - back)

        if random.random() < 0.08:
            scrolls.append((0, random.uniform(0.3, 1.2)))

    return scrolls


def generate_natural_scroll(pages: int = 1) -> List[ScrollStep]:
    scrolls: List[ScrollStep] = []

    for i in range(pages):
        page_height = random.randint(700, 1200)
        scrolls.extend(generate_human_scroll(page_height, "down"))

        if i < pages - 1:
            scrolls.append((0, random.uniform(0.5, 2.0)))

    return scrolls


def generate_search_scroll() -> List[ScrollStep]:
    scrolls: List[ScrollStep] = []

    initial = random.randint(400, 1000)
    scrolls.extend(generate_human_scroll(initial, "down"))

    scrolls.append((0, random.uniform(0.2, 0.6)))

    for _ in range(random.randint(2, 5)):
        direction = random.choice(("down", "up"))
        step = random.randint(10, 50)
        pause = random.uniform(0.08, 0.25)
        scrolls.append((step if direction == "down" else -step, pause))

    if random.random() < 0.3:
        scrolls.extend(generate_human_scroll(random.randint(100, 300), "up"))

    return scrolls


# ============================================================
# Optional execution helpers
# ============================================================


def scroll_delay(delay_range=(0.05, 0.2)):
    time.sleep(random.uniform(*delay_range))


def reading_pause():
    time.sleep(random.uniform(0.4, 1.5))


# ============================================================
# Internal helpers
# ============================================================


def _choose_pattern() -> str:
    return random.choices(
        ("normal", "fast", "precise", "reading"), weights=(0.5, 0.2, 0.15, 0.15)
    )[0]


def _pattern_params(pattern: str):
    if pattern == "fast":
        return (random.randint(100, 200), random.uniform(0.02, 0.08), 0.1)
    if pattern == "precise":
        return (random.randint(15, 50), random.uniform(0.1, 0.3), 0.4)
    if pattern == "reading":
        return (random.randint(20, 60), random.uniform(0.15, 0.4), 0.3)

    # normal
    return (random.randint(40, 120), random.uniform(0.05, 0.2), 0.2)
