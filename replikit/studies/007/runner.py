from dotenv import load_dotenv
from base.runner import StudyRunner
import docker
import os
import sys
import shutil


class Runner(StudyRunner):
    """
    Base class for running the study replication package.
    """

    def __init__(self, config):
        self.config = config
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        self.tmp_evidence_dir = "tmp/{}".format(
            self.config['description'].lower().replace(" ", "").replace(".", "-").replace(":", "-")
        )
        self.evidence_dir = os.path.join(parent_dir, 'evidence')
        self.tmp_evidence_dir = os.path.join(parent_dir, self.tmp_evidence_dir)
        print("Temporary evidence directory:", self.tmp_evidence_dir)
        print("Evidence directory:", self.evidence_dir)
        if self.config.get('reset', False):
            shutil.rmtree(self.tmp_evidence_dir, ignore_errors=True)
            shutil.rmtree(self.evidence_dir, ignore_errors=True)
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
        # docker run
        client = docker.from_env()
        load_dotenv()
        container = client.containers.create(
            image=self.config["docker_image_name"],
            working_dir="/app",
            command="./run_scripts.sh",
            volumes={self.tmp_evidence_dir: {"bind": "/app/generated_results", "mode": "rw"}}, # TODO change back to generated_results
            environment={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")},
            tty=True,
            stdin_open=True,
            detach=True,
        )

        container.start()
        try:
            log_stream = container.logs(stream=True, stdout=True, stderr=True)
            for chunk in log_stream:
                try:
                    sys.stdout.write(chunk.decode(errors='replace'))
                    sys.stdout.flush()
                except Exception as decode_error:
                    print(f"[Warning] Log chunk decode error: {decode_error}")
                    continue
        except Exception as stream_error:
            print(f"[Warning] Error while accessing log stream: {stream_error}")
            print("Continuing... container is still running.")

    def save_evidence(self, run_number):
        if self._skip_run(run_number):
            return
        e_dir = os.path.join(self.evidence_dir, "{}".format(run_number))
        os.makedirs(e_dir, exist_ok=True)
        # copy the evidence from the container to the evidence directory
        shutil.copytree(self.tmp_evidence_dir, e_dir, dirs_exist_ok=True)
