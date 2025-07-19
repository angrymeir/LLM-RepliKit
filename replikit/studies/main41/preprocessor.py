from typing import Any
from base.preprocessor import StudyPreprocessor
import os
import shutil
from git import Repo
import docker


class Preprocessor(StudyPreprocessor):

    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        super()._configure()

    def magic(self):
        self._download_source_files(self.config['source_files'])
        self._preprocess_source_files()
        self._prepare_environment("")
        print("Preprocessing everything...")

    def _load_data(self, reference: Any) -> Any:
        pass

    def _process_data(self, data: Any) -> Any:
        pass

    def _download_source_files(self, reference: Any) -> Any:
        pass

    def _preprocess_source_files(self, **kwargs) -> Any:
        pass

    def _prepare_environment(self, environment: Any) -> None:
        print("Building docker image...")
        client = docker.from_env()

        dockerfile_path = str(self.study_dir)

        try:
            if self.config.get('reset', False):
                client.images.build(path=dockerfile_path, tag=self.config["docker_image_name"], nocache=True)
                print("Docker image built successfully!")
        except docker.errors.BuildError as e:
            print("Build failed:", e)
        except Exception as e:
            print("Error:", e)
        print("Docker image built successfully!")
