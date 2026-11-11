"""Disk-backed exact encoded-position audit and optional evaluation cleanup.

Only identical 15-plane inputs are counted. This cannot establish game-level
independence for legacy datasets without game IDs. New mined shards include
game keys, which are checked when creating cleaned evaluation shards.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

import numpy as np

from Backend.data_pipeline.mine_rated_pgn import ShardWriter


def chunk_paths(directory: Path) -> list[Path]:
    paths = [p for p in directory.iterdir() if re.fullmatch(r"chunk_\d+\.npy", p.name)]
    return sorted(paths, key=lambda p: int(p.stem.split("_")[1]))


def input_hash(row) -> bytes:
    return hashlib.sha256(np.ascontiguousarray(row, dtype=np.bool_).tobytes()).digest()


def audit(training_inputs: list[Path], evaluation_inputs: list[Path],
          index_path: Path, *, cleaned_dir: Path | None = None,
          shard_rows: int = 10000, block_rows: int = 4096):
    if not training_inputs or not evaluation_inputs or index_path.exists():
        raise ValueError("Provide both input lists and a new SQLite index path")
    if cleaned_dir is not None and cleaned_dir.exists():
        raise FileExistsError(cleaned_dir)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(index_path)
    db.execute("CREATE TABLE train_hashes (hash BLOB PRIMARY KEY) WITHOUT ROWID")
    db.execute("CREATE TABLE eval_hashes (hash BLOB PRIMARY KEY) WITHOUT ROWID")
    db.execute("CREATE TABLE train_games (game_key BLOB PRIMARY KEY) WITHOUT ROWID")
    counts = {"training_rows": 0, "training_duplicate_rows": 0,
              "evaluation_rows": 0, "evaluation_overlap_rows": 0,
              "evaluation_duplicate_rows": 0, "evaluation_kept_rows": 0,
              "evaluation_game_overlap_rows": 0}
    writer = ShardWriter(cleaned_dir, "evaluation", shard_rows) if cleaned_dir else None
    try:
        for path in training_inputs:
            x = np.load(path, mmap_mode="r", allow_pickle=False)
            if x.ndim != 4 or x.shape[1:] != (15, 8, 8):
                raise ValueError(f"Bad input shape: {path}")
            keys_path = path.with_name(path.stem + "_game_keys.npy")
            keys = np.load(keys_path, mmap_mode="r", allow_pickle=False) if keys_path.exists() else None
            if keys is not None and len(keys) != len(x):
                raise ValueError(f"Misaligned game keys: {keys_path}")
            for start in range(0, len(x), block_rows):
                for offset, row in enumerate(x[start:start + block_rows]):
                    counts["training_rows"] += 1
                    before = db.total_changes
                    db.execute("INSERT OR IGNORE INTO train_hashes VALUES (?)", (input_hash(row),))
                    if db.total_changes == before:
                        counts["training_duplicate_rows"] += 1
                    if keys is not None:
                        db.execute("INSERT OR IGNORE INTO train_games VALUES (?)", (bytes(keys[start + offset]),))
                db.commit()
        for path in evaluation_inputs:
            x = np.load(path, mmap_mode="r", allow_pickle=False)
            if x.ndim != 4 or x.shape[1:] != (15, 8, 8):
                raise ValueError(f"Bad input shape: {path}")
            if writer:
                y = np.load(path.with_name(path.stem + "_y.npy"), mmap_mode="r", allow_pickle=False)
                keys = np.load(path.with_name(path.stem + "_game_keys.npy"), mmap_mode="r", allow_pickle=False)
                ply = np.load(path.with_name(path.stem + "_ply.npy"), mmap_mode="r", allow_pickle=False)
                promotion = np.load(path.with_name(path.stem + "_promotion.npy"), mmap_mode="r", allow_pickle=False)
                if any(len(a) != len(x) for a in (y, keys, ply, promotion)):
                    raise ValueError(f"Misaligned evaluation arrays: {path}")
            for start in range(0, len(x), block_rows):
                for offset, row in enumerate(x[start:start + block_rows]):
                    i = start + offset
                    counts["evaluation_rows"] += 1
                    digest = input_hash(row)
                    if db.execute("SELECT 1 FROM train_hashes WHERE hash=?", (digest,)).fetchone():
                        counts["evaluation_overlap_rows"] += 1
                        continue
                    if writer and db.execute("SELECT 1 FROM train_games WHERE game_key=?", (bytes(keys[i]),)).fetchone():
                        counts["evaluation_game_overlap_rows"] += 1
                        continue
                    before = db.total_changes
                    db.execute("INSERT OR IGNORE INTO eval_hashes VALUES (?)", (digest,))
                    if db.total_changes == before:
                        counts["evaluation_duplicate_rows"] += 1
                        continue
                    counts["evaluation_kept_rows"] += 1
                    if writer:
                        writer.append(row, y[i], bytes(keys[i]), int(ply[i]), int(promotion[i]))
                db.commit()
        if writer:
            writer.flush()
            report = {"status": "complete", "counts": counts,
                      "evaluation_shards": writer.shards,
                      "training_inputs": [str(p) for p in training_inputs],
                      "evaluation_inputs": [str(p) for p in evaluation_inputs]}
            (cleaned_dir / "overlap_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return counts
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-dir", type=Path, required=True)
    parser.add_argument("--evaluation-dir", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--cleaned-dir", type=Path)
    parser.add_argument("--shard-rows", type=int, default=10000)
    args = parser.parse_args()
    result = audit(chunk_paths(args.training_dir), chunk_paths(args.evaluation_dir),
                   args.index, cleaned_dir=args.cleaned_dir, shard_rows=args.shard_rows)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
