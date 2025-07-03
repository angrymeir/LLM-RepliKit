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

It also produces the same error if the model `gpt-3.5-turbo-0125` is given as an argument:

```sh
> openai api fine_tunes.create -t gpt3/mix_data_train.jsonl -m gpt-3.5-turbo-0125
```

Potential explanations are API changes for fine-tuning models.

## LLM model

The study used GPT-3 in an unspecified version.
Via the API, the model `gpt-3.5-turbo-0125` is available as the only GPT-3 model.

## Other problems

The used [Appium Desktop](https://github.com/appium/appium-desktop) application is deprecated and was archived on April 25, 2023.
