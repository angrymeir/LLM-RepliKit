# Study nier7

**Title:** RegExEval: Evaluating Generated Regular Expressions and their Proneness to DoS Attacks

## Can we reproduce the results?

Answer: No, but we can run the study

## How to run the study?

1. Set the environment variable `OPENAI_API_KEY` to your OpenAI API key
2. Run `uv run main.py --study 002`

## Changes

### Implemented in Dockerfile

- Integration of external evaluation repositories (ReScue, ReDoSHunter) as not provided by original research artefact

### Implemented in run_pipeline.sh

- Inject OpenAI API automatically
- Restrict experiment to GPT-3.5 only
- Setup pipeline to run everything together
- Copies output files to /workspace/output for archiving
