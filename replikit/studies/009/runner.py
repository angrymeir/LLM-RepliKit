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
        self.tmp_evidence_dir = "/tmp/{}/fix_reports".format(
            self.config['description'].lower().replace(" ", "").replace(".", "-").replace(":", "-")
        )
        self.evidence_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evidence')
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

        container.stop()
        client.containers.prune()
        
    def save_evidence(self, run_number):

        if self._skip_run(run_number):
            return
        # get this files parent directory
        e_dir = os.path.join(self.evidence_dir, '{}'.format(
            run_number
        ))
        os.makedirs(e_dir, exist_ok=True)
        # copy the evidence from the container to the evidence directory
        shutil.copytree(self.tmp_evidence_dir, e_dir, dirs_exist_ok=True)
        # delete the tmp_evidence_dir
        shutil.rmtree(self.tmp_evidence_dir, ignore_errors=True)