"""Shared configuration for the runner and interactive notebooks."""
import json
import re
from pathlib import Path


DEFAULT_CONFIG = Path(__file__).with_name("run_config.json")


def load_config(path=DEFAULT_CONFIG):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    defaults = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    if "evaluation_dataset" in config and "evaluation_datasets" not in config:
        config["evaluation_datasets"] = [config.pop("evaluation_dataset")]
    if set(config) != set(defaults):
        raise ValueError("Run configuration must contain exactly the fields in run_config.json.")
    architecture = config["architecture"]
    if not isinstance(architecture, dict) or set(architecture) != {"factory", "parameters"}:
        raise ValueError("Architecture must contain factory and parameters.")
    if architecture["factory"] != "source_resnet":
        raise ValueError("This training configuration supports source_resnet.")
    parameters = architecture["parameters"]
    if not isinstance(parameters, dict) or set(parameters) != {"conv_filters", "residual_blocks"}:
        raise ValueError("source_resnet requires conv_filters and residual_blocks.")
    positive = ["chunk_count", "epochs_per_chunk", "batch_size"]
    nonnegative = ["start_chunk", "seed", "final_chunk_holdout"]
    for name in positive + nonnegative:
        value = config[name]
        if type(value) is not int or value < (1 if name in positive else 0):
            raise ValueError(f"Invalid integer setting: {name}")
    if any(type(value) is not int or value < 1 for value in parameters.values()):
        raise ValueError("Architecture parameters must be positive integers.")
    limit = config["max_training_rows_per_chunk"]
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("Training row cap must be null or a positive integer.")
    datasets = config["evaluation_datasets"]
    if (not isinstance(datasets, list) or not datasets
            or any(not isinstance(dataset, str)
                   or not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_-]+", dataset)
                   for dataset in datasets)):
        raise ValueError("evaluation_datasets must contain Kaggle dataset IDs.")
    if not isinstance(config["training_dataset"], str) or not re.fullmatch(
            r"[A-Za-z0-9_-]+/[A-Za-z0-9_-]+", config["training_dataset"]):
        raise ValueError("Invalid Kaggle dataset: training_dataset")
    if not isinstance(config["year_month"], str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}", config["year_month"]):
        raise ValueError("year_month must use YYYY-MM format.")
    return config
