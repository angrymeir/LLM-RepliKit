import docker
import os
import shutil
from base.runner import StudyRunner


class Runner(StudyRunner):
    """
    Base class for running the study replication package.
    """
    def __init__(self, config):
        self.config = config
        self.tmp_evidence_dir = "/tmp/{}".format(
            self.config['description'].lower().replace(" ", "").replace(".", "-").replace(":", "-")
        )
        self.evidence_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evidence')
        
        if not os.path.exists(self.tmp_evidence_dir):
            os.makedirs(self.tmp_evidence_dir, exist_ok=True)

    def _skip_run(self, run_number):
        """
        Check if the run should be skipped based on the evidence directory.
        """
        return os.path.exists(os.path.join(self.evidence_dir, "{}".format(run_number)))

    def run(self, run_number):
        if self._skip_run(run_number):
            print("Skipping run {}: evidence already exists.".format(run_number))
            return
        print("Running the study replication package...", run_number)
        
        client = docker.from_env()
        
        container = client.containers.run(
            self.config['docker_image_name'],
            command=[
                "sh", "-c",
                "python benchmark.py --data_type 2k --model gpt-3.5-turbo-0125 && cd evaluation && python logbatcher_eval.py --config logbatcher_2k"
                ],
            volumes={
                self.tmp_evidence_dir: {
                    'bind': '/app/outputs/parser/logbatcher_2k', 
                    'mode': 'rw'
                }
            },
            detach=False,
            remove=True
        )

    def save_evidence(self, run_number):
        if self._skip_run(run_number):
            return

        print("Saving evidence...", run_number)
        
        evidence_run_dir = os.path.join(self.evidence_dir, f'{run_number}')
        os.makedirs(evidence_run_dir, exist_ok=True)
        
        if os.path.exists(self.tmp_evidence_dir) and os.listdir(self.tmp_evidence_dir):
            shutil.copytree(self.tmp_evidence_dir, evidence_run_dir, dirs_exist_ok=True)
            shutil.rmtree(self.tmp_evidence_dir, ignore_errors=True)