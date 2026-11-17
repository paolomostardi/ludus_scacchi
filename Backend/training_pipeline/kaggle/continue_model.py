"""Fine-tune a saved model and evaluate it on the fixed comparison suite."""
import hashlib
import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

os.environ["KERAS_BACKEND"] = "tensorflow"


def checksum(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def mounted(dataset):
    matches = [path for path in Path("/kaggle/input").rglob(dataset.split("/")[-1])
               if path.is_dir()]
    if len(matches) != 1:
        raise ValueError(f"Expected one mount for {dataset}: {matches}")
    return matches[0]


def batches(root, expected_rows):
    import numpy as np
    from Backend.training_pipeline.validation import validate_arrays

    paths = sorted(
        (p for p in root.glob("chunk_*.npy") if re.fullmatch(r"chunk_\d+\.npy", p.name)),
        key=lambda p: int(p.stem.split("_")[1]),
    )
    total = 0
    for path in paths:
        x = np.load(path, mmap_mode="r", allow_pickle=False)
        y = np.load(path.with_name(path.stem + "_y.npy"), mmap_mode="r", allow_pickle=False)
        if y.shape[1:] == (2, 8, 8):
            y = y[:, 0].reshape(-1, 64)
        validate_arrays(x, y)
        total += len(x)
        yield x, y
    if total != expected_rows:
        raise ValueError(f"{root.name}: expected {expected_rows} rows, found {total}")


def dataset_root(dataset):
    root = mounted(dataset["id"])
    expected = dataset["manifest_sha256"]
    if expected and checksum(root / "dataset_manifest.json") != expected:
        raise ValueError(f"{dataset['id']} does not match the configured dataset manifest")
    return root


def main():
    # The launcher prepends the run settings to the submitted script.
    repo = Path("/tmp/ludus-continue-model")
    subprocess.run(["git", "clone", SETTINGS["repository"], str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", SETTINGS["revision"]], check=True)
    sys.path.insert(0, str(repo))
    if importlib.util.find_spec("chess") is None:
        subprocess.run([sys.executable, "-m", "pip", "install", "python-chess==1.999"], check=True)

    import keras
    import tensorflow as tf
    from Backend.model_evaluation.simple_positions import (
        catalog_identity, load_catalog, prepare, score_predictions,
    )
    from Backend.training_pipeline.validation import validate_metrics

    if not tf.config.list_physical_devices("GPU"):
        raise RuntimeError("The Kaggle job requires a GPU")
    training = SETTINGS["training"]
    keras.utils.set_random_seed(training["seed"])
    source = mounted(SETTINGS["checkpoint_dataset"])
    config = json.loads((source / "model_config.json").read_text(encoding="utf-8"))
    checkpoint = source / config["artifact_file"]
    if config["run_id"] != SETTINGS["parent"] or checksum(checkpoint) != SETTINGS["source_sha256"]:
        raise ValueError("Mounted checkpoint does not match the selected run")
    factory_name = config["factory"]
    module = importlib.import_module(
        "Backend.model_architecture.implementation.experimental." + factory_name
    )
    model = getattr(module, factory_name)(**config["parameters"])
    model.load_weights(checkpoint)
    model.compile(
        optimizer=keras.optimizers.SGD(
            learning_rate=training["learning_rate"], momentum=training["momentum"],
            weight_decay=training["weight_decay"],
        ),
        loss="categorical_crossentropy",
        metrics=["accuracy", keras.metrics.TopKCategoricalAccuracy(k=3, name="top3_accuracy")],
    )

    output = Path("/kaggle/working")
    train = SETTINGS["train"]
    training_root = dataset_root(train)
    evaluation_roots = [(dataset, dataset_root(dataset)) for dataset in SETTINGS["evaluation"]]
    for epoch in range(1, training["planned_epochs"] + 1):
        started = time.time_ns() // 1_000_000
        for x, y in batches(training_root, train["rows"]):
            model.fit(x, y, batch_size=training["batch_size"], epochs=1, shuffle=True, verbose=2)
        folder = output / f"epoch-{epoch}"
        folder.mkdir()
        evaluate_checkpoint(model, folder, epoch, started, training_root, evaluation_roots,
                            load_catalog, catalog_identity, prepare, score_predictions, validate_metrics)


def evaluate_checkpoint(model, output, epoch, started, training_root, evaluation_roots,
                        load_catalog, catalog_identity, prepare, score_predictions, validate_metrics):
    weights = output / "model.weights.h5"
    model.save_weights(weights)
    finished = time.time_ns() // 1_000_000

    evaluations = {}
    for dataset, root in evaluation_roots:
        sums = dict(accuracy=0., top3_accuracy=0., loss=0.)
        for x, y in batches(root, dataset["rows"]):
            scores = model.evaluate(x, y, batch_size=128, verbose=0, return_dict=True)
            validate_metrics(scores)
            for name in sums:
                sums[name] += float(scores[name]) * len(x)
        evaluations[dataset["id"]] = {
            **dataset, "metrics": {name: value / dataset["rows"] for name, value in sums.items()},
            "sha256": checksum(root / "dataset_manifest.json"),
        }
    catalog = load_catalog()
    identity = catalog_identity(catalog)
    boards, _ = prepare(catalog)
    scores = score_predictions(catalog, model.predict(boards, batch_size=128, verbose=0))["metrics"]
    evaluations["simple_v2"] = {
        "version": identity["version"], "rows": identity["sample_count"],
        "sha256": identity["sha256"],
        "metrics": {name: scores[name] for name in ("accuracy", "top3_accuracy", "loss")},
    }
    validate_metrics(evaluations["simple_v2"]["metrics"])
    manifest = training_root / "dataset_manifest.json"
    result = {
        "settings": SETTINGS, "epoch": epoch, "start_time": started, "end_time": finished,
        "training_manifest_sha256": checksum(manifest) if manifest.is_file() else None,
        "total_parameters": model.count_params(), "checkpoint_sha256": checksum(weights),
        "evaluations": evaluations,
    }
    (output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
