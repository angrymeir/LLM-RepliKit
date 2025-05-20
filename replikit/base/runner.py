from typing import Any

class StudyRunner:
    """
    Base class for running the study replication package.

    This class defines the interface for executing a study run
    and saving evidence from that run. Subclasses should provide
    implementations for the abstract methods.
    """

    def run(self, run_number: int) -> None:
        """
        Execute a single run of the study replication package.

        Args:
            run_number (int): The index or identifier of the current run.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def save_evidence(self, run_number: int) -> None:
        """
        Save the evidence generated during a single run.

        Args:
            run_number (int): The index or identifier of the run for which to save evidence.
        """
        raise NotImplementedError("This method should be overridden by subclasses")