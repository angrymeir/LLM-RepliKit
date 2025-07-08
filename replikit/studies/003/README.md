# Study: An Empirical Study on Compliance with Ranking Transparency in the Software Documentation of EU Online Platforms 

### Can we replicate the results?
Answer: No

### Issues
- Could not clone repository completely, as authors account ran out of data packs to support git lfs
- The employed model gpt-3.5-turbo-16k-0613 has been deprecated. 
- Can not run gpt3.5 part, as the context window length has changed and the newer gpt3.5 models don't support such as large context window.
- Parts of the code are missing (e.g. copying of results - could be substituted by `convert_results.py`, but at cost of potentially deviating from the authors original code)
- Dependencies are missing (seaborn)
- No proper error handling (given, that full execution takes longer than 24h it is impossible to not run into errors such as OpenAI API returning 500 or similar)
