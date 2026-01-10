import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Job:
    """
    Represents a unit of work.

    IMPORTANT:
    - payload is completely opaque to the queue
    - the queue never inspects payload contents
    """

    payload: Dict[str, Any]

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

    # Retry / execution tracking
    attempts: int = 0
    started_at: Optional[float] = None

    # Failure metadata (only set when permanently failed)
    error: Optional[str] = None
    failed_at: Optional[float] = None

    def to_json(self) -> str:
        """Serialize job to JSON for Redis storage."""
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, raw: str) -> "Job":
        """Deserialize job from Redis JSON."""
        return cls(**json.loads(raw))
