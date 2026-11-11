# April 2017 rated/clock dataset pilot

Run: 11 November 2026, workstation CPU. This is a bounded feasibility sample,
not a representative evaluation dataset or a published Kaggle upload.

## Source and selection

- Lichess archive: `lichess_db_standard_rated_2017-04.pgn.zst`.
- HTTP `Range: bytes=0-4194303` returned 206 and exactly 4,194,304 bytes;
  the total compressed archive length reported by the server was 3,481,200,992
  bytes. Prefix SHA-256:
  `bc45ee5b3b8bc609dd75eba0d3579a8769e08328e3126d80ca5a9cf7e675d3d0`.
  The [published full-archive checksum](https://database.lichess.org/standard/sha256sums.txt)
  applies to the full file, not this prefix.
- The miner read the first 8,000 **complete** PGNs from the prefix and dropped
  any trailing partial game. It excluded Bullet games, selected moves by a
  **1450–1550 inclusive mover rating**, and required at least 15 seconds on
  that player's clock **before** the move. A missing clock excludes the move.
- Whole games were assigned to training or evaluation by the first eight bytes
  of SHA-256(Lichess game ID) modulo 100; values below 20 go to evaluation.
  This rule is deterministic and game-level. Rows with exact matching 15-plane
  inputs in training were removed from evaluation; repeated evaluation inputs
  were also removed.

| Pilot measure | Result |
| --- | ---: |
| PGNs scanned | 8,000 |
| Bullet games excluded | 2,399 |
| Games without a usable initial time control | 35 |
| Moves scanned in accepted non-Bullet games / missing `%clk` after-move comments | 375,515 / 0 |
| Moves by rated-in-range players | 50,414 |
| Rated-in-range moves below 15 seconds | 1,206 |
| Provisional training / evaluation positions | 40,310 / 8,898 |
| Evaluation positions identical to a training input | 840 |
| Repeated evaluation inputs removed | 33 |
| Clean evaluation positions | 8,025 |
| Whole-game-key overlap after splitting | 0 |
| Few-piece training positions, 3–6 pieces | 943 from 87 games |
| Few-piece evaluation positions, 3–6 pieces | 260 from 20 games |
| Exact overlap between few-piece train/evaluation inputs | 0 |
| Mining time / peak workstation working set | 80.02 seconds / 113,369,088 bytes |
| General mined shard files | 55,267,624 bytes |

The few-piece input/target arrays were reviewed through decoded examples;
1,203/1,203 reconstructed moves are legal under the decoded board with no
castling or en-passant rights. The source PGN parser itself supplies the legal
moves. Promotion piece types are preserved separately in
`chunk_N_promotion.npy`; the two target planes still encode only source and
destination. The sample contains 19 training and 9 evaluation promotions.
All 55 general shard files, 10 cleaned-evaluation shard files and 12 few-piece
shard files matched their recorded SHA-256 hashes.

## Reproduction and limits

`Backend/data_pipeline/mine_rated_pgn.py` consumes the `.zst` prefix (with
`zstandard`) or a complete PGN and writes aligned bitboard, target, game-key,
ply and promotion arrays. For the bounded pilot, use `--partial --max-games
8000 --shard-rows 5000`. `audit_position_overlap.py` writes clean evaluation
shards and a report with a disk-backed SQLite index. Run `build_endgames.py`
separately on training and cleaned evaluation, with `--max-pieces 6` and the
actual chunk indices from the mining manifest.

From the repository root, with `numpy`, `pandas`, `chess` and `zstandard`
installed, the pilot commands are:

```bash
python -m Backend.data_pipeline.download_lichess_prefix --month 2017-04 --output /work/lichess_db_standard_rated_2017-04.pgn.zst.prefix --max-bytes 4194304
python -m Backend.data_pipeline.mine_rated_pgn --input /work/lichess_db_standard_rated_2017-04.pgn.zst.prefix --partial --max-games 8000 --shard-rows 5000 --output-dir /work/pilot-general
python -m Backend.data_pipeline.audit_position_overlap --training-dir /work/pilot-general/training --evaluation-dir /work/pilot-general/evaluation --index /work/pilot-overlap.sqlite --cleaned-dir /work/pilot-clean-eval --shard-rows 5000
python -m Backend.data_pipeline.build_endgames --input-dir /work/pilot-general/training --chunks 0 1 2 3 4 5 6 7 8 --source-id lichess-2017-04-prefix-4mib-1500-clock15-training --split training --output-dir /work/pilot-endgames-training --max-pieces 6
python -m Backend.data_pipeline.build_endgames --input-dir /work/pilot-clean-eval/evaluation --chunks 0 1 --source-id lichess-2017-04-prefix-4mib-1500-clock15-evaluation --split evaluation --output-dir /work/pilot-endgames-evaluation --max-pieces 6
```

Read the actual shard indices from each manifest before repeating the builder
commands with another prefix or game limit. The pilot used Python 3.13.3,
NumPy 2.2.4, pandas 2.3.0, chess 1.11.2 and zstandard 0.25.0.

The prefix and all generated arrays are in the local ignored workspace
`.tmp-april-2017`, not in Git. The prefix is ordered by the source export and
is **not representative of the whole month**. Only 20 games contribute to the
few-piece evaluation subset. Before publication or model comparison, scan a
wider source with a deterministic game sample, check split and duplicate
policies, and repeat the manifest, legal-move, and storage audits.

Separately, the old 2013 datasets were audited on Kaggle: 705,726 of 1,000,000
evaluation inputs exactly match the existing training inputs. See the
[dataset inventory](dataset_inventory.md) for the limits of that finding.
