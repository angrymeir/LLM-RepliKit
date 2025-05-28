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
        client = docker.from_env()

        container = client.containers.create(
            image=self.config['docker_image_name'],
            working_dir="/replicationpackage",
            command="bash entrypoint.sh",
            volumes={
                "/tmp/{}".format(
                    self.config['description'].lower().replace(" ", "").replace(".", "-").replace(":", "-")
                ): {'bind': '/tmp', 'mode': 'rw'}
            },
            tty=True,
            stdin_open=True,
            detach=True
        )

        container.start()

        log_stream = container.logs(stream=True, stdout=True, stderr=True)

        for chunk in log_stream:
            sys.stdout.write(chunk.decode())
            sys.stdout.flush()
        
    def save_evidence(self, run_number):
        tmp_evidence_dir = "/tmp/{}/fix_reports".format(
            self.config['description'].lower().replace(" ", "").replace(".", "-").replace(":", "-")
        )
        # get this files parent directory
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, 'evidence/{}'.format(
            run_number
        ))
        os.makedirs(evidence_dir, exist_ok=True)
        # copy the evidence from the container to the evidence directory
        shutil.copytree(tmp_evidence_dir, evidence_dir, dirs_exist_ok=True)