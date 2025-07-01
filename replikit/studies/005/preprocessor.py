from base.preprocessor import StudyPreprocessor
import requests
import docker
import os


class Preprocessor(StudyPreprocessor):

    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        super()._configure()
        self.repl_package_path = self.study_dir / self.config['source_dir']
        self.reset = self.config.get('reset', False)

    def magic(self):
        print("Preprocessing everything...")
        self._download_source_files(None)
        self._prepare_environment(None)

    def _download_source_files(self, reference):
        url = "https://zenodo.org/records/13752709/files/logbatcher.tar?download=1"
        filename = "logbatcher.tar"
        filepath = self.study_dir / filename
        
        if filepath.exists():
            print(f"Source file {filename} already exists, skipping download")
        else:
            print(f"Downloading {filename} from Zenodo...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            print(f"Downloaded {filename} successfully")
        
        # Load the tar file into Docker
        print(f"Loading {filename} into Docker...")
        client = docker.from_env()
        
        with open(filepath, 'rb') as f:
            images = client.images.load(f.read())
            
        if images:
            print(f"Successfully loaded Docker image from {filename}")
            for image in images:
                print(f"Loaded image: {image.id}")
        else:
            raise RuntimeError(f"Failed to load Docker image from {filename}")
            
        # Download the config to fill in the API key
        url = "https://raw.githubusercontent.com/LogIntelligence/LogBatcher/refs/heads/master/config.json"
        filename = "config.json"
        filepath = self.study_dir / filename
        
        if filepath.exists():
            print(f"Source file {filename} already exists, skipping download")
        else:
            print(f"Downloading {filename} from GitHub...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            print(f"Downloaded {filename} successfully")
        return images

    def _prepare_environment(self, environment):
        print("Building docker image...")
        client = docker.from_env()

        with open(self.study_dir / "config.json", 'r') as f:
            config = f.read()
            config = config.replace("'<OpenAI_API_KEY>", os.getenv("OPENAI_API_KEY"))

        with open(self.study_dir / "config.json", 'w') as f:    
            f.write(config)

        dockerfile_path = str(self.study_dir)

        try:
            if self.config.get('reset', False):
                client.images.build(path=dockerfile_path, tag="005:latest", nocache=True)
                print("Docker image built successfully!")
            # if image doesn't exist, build it
            elif "005:latest" not in [img.tags for img in client.images.list()]:
                client.images.build(path=dockerfile_path, tag="005:latest", nocache=True)
        except docker.errors.BuildError as e:
            print("Build failed:", e)
        except Exception as e:
            print("Error:", e)
        print("Docker image built successfully!")

