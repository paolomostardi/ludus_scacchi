# First-model training and evaluation batch

This package owns training and evaluation orchestration. It does not download monthly PGNs, extract games, or build training datasets; those jobs remain under `Backend/data_pipeline`.

## Batch sequence

`run_batch.py` stages clean copies of the current training and evaluation notebooks, then:

1. Runs a short Kaggle smoke notebook on a 256-row sample and the current simple positions set.
2. Confirms the smoke notebook returned finite metrics and a run ID from remote MLflow.
3. Pushes and monitors the full fit notebook, then downloads its model and MLflow run metadata.
4. Pushes and monitors the evaluation notebook, then checks its report uses the same MLflow run and experiment IDs and contains metrics for each evaluation set.
5. Writes `batch-summary.json` and command logs under the configured output directory for the morning review.

The notebook inputs are staged from the repository's root `fit-model.ipynb` and `Backend/kaggle/notebooks/evaluate-model.ipynb`. Kaggle metadata is generated per run so the evaluation kernel depends on the fit kernel output. The notebooks currently expect these Kaggle datasets:

- `paolomostardi/lichess-bitboards-2013-01` for smoke and training.
- `paolomostardi/eval-training-2013-chunk-9` for the separate evaluation chunk.

The smoke, fit, and evaluation kernels use the same MLflow experiment name, `ludus_cnn`; the full evaluation must log under the fit run ID. MLflow credentials remain Kaggle notebook secrets named `IP_MLFLOW`, `USERNAME_MLFLOW`, and `PASSWORD_MLFLOW`.

## Run on the remote machine

On the Windows controller, configure an SSH alias/key in OpenSSH and set:

```powershell
$env:LUDUS_SSH_TARGET = 'your-ssh-alias'
$env:LUDUS_REMOTE_REPO = '/path/to/ludus_scacchi'
```

Run these modes in order:

```powershell
.\scripts\run_training_batch_over_ssh.ps1 -Mode plan
.\scripts\run_training_batch_over_ssh.ps1 -Mode preflight
.\scripts\run_training_batch_over_ssh.ps1
```

`plan` stages the notebooks without network access. `preflight` checks remote SSH, Kaggle CLI, and read authentication without submitting a kernel. The default mode submits Kaggle jobs that use compute quota; it only does so after preflight passes.

Before the first full run, push the repository branch referenced by the notebooks to GitHub and update the remote checkout; Kaggle clones that branch to import the bitboard encoder and model code. Do not put SSH keys, Kaggle tokens, or MLflow passwords in this repository.

Kaggle's CLI `kernels push` submits and runs a notebook, `kernels status` reports its latest run, and `kernels output` downloads generated files; see the [official Kaggle kernel CLI reference](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md) and [kernel metadata reference](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md).

## Current access status

Kaggle CLI authentication succeeded from the workstation. The smoke, fit, and evaluation kernels completed; evaluation metrics and its report were recorded under the fit run in MLflow. The current fit configuration is intentionally still a large run over five chunks, three epochs per chunk, so use a reduced sample configuration for quick iteration.

The VPS is the orchestration and MLflow host; model training and evaluation execute on Kaggle. MLflow is running from `/opt/mlflow/venv` behind Nginx. A complete end-to-end invocation through `run_batch.py` and recurring VPS scheduling still need validation. Keep the local Kaggle outputs and temporary staging folders out of commits; the root `.gitignore` excludes `.tmp-*` folders.

## Model configuration handoff

Fit exports `model_config.json` beside its model and `mlflow_ids.txt`, and logs it as an MLflow configuration artifact. It records the supported factory, constructor parameters, model filename, and training run/experiment IDs. Evaluation validates those IDs and reconstructs the model with the recorded parameters before loading its weights. Existing fit outputs without the JSON file use their recorded MLflow parameters; missing settings or unsupported factories fail explicitly. Add new architectures to the evaluation factory mapping when introducing them.

Fit also exports `training_manifest.json` and logs it under `configuration` in MLflow. It records the mounted dataset name/path, architecture parameters, actual row counts for each chunk before and after holdout, array shapes, total training rows, epochs, and batch size. The settings used in `fit()` are the same variables logged to MLflow. Dataset versions/checksums and a game-level split remain separate provenance work.

## Small pipeline validation

Use `--pipeline-mode validation` to exercise the same smoke → fit → evaluation sequence with a bounded workload. Fit uses the first configured chunk, at most 50,000 positions, and one epoch; the large evaluation dataset is capped at 1,000 positions while the eight simple positions remain included. Arrays are memory-mapped and sliced before label conversion. This checks execution and logging, not model quality. The existing smoke stage remains a 256-position check in both modes.

From the VPS checkout:

```bash
python3 -m Backend.training_pipeline.run_batch --pipeline-mode validation --plan-only
python3 -m Backend.training_pipeline.run_batch --pipeline-mode validation --preflight-only
python3 -m Backend.training_pipeline.run_batch --pipeline-mode validation
```

From the Windows SSH launcher:

```powershell
.\scripts\run_training_batch_over_ssh.ps1 -Mode plan -PipelineMode validation
.\scripts\run_training_batch_over_ssh.ps1 -Mode preflight -PipelineMode validation
.\scripts\run_training_batch_over_ssh.ps1 -Mode run -PipelineMode validation
```

`--validation-fit-rows` and `--validation-eval-rows` (SSH: `-ValidationFitRows` and `-ValidationEvalRows`) customize the sample caps. These limits apply only to validation mode. The default `--pipeline-mode training` / `-PipelineMode training` retains all configured fit chunks, three epochs per chunk, the existing final-chunk holdout, and the full evaluation dataset. Opening either notebook directly also defaults to training mode; the batch runner adds an explicit execution-settings cell to its staged copies.

The selected mode and limits appear in `batch-summary.json`; fit records its mode and actual row counts in MLflow and `training_manifest.json`, and evaluation records its mode and sample counts in `evaluation_report.json`. Validation uses the same Kaggle kernel IDs and existing secrets as training, so it creates new kernel versions and replaces their latest outputs. Model/run IDs and recorded mode distinguish its results from training results.

### Run configuration

The default workload is defined in `Backend/training_pipeline/run_config.json`.
It contains the architecture factory and parameters, Kaggle dataset IDs, starting
chunk and chunk count, optional row cap, epochs per chunk, batch size, seed,
final-chunk holdout, and dataset month. The supported training factory is
`source_resnet`. Input datasets must retain the existing chunk filenames and
encoding. Evaluation retains its existing chunk layout and eight simple cases.

Use `--config /path/to/run-config.json` to select another complete configuration.
Existing dataset CLI options override the corresponding configuration values.
Validation mode uses one chunk, one epoch, and the validation row limits.
Each batch saves `run-config.json` and embeds the configuration in staged
notebooks. Fit includes it in its training manifest.

Inspect a future run without submitting jobs:

```bash
python -m Backend.training_pipeline.run_batch --config Backend/training_pipeline/run_config.json --pipeline-mode training --plan-only
```

### Runtime provenance and evaluation recovery

Install the known working VPS CLI with
\`python -m pip install -r Backend/training_pipeline/requirements-runner.txt\`.
New submissions record the Git revision and check it out inside Kaggle before
importing project code. Training and evaluation export package-version snapshots
and record key versions in MLflow. Kaggle library pins require the versions from
a successful runtime before a compatible lock can be finalized.

To recover evaluation after fit completed, use
\`python -m Backend.training_pipeline.run_batch --resume-dir /path/to/batch\`.
Resume retains the staged notebooks and training IDs. It reattaches to evaluation
when its saved state is running, or submits evaluation again after failure.
If a running evaluation has failed, the first resume records that failure and
the next invocation retries it. Completed training is reused. Resume requires
downloaded fit outputs and never submits training. Old batches are supported
when their staged evaluation contains the expected run-ID cell.
New CLI invocations use a host-wide process lock. Already-running older runners
do not hold that lock, so wait for them to finish before using the new runner.

Arrays are checked in bounded-size slices for aligned lengths, expected shapes,
finite values, and one-hot targets. Fit histories and evaluation metrics must
be finite. The runner also validates downloaded report metrics and run IDs.
