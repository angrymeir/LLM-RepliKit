# Study ASE Main5

**Title:** Demonstration-Free: Towards More Practical Log Parsing with Large Language Models

## Can we reproduce the results?

Answer: Partially

## How to run the study?

1. Set the environment variable `OPENAI_API_KEY` to your OpenAI API key
2. Run `uv run main.py --study 005`

## Changes

### Implemented in Dockerfile

- Inject OpenAI API automatically via config.json

### Implemented in runner.py

- Restrict experiment to the 2k dataset, as docker container lacks dependencies to download other dataset
- Only perform experiment for the gpt-3.5-turbo-0125 model
