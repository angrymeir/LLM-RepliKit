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
        self.repl_package_path = self.study_dir / self.config['source_dir']
        self.reset = self.config.get('reset', False)

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
        if self.reset:
            shutil.rmtree(self.repl_package_path)
        if not os.path.exists(self.repl_package_path):
            os.makedirs(self.repl_package_path)
            Repo.clone_from(reference, self.repl_package_path)

    def _preprocess_source_files(self) -> Any:
        # create .env file
        env_file = self.repl_package_path / ".env"
        with open(env_file, 'w') as f:
            f.write("OPENAI_API_KEY={}".format(os.getenv("OPENAI_API_KEY")))

    def _prepare_environment(self, environment: Any) -> None:
        print("Building docker image...")
        client = docker.from_env()

        dockerfile_path = str(self.study_dir)

        try:
            if self.config.get('reset', False):
                client.images.build(path=dockerfile_path, tag="009:latest", nocache=True)
                print("Docker image built successfully!")
            # if image doesn't exist, build it
            elif "009:latest" not in [img.tags for img in client.images.list()]:
                client.images.build(path=dockerfile_path, tag="009:latest", nocache=True)
        except docker.errors.BuildError as e:
            print("Build failed:", e)
        except Exception as e:
            print("Error:", e)
        print("Docker image built successfully!")  
