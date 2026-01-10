# human_mouse.py
# Clean, realistic human-like mouse movement generator
# Public API: generate_human_path(start, target)

import random
import math
import time
from typing import List, Tuple

Point = Tuple[int, int]


# ============================================================
# Public API
# ============================================================


def generate_human_path(
    start: Point, target: Point, screen_size: Point = (1920, 1080)
) -> List[Point]:
    sx, sy = start
    tx, ty = target

    distance = _distance(start, target)
    steps = _calculate_steps(distance)

    style = _choose_style(distance)
    path = _build_path(style, start, target, steps, distance)

    path = _apply_jitter(path)
    path = _clamp_to_screen(path, screen_size)

    if random.random() < 0.3:
        path = _add_overshoot(path, target)

    if path[-1] != target:
        path.append(target)

    return path


# ============================================================
# Timing helpers (optional execution helpers)
# ============================================================


def human_delay():
    time.sleep(random.uniform(0.001, 0.012))


def human_pause():
    if random.random() < 0.03:
        time.sleep(random.uniform(0.1, 0.5))


# ============================================================
# Internal helpers
# ============================================================


def _distance(a: Point, b: Point) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _calculate_steps(distance: float) -> int:
    steps = int(20 + distance / 10)
    steps = max(20, min(steps, 100))
    return steps + random.randint(-5, 5)


def _choose_style(distance: float) -> str:
    if distance < 100:
        return random.choice(("direct", "arc"))
    if distance < 400:
        return random.choice(("arc", "arc", "bezier"))
    return random.choice(("bezier", "bezier", "arc"))


def _build_path(style, start, target, steps, distance):
    if style == "bezier":
        return _bezier_path(start, target, steps, distance)
    if style == "arc":
        return _arc_path(start, target, steps)
    return _direct_path(start, target, steps)


def _ease(t: float) -> float:
    if t < 0.5:
        return 4 * t**3
    return 1 - ((-2 * t + 2) ** 3) / 2


# ============================================================
# Path generators
# ============================================================


def _bezier_path(start, target, steps, distance):
    sx, sy = start
    tx, ty = target

    spread = min(distance * 0.3, 300)

    c1 = (
        sx + random.uniform(-spread, spread),
        sy + random.uniform(-spread, spread),
    )
    c2 = (
        tx + random.uniform(-spread, spread),
        ty + random.uniform(-spread, spread),
    )

    path = []
    for i in range(steps):
        t = _ease(i / (steps - 1))
        u = 1 - t

        x = u**3 * sx + 3 * u**2 * t * c1[0] + 3 * u * t**2 * c2[0] + t**3 * tx
        y = u**3 * sy + 3 * u**2 * t * c1[1] + 3 * u * t**2 * c2[1] + t**3 * ty
        path.append((x, y))

    return path


def _arc_path(start, target, steps):
    sx, sy = start
    tx, ty = target

    dx, dy = tx - sx, ty - sy
    dist = math.hypot(dx, dy)
    curvature = random.uniform(0.15, 0.4)

    path = []
    for i in range(steps):
        t = _ease(i / (steps - 1))

        x = sx + dx * t
        y = sy + dy * t

        if dist:
            offset = 4 * curvature * dist * t * (1 - t)
            x += (-dy / dist) * offset
            y += (dx / dist) * offset

        path.append((x, y))

    return path


def _direct_path(start, target, steps):
    sx, sy = start
    tx, ty = target

    path = []
    for i in range(steps):
        t = _ease(i / (steps - 1))
        path.append((sx + (tx - sx) * t, sy + (ty - sy) * t))

    return path


# ============================================================
# Post-processing
# ============================================================


def _apply_jitter(path):
    return [
        (int(x + random.gauss(0, 1.0)), int(y + random.gauss(0, 1.0))) for x, y in path
    ]


def _clamp_to_screen(path, screen):
    w, h = screen
    return [(max(0, min(x, w - 1)), max(0, min(y, h - 1))) for x, y in path]


def _add_overshoot(path, target):
    tx, ty = target
    lx, ly = path[-1]

    dx, dy = tx - lx, ty - ly
    dist = math.hypot(dx, dy)

    if not dist:
        return path

    overshoot = random.randint(5, 25)
    ox = tx + (dx / dist) * overshoot
    oy = ty + (dy / dist) * overshoot

    steps = random.randint(3, 6)
    for i in range(1, steps + 1):
        t = _ease(i / steps)
        x = ox + (tx - ox) * t + random.gauss(0, 0.8)
        y = oy + (ty - oy) * t + random.gauss(0, 0.8)
        path.append((int(x), int(y)))

    return path
