# human_biometrics.py
# Human Behavior Emulation - Defeats reCAPTCHA v3 & Shannon Entropy Analysis
#
# Purpose: Single Responsibility - Add realistic human patterns to bot behavior.
#
# How it works:
# - reCAPTCHA v3 calculates Shannon Entropy of user actions
# - Bots move smoothly (low entropy) = detected
# - Humans have jitters, pauses, micro-hesitations = high entropy
# - We inject Gaussian noise (micro-tremors) + random pauses (cognition)
#
# The Math:
# Shannon Entropy = -Σ p(x) * log(p(x))
# High entropy (many movement patterns) = looks human
# Low entropy (same patterns) = looks bot

import asyncio
import random
import math
from typing import Tuple, List


class HumanBiometrics:
    """
    Generate human-like interaction patterns.
    
    This defeats Shannon Entropy analysis by injecting realistic randomness
    into every action (mouse movement, typing speed, pause duration).
    """
    
    @staticmethod
    def gaussian_jitter(mean: float = 0, std_dev: float = 0.02) -> float:
        """
        Generate Gaussian random noise (micro-tremors).
        
        Simulates tiny involuntary hand movements humans make while interacting.
        Uses standard normal distribution for realistic variation.
        
        Args:
            mean: Center of distribution
            std_dev: Standard deviation (controls jitter magnitude)
        
        Returns:
            Random jitter value
        """
        return random.gauss(mean, std_dev)
    
    @staticmethod
    def cognitive_pause(min_sec: float = 0.5, max_sec: float = 3.0) -> float:
        """
        Generate a "thinking pause" duration.
        
        Humans pause to read/process content. Bots don't.
        Uses triangular distribution (peaks at 1-2 seconds, realistic).
        
        Args:
            min_sec: Minimum pause
            max_sec: Maximum pause
        
        Returns:
            Pause duration in seconds
        """
        # Triangular distribution: more pauses at 1-2s (realistic reading time)
        return random.triangular(min_sec, max_sec, (min_sec + max_sec) / 2)
    
    @staticmethod
    def typing_delay(min_ms: float = 30, max_ms: float = 150, 
                     burst_chance: float = 0.2) -> float:
        """
        Generate realistic typing delay between keystrokes.
        
        Humans don't type at constant speed. They have bursts (fast) and pauses (slow).
        
        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
            burst_chance: Probability of fast typing burst
        
        Returns:
            Delay in seconds
        """
        if random.random() < burst_chance:
            # Fast burst: 20-50ms per key
            delay_ms = random.uniform(20, 50)
        else:
            # Normal typing: min_ms to max_ms
            delay_ms = random.uniform(min_ms, max_ms)
        
        return delay_ms / 1000.0
    
    @staticmethod
    def mouse_movement_path(start: Tuple[int, int], 
                           end: Tuple[int, int], 
                           num_points: int = 10) -> List[Tuple[int, int]]:
        """
        Generate a human-like curved mouse path with jitter.
        
        Humans don't move mice in straight lines - they use curved paths
        with micro-tremors (Gaussian jitter).
        
        Args:
            start: Starting (x, y) coordinates
            end: Ending (x, y) coordinates
            num_points: Number of path points to generate
        
        Returns:
            List of (x, y) coordinates forming curved path
        """
        path = []
        start_x, start_y = start
        end_x, end_y = end
        
        for i in range(num_points):
            # Linear interpolation (0 to 1)
            t = i / (num_points - 1) if num_points > 1 else 0
            
            # Bezier curve (quadratic, for natural curves)
            # Add control point above the line for realistic curve
            control_x = (start_x + end_x) / 2 + random.uniform(-50, 50)
            control_y = (start_y + end_y) / 2 - random.uniform(20, 100)
            
            # Quadratic Bezier formula
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * end_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * end_y
            
            # Add Gaussian jitter (micro-tremors)
            x += HumanBiometrics.gaussian_jitter(0, 2)
            y += HumanBiometrics.gaussian_jitter(0, 2)
            
            path.append((int(x), int(y)))
        
        return path
    
    @staticmethod
    async def human_like_action(action_name: str, 
                               min_pause: float = 0.3, 
                               max_pause: float = 1.5) -> None:
        """
        Execute any action with pre and post human-like delays.
        
        Args:
            action_name: Description of action (for logging)
            min_pause: Minimum pause before action
            max_pause: Maximum pause after action
        """
        # Pre-action cognitive pause
        pre_pause = random.uniform(min_pause, max_pause)
        await asyncio.sleep(pre_pause)
        
        # Post-action pause (shorter)
        post_pause = random.uniform(min_pause / 2, max_pause / 2)
        await asyncio.sleep(post_pause)
    
    @staticmethod
    def shannon_entropy_variation(num_samples: int = 5) -> List[float]:
        """
        Generate varied delays to increase Shannon Entropy.
        
        Higher entropy = looks more human to ML models.
        Returns a list of delays with natural distribution.
        
        Args:
            num_samples: Number of delay samples
        
        Returns:
            List of delays with high entropy
        """
        # Generate delays with high variance (high entropy)
        delays = [
            random.uniform(0.1, 0.2),
            random.uniform(0.5, 1.5),
            random.uniform(0.05, 0.1),
            random.uniform(1.0, 3.0),
            random.uniform(0.2, 0.5),
        ]
        random.shuffle(delays)
        return delays[:num_samples]
