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
        self.tmp_evidence_dir = "/tmp/{}/".format(self.config['description'].lower().replace(" ", "").replace(".", "-").replace(":", "-"))
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
            print("Skipping run {}: evidence already exists".format(run_number))
            return
        
        print("Running the study replication package...", run_number)
        # docker run
        client = docker.from_env()

        container = client.containers.create(
            image=self.config['docker_image_name'],
            command="bash -c './run_automated_assessments.sh && python3.11 convert_results.py && cd expert_vs_gpt_vs_doxpy/code/data_analysis/experts_vs_tools && ../../../../.env/bin/python data_analysis.py'", 
            volumes={
                self.tmp_evidence_dir + "marketplaces": {'bind': '/usr/src/app/expert_vs_gpt_vs_doxpy/code/gpt_based_approach/marketplaces/results', 'mode': 'rw'},
                self.tmp_evidence_dir + "searchengines": {'bind': '/usr/src/app/expert_vs_gpt_vs_doxpy/code/gpt_based_approach/search_engines/results', 'mode': 'rw'},
            },
            tty=True,
            stdin_open=True,
            detach=True
        )

        container.start()

        log_stream = container.logs(stream=True, stdout=True, stderr=True)

        with open(self.tmp_evidence_dir + "container_logs.txt", "w") as log_file:
            for chunk in log_stream:
                decoded = chunk.decode()
                sys.stdout.write(decoded)
                sys.stdout.flush()
                log_file.write(decoded)
                log_file.flush()
        
    def save_evidence(self, run_number):
        if self._skip_run(run_number):
            return
        e_dir = os.path.join(self.evidence_dir, "{}".format(run_number))
        e_dir_ma = os.path.join(self.evidence_dir, "{}".format(run_number), "marketplaces")
        e_dir_se = os.path.join(self.evidence_dir, "{}".format(run_number), "searchengines")
        os.makedirs(e_dir, exist_ok=True)
        os.makedirs(e_dir_ma, exist_ok=True)
        os.makedirs(e_dir_se, exist_ok=True)
        shutil.copytree(self.tmp_evidence_dir + "marketplaces/gpt4/", e_dir_ma, dirs_exist_ok=True)
        shutil.copytree(self.tmp_evidence_dir + "searchengines/gpt4/", e_dir_se, dirs_exist_ok=True)
        shutil.copy(self.tmp_evidence_dir + "container_logs.txt", e_dir)
        shutil.rmtree(self.tmp_evidence_dir, ignore_errors=True)