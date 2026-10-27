# Training pipeline

## Goal

Use monthly Lichess games to train and compare models for the **first task: choosing the piece to move**. A remote machine should run a configured batch overnight and leave a clear report for review the next morning. The model that chooses a destination square is a later stage.

## Current flow

1. **Acquire a month of games.** Lichess publishes monthly PGN archives. Older months generally contain fewer games, so they are useful for developing the pipeline before processing larger months. The current raw-data notebook reads a compressed archive on Kaggle.
2. **Extract positions and moves.** [`from_raw_create_dataset.ipynb`](../Backend/kaggle/notebooks/from_raw_create_dataset.ipynb) filters Bullet games, converts each game to position and next-move pairs, and uses pandas to write an intermediate CSV. It currently collects all pairs in memory before writing them. It also keeps only one move for each position when preparing bitboards.
3. **Build bitboards.** [`gm_pipeline.py`](../Backend/data_pipeline/gm_pipeline.py) and [`from_PGN_generate_bitboards.py`](../Backend/data_pipeline/from_PGN_generate_bitboards.py) use pandas and NumPy to create matching chunks. Each input has 15 planes of size 8×8; each move target has source and destination planes of size 8×8. The first model trains on the source plane flattened to 64 classes. Chunks are saved as `.npy` files and can be hosted as Kaggle datasets.
4. **Train one architecture.** [`fit-model.ipynb`](../fit-model.ipynb) currently selects `model_testing_mlflow`, loads configured chunks from the 2013-01 dataset, trains for three epochs per chunk, saves a Keras model, and records parameters and results in remote MLflow. Architecture choice and chunk range are edited in the notebook; automatic selection is not implemented.
5. **Evaluate.** [`evaluate-model.ipynb`](../Backend/kaggle/notebooks/evaluate-model.ipynb) loads the saved model, evaluates a separate chunk and a small set of simple positions, and logs metrics to the same remote MLflow run. The fit notebook exports the run and experiment IDs for this handoff. The current notebooks do not establish a recorded, game-level train/evaluation split.

```text
Lichess monthly PGN -> game/position CSV -> aligned NumPy bitboard chunks
                   -> first-model training -> evaluation -> MLflow results
```

## Next steps, in order

1. **Define one run configuration and dataset manifest.** Record month, source archive and checksum, repository revision, filters, chunk size, split rule, architecture ID, hyperparameters, random seed, and output paths. Keep credentials in server secrets. Give each run a unique ID so its inputs, model, and metrics can be traced together.
2. **Make preparation resumable and bounded in memory.** Stream games into position/move batches instead of accumulating a whole month in `all_rows`. Save each completed chunk and its row count, verify that input and target counts match, and resume from the last verified chunk after interruption. Start with a small older month, then increase the month size.
3. **Create stable training and evaluation splits.** Split by game before turning games into positions, and keep the evaluation set fixed for comparisons. Record which games and positions went into each split. Decide explicitly whether repeated positions should preserve move frequencies or be reduced to one target; the current notebook's first-move choice changes the learning target.
4. **Select models through configuration.** Add a small registry of model factories, starting with `model_testing_mlflow`. A run should select an architecture ID from its configuration and save that ID with the artifact. Once at least two candidates share the same data and evaluation protocol, an experiment job can choose the next candidate based on a defined metric and compute budget.
5. **Provide one batch entry point.** A command should run prepare → train → evaluate → publish using the run configuration. It should verify chunk shapes and counts before fitting, save checkpoints and the final model, and mark each stage as complete or failed. Re-running the same run ID should resume safely rather than repeat finished stages.
6. **Schedule on the remote machine.** After the batch command works manually, use the server's scheduler to start it at a chosen evening time. Limit concurrent runs, set a deadline and retry policy, persist logs and artifacts, and report failure clearly. The MLflow tracking service can remain remote; the scheduler and training worker need their own explicit configuration.
7. **Produce a morning review.** Publish a compact summary containing run ID, month and dataset size, architecture and settings, evaluation loss and accuracy, comparison with the previous accepted run, model and log locations, and any failed stages. Human feedback becomes the next run's configuration; new models are not promoted solely because a nightly job finished.

## First milestone

Run one small monthly archive end to end from a single command, with a fixed evaluation split, a recoverable checkpoint, a complete MLflow record, and a morning summary. Only then enable recurring overnight execution.
