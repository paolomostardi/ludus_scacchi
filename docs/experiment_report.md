# Ludus experiment report

Run the read-only report server with Node.js 22 or newer from the repository root.
It uses the `ludus_cnn` MLflow experiment by default. Set `MLFLOW_TRACKING_URI`
in the server environment and use `MLFLOW_TRACKING_TOKEN` or
`MLFLOW_TRACKING_USERNAME` and `MLFLOW_TRACKING_PASSWORD` if required.

```sh
node Backend/model_evaluation/experiment_report.mjs
```

Open `http://127.0.0.1:8765/report` or save the same HTML for offline viewing:

```sh
curl --fail http://127.0.0.1:8765/report -o ludus-report.html
```

Use `curl.exe` in Windows PowerShell. Override the experiment with
`LUDUS_MLFLOW_EXPERIMENT` and the port with `LUDUS_REPORT_PORT`. The server
binds to loopback. The HTML contains experiment and dataset metadata, so keep
the endpoint and saved reports private. On a remote operator machine, access
the endpoint through an SSH tunnel.

Training runs use the latest recorded MLflow value for each metric key.
Reevaluations with MLflow parent run IDs appear alongside their training run.
A dash indicates missing metadata. The documented 4x64 and 6x64 parameter totals
are used when a run identifies its exact architecture variant and lacks a total.

Dataset variations come from the checked-in inventory and version or hash
metadata recorded on the runs. Inventory snapshot versions describe known
uploads. An older run's exact dataset version requires its own logged metadata.


When an SSH tunnel forwards a different local port and MLflow validates the
HTTP Host header, set `LUDUS_MLFLOW_HOST` to the host and port MLflow accepts.
For example, with a local forward from port 15000 to VPS port 5000:

```powershell
$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:15000"
$env:LUDUS_MLFLOW_HOST = "localhost:5000"
node Backend/model_evaluation/experiment_report.mjs
```


The training runs table shows one row per training run and one column per evaluation dataset. Evaluation cells show top-1 and top-3 accuracy. Training dataset columns show true or false based on the datasets recorded for that run. A dash in the training columns means the run lacks training dataset metadata. Dataset tables show the total number of data points when known. When several runs evaluated the same checkpoint on the same dataset, the table uses the result with the largest recorded sample count. A dash indicates missing results. The evaluation dataset table includes the final simple-position catalog (simple-v2).

Set the MLflow tag `ludus_report=exclude` to hide a run from the report. For a
multi-stage fit, log the MLflow parameter `training_dataset_sequence` as a JSON
array of dataset names in training order, including versions where known.
Ordinary MLflow dataset inputs provide dataset membership without stage order.
