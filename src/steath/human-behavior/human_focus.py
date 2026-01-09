# human_focus.py
# Simulates occasional tab/window focus and blur events

import random
import time


def random_focus_blur(chance=0.12, min_blur=0.8, max_blur=3.5):
    """
    Randomly simulates tab/window losing focus and regaining it.
    Use in automation (Selenium / Playwright) to mimic human behavior.

    chance: probability of a focus/blur event per check
    min_blur / max_blur: duration of blur in seconds
    """
    if random.random() < chance:
        blur_duration = random.uniform(min_blur, max_blur)
        # In automation frameworks, you could switch window/tab or send JS
        # Here we just sleep to simulate the blur period
        print(f"Tab blurred for {blur_duration:.2f} seconds")
        time.sleep(blur_duration)
        print("Tab focused again")


# Example usage
if __name__ == "__main__":
    for _ in range(15):
        random_focus_blur()
        time.sleep(random.uniform(0.3, 1.0))
