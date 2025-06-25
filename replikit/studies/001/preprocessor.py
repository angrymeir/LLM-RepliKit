from base.preprocessor import StudyPreprocessor


class Preprocessor(StudyPreprocessor):

    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        pass

    def magic(self):
        print("Preprocessing everything...")

