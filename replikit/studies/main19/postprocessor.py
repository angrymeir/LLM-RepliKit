from base.postprocessor import StudyPostprocessor

class PostProcessor(StudyPostprocessor):

    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        pass

    def postprocess(self):
        print("Postprocessing everthing...")