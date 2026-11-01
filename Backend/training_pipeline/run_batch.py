"""Run Kaggle smoke, fit, and evaluation kernels as one verified batch."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FIT_NOTEBOOK = REPO_ROOT / "fit-model.ipynb"
EVAL_NOTEBOOK = REPO_ROOT / "Backend" / "kaggle" / "notebooks" / "evaluate-model.ipynb"
SMOKE_NOTEBOOK = REPO_ROOT / "Backend" / "training_pipeline" / "kaggle" / "smoke-test.py"
GITHUB_CLONE = "https://github.com/paolomostardi/ludus_scacchi.git"


class BatchError(RuntimeError):
    """An external command failed or an expected batch artifact was missing."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def notebook_source(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def set_notebook_source(cell: dict[str, Any], source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def stage_notebook(source_path: Path, destination: Path, branch: str, owner: str, fit_slug: str, runtime_settings: dict[str, str] | None = None) -> None:
    if not source_path.is_file():
        raise BatchError(f"Notebook source is missing: {source_path}")
    if source_path.suffix.lower() == ".py":
        source = source_path.read_text(encoding="utf-8-sig")
        notebook = {
            "cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.splitlines(keepends=True)}],
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
    else:
        notebook = json.loads(source_path.read_text(encoding="utf-8-sig"))
    for cell in notebook.get("cells", []):
        source = notebook_source(cell)
        source = source.replace("__LUDUS_GIT_BRANCH__", branch)
        source = source.replace(
            f"git clone {GITHUB_CLONE}",
            f"git clone --branch {branch} {GITHUB_CLONE}",
        )
        source = source.replace(
            '"/kaggle/input/notebooks/paolomostardi/fit-model',
            f'"/kaggle/input/notebooks/{owner}/{fit_slug}',
        )
        set_notebook_source(cell, source)
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    if runtime_settings:
        notebook["cells"].insert(0, {
            "cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": ["# Batch execution settings\n", "import os\n",
                       f"os.environ.update({runtime_settings!r})\n"],
        })
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def kernel_metadata(
    owner: str,
    slug: str,
    title: str,
    code_file: str,
    datasets: list[str],
    kernels: list[str],
    gpu: bool,
) -> dict[str, Any]:
    return {
        "id": f"{owner}/{slug}",
        "title": title,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": "true" if gpu else "false",
        "enable_tpu": "false",
        "enable_internet": "true",
        "code_file": code_file,
        "dataset_sources": datasets,
        "competition_sources": [],
        "kernel_sources": kernels,
        "model_sources": [],
    }


def stage_kernels(args: argparse.Namespace, run_dir: Path) -> dict[str, dict[str, Any]]:
    runtime_settings = {
        "LUDUS_PIPELINE_MODE": args.pipeline_mode,
        "LUDUS_VALIDATION_FIT_ROWS": str(args.validation_fit_rows),
        "LUDUS_VALIDATION_EVAL_ROWS": str(args.validation_eval_rows),
    }
    owner = args.kaggle_owner
    fit_id = f"{owner}/{args.fit_slug}"
    eval_id = f"{owner}/{args.eval_slug}"
    smoke_id = f"{owner}/{args.smoke_slug}"
    specs = {
        "smoke": {
            "id": smoke_id,
            "source": SMOKE_NOTEBOOK,
            "code": "smoke-test.ipynb",
            "datasets": [args.training_dataset],
            "kernels": [],
            "gpu": True,
            "title": args.smoke_slug,
        },
        "fit": {
            "id": fit_id,
            "source": FIT_NOTEBOOK,
            "code": "fit-model.ipynb",
            "datasets": [args.training_dataset],
            "kernels": [],
            "gpu": True,
            "title": args.fit_slug,
        },
        "evaluate": {
            "id": eval_id,
            "source": EVAL_NOTEBOOK,
            "code": "evaluate-model.ipynb",
            "datasets": [args.evaluation_dataset],
            "kernels": [fit_id],
            "gpu": False,
            "title": args.eval_slug,
        },
    }
    staged: dict[str, dict[str, Any]] = {}
    for name, spec in specs.items():
        kernel_dir = run_dir / "staged" / name
        stage_notebook(spec["source"], kernel_dir / spec["code"], args.repository_branch, owner, args.fit_slug, runtime_settings)
        metadata = kernel_metadata(
            owner, spec["id"].split("/", 1)[1], spec["title"], spec["code"],
            spec["datasets"], spec["kernels"], spec["gpu"],
        )
        write_json(kernel_dir / "kernel-metadata.json", metadata)
        staged[name] = {"id": spec["id"], "directory": kernel_dir, "metadata": metadata}
    return staged


def sanitize(text: str) -> str:
    text = re.sub(r"(?i)(password|token|secret|api[_-]?key)(\s*[=:]\s*)[^\s,;]+", r"\1\2[REDACTED]", text)
    return text.strip()


def run_command(command: list[str], log_path: Path, timeout: int = 120) -> str:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    command_env = os.environ.copy()
    command_env["PYTHONIOENCODING"] = "utf-8"
    command_env["PYTHONUTF8"] = "1"

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=command_env,
        timeout=timeout,
        check=False,
    )
    combined = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    log_path.write_text(combined, encoding="utf-8")
    if result.returncode:
        summary = sanitize(combined[-1200:]) or f"exit code {result.returncode}"
        raise BatchError(f"Command failed ({result.returncode}): {' '.join(command[:3])}\n{summary}")
    return combined.strip()


def kaggle_preflight(kaggle: str, run_dir: Path) -> None:
    version = run_command([kaggle, "--version"], run_dir / "logs" / "kaggle-version.log")
    print(f"Kaggle CLI: {version}")
    # This authenticated read-only call catches a missing or rejected token before any kernel is submitted.
    run_command(
        [kaggle, "kernels", "list", "--mine", "--page", "1", "--page-size", "1"],
        run_dir / "logs" / "kaggle-auth-check.log",
        timeout=90,
    )
    print("Kaggle API authentication succeeded.")


def state_from_status(status: str) -> str:
    tokens = re.findall(r"\b[A-Z_]{3,}\b", status.upper())
    states = {
        "COMPLETE", "COMPLETED", "SUCCESS", "SUCCEEDED", "ERROR", "FAILED",
        "CANCELLED", "CANCELED", "RUNNING", "QUEUED", "STARTING", "INITIALIZING",
    }
    for token in reversed(tokens):
        if token in states:
            return token
    return "UNKNOWN"


def wait_for_kernel(kaggle: str, kernel_id: str, log_dir: Path, timeout_seconds: int, poll_seconds: int) -> str:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        status = run_command(
            [kaggle, "kernels", "status", kernel_id],
            log_dir / "status-latest.log",
            timeout=90,
        )
        state = state_from_status(status)
        print(f"{kernel_id}: {state}")
        if state in {"COMPLETE", "COMPLETED", "SUCCESS", "SUCCEEDED"}:
            return status
        if state in {"ERROR", "FAILED", "CANCELLED", "CANCELED"}:
            raise BatchError(f"Kaggle kernel {kernel_id} ended with {state}: {sanitize(status)}")
        time.sleep(poll_seconds)
    raise BatchError(f"Timed out waiting for Kaggle kernel {kernel_id} after {timeout_seconds} seconds.")


def find_output(output_dir: Path, name: str) -> Path:
    matches = list(output_dir.rglob(name))
    if not matches:
        raise BatchError(f"Expected Kaggle output {name!r} was not downloaded to {output_dir}.")
    return matches[0]


def parse_training_ids(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    if not values.get("run_id") or not values.get("experiment_id"):
        raise BatchError(f"Training output has incomplete MLflow IDs: {path}")
    return values


def validate_smoke_report(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if not report.get("mlflow_logged") or not report.get("run_id") or not report.get("experiment_id"):
        raise BatchError("Smoke report does not confirm a recorded MLflow run.")
    if not report.get("metrics"):
        raise BatchError("Smoke report contains no training/evaluation metrics.")
    return report


def validate_evaluation_report(path: Path, training_ids: dict[str, str]) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("run_id") != training_ids["run_id"]:
        raise BatchError("Evaluation report run_id does not match the training run.")
    if report.get("experiment_id") != training_ids["experiment_id"]:
        raise BatchError("Evaluation report experiment_id does not match the training experiment.")
    if not report.get("mlflow_logged") or not report.get("datasets"):
        raise BatchError("Evaluation report does not confirm logged per-dataset metrics.")
    return report


def submit_and_download(
    kaggle: str,
    spec: dict[str, Any],
    run_dir: Path,
    timeout_seconds: int,
    poll_seconds: int,
    kernel_timeout: int,
) -> Path:
    name = spec["name"]
    kernel_id = spec["id"]
    stage_log_dir = run_dir / "logs" / name
    run_command(
        [kaggle, "kernels", "push", "-p", str(spec["directory"]), "-t", str(kernel_timeout)],
        stage_log_dir / "push.log",
        timeout=180,
    )
    wait_for_kernel(kaggle, kernel_id, stage_log_dir, timeout_seconds, poll_seconds)
    output_dir = run_dir / "outputs" / name
    output_dir.mkdir(parents=True, exist_ok=True)
    run_command(
        [kaggle, "kernels", "output", kernel_id, "-p", str(output_dir)],
        stage_log_dir / "output.log",
        timeout=900,
    )
    return output_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline-mode", choices=("training", "validation"), default="training",
                        help="Validation runs one fit chunk for one epoch and caps fit/evaluation rows.")
    parser.add_argument("--validation-fit-rows", type=int, default=50000)
    parser.add_argument("--validation-eval-rows", type=int, default=1000)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=Path("~/ludus-artifacts/training-batches"))
    parser.add_argument("--kaggle-owner", default=os.environ.get("KAGGLE_USERNAME", "paolomostardi"))
    parser.add_argument("--training-dataset", default="paolomostardi/lichess-bitboards-2013-01")
    parser.add_argument("--evaluation-dataset", default="paolomostardi/eval-training-2013-chunk-9")
    parser.add_argument("--smoke-slug", default="ludus-first-model-smoke")
    parser.add_argument("--fit-slug", default="fit-model")
    parser.add_argument("--eval-slug", default="evaluate-model")
    parser.add_argument("--repository-branch", default="main")
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--timeout-seconds", type=int, default=12 * 60 * 60)
    parser.add_argument("--kernel-timeout-seconds", type=int, default=12 * 60 * 60)
    parser.add_argument("--plan-only", action="store_true", help="Stage notebooks and print the plan without contacting Kaggle.")
    parser.add_argument("--preflight-only", action="store_true", help="Check Kaggle CLI authentication without submitting work.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.validation_fit_rows < 1 or args.validation_eval_rows < 1:
        raise SystemExit("Validation row limits must be positive.")
    repo_root = args.repo_root.expanduser().resolve()
    args.output_dir = args.output_dir.expanduser().resolve()
    if args.poll_seconds < 1 or args.timeout_seconds < 1 or args.kernel_timeout_seconds < 1:
        raise SystemExit("Polling and timeout values must be positive.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.repository_branch):
        raise SystemExit("Repository branch must contain only letters, numbers, underscores, and hyphens.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.kaggle_owner):
        raise SystemExit("Kaggle owner contains invalid characters.")
    for slug in (args.smoke_slug, args.fit_slug, args.eval_slug):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
            raise SystemExit(f"Invalid Kaggle kernel slug: {slug!r}")
    for dataset in (args.training_dataset, args.evaluation_dataset):
        if not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_-]+", dataset):
            raise SystemExit(f"Invalid Kaggle dataset ID: {dataset!r}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = args.output_dir / batch_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary: dict[str, Any] = {
        "batch_id": batch_id,
        "pipeline_mode": args.pipeline_mode,
        "validation_limits": ({"fit_rows": args.validation_fit_rows,
                               "evaluation_rows": args.validation_eval_rows,
                               "fit_chunks": 1, "epochs": 1}
                              if args.pipeline_mode == "validation" else None),
        "started_at": utc_now(),
        "repository_root": str(repo_root),
        "repository_branch": args.repository_branch,
        "status": "preparing",
        "stages": {},
    }
    summary_path = run_dir / "batch-summary.json"
    write_json(summary_path, summary)

    try:
        smoke_source = repo_root / "Backend" / "training_pipeline" / "kaggle" / "smoke-test.py"
        fit_source = repo_root / "fit-model.ipynb"
        eval_source = repo_root / "Backend" / "kaggle" / "notebooks" / "evaluate-model.ipynb"
        global SMOKE_NOTEBOOK, FIT_NOTEBOOK, EVAL_NOTEBOOK
        SMOKE_NOTEBOOK, FIT_NOTEBOOK, EVAL_NOTEBOOK = smoke_source, fit_source, eval_source
        staged = stage_kernels(args, run_dir)
        for name, spec in staged.items():
            spec["name"] = name
        if args.plan_only:
            summary["status"] = "plan_ready"
            summary["kernel_ids"] = {name: spec["id"] for name, spec in staged.items()}
            write_json(summary_path, summary)
            print(json.dumps({"status": summary["status"], "run_dir": str(run_dir), "kernel_ids": summary["kernel_ids"]}, indent=2))
            return 0

        kaggle = shutil.which("kaggle")
        if not kaggle:
            raise BatchError("Kaggle CLI is not installed or not on PATH on this machine.")
        kaggle_preflight(kaggle, run_dir)
        if args.preflight_only:
            summary["status"] = "preflight_passed"
            summary["finished_at"] = utc_now()
            write_json(summary_path, summary)
            print(f"Kaggle preflight succeeded; no kernels were submitted. Details: {summary_path}")
            return 0

        summary["status"] = "running"
        for name in ("smoke", "fit", "evaluate"):
            spec = staged[name]
            summary["current_stage"] = name
            summary["stages"][name] = {"status": "running", "started_at": utc_now()}
            write_json(summary_path, summary)
            print(f"Submitting {name} kernel {spec['id']}.")
            output_dir = submit_and_download(
                kaggle, spec, run_dir, args.timeout_seconds, args.poll_seconds,
                args.kernel_timeout_seconds,
            )
            if name == "smoke":
                report_path = find_output(output_dir, "smoke_report.json")
                report = validate_smoke_report(report_path)
                summary["smoke_run"] = report
            elif name == "fit":
                model_path = find_output(output_dir, "model_testing_mlflow.keras")
                ids_path = find_output(output_dir, "mlflow_ids.txt")
                training_ids = parse_training_ids(ids_path)
                summary["training_run"] = training_ids
                summary["model_artifact"] = str(model_path.relative_to(run_dir))
            else:
                report_path = find_output(output_dir, "evaluation_report.json")
                report = validate_evaluation_report(report_path, summary["training_run"])
                summary["evaluation"] = report
            summary["stages"][name] = {"status": "complete", "finished_at": utc_now()}
            write_json(summary_path, summary)

        summary["status"] = "complete"
        summary["finished_at"] = utc_now()
        write_json(summary_path, summary)
        print(f"Training and evaluation batch completed: {summary_path}")
        return 0
    except Exception as exc:  # Preserve a machine-readable failure report for the morning review.
        summary["status"] = "failed"
        summary["failed_at"] = utc_now()
        summary["error"] = sanitize(str(exc))
        write_json(summary_path, summary)
        print(f"Batch failed: {summary['error']}", file=sys.stderr)
        print(f"Failure report: {summary_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())