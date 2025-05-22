from typing import Any
from base.preprocessor import StudyPreprocessor
import os
import shutil

class Preprocessor(StudyPreprocessor):
    
    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        super()._configure()
        self.repl_package_path = self.study_dir / self.config['source_dir']
        self.reset = self.config.get('reset', False)

    def magic(self):
        self._download_source_files(self.config['source_files'])
        print("Preprocessing everthing...")

    def _load_data(self, reference: Any) -> Any:
        pass

    def _process_data(self, data: Any) -> Any:
        return super()._process_data(data)
    
    def _download_source_files(self, reference: Any) -> Any:
        if self.reset:
            shutil.rmtree(self.repl_package_path)
        if not os.path.exists(self.repl_package_path):
            os.makedirs(self.repl_package_path)

        # TODO: download the source files from the reference URL

    def _preprocess_source_files(self, source_files: Any) -> Any:
        pass
    
    def _prepare_environment(self, environment: Any) -> None:
        pass