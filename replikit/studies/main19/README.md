# Study main19

**Title:** Large Language Models are Few-Shot Summarizers: Multi-Intent Comment Generation via In-Context Learning

## Can we replicate the results?

Answer: No

## How to run the study?

Only the pre-processor script is runnable.

Either run the pre-processor script directly

```sh
python preprocess.py
```

or run the study via the RepliKit CLI:

```sh
uv run main.py --study main19`
```

## Changes

### Requirements.txt

- In the original artefact, dependencies are not specified. We recovered working dependencies for the study original artefact.

## Errors

Numerous `index out of range` errors occurred while running the `test_codex.py` script. It seems that the dataset access implementation is incorrect.

Runs and errors:

```sh
> python test_codex.py --rerank token --retrieve semantic

Traceback (most recent call last):
  File "/Users/andi/dev/angrymeir/LLM-RepliKit/replikit/studies/main19/replicationpackage/test_codex.py", line 574, in <module>
    test_metric(references, candidates)
  File "/Users/andi/dev/angrymeir/LLM-RepliKit/replikit/studies/main19/replicationpackage/test_codex.py", line 499, in test_metric
    candidate = candidates[i]
                ~~~~~~~~~~^^^
IndexError: list index out of range
```

```sh
> python test_codex.py --rerank token --retrieve false

Traceback (most recent call last):
  File "/Users/andi/dev/angrymeir/LLM-RepliKit/replikit/studies/main19/replicationpackage/test_codex.py", line 563, in <module>
    test_sample_rerank(
  File "/Users/andi/dev/angrymeir/LLM-RepliKit/replikit/studies/main19/replicationpackage/test_codex.py", line 238, in test_sample_rerank
    code_tokens = tokenize(training_comments[int(sim_ids[0])])
                           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
IndexError: list index out of range

```

```sh
> python test_codex.py --rerank false --retrieve semantic

Traceback (most recent call last):
  File "/Users/andi/dev/angrymeir/LLM-RepliKit/replikit/studies/main19/replicationpackage/test_codex.py", line 553, in <module>
    test_sample_retrieve(
  File "/Users/andi/dev/angrymeir/LLM-RepliKit/replikit/studies/main19/replicationpackage/test_codex.py", line 178, in test_sample_retrieve
    "\n#Example Code{}:\n".format(i) + training_codes[int(sim_ids[i])]
IndexError: list index out of range                                       ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
```

## LLM model

The model `code-davinci-002` has been deprecated.
Recommended replacement for the model (according to https://platform.openai.com/docs/deprecations) is `gpt-3.5-turbo-instruct`.
