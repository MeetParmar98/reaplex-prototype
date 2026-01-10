import logging
import time
import signal
from typing import Callable, Dict, Any, Optional

# Adjust import based on your project structure
try:
    from src.queue.queue import Queue
except ImportError:
    import sys, os

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.queue.queue import Queue

logger = logging.getLogger(__name__)


class Worker:
    """
    Generic Redis-backed Queue Worker.

    Responsibilities:
    - Poll the Queue for jobs
    - Execute a handler on job payload
    - Mark jobs success/failure in the Queue
    - Gracefully handle shutdown signals
    """

    def __init__(
        self,
        queue: Queue,
        handler: Callable[[Dict[str, Any]], None],
        poll_interval: float = 0.1,
    ):
        """
        Initialize the Worker.

        Args:
            queue (Queue): The Queue instance to poll.
            handler (Callable): A function or Executor.run that processes job payloads.
            poll_interval (float): Sleep duration when queue is empty.
        """
        self.queue = queue
        self.handler = handler
        self.poll_interval = poll_interval
        self._running = False
        self._shutdown_requested = False

        # Hook signals for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info(f"Signal {signum} received. Stopping worker gracefully...")
        self.stop()

    def start(self, timeout: Optional[float] = None) -> None:
        """
        Start the Worker loop.

        Args:
            timeout (Optional[float]): Max duration to run the worker (seconds). None = infinite.
        """
        self._running = True
        self._shutdown_requested = False
        start_time = time.time()
        logger.info("Worker started. Polling queue...")

        while self._running:
            # Stop if timeout reached
            if timeout and (time.time() - start_time > timeout):
                logger.info("Worker timeout reached. Stopping.")
                break

            if self._shutdown_requested:
                break

            try:
                # Poll a job from the queue
                job = self.queue.dequeue(timeout=1)

                if job:
                    self._process_job(job)
                else:
                    # Queue empty; loop again after short sleep
                    time.sleep(self.poll_interval)

            except Exception as e:
                # Unexpected worker loop error
                logger.error(f"Unexpected error in worker loop: {e}", exc_info=True)
                time.sleep(1)

        logger.info("Worker stopped.")
        self._running = False

    def stop(self) -> None:
        """
        Request a graceful stop for the worker loop.
        """
        logger.info("Stopping worker...")
        self._shutdown_requested = True
        self._running = False

    def _process_job(self, job: Dict[str, Any]) -> None:
        """
        Internal method to execute a job payload and ack result.

        Args:
            job (Dict[str, Any]): Job dictionary from Queue (must have 'id' and 'payload')
        """
        job_id = job.get("id")
        payload = job.get("payload", {})

        if not job_id:
            logger.error(f"Invalid job structure received: {job}")
            return

        logger.info(f"Starting job {job_id}")

        try:
            # Execute the handler
            self.handler(payload)
            # Acknowledge success
            self.queue.ack_success(job_id)
            logger.info(f"Job {job_id} succeeded")
        except Exception as e:
            # Acknowledge failure with error info
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            self.queue.ack_failure(job_id, str(e))
