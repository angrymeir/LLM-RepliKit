# LLM-RepliKit

RepliKit is a framework to reproduce experimental software studies.
It is built to reproduce LLM studies, but can also be employed for other experimental software studies.

## How to get started
- Under `studies` create a new directory (e.g. 002)
- Instantiate the preprocessor, runner, and postprocessor from `base`
- Configure the `global_config.yaml` to your liking
- Run `python3 main.py --study <yourstudy> --sample_estimation`
