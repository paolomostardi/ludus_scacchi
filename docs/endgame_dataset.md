# Few-piece dataset preparation

This is a separate data-mining step. It does not train models or start Kaggle
jobs. Run it where the source arrays are mounted, preferably on Kaggle or a
workstation with storage, rather than downloading the large source onto the orchestration host.

`Backend/data_pipeline/build_endgames.py` selects positions with 3–6 pieces by
default, including both kings and all pawns. It counts occupancy in planes 0–11;
legal-destination planes and the turn plane do not contribute to the count.
It preserves the existing source/destination labels. These are human played
moves, not tablebase-optimal moves. This is an endgame-focused imitation task,
and improved performance on it would not establish improved opening play.

Example on Kaggle after cloning the published repository and changing into it
(adjust the input path to the actual dataset mount):

```bash
python -m Backend.data_pipeline.build_endgames --input-dir /kaggle/input/lichess-bitboards-2013-01 --chunks 0 1 2 3 4 --source-id lichess-bitboards-2013-01-training-chunks-0-4 --split training --output-dir /kaggle/working/endgames-training --max-pieces 6
```

Each output shard contains `chunk_N.npy` (boolean board planes),
`chunk_N_y.npy` (uint8 original target planes) and `chunk_N_source_rows.npy`.
When the source shards include game keys, ply and promotion type, the builder
also copies aligned `chunk_N_game_keys.npy`, `chunk_N_ply.npy` and
`chunk_N_promotion.npy`. A zero promotion code means no promotion; 2–5 are
python-chess's knight, bishop, rook and queen codes.
The latter stores `(source_index, original_row)` pairs, with `source_index`
referring to the manifest's `sources` list. Chunk boundaries may change; labels
and board orientation do not. The last shard can be shorter than the default
100,000 rows. Memory maps and 4,096-row scans bound memory usage.

`dataset_manifest.json` records the selection limits, supplied source identity,
input/output SHA-256 hashes, source row counts, selected row counts and piece
histogram. Only a `complete` manifest represents a usable build. Existing output
directories are refused. A failed build retains a failed manifest for diagnosis.
Checks reject bad shapes/lengths, non-binary or non-finite values, overlapping
pieces, missing kings, inconsistent turn planes, invalid one-hot labels and a
source label that does not belong to the moving side. These checks do not prove
full chess legality or validate the historical legal-destination plane encoding.

## Evaluation partition and rollout

- Prepare evaluation from separately held-out **games** before encoding, or from
  a source partition whose game separation can be established. Adjacent rows or
  different chunk numbers alone do not establish independence. This builder
  cannot recover game IDs from bitboards and deliberately does not split rows.
- Run the builder separately with `--split evaluation` and a new output path.
  That flag records provenance; it does not itself enforce a game-level split.
  Remove cross-partition duplicate positions or report their overlap before
  claiming generalization performance.
- Review the selected count and distributions (material, side to move, source
  squares); audit example positions before uploading a private Kaggle dataset.
- Set the training dataset ID and actual `chunk_count` in a separate run config.
  Use `final_chunk_holdout: 0` only after creating an independent evaluation set,
  so a short final shard is not accidentally discarded by the old 10,000-row rule.
- Evaluation currently expects its historical month/chunk layout. Add a dataset
  specification for the new endgame evaluation files before connecting this
  dataset to a full batch. Do not reuse the general dataset and label it endgame.
- First run pipeline validation, then compare 4x64 on general versus endgame
  data. Test 6x64 separately to distinguish data changes from architecture changes.

The builder has passed synthetic checks and a small real-data
[April 2017 pilot](april_2017_pilot.md): 943 training and 260 independent-game
evaluation positions, with zero exact encoded-input overlap. This prefix
sample is not yet published or attached to the training pipeline.
