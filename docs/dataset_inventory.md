# Dataset inventory

Snapshot: 11 November 2026. The Kaggle IDs and current version numbers below
were read from the account's dataset listing. They are an inventory of **existing
uploads**, not a claim that their filters, game splits, or checksums have been
verified. A Kaggle dataset name alone does not identify the exact source files
used by an older run; future runs should record the dataset version explicitly.

| Kaggle dataset ID (`paolomostardi/…`) | Current version | Known role |
| --- | ---: | --- |
| `lichess-bitboards-2013-01` | 1 | Current first-model training input; five `chunk_0`–`chunk_4` input/target pairs inspected. |
| `eval-training-2013-chunk-9` | 2 | Current general evaluation input; its 2013-01 files are actually named `my_processed_chunks/2013-01/chunk_6_x.npy` and `chunk_6_y.npy`. The slug does not describe that file number. |
| `lichess-raw-dataset-2013-01` | 1 | Raw monthly PGN upload; no per-move clock requirement can be met from this month. |
| `lichess-raw-dataset-2015-01` | 1 | Raw monthly PGN upload; no standard monthly `%clk` annotations expected. |
| `simple-chess-positions` | 1 | Older small upload; distinct from the current, versioned simple-position catalog in the repository. |
| `model-evaluation-combined` | 6 | Older evaluation/metadata CSV upload; not the current general evaluation input. |
| `lichess-bitboards-2013-04` | 4 | Historical bitboard upload; current run use unverified. |
| `lichess-bitboards-2014-07` | 3 | Historical bitboard upload; current run use unverified. |
| `lichess-2013-01` | 2 | Historical Lichess upload; content and run use unverified. |
| `masters-game-in-bitboards` | 6 | Historical master-game upload; content and run use unverified. |
| `chess-grandmasters-moves` | 2 | Historical grandmaster upload; content and run use unverified. |
| `pgn-games-1700` | 1 | Historical 1700-rated PGN upload; filters and source-game membership unverified. |
| `1700-lichess-user-bitboards` | 4 | Historical 1700-rated bitboard upload; filters and source-game membership unverified. |

The current run configurations point to `lichess-bitboards-2013-01` and
`eval-training-2013-chunk-9`. The training notebook reports five million source
rows across its five selected chunks. A private Kaggle CPU audit on 11 November
2026 hashed every 15-plane input in these mounted datasets. **705,726 of the
1,000,000 evaluation rows (70.57%) exactly match a training input**. It also
found 60,724 repeated training rows and 2,087 repeated evaluation inputs among
the non-overlapping rows; only 292,187 evaluation rows are unique new inputs.
The downloaded `legacy_overlap_report.json` is retained with the local pilot
artifacts. This is an exact-input check, not a game or near-duplicate check:
source game IDs are absent, so game independence remains unknown. Historical
general-set model accuracies must not be presented as held-out performance.
The few-piece builder writes a
`dataset_manifest.json` for new outputs, but no real few-piece upload exists yet.

## Planned 1500-rated collection

Proposed family: `lichess-1500-clock15`, starting with version `v1`. This is a
**specification**, not a published Kaggle dataset. A bounded
[April 2017 pilot](april_2017_pilot.md) has been mined locally. Keep separate immutable training and
evaluation outputs and allow a few-piece subset to refer back to the same
source-game partition.

- Source: `lichess_db_standard_rated_2017-04.pgn.zst` from the
  [Lichess standard-game archive](https://database.lichess.org/). Lichess's
  [published checksum list](https://database.lichess.org/standard/sha256sums.txt)
  gives SHA-256
  `559222b0e933bc02281643724fbd9bd46690074b10d784c4f264e0bff6c5992c`.
  This is the expected checksum for the **complete** archive; no local copy has
  been checked against it yet. April 2017 is the first month Lichess documents
  `%clk` annotations, not
  a guarantee that every game or move has one. Measure actual coverage in the
  selected source before building the dataset.
- Rating: the player **making the recorded move** has `WhiteElo` or `BlackElo`
  from **1450 through 1550**, inclusive. The opponent's rating is unrestricted.
- Time control: exclude games classified as `Bullet`. Record the accepted event
  classes and the raw `TimeControl` header; do not infer a class from rating.
- Clock: the mover has **at least 15 seconds before making that move**. A
  `%clk` value after a move is not the before-move clock. Derive the first
  before-move clock from a valid initial `TimeControl`, and later clocks from
  that same player's previous after-move `%clk`. Exclude moves with missing or
  ambiguous timing and count those exclusions in the manifest.
- Split: assign an entire source game to one partition before extracting any
  positions. Record the deterministic split rule, game IDs or hashes, and counts.
  Audit exact encoded-input overlap across partitions; record how repeated
  positions and different played moves from one position are handled.
- Format: produce bounded shards with aligned 15-plane inputs and source-move
  targets, plus a versioned manifest. Record source archive, code revision,
  encoding version, filters, row counts, shard byte sizes and SHA-256 hashes,
  split membership, and exclusions. Publish only after a small sample has been
  checked for clock arithmetic, board orientation, and legal targets.

Lichess documents `%clk` in standard monthly games [since April 2017](https://database.lichess.org/).
The currently used 2013 PGNs/bitboards therefore cannot be retroactively
filtered to this 15-second rule. The older notebook also drops rating and clock
context before bitboard generation. The pilot miner
`Backend/data_pipeline/mine_rated_pgn.py` retains per-game and per-move
metadata through filtering; a full-source build and publication remain open.

The April 2017 standard archive is listed at **3.48 GB compressed** and
11,348,506 games; Lichess estimates decompressed PGNs at about 7.1 times the
compressed size. Start with a small, bounded prefix to validate parsing,
clock coverage, filters and output size. Lichess says its `.zst` files are
partially decompressable and can also be decompressed while streaming. Record
the prefix byte limit and selection bias; a prefix is a pipeline sample, not a
representative evaluation set. For a production sample, stream across the
chosen source and use a deterministic game-hash selection rule plus a position
budget, writing completed shards as you go. This still reads the compressed
source, but does not stage the whole decompressed month on Kaggle disk or the
VPS.

## Storage and overlap policy

Keep dataset versions separate by purpose and mount only the versions needed
for a job. The VPS orchestrates jobs and stores compact manifests/reports; the
large mining output belongs on Kaggle or another data worker. Use bounded
scans and shards rather than a single global FEN JSON dictionary in RAM. For
exact model-input overlap, hash a canonical 15-plane encoded position; retain
source-game membership separately because an input hash cannot detect related
positions from the same game. Measure actual Kaggle disk use before choosing a
full-month mining workload.

For each future dataset, add one catalog entry with: stable ID and version,
role, source archive/version/checksum, game split, filters, encoding version,
shard list and checksums, row count, storage location, and overlap-audit result.
Mark unknown fields as unknown rather than inferring them from a dataset slug.
