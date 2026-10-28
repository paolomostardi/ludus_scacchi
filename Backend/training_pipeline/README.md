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
