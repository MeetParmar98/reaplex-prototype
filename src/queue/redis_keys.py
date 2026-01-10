from enum import Enum


class QueueKeys(str, Enum):
    """
    Centralized Redis key names.

    This file is the single source of truth for all Redis structures.
    """

    SEEN = "queue:seen"  # SET   → deduplication
    PENDING = "queue:pending"  # LIST  → waiting jobs
    PROCESSING = "queue:processing"  # HASH → active jobs
    DONE = "queue:done"  # SET   → completed job ids
    FAILED = "queue:failed"  # HASH  → permanently failed jobs
