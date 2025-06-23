from typing import Any
from base.preprocessor import StudyPreprocessor
import os
import docker


class Preprocessor(StudyPreprocessor):
    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        super()._configure()
        self.repl_package_path = self.study_dir / self.config["source_dir"]
        self.reset = self.config.get("reset", False)

    def magic(self):
        if not self.config.get("use_kubernetes", False):
            self._prepare_environment("")
        print("Preprocessing everything...")

    def _load_data(self, reference: Any) -> Any:
        pass

    def _process_data(self, data: Any) -> Any:
        pass

    def _preprocess_source_files(self) -> Any:
        pass

    def _prepare_environment(self, environment: Any) -> None:
        print("Building docker image...")
        client = docker.from_env()

        dockerfile_path = str(self.study_dir)

        try:
            if self.config.get("reset", False):
                client.images.build(
                    path=dockerfile_path, tag="002:latest", nocache=True
                )
            elif "002:latest" not in [tag for img in client.images.list() for tag in img.tags]:
                client.images.build(path=dockerfile_path, tag="002:latest", nocache=True)
                print("Docker image built successfully!")
        except docker.errors.BuildError as e:
            print("Build failed:", e)
        except Exception as e:
            print("Error:", e)
        print("Docker image built successfully!")
