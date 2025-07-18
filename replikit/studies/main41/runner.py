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
        self.tmp_evidence_dir = "/tmp/" + self.config['description'].lower().replace(" ", "").replace(".", "-").replace(":", "-")

    def get_tmp_evidence_dir(self,  run_number) -> str:
        return self.tmp_evidence_dir + "/" + str(run_number)

    def run(self, run_number):
        print("Running the study replication package...", run_number)
        # docker run
        client = docker.from_env()
        local_path = self.get_tmp_evidence_dir(run_number)
        os.makedirs(local_path, exist_ok=True)
        container_path = "/tmp/evidence"

        if not os.environ.get("OPENAI_API_KEY"):
            print("Warning: OpenAI API key not set")

        container = client.containers.create(
            image=self.config['docker_image_name'],
            command="bash entrypoint.sh",
            environment = {"OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
                           "EVIDENCE_DIR": container_path},
            volumes={
                local_path: {'bind': container_path, 'mode': 'rw'}
            },
            tty=True,
            stdin_open=True,
            detach=True
        )

        container.start()
        container.wait()

    def save_evidence(self, run_number):
        tmp_evidence_dir = self.get_tmp_evidence_dir(run_number)
        # get this files parent directory
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, 'evidence/{}'.format(
            run_number
        ))
        os.makedirs(evidence_dir, exist_ok=True)
        # copy the evidence from the container to the evidence directory
        shutil.copytree(tmp_evidence_dir, evidence_dir, dirs_exist_ok=True)