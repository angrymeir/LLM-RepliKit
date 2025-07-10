from base.runner import StudyRunner

class Runner(StudyRunner):
    """
    Base class for running the study replication package.
    """

    def run(self, run_number):
        print("Running the study replication package...", run_number)
    
    def save_evidence(self, run_number):
        print("Saving evidence...", run_number)