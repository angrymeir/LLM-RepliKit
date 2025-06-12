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

    def run(self, run_number):
        print("Running the study replication package...", run_number)
        # docker run
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        host_dir = "tmp/{}".format(
            self.config["description"]
            .lower()
            .replace(" ", "")
            .replace(".", "-")
            .replace(":", "-")
        )

        host_dir = os.path.join(parent_dir, host_dir)
        os.makedirs(host_dir, exist_ok=True)
        client = docker.from_env()
        load_dotenv()
        container = client.containers.create(
            image=self.config["docker_image_name"],
            volumes={host_dir: {"bind": "/workspace/output", "mode": "rw"}},
            tty=True,
            stdin_open=True,
            detach=True,
            environment=["OPENAI_API_KEY={}".format(os.getenv("OPENAI_API_KEY"))],
        )

        container.start()

        log_stream = container.logs(stream=True, stdout=True, stderr=True)

        for chunk in log_stream:
            try:
                sys.stdout.write(chunk.decode())
                sys.stdout.flush()
            except UnicodeDecodeError:
                continue  # skip problematic chunks -> some prints were chinese in this study and caused problems

    def save_evidence(self, run_number):
        tmp_evidence_dir = "tmp/{}".format(
            self.config["description"]
            .lower()
            .replace(" ", "")
            .replace(".", "-")
            .replace(":", "-")
        )
        # get this files parent directory
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        tmp_evidence_dir = os.path.join(parent_dir, tmp_evidence_dir)
        evidence_dir = os.path.join(parent_dir, "evidence/{}".format(run_number))
        os.makedirs(evidence_dir, exist_ok=True)
        # copy the evidence from the container to the evidence directory
        shutil.copytree(tmp_evidence_dir, evidence_dir, dirs_exist_ok=True)
