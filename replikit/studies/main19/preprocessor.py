import os
import shutil
from typing import Any

from git import Repo

from base.preprocessor import StudyPreprocessor


class Preprocessor(StudyPreprocessor):

    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        super()._configure()
        self.repl_package_path = self.study_dir / self.config['source_dir']
        self.reset = self.config.get('reset', False)

    def _download_source_files(self, reference: Any) -> Any:
        print("Downloading source files...")
        if self.reset:
            shutil.rmtree(self.repl_package_path)
        if not os.path.exists(self.repl_package_path):
            os.makedirs(self.repl_package_path)
            Repo.clone_from(reference, self.repl_package_path)

    def magic(self):
        print("Preprocessing everything...")
        self._download_source_files(self.config['source_files'])

