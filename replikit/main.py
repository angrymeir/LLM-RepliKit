import argparse
import yaml
import importlib
import os
from typing import Any, Dict

def load_yaml(path: str) -> Dict[str, Any]:
    """
    Load a YAML file from the given path.

    Args:
        path (str): The path to the YAML configuration file.

    Returns:
        Dict[str, Any]: Parsed contents of the YAML file as a dictionary.
    """
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def load_class(module_path: str, class_name: str) -> Any:
    """
    Dynamically load and return a class (e.g. preprocessor) from the specified study.

    Args:
        module_path (str): Dotted path to the module.
        class_name (str): Name of the class to load.

    Returns:
        Any: The loaded class object.
    """
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)

def prepare(study: str, global_config: Dict[str, Any]) -> bool:
    """
    Prepare the study replication package.

    This includes checking necessary directories and initializing the preprocessor.

    Args:
        study (str): The name of the study.
        global_config (Dict[str, Any]): Global configuration dictionary.

    Returns:
        bool: Result from the preprocessor's `magic` method. True if succeeded
    """
    
    study_config = global_config['study'][study]

    # check that directories exist
    if not os.path.exists("studies/{}".format(study)):
        raise FileNotFoundError(f"No directory found for study: {study}. You need to supply the preprocessor and postprocessor in this directory first.")
    if not os.path.exists("{}/{}".format(global_config['evidence_dir'], study)):
        os.makedirs("{}/{}".format(global_config['evidence_dir'], study))

    pre_class = load_class(global_config['study_dir'] + "." + study_config['preprocessor_module'], "Preprocessor")
    preprocessor = pre_class(study_config)

    status = preprocessor.magic()
    return status

def run(study: str, test: int, global_config: Dict[str, Any]) -> None:
    """
    Run the study replication package.

    Either executes the replication package to test if everything works as expected or runs the replication package for a given sample size.

    Args:
        study (str): The name of the study.
        test (int): Whether to run the replication package to test if it works.
        global_config (Dict[str, Any]): Global configuration dictionary.
    """
    
    study_config = global_config['study'][study]
    runner = load_class(global_config['study_dir'] + "." + study_config['runner_module'], "Runner")
    runner = runner(study_config)
    if test:
        for i in range(test):
            runner.run(i)
            runner.save_evidence(i)
    else:
        for i in range(study_config['significant_sample_size']):
            runner.run(i)
            runner.save_evidence(i)

def postprocess(study: str, global_config: Dict[str, Any], statistics_only: bool) -> None:
    """
    Postprocess the evidence of the study replication package and generates a report.

    This involves calling the postprocessor's postprocess method.

    Args:
        study (str): The name of the study.
        global_config (Dict[str, Any]): Global configuration dictionary.
        no_execution (bool): Whether to perform changes or only compute statistics.
    """
    study_config = global_config['study'][study]
    post_class = load_class(global_config['study_dir'] + "." + study_config['postprocessor_module'], "PostProcessor")
    postprocessor = post_class(study_config)
    postprocessor.postprocess(statistics_only)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--study", required=True)
    parser.add_argument("--test", default=0, type=int)
    parser.add_argument("--no_execution", action='store_true')
    parser.add_argument("--global_config", default="configs/global.yaml")
    parser.add_argument("--reset", action='store_true', help="Reset the study and re-download source files if necessary.")
    args = parser.parse_args()

    global_config: Dict[str, Any] = load_yaml(args.global_config)
    global_config['reset'] = args.reset
    if not args.no_execution:
        prepare(args.study, global_config)
        run(args.study, args.test, global_config)
    postprocess(args.study, global_config, args.no_execution)