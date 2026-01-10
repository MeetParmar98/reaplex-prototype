from abc import ABC, abstractmethod
from typing import Dict, Any


class Executor(ABC):
    """
    Abstract base class for job executors.
    """

    @abstractmethod
    def run(self, payload: Dict[str, Any]) -> None:
        """
        Execute the job with the given payload.

        Args:
           payload (Dict[str, Any]): The job data.
        """
        pass


class DummyExecutor(Executor):
    """
    A dummy executor for testing purposes.
    """

    def run(self, payload: Dict[str, Any]) -> None:
        print(f"DummyExecutor: Processing {payload}")
