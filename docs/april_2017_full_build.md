# April 2017 rated dataset, full-source sample

The first version scans the complete [Lichess April 2017 standard rated archive](https://database.lichess.org/) while keeping games where bytes 8–15 of SHA-256(the eight-character Lichess game ID), interpreted as an integer, are below 1 modulo 100. This selects about 1% of games throughout the month. An initial direct HTTP stream was interrupted after 7,995,296 games and was rejected. A resumable download on the local mining worker then verified the complete 3,481,200,992-byte compressed archive against Lichess's published SHA-256. Mining reads that compressed file as a stream; it never stages the much larger decompressed PGN. The temporary compressed cache is removed after the reviewed datasets are published and validated.

For selected games, the moving player's rating must be 1450–1550, the event must not be Bullet, and their clock before the move must be at least 15 seconds. A whole game is assigned to training or evaluation from a separate eight-byte part of the game hash, with 20% assigned to evaluation. The target is the human-played **source square**; destination and promotion piece are retained for audit, but this first CNN does not predict them.

Training keeps repeated positions and their played moves because they represent the source game's empirical move distribution. The evaluation cleanup removes exact duplicate 15-plane inputs, inputs present in the new training split, and inputs present in the existing five-million-row 2013 training set. The latter is checked with a private Kaggle export of SHA-256 hashes, without copying the legacy bitboards to the mining worker. The game-key split gives independence from the new 2017 training games; the 2013 archive is a different month and its exact input overlap is separately removed. Similar but nonidentical positions can still occur in both sets.

The general and 3–6-piece subsets each have distinct, private Kaggle training and evaluation dataset IDs. Each version carries aligned `.npy` shards, source-game hashes, ply and promotion metadata, checksums and build manifests. Published versions are immutable inputs to run configurations. The 2013 evaluation dataset is retained as a legacy artifact but must not be used for held-out model comparisons: 70.57% of its inputs exactly match 2013 training inputs.

## Build and review gates

1. Stream the archive with `mine_rated_pgn.py --input-url https://database.lichess.org/standard/lichess_db_standard_rated_2017-04.pgn.zst --sample-percent 1`. Require a complete manifest and the expected full-archive SHA-256.
2. Run `audit_position_overlap.py` against the general splits and `--external-training-hashes` from the private 2013 hash export. Require zero retained exact input overlap and zero game-key overlap.
3. Build 3–6-piece train and evaluation shards separately with `build_endgames.py`. Check array shapes, lengths, labels, legal decoded moves, game-key separation, shard hashes, and representative boards.
4. Record output bytes and the measured disk high-water mark on the mining worker. Publish the four datasets privately only after these checks pass. Kaggle's CLI [creates datasets privately by default](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md); omit `--public`.
5. Run the separate endgame configuration in pipeline-validation mode before any full fit. Validation limits the fit to one chunk, 50,000 rows and one epoch, and evaluates 1,000 held-out few-piece rows plus the simple-position benchmark.

The bounded sample is a first experimental dataset, not the entire population of 1500-rated games. Reusing the same game-hash split for a later version allows overlap checks against this version; it does not by itself make successive versions independent.

## Reviewed 12 November 2026 result

| Measure | Value |
| --- | ---: |
| Full PGNs scanned / hash-selected games | 11,348,506 / 113,638 |
| Provisional training / evaluation positions | 542,568 / 132,495 |
| Duplicate inputs within new training | 63,327 |
| New training positions also present in 2013 training | 76,218 |
| Evaluation inputs matching new or 2013 training | 20,769 |
| Repeated evaluation inputs removed | 450 |
| Clean general evaluation positions | 111,276 |
| 3–6-piece training / evaluation positions | 14,756 / 3,107 |
| Few-piece training / evaluation games | 1,114 / 267 |
| Cross-partition game-key overlap | 0 |
| Shard files verified against SHA-256 | 417 |
| Peak tracked local project-artifact disk use | 4,985,956,705 bytes (including the compressed archive and SQLite index) |

All 17,863 few-piece move records were checked against reconstructed boards. One training move was en passant; the board decoder needed to restore the omitted en passant square from the recorded pawn move and adjacent opposing pawn before the legal-move check. No other illegal move remained. The source PGN supplies the played moves; these checks verify encoding, alignment, and reconstruction, not that a human move was optimal. The full review report and disk monitor are kept outside Git under the local ignored `.tmp-april-2017` workspace folder.
