# Study main2

## Can we replicate the results?

Answer: No

Runs and errors:

```sh
> openai api fine_tunes.create -t gpt3/mix_data_train.jsonl -m curie

Upload progress: 100%|███████████████████████████████████████████████████████████████████████████████| 901k/901k [00:00<00:00, 12.1Mit/s]
Uploaded file from gpt3/mix_data_train.jsonl: file-2psWhFrjdF1LkHvmwQ6WzV
Error: Invalid response body from API: <html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
 (HTTP response code was 404) (HTTP status code: 404)
```

It also produces the same error if the model `gpt-3.5-turbo` is given as an argument:

```sh
> openai api fine_tunes.create -t gpt3/mix_data_train.jsonl -m gpt-3.5-turbo
```

Potential explanations are API changes for fine-tuning models.
The `openai` python app and the API itself now use different names to manage jobs, e.g., `fine_tuning.jobs.create` instead of `fine_tunes.create `.

Using the new API endpoints doesn't resolve the issues.

```sh
> openai api fine_tuning.jobs.create  -F gpt3/mix_data_train.jsonl -m curie

Error: Error code: 400 - {'error': {'message': 'invalid training_file: gpt3/mix_data_train.jsonl', 'type': 'invalid_request_error', 'param': 'training_file', 'code': None}}
```


Further sources of problems are that the [Appium Desktop](https://github.com/appium/appium-desktop) application is deprecated and was archived on April 25, 2023.

## LLM model

The study used GPT-3 in an unspecified version.
Via the API, the model `gpt-3.5-turbo-0125` is available as the only GPT-3 model.


