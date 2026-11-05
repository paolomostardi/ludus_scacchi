# Remote smoke run: fit on a small sample, evaluate simple positions, and verify MLflow writes.
import json
import math
import os
import subprocess
import sys
from pathlib import Path

subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'chess', 'mlflow'], check=True)

import numpy as np
import pandas as pd
import mlflow
from kaggle_secrets import UserSecretsClient

repo_path = Path('/tmp/ludus_scacchi')
if not repo_path.exists():
    subprocess.run([
        'git', 'clone', '--branch', '__LUDUS_GIT_BRANCH__',
        'https://github.com/paolomostardi/ludus_scacchi.git', str(repo_path)
    ], check=True)
sys.path.insert(0, str(repo_path))

from Backend.data_pipeline import from_PGN_generate_bitboards as gen
from Backend.data_pipeline import gm_pipeline
from Backend.model_architecture.implementation.experimental.model_testing_mlflow import model_testing_mlflow
from Backend.model_evaluation import create_dataset_for_simple_positions as create_simple

secrets = UserSecretsClient()
mlflow_ip = secrets.get_secret('IP_MLFLOW')
os.environ['MLFLOW_TRACKING_URI'] = f'http://{mlflow_ip}'
os.environ['MLFLOW_SUPPRESS_PRINTING_URL_TO_STDOUT'] = 'true'
os.environ['MLFLOW_TRACKING_USERNAME'] = secrets.get_secret('USERNAME_MLFLOW')
os.environ['MLFLOW_TRACKING_PASSWORD'] = secrets.get_secret('PASSWORD_MLFLOW')
mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
mlflow.set_experiment('ludus_cnn')

run_config = json.loads(os.environ.get('LUDUS_RUN_CONFIG', '{}'))
training_dataset_name = run_config.get('training_dataset', 'paolomostardi/lichess-bitboards-2013-01').split('/')[-1]
input_root = Path('/kaggle/input')
x_candidates = [p for p in input_root.rglob('chunk_0.npy') if p.parent.name == training_dataset_name]
if not x_candidates:
    mounted_inputs = sorted(p.name for p in input_root.iterdir())
    raise FileNotFoundError(
        f"Dataset 'lichess-bitboards-2013-01' is not mounted under {input_root}. Mounted inputs: {mounted_inputs}."
    )
if len(x_candidates) > 1:
    raise RuntimeError(f"Found multiple matching training chunks: {x_candidates}")
x_path = x_candidates[0]
y_path = x_path.with_name('chunk_0_y.npy')
if not y_path.is_file():
    raise FileNotFoundError(f"Missing matching labels file: {y_path}")
x_memmap = np.load(x_path, mmap_mode='r')
y_memmap = np.load(y_path, mmap_mode='r')
sample_count = min(256, len(x_memmap), len(y_memmap))
if sample_count < 2:
    raise RuntimeError(f'Need at least two aligned training rows; found {sample_count}.')
x_sample = np.asarray(x_memmap[:sample_count], dtype=np.float32)
y_sample = np.asarray(y_memmap[:sample_count, 0].reshape(sample_count, 64), dtype=np.float32)

model = model_testing_mlflow(conv_filters=12, upsample_factor=4)
create_simple.main()
simple_path = Path('/kaggle/working/Backend/model_evaluation/simple_positions.csv')
simple_df = pd.read_csv(simple_path)
x_simple = np.stack([gm_pipeline.from_fen_create_bitboard(fen) for fen in simple_df['FEN']])
y_simple = np.zeros((len(simple_df), 64), dtype=np.float32)
for row, square in enumerate(simple_df['TargetSquare']):
    y_simple[row, gen.chess_square_to_source_index(int(square))] = 1.0

with mlflow.start_run(run_name='first_model_smoke_test') as run:
    mlflow.log_params({
        'test_type': 'pipeline_smoke',
        'model_factory': 'model_testing_mlflow',
        'conv_filters': 12,
        'upsample_factor': 4,
        'training_sample_count': sample_count,
        'epochs': 1,
    })
    model.fit(x_sample, y_sample, batch_size=32, epochs=1, verbose=0)
    sample_metrics = model.evaluate(x_sample, y_sample, batch_size=32, verbose=0, return_dict=True)
    simple_metrics = model.evaluate(x_simple, y_simple, batch_size=32, verbose=0, return_dict=True)
    metrics = {
        'smoke_sample_loss': float(sample_metrics['loss']),
        'smoke_sample_accuracy': float(sample_metrics['accuracy']),
        'smoke_simple_loss': float(simple_metrics['loss']),
        'smoke_simple_accuracy': float(simple_metrics['accuracy']),
    }
    if not all(math.isfinite(value) for value in metrics.values()):
        raise RuntimeError(f'Non-finite smoke metrics: {metrics}')
    mlflow.log_metrics(metrics)
    model_path = Path('/kaggle/working/smoke_model.keras')
    model.save(model_path)
    mlflow.log_artifact(str(model_path), artifact_path='smoke')
    report = {
        'status': 'complete',
        'mlflow_logged': True,
        'run_id': run.info.run_id,
        'experiment_id': run.info.experiment_id,
        'metrics': metrics,
        'training_sample_count': sample_count,
        'simple_position_count': len(simple_df),
        'model_artifact': str(model_path),
    }
    report_path = Path('/kaggle/working/smoke_report.json')
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    mlflow.log_artifact(str(report_path), artifact_path='smoke')
print(json.dumps(report, indent=2))