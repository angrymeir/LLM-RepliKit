from time import sleep

from dotenv import load_dotenv
from base.runner import StudyRunner
import docker
import os
import sys
import shutil
from kubernetes import client as kclient
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

            docker_client = docker.from_env()
            container = docker_client.containers.create(
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
            # kconfig.load_kube_config() # use on local machines only with KUBECONFIG set
            kconfig.load_incluster_config()  # for use with ServiceAccounts
            namespace = os.getenv("MY_POD_NAMESPACE")

            # Set up job name and image
            job_name = f"study-replication-job-{run_number}"
            image = self.config["docker_image_name"]

            # Define the Job spec
            job = kclient.V1Job(
                metadata=kclient.V1ObjectMeta(name=job_name),
                spec=kclient.V1JobSpec(
                    template=kclient.V1PodTemplateSpec(
                        spec=kclient.V1PodSpec(
                            image_pull_secrets=[kclient.V1LocalObjectReference(name="replikit-access")],
                            containers=[
                                kclient.V1Container(
                                    name="replication",
                                    image=image,
                                    tty=True,
                                    stdin=True,
                                    env_from=[
                                      kclient.V1EnvFromSource(
                                          secret_ref=kclient.V1SecretEnvSource(name="openai-access")
                                      )
                                    ],
                                    volume_mounts=[
                                        kclient.V1VolumeMount(
                                            name="output-volume",
                                            mount_path="/experiment/output"
                                        )
                                    ]
                                )
                            ],
                            restart_policy="Never",
                            volumes=[
                                kclient.V1Volume(
                                    name="output-volume",
                                    #  manually created pvc
                                    persistent_volume_claim=kclient.V1PersistentVolumeClaimVolumeSource(
                                        claim_name="exp-002-evidence")
                                )
                            ]
                        )
                    ),
                    backoff_limit=1
                )
            )

            # Create the Job
            batch_v1 = kclient.BatchV1Api()
            api_response = batch_v1.create_namespaced_job(
                body=job,
                namespace=namespace
            )
            print(f"Job {job_name} submitted.")

            # Stream logs (optional)
            core_v1 = kclient.CoreV1Api()
            pod_list = core_v1.list_namespaced_pod(namespace=namespace, label_selector=f"job-name={job_name}")
            while not pod_list.items:
                pod_list = core_v1.list_namespaced_pod(namespace=namespace, label_selector=f"job-name={job_name}")

            pod_name = pod_list.items[0].metadata.name
            log_stream = None
            retries = 0
            while not log_stream and retries < 10:
                try:
                    log_stream = core_v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, follow=True, _preload_content=False)
                except kclient.exceptions.ApiException:  # Exception if Container is still creating
                    retries += 1
                    if retries >= 10:
                        raise

                    sleep(5)

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