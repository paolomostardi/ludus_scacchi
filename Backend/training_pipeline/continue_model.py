"""Continue training a model selected by its Ludus report row ID."""
import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from Backend.model_evaluation.evaluation_suite import DATASETS, SIMPLE, SUITE_ID
from Backend.training_pipeline.run_batch import (
    BatchError, GITHUB_CLONE, REPO_ROOT, kaggle_preflight, kernel_metadata,
    run_command, submit_and_download, write_json,
)

OWNER = "paolomostardi"
REVISION = "27b431e5f992b6fcf74f6b70075033331fcd5914"
TRAINING = {
    "january": ("lichess-bitboards-2013-01", 1, 5_000_000),
    "general": ("ludus-1500-2017-04-general-train-v1", 1, 542_568),
    "endgame": ("ludus-1500-2017-04-endgame-train-v1", 1, 14_756),
}
MANIFESTS = {
    "ludus-1500-2017-04-general-train-v1": "376f0dca724163359898bc18fb54d1e1d29a29879eb6f7d469f4985ff7a15c33",
    "ludus-1500-2017-04-endgame-train-v1": "21aebcadc571ccbb52fea8c249203ae7a0c1885b264d06a35666653f3bb0eff8",
}


def dataset(spec):
    slug, version, rows = spec
    return {"id": f"{OWNER}/{slug}", "version": version, "rows": rows,
            "manifest_sha256": MANIFESTS.get(slug)}


def mlflow(route, body=None):
    headers = {"Accept": "application/json"}
    if host := os.environ.get("LUDUS_MLFLOW_HOST"):
        headers["Host"] = host
    if token := os.environ.get("MLFLOW_TRACKING_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    elif (user := os.environ.get("MLFLOW_TRACKING_USERNAME")) and (
        password := os.environ.get("MLFLOW_TRACKING_PASSWORD")
    ):
        key = base64.b64encode(f"{user}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {key}"
    if body is not None:
        headers["Content-Type"] = "application/json"
    url = os.environ["MLFLOW_TRACKING_URI"].rstrip("/") + "/api/2.0/mlflow/" + route
    with urlopen(Request(url, data=None if body is None else json.dumps(body).encode(),
                         headers=headers), timeout=20) as response:
        return json.load(response)


def report():
    generator = REPO_ROOT / "Backend/model_evaluation/experiment_report.mjs"
    return subprocess.check_output(["node", str(generator), "--snapshot"], timeout=60).decode()


def save_report(path, html):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    tmp.write_text(html, encoding="utf-8")
    tmp.replace(path)


def checkpoint_for(root, run):
    run_id = run["info"]["run_id"]
    params = {item["key"]: item["value"] for item in run["data"].get("params", [])}
    for path in sorted(root.rglob("model_config.json")):
        config = json.loads(path.read_text(encoding="utf-8-sig"))
        if config.get("run_id") != run_id:
            continue
        artifact = config.get("artifact_file", "")
        if not artifact or Path(artifact).name != artifact:
            continue
        weights = path.with_name(artifact)
        if not weights.is_file():
            continue
        if config.get("factory") not in {"source_resnet", "model_testing_mlflow"}:
            raise BatchError(f"Unsupported model factory: {config.get('factory')}")
        digest = checksum(weights)
        if params.get("checkpoint_sha256", digest) != digest:
            continue
        return config, weights, digest, params
    raise BatchError(f"No matching checkpoint for MLflow run {run_id} under {root}. "
                     "Put its weights and model_config.json there and retry.")


def checksum(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fields(values):
    return [{"key": key, "value": str(value)} for key, value in values.items()]


def log_result(result, config, parent_params):
    settings = result["settings"]
    train = settings["train"]
    sequence = json.loads(parent_params["training_dataset_sequence"]) if (
        parent_params.get("training_dataset_sequence")
    ) else [parent_params["training_dataset"]] if parent_params.get("training_dataset") else []
    architecture = config.get("architecture_metadata", {}).get("architecture_variant", config["factory"])
    tags = {"initialization_run_id": settings["parent"], "evaluation_suite": settings["evaluation_suite"],
            "evaluation_scope": "full"}
    metrics = []
    for name, evaluation in result["evaluations"].items():
        suffix = name.split("/")[-1].replace("-", "_")
        tags["evaluation_dataset." + suffix] = name
        tags["evaluation_dataset_version." + suffix] = evaluation["version"]
        tags["evaluation_dataset_sha256." + suffix] = evaluation["sha256"]
        if suffix == "simple_v2":
            tags.update(simple_v2_version=evaluation["version"], simple_v2_sha256=evaluation["sha256"])
        for metric, value in {**evaluation["metrics"], "sample_count": evaluation["rows"]}.items():
            metrics.append({"key": f"{metric}_{suffix}", "value": value,
                            "timestamp": result["end_time"], "step": 0})
    params = {
        "architecture_variant": architecture, "model_factory": config["factory"],
        "total_parameters": result["total_parameters"], "training_dataset": train["id"],
        "training_dataset_version": train["version"],
        "training_dataset_sequence": json.dumps([*sequence, train["id"]]),
        "total_training_rows": train["rows"], "checkpoint_sha256": result["checkpoint_sha256"],
        "initialization_checkpoint_sha256": settings["source_sha256"],
        "pipeline_mode": "fine-tune", **settings["training"], "epochs": result["epoch"],
        "kaggle_kernel": settings["kernel"],
    }
    if result["training_manifest_sha256"]:
        params["dataset_manifest_sha256"] = result["training_manifest_sha256"]
    run_id = mlflow("runs/create", {
        "experiment_id": settings["experiment_id"], "start_time": result["start_time"],
        "run_name": (f"{architecture} fine-tune on {train['id'].split('/')[-1]}"
                     f" (LR {settings['training']['learning_rate']:g}, epoch {result['epoch']})"),
        "tags": fields(tags),
    })["run"]["info"]["run_id"]
    print(f"MLflow run: {run_id}", flush=True)
    mlflow("runs/log-batch", {"run_id": run_id, "params": fields(params), "metrics": metrics})
    mlflow("runs/update", {"run_id": run_id, "status": "FINISHED", "end_time": result["end_time"]})
    return run_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("id", type=int, nargs="?", help="Number in the report's ID column")
    parser.add_argument("--dataset", choices=TRAINING, help="Training dataset for this run")
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("checkpoints"))
    parser.add_argument("--report", type=Path, required=True, help="HTML snapshot used to resolve IDs and save results")
    parser.add_argument("--refresh-report", action="store_true", help="Refresh the snapshot from MLflow and exit")
    parser.add_argument("--plan", action="store_true", help="Resolve the ID and check inputs without submitting")
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--jobs-dir", type=Path, default=Path("ludus-jobs"))
    parser.add_argument("--kaggle", default="kaggle", help="Path to the authenticated Kaggle CLI")
    parser.add_argument("--kaggle-owner", default=os.environ.get("KAGGLE_USERNAME", OWNER))
    args = parser.parse_args()
    if not 0 < args.learning_rate < float("inf") or args.epochs < 1:
        parser.error("Use a finite positive learning rate and at least one epoch.")
    training = {
        "optimizer": "SGD", "momentum": 0.9, "weight_decay": 0,
        "learning_rate": args.learning_rate, "planned_epochs": args.epochs,
        "batch_size": 128, "seed": 42, "lr_schedule": "constant",
    }
    if not os.environ.get("MLFLOW_TRACKING_URI"):
        parser.error("Set MLFLOW_TRACKING_URI to the tracking server HTTP(S) URL")
    if args.refresh_report:
        save_report(args.report, report())
        print(args.report.resolve())
        return
    if args.id is None or args.dataset is None:
        parser.error("ID and --dataset are required to continue training")

    rows = re.findall(r'<td data-run-id="([0-9a-f]{32})">(\d+)</td>',
                      args.report.read_text(encoding="utf-8"))
    by_id = {number: run_id for run_id, number in rows}
    if not by_id:
        raise BatchError("This report predates run ID mapping. Run --refresh-report and reopen it.")
    if str(args.id) not in by_id:
        raise BatchError(f"No row ID {args.id} in {args.report}")
    parent = by_id[str(args.id)]
    run = mlflow("runs/get?" + urlencode({"run_id": parent}))["run"]
    print(f"Row {args.id}: {run['info'].get('run_name', parent)} ({parent})", flush=True)
    if run["info"]["status"] != "FINISHED":
        raise BatchError("The selected MLflow run is not finished.")
    config, weights, digest, params = checkpoint_for(args.checkpoint_dir, run)
    train = dataset(TRAINING[args.dataset])
    evaluations = list(DATASETS)
    print(f"Checkpoint: {weights}\nTraining: {train['id']} ({train['rows']:,} rows)", flush=True)
    print("Evaluation: " + ", ".join([item["id"] for item in evaluations] + ["simple_v2"]), flush=True)
    print(f"Training settings: {training}", flush=True)
    if args.plan:
        return

    slug = "ludus-continue-" + uuid.uuid4().hex[:12]
    work = args.jobs_dir.resolve() / slug
    kernel_id = f"{args.kaggle_owner}/{slug}"
    checkpoint_id = kernel_id + "-checkpoint"
    settings = {
        "kernel": kernel_id, "checkpoint_dataset": checkpoint_id,
        "repository": GITHUB_CLONE, "revision": REVISION, "source_sha256": digest,
        "parent": parent, "experiment_id": run["info"]["experiment_id"],
        "train": train, "evaluation": evaluations, "training": training, "evaluation_suite": SUITE_ID,
        "simple_evaluation": SIMPLE,
    }
    kaggle_preflight(args.kaggle, work)
    upload = work / "upload"
    write_json(upload / "model_config.json", config)
    write_json(upload / "dataset-metadata.json", {
        "id": checkpoint_id, "title": slug + "-checkpoint", "licenses": [{"name": "other"}],
    })
    shutil.copy2(weights, upload / weights.name)
    run_command([args.kaggle, "datasets", "create", "-p", str(upload)],
                work / "logs/checkpoint-upload.log", timeout=300)
    staged = work / "kernel"
    code = "continue_model.py"
    worker = Path(__file__).with_name("kaggle") / code
    metadata = kernel_metadata(args.kaggle_owner, slug, slug, code,
                               [checkpoint_id, train["id"], *(item["id"] for item in evaluations)],
                               [], True)
    metadata["kernel_type"] = "script"
    write_json(staged / "kernel-metadata.json", metadata)
    (staged / code).write_text(f"SETTINGS = {settings!r}\n" + worker.read_text(encoding="utf-8"),
                               encoding="utf-8")
    print(f"Submitting Kaggle kernel {kernel_id}", flush=True)
    output = submit_and_download(args.kaggle, {
        "name": "fit-evaluate", "id": kernel_id, "directory": staged,
    }, work, 12 * 3600, 30, 12 * 3600)
    checkpoints = []
    for epoch in range(1, args.epochs + 1):
        folder = output / f"epoch-{epoch}"
        result = json.loads((folder / "result.json").read_text(encoding="utf-8"))
        weights = folder / "model.weights.h5"
        if (result["settings"] != settings or result["epoch"] != epoch
                or checksum(weights) != result["checkpoint_sha256"]
                or set(result["evaluations"]) != {*(item["id"] for item in evaluations), "simple_v2"}):
            raise BatchError(f"Kaggle outputs do not match {kernel_id}, epoch {epoch}")
        checkpoints.append((result, weights))
    for result, weights in checkpoints:
        run_id = log_result(result, config, params)
        saved = args.checkpoint_dir / run_id
        saved.mkdir(parents=True, exist_ok=True)
        shutil.copy2(weights, saved / weights.name)
        write_json(saved / "model_config.json", {
            **config, "run_id": run_id, "experiment_id": settings["experiment_id"],
            "artifact_file": weights.name, "initialization_run_id": parent,
        })
        print(f"Checkpoint: {saved.resolve()}")
    save_report(args.report, report())
    print(f"Report: {args.report.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except (BatchError, OSError, ValueError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
