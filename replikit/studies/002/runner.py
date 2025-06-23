from dotenv import load_dotenv
from base.runner import StudyRunner
import docker
import os
import sys
import shutil
from kubernetes import client
from kubernetes import config as kconfig




class Runner(StudyRunner):
    """
    Base class for running the study replication package.
    """

    # def __init__(self, config):
    #     self.config = config

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

        # parent_dir = os.path.dirname(os.path.abspath(__file__))
        # host_dir = "tmp/{}".format(
        #     self.config["description"]
        #     .lower()
        #     .replace(" ", "")
        #     .replace(".", "-")
        #     .replace(":", "-")
        # )

        load_dotenv()

        if not self.config.get("use_kubernetes", False):

            client = docker.from_env()
            container = client.containers.create(
                image=self.config["docker_image_name"],
                volumes={self.tmp_evidence_dir: {"bind": "/workspace/output", "mode": "rw"}},
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
        else:
            kconfig.load_kube_config()
            openai_key = os.getenv("OPENAI_API_KEY")

            # Set up job name and image
            job_name = f"study-replication-job-{run_number}"
            image = self.config["docker_image_name"]

            # Define the Job spec
            job = client.V1Job(
                metadata=client.V1ObjectMeta(name=job_name),
                spec=client.V1JobSpec(
                    template=client.V1PodTemplateSpec(
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="replication",
                                    image=image,
                                    tty=True,
                                    stdin=True,
                                    env=[
                                        client.V1EnvVar(name="OPENAI_API_KEY", value=openai_key)
                                    ],
                                    volume_mounts=[
                                        client.V1VolumeMount(
                                            name="output-volume",
                                            mount_path="/workspace/output"
                                        )
                                    ]
                                )
                            ],
                            restart_policy="Never",
                            volumes=[
                                client.V1Volume(
                                    name="output-volume",
                                    host_path=client.V1HostPathVolumeSource(
                                        path=self.tmp_evidence_dir,
                                        type="DirectoryOrCreate"
                                    )
                                )
                            ]
                        )
                    ),
                    backoff_limit=1
                )
            )

            # Create the Job
            batch_v1 = client.BatchV1Api()
            api_response = batch_v1.create_namespaced_job(
                body=job,
                namespace="default"
            )
            print(f"Job {job_name} submitted.")

            # Stream logs (optional)
            core_v1 = client.CoreV1Api()
            pod_list = core_v1.list_namespaced_pod(namespace="default", label_selector=f"job-name={job_name}")
            while not pod_list.items:
                pod_list = core_v1.list_namespaced_pod(namespace="default", label_selector=f"job-name={job_name}")

            pod_name = pod_list.items[0].metadata.name
            log_stream = core_v1.read_namespaced_pod_log(name=pod_name, namespace="default", follow=True, _preload_content=False)
            for line in log_stream:
                try:
                    sys.stdout.write(line.decode("utf-8"))
                    sys.stdout.flush()
                except UnicodeDecodeError:
                    continue

    def save_evidence(self, run_number):
        if self._skip_run(run_number):
            return
        e_dir  = os.path.join(self.evidence_dir, "{}".format(run_number))
        os.makedirs(e_dir , exist_ok=True)
        # copy the evidence from the container to the evidence directory
        shutil.copytree(self.tmp_evidence_dir, e_dir , dirs_exist_ok=True)