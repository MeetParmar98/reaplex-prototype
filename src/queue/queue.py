import json
import time
import hashlib
import logging
from typing import Any, Dict, Optional

from redis import Redis

from .models import Job
from .redis_keys import QueueKeys

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
POLL_INTERVAL = 0.1


class Queue:
    """
    Redis-backed job queue.

    Design rules:
    - Owns STATE, not LOGIC
    - Payload is opaque
    - Guarantees at-least-once delivery
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    # ------------------------------------------------------------------
    # ENQUEUE
    # ------------------------------------------------------------------

    def enqueue(self, payload: Dict[str, Any]) -> bool:
        """
        Enqueue a new job.

        Returns:
            True  -> job enqueued
            False -> duplicate detected
        """
        payload_hash = self._hash_payload(payload)
        job = Job(payload=payload)

        lua = """
        if redis.call("SADD", KEYS[1], ARGV[1]) == 1 then
            redis.call("LPUSH", KEYS[2], ARGV[2])
            return 1
        else
            return 0
        end
        """

        result = self.redis.eval(
            lua,
            2,
            QueueKeys.SEEN,
            QueueKeys.PENDING,
            payload_hash,
            job.to_json(),
        )

        return bool(result)

    # ------------------------------------------------------------------
    # DEQUEUE
    # ------------------------------------------------------------------

    def dequeue(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Fetch a job from the queue.

        This is a safe polling dequeue:
        - Atomic transfer PENDING → PROCESSING
        - No job loss on crash
        """
        deadline = time.time() + timeout

        while time.time() < deadline:
            job = self._dequeue_once()
            if job:
                return job

            time.sleep(POLL_INTERVAL)

        return None

    def _dequeue_once(self) -> Optional[Dict[str, Any]]:
        """
        Single atomic dequeue attempt.
        """
        lua = """
        local raw = redis.call("RPOP", KEYS[1])
        if not raw then return nil end

        local job = cjson.decode(raw)
        job.started_at = tonumber(ARGV[1])

        local updated = cjson.encode(job)
        redis.call("HSET", KEYS[2], job.id, updated)

        return updated
        """

        raw = self.redis.eval(
            lua,
            2,
            QueueKeys.PENDING,
            QueueKeys.PROCESSING,
            time.time(),
        )

        return json.loads(raw) if raw else None

    # ------------------------------------------------------------------
    # ACKNOWLEDGEMENT
    # ------------------------------------------------------------------

    def ack_success(self, job_id: str) -> None:
        """
        Mark job as completed.

        NOTE:
        - This guarantees at-least-once delivery
        - If the job was already requeued, it may still run again
        """
        pipe = self.redis.pipeline()
        pipe.hdel(QueueKeys.PROCESSING, job_id)
        pipe.sadd(QueueKeys.DONE, job_id)
        pipe.execute()

    def ack_failure(self, job_id: str, error: str) -> None:
        """
        Permanently fail a job.
        """
        lua = """
        local raw = redis.call("HGET", KEYS[1], ARGV[1])
        if not raw then return 0 end

        local job = cjson.decode(raw)
        job.error = ARGV[2]
        job.failed_at = tonumber(ARGV[3])

        redis.call("HSET", KEYS[2], ARGV[1], cjson.encode(job))
        redis.call("HDEL", KEYS[1], ARGV[1])

        return 1
        """

        self.redis.eval(
            lua,
            2,
            QueueKeys.PROCESSING,
            QueueKeys.FAILED,
            job_id,
            error,
            time.time(),
        )

    # ------------------------------------------------------------------
    # STALE REQUEUE
    # ------------------------------------------------------------------

    def requeue_stale(self, timeout: int) -> int:
        """
        Requeue jobs stuck in PROCESSING longer than timeout.
        """
        moved = 0
        cursor = 0

        while True:
            cursor, entries = self.redis.hscan(
                QueueKeys.PROCESSING, cursor=cursor, count=100
            )

            for job_id in entries.keys():
                if self._requeue_one(job_id, timeout):
                    moved += 1

            if cursor == 0:
                break

        return moved

    def _requeue_one(self, job_id: bytes, timeout: int) -> bool:
        """
        Atomically requeue or fail a single stale job.
        """
        lua = """
        local raw = redis.call("HGET", KEYS[1], ARGV[1])
        if not raw then return 0 end

        local job = cjson.decode(raw)
        local started = job.started_at or 0

        if (ARGV[2] - started) <= ARGV[3] then
            return 0
        end

        job.attempts = (job.attempts or 0) + 1
        job.started_at = nil

        if job.attempts < ARGV[4] then
            redis.call("LPUSH", KEYS[2], cjson.encode(job))
        else
            job.error = "Timeout: max attempts exceeded"
            job.failed_at = tonumber(ARGV[2])
            redis.call("HSET", KEYS[3], job.id, cjson.encode(job))
        end

        redis.call("HDEL", KEYS[1], ARGV[1])
        return 1
        """

        return bool(
            self.redis.eval(
                lua,
                3,
                QueueKeys.PROCESSING,
                QueueKeys.PENDING,
                QueueKeys.FAILED,
                job_id,
                time.time(),
                timeout,
                MAX_ATTEMPTS,
            )
        )

    # ------------------------------------------------------------------
    # STATS
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, int]:
        """Return current queue stats."""
        pipe = self.redis.pipeline()
        pipe.scard(QueueKeys.SEEN)
        pipe.llen(QueueKeys.PENDING)
        pipe.hlen(QueueKeys.PROCESSING)
        pipe.scard(QueueKeys.DONE)
        pipe.hlen(QueueKeys.FAILED)

        seen, pending, processing, done, failed = pipe.execute()

        return {
            "seen": seen,
            "pending": pending,
            "processing": processing,
            "done": done,
            "failed": failed,
        }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_payload(payload: Dict[str, Any]) -> str:
        """Stable hash used for deduplication."""
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()
