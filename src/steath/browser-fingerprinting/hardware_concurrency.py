# hardware_concurrency.py
import random

# Realistic hardware concurrency values by device type
HARDWARE_CONCURRENCY = {
    "mobile": [2, 4, 6, 8],
    "laptop": [4, 8],
    "desktop": [8, 12, 16],
}


def get_hardware_concurrency(device_type="desktop"):
    """
    Returns a realistic hardwareConcurrency value based on device type.

    device_type: 'mobile', 'laptop', or 'desktop'
    """
    values = HARDWARE_CONCURRENCY.get(device_type, HARDWARE_CONCURRENCY["desktop"])
    return random.choice(values)
