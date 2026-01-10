import logging
from typing import Dict

from .classifier import classify
from .executors import HtmlExecutor, BrowserExecutor
from src.worker.executor import Executor

logger = logging.getLogger(__name__)

# Pre-instantiate executors to avoid creating new instances per job
EXECUTORS: Dict[str, Executor] = {
    "html": HtmlExecutor(),
    "browser": BrowserExecutor(),
}


def job_handler(payload: Dict) -> None:
    """
    Main handler function for the Worker.

    Workflow:
    1. Classify payload
    2. Map classification to an executor
    3. Execute job via the executor
    4. Logs any skipped jobs or errors

    Args:
        payload (Dict): The job payload from the Queue
    """
    job_type = classify(payload)

    if job_type == "skip":
        logger.info(f"Handler: Skipping job. Payload: {payload}")
        return

    executor = EXECUTORS.get(job_type)
    if not executor:
        logger.error(
            f"Handler: Unknown job type '{job_type}' from classifier. Payload: {payload}"
        )
        return

    try:
        executor.run(payload)
    except Exception as e:
        # Worker will handle failure, but log details here
        logger.error(f"Handler: Error executing {job_type} job: {e}", exc_info=True)
        raise e
