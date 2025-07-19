# Study Main41

**Title:** Automatic Semantic Augmentation of Language Model Prompts (for Code Summarization)

## Can we reproduce the results?

Answer: No

## How to run the study?

1. Set the environment variable `OPENAI_API_KEY` to your OpenAI API key
2. Run `uv run main.py --study main41`

## Changes

### Requirements.txt

- In the original artefact, dependencies are not specified. We recovered working dependencies for the study original artefact.

### Implemented in entrypoint.sh

- Restrict experiment to the gpt-3.5-turbo model
- Pipeline to run experiments automatically
- Copy output files to /workspace/output for archiving
