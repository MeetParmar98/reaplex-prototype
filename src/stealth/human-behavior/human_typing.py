# human_typing.py
# Human-like typing delay and behavior simulation

import random
import time
import string


def human_typing_sequence(
    text,
    base_delay=(0.04, 0.18),
    fast_burst_chance=0.25,
    pause_chance=0.12,
    mistake_chance=0.06,
    correction_chance=0.85,
):
    """
    Yields characters with realistic human typing delays.
    Includes speed variance, pauses, and occasional mistakes.
    """
    typed = ""

    for ch in text:
        # Thinking pause
        if random.random() < pause_chance:
            time.sleep(random.uniform(0.3, 0.9))

        # Fast typing burst
        if random.random() < fast_burst_chance:
            delay = random.uniform(0.01, 0.04)
        else:
            delay = random.uniform(*base_delay)

        # Mistake simulation
        if random.random() < mistake_chance and ch.isalpha():
            wrong = random.choice(string.ascii_lowercase)
            typed += wrong
            yield wrong, delay
            time.sleep(random.uniform(0.08, 0.25))

            if random.random() < correction_chance:
                # Backspace
                yield "\b", random.uniform(0.05, 0.15)
                typed = typed[:-1]

        typed += ch
        yield ch, delay


def type_like_human(send_key_func, text):
    """
    send_key_func: function that sends a single key (e.g. Selenium, Playwright)
    """
    for ch, delay in human_typing_sequence(text):
        send_key_func(ch)
        time.sleep(delay)


# Example (framework-agnostic)
if __name__ == "__main__":

    def printer(k):
        print(k, end="", flush=True)

    type_like_human(printer, "Hello, this is human typing.")
