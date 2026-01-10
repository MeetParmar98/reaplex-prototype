# human_wait.py
# Random human-like wait / idle timing simulation

import random
import time


def micro_wait():
    """Very small hesitation (eye/hand sync)"""
    time.sleep(random.uniform(0.01, 0.06))


def short_wait():
    """Normal interaction delay"""
    time.sleep(random.uniform(0.1, 0.4))


def medium_wait():
    """Reading / scanning content"""
    time.sleep(random.uniform(0.6, 2.0))


def long_wait():
    """Thinking / distraction"""
    time.sleep(random.uniform(2.5, 6.5))


def random_human_wait(weights=(0.4, 0.3, 0.2, 0.1)):
    """
    Chooses a random wait type based on human-like probability.
    """
    wait_fn = random.choices(
        [micro_wait, short_wait, medium_wait, long_wait], weights=weights, k=1
    )[0]
    wait_fn()


# Example usage
if __name__ == "__main__":
    for _ in range(10):
        print("Waiting...")
        random_human_wait()
