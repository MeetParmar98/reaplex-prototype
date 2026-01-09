# human_biometrics.py
# Human Behavior Emulation - Defeats reCAPTCHA v3 & Shannon Entropy Analysis
#
# Purpose: Generate realistic human interaction patterns to evade automated detection.
#
# How it works:
# - reCAPTCHA v3 uses Shannon Entropy of user actions to detect bots
# - Bots: low entropy (smooth, predictable movements)
# - Humans: high entropy (jitters, micro-pauses, irregular timing)
# - Inject Gaussian noise (micro-tremors) + random pauses (cognition) to mimic humans
#
# Math:
# Shannon Entropy = -Σ p(x) * log(p(x))
# High entropy = human-like patterns
# Low entropy = bot-like patterns

import asyncio
import random
from typing import Tuple, List


class HumanBiometrics:
    """
    Generate human-like interaction patterns.

    This class adds randomness to mouse movements, typing, and pauses to
    defeat entropy-based bot detection systems.
    """

    # -----------------------------------------------------------------------
    # Random Noise / Timing Utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def gaussian_jitter(mean: float = 0.0, std_dev: float = 0.02) -> float:
        """
        Generate Gaussian random noise (micro-tremors) for human-like movement.

        Args:
            mean: Mean of the distribution
            std_dev: Standard deviation (magnitude of jitter)

        Returns:
            Random jitter value
        """
        return random.gauss(mean, std_dev)

    @staticmethod
    def cognitive_pause(min_sec: float = 0.5, max_sec: float = 3.0) -> float:
        """
        Generate a "thinking pause" to simulate human reading/processing.

        Args:
            min_sec: Minimum pause
            max_sec: Maximum pause

        Returns:
            Pause duration in seconds
        """
        mode = (min_sec + max_sec) / 2
        return random.triangular(min_sec, max_sec, mode)

    @staticmethod
    def typing_delay(min_ms: float = 30, max_ms: float = 150, burst_chance: float = 0.2) -> float:
        """
        Generate a realistic delay between keystrokes.

        Args:
            min_ms: Minimum typing delay in milliseconds
            max_ms: Maximum typing delay in milliseconds
            burst_chance: Probability of a fast typing burst

        Returns:
            Delay in seconds
        """
        if random.random() < burst_chance:
            delay_ms = random.uniform(20, 50)
        else:
            delay_ms = random.uniform(min_ms, max_ms)
        return delay_ms / 1000.0

    # -----------------------------------------------------------------------
    # Mouse Movement
    # -----------------------------------------------------------------------

    @staticmethod
    def mouse_movement_path(
        start: Tuple[int, int],
        end: Tuple[int, int],
        num_points: int = 10
    ) -> List[Tuple[int, int]]:
        """
        Generate a human-like curved mouse path with micro-jitters.

        Humans rarely move in straight lines; this adds curves and tremors.

        Args:
            start: Starting (x, y) coordinates
            end: Ending (x, y) coordinates
            num_points: Number of intermediate path points

        Returns:
            List of (x, y) coordinates
        """
        path: List[Tuple[int, int]] = []
        start_x, start_y = start
        end_x, end_y = end

        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0

            # Random control point for natural curve
            control_x = (start_x + end_x) / 2 + random.uniform(-50, 50)
            control_y = (start_y + end_y) / 2 - random.uniform(20, 100)

            # Quadratic Bezier interpolation
            x = (1 - t)**2 * start_x + 2 * (1 - t) * t * control_x + t**2 * end_x
            y = (1 - t)**2 * start_y + 2 * (1 - t) * t * control_y + t**2 * end_y

            # Add Gaussian jitter
            x += HumanBiometrics.gaussian_jitter(0, 2)
            y += HumanBiometrics.gaussian_jitter(0, 2)

            path.append((int(x), int(y)))

        return path

    # -----------------------------------------------------------------------
    # Human-Like Action Execution
    # -----------------------------------------------------------------------

    @staticmethod
    async def human_like_action(action_name: str, min_pause: float = 0.3, max_pause: float = 1.5) -> None:
        """
        Wrap an action with human-like pre and post pauses.

        Args:
            action_name: Description of the action (logging purposes)
            min_pause: Minimum pre-action pause
            max_pause: Maximum post-action pause
        """
        pre_pause = random.uniform(min_pause, max_pause)
        await asyncio.sleep(pre_pause)

        # Short post-action pause
        post_pause = random.uniform(min_pause / 2, max_pause / 2)
        await asyncio.sleep(post_pause)

    # -----------------------------------------------------------------------
    # Shannon Entropy Utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def shannon_entropy_variation(num_samples: int = 5) -> List[float]:
        """
        Generate varied delays to increase entropy and appear human-like.

        Args:
            num_samples: Number of delay samples to return

        Returns:
            List of randomized delays
        """
        delays = [
            random.uniform(0.1, 0.2),
            random.uniform(0.5, 1.5),
            random.uniform(0.05, 0.1),
            random.uniform(1.0, 3.0),
            random.uniform(0.2, 0.5),
        ]
        random.shuffle(delays)
        return delays[:num_samples]
