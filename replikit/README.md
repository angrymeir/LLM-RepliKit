# LLM-RepliKit

RepliKit is a framework to reproduce experimental software studies.
It is built to reproduce LLM studies, but can also be employed for other experimental software studies.

## Pre-requisites

This project used [UV](https://docs.astral.sh/uv/) as a package manger and requires Python 3.11 or later to run.

To install UV, you can use the following command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

To install the dependencies required to run RepliKit, run:

```bash
uv sync
```

## Project structure

The relevant files and directories in the project structure are:

```plaintext
replikit/
├── README.md
├── base/               <-- Base classes of RepliKit
├── configs/global.yaml <-- Configuration of studies
├── evidence/           <-- Store results here
├── studies/            <-- Setup to replicate studies
│   └── study01/        <-- Specific study
```

## Run RepliKit

To run RepliKit, you can use the following command:

```bash
uv run main.py --study <STUDY_ID> --test <TESTREPETITIONS> --reset
```

## Add a new study to RepliKit

To add a new study to RepliKit, you can follow these steps:

1. Extend the global configuration file `configs/global.yaml` with the new study ID.
2. Create a new directory in `studies/` with the study ID.
3. Copy the template files `studies/template/` into the new study directory.
4. Implement the study-specific logic for `preprocessor.py`, `runner.py`, and `postprocessor.py`.

We recommend to create a Dockerfile for each study to ensure a consistent environment for running the study.

## Credentials

> [!warning]
> The OpenAI API key belongs in a local environment variable, not in our code
