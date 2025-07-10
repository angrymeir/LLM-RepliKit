# Study 007: Large Language Model for Vulnerability Detection

This study replicates experiments evaluating ChatGPT's ability to detect vulnerabilities in code using different prompting strategies.

## Code Modifier

The `modifier.py` script automatically prepares the original vulnerability detection code for experimental execution. It generates multiple script variants based on different prompting strategies without altering the core detection logic.

### What the Modifier Does

The modifier takes an original vulnerability detection script and creates multiple experimental variants by:

1. **Path Corrections**: Updates file paths to work within the containerized environment
   - Changes relative paths (`../dataset/`) to absolute paths (`dataset/`)
   - Updates pickle file paths to work with the container structure

2. **API Key Management**: Replaces hardcoded API keys with environment variable loading
   - Comments out hardcoded OpenAI API key assignments
   - Adds `dotenv` loading for secure API key management

3. **Output Directory Setup**: Creates necessary directories for result storage
   - Ensures `generated_results` directory exists
   - Sets up file paths for evidence collection

4. **Experiment Configuration**: Modifies key parameters for each experimental variant
   - Sets `top_k` values (1, 3, 5) for retrieval-based prompting
   - Configures prompting strategies (basic, A1, A2, A3, A4, A5)
   - Uncomments execution code that was disabled in the original

5. **Evidence Collection**: Adds comprehensive result tracking
   - Enables data collection for all test cases (not just a subset)
   - Adds metrics calculation (accuracy, precision, recall, F1, F0.5)
   - Saves results in both JSON and text formats

6. **Enhanced Prompting**: Adds the A54 prompting strategy
   - Copies A54 prompting logic from ChatGPT_on_binary_vulner_detection_run54.py in the original study for completeness
   - Consolidates all prompting strategies into a single file for cleaner execution
   - Preserves original prompting logic while making it self-contained

### Key Modifications Made

#### File Structure Changes
- **Input**: Single original vulnerability detection script
- **Output**: Multiple scripts in `scripts/` directory named `vulner_detector_gpt3dot5_{option}_{top_k}.py`

#### Code Transformations
- **Uncommented Execution**: Enables full dataset processing instead of limited range testing
- **Metrics Addition**: Imports `fbeta_score` for F0.5 calculation
- **Result Persistence**: Adds JSON output for structured result storage
- **Error Handling**: Wraps metric calculations in try-catch blocks

#### Configuration-Driven Generation
Based on `replication_config.json`, the modifier generates scripts for:
- Basic prompting (no examples)
- A1-A5 prompting strategies with different retrieval configurations
- Various top-k values for retrieval-based approaches

### Important Notes

**Logic Preservation**: All modifications are purely infrastructural - the core vulnerability detection algorithm, prompting strategies, and evaluation logic remain unchanged from the original study.

**Experimental Variants**: Each generated script represents a specific experimental condition (prompting strategy + top-k value) that can be executed independently.

**Evidence Collection**: The modifier ensures all experimental runs produce standardized output formats for consistent analysis and comparison.

### Usage

The modifier is automatically called during the preprocessing phase but can be run manually:

```bash
python modifier.py /path/to/original/script.py
```

This generates all experimental variants in the `scripts/` directory based on the configuration in `replication_config.json`.