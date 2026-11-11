"""Filter existing Ludus bitboards without changing their played-move targets.

Run independently of training. Source games must already be split before encoding
if these outputs will be used for independent train/evaluation measurements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_block(x, y):
    """Check encoding assumptions before counting occupancy or copying labels."""
    if not np.all((x == 0) | (x == 1)) or not np.all((y == 0) | (y == 1)):
        raise ValueError("Inputs and targets must contain finite binary values.")
    occupancy = x[:, :12].sum(axis=1)
    if np.any(occupancy > 1):
        raise ValueError("Multiple pieces occupy the same square.")
    if np.any(x[:, [5, 11]].sum(axis=(2, 3)) != 1):
        raise ValueError("Each position must contain exactly one king per color.")
    if np.any(y.sum(axis=(2, 3)) != 1):
        raise ValueError("Each target plane must contain exactly one square.")
    white_turn = x[:, 14, 0, 0].astype(bool)
    if np.any(x[:, 14] != white_turn[:, None, None]):
        raise ValueError("Side-to-move plane must be constant across the board.")
    own = np.where(white_turn[:, None, None], x[:, :6].sum(axis=1), x[:, 6:12].sum(axis=1))
    if np.any((own * y[:, 0]).sum(axis=(1, 2)) != 1):
        raise ValueError("Source target must contain a piece of the side to move.")
    return occupancy.sum(axis=(1, 2)).astype(np.int64)


def build_dataset(input_dir, output_dir, chunks, source_id, split,
                  min_pieces=3, max_pieces=6, shard_rows=100000, block_rows=4096):
    if not 2 <= min_pieces <= max_pieces <= 32:
        raise ValueError("Piece limits must satisfy 2 <= min <= max <= 32.")
    if shard_rows < 1 or block_rows < 1:
        raise ValueError("Shard and block sizes must be positive.")
    if not chunks or len(set(chunks)) != len(chunks) or any(i < 0 for i in chunks):
        raise ValueError("Provide distinct nonnegative chunk indices.")
    if not source_id.strip() or split not in {"training", "evaluation"}:
        raise ValueError("Provide a source identity and training/evaluation split.")
    input_dir, output_dir = Path(input_dir).resolve(), Path(output_dir).resolve()
    pairs = [(input_dir / f"chunk_{i}.npy", input_dir / f"chunk_{i}_y.npy") for i in chunks]
    for pair in pairs:
        for path in pair:
            if not path.is_file():
                raise FileNotFoundError(path)
    # Never overwrite another build or accidentally treat partial output as complete.
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": 1, "status": "building", "source_id": source_id, "split": split,
        "selection": {"min_pieces": min_pieces, "max_pieces": max_pieces, "includes_kings": True},
        "label_policy": "unchanged played moves; plane 0 is the source square",
        "split_policy": "provided source partition; game independence not verified by this builder",
        "input_rows": 0, "selected_rows": 0, "piece_counts": {}, "sources": [], "shards": [],
        "source_metadata_policy": "unknown until source chunks are inspected",
    }
    def save_manifest():
        (output_dir / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    buffers = [[], [], []]
    extra_suffixes = ("_game_keys", "_ply", "_promotion")
    extra_buffers = {suffix: [] for suffix in extra_suffixes}
    extra_policy = None
    buffered = 0
    target_planes = None

    def flush():
        nonlocal buffered
        index = len(manifest["shards"])
        entry = {"index": index, "rows": buffered, "files": {}}
        for parts, suffix in zip(buffers, ("", "_y", "_source_rows")):
            name = f"chunk_{index}{suffix}.npy"
            np.save(output_dir / name, np.concatenate(parts), allow_pickle=False)
            entry["files"][name] = {"sha256": sha256(output_dir / name)}
            parts.clear()
        if extra_policy:
            for suffix in extra_suffixes:
                name = f"chunk_{index}{suffix}.npy"
                np.save(output_dir / name, np.concatenate(extra_buffers[suffix]), allow_pickle=False)
                entry["files"][name] = {"sha256": sha256(output_dir / name)}
                extra_buffers[suffix].clear()
        manifest["shards"].append(entry)
        buffered = 0

    save_manifest()
    try:
        for source_index, (x_path, y_path) in enumerate(pairs):
            x = np.load(x_path, mmap_mode="r", allow_pickle=False)
            y = np.load(y_path, mmap_mode="r", allow_pickle=False)
            extra_paths = {suffix: x_path.with_name(x_path.stem + suffix + ".npy")
                           for suffix in extra_suffixes}
            present = tuple(path.is_file() for path in extra_paths.values())
            if len(set(present)) != 1 or (extra_policy is not None and present[0] != extra_policy):
                raise ValueError("All source chunks must consistently include game, ply, and promotion metadata.")
            extra_policy = present[0]
            manifest["source_metadata_policy"] = ("game keys, ply and promotion preserved" if extra_policy
                                                  else "legacy arrays without per-move metadata")
            extra = {suffix: np.load(path, mmap_mode="r", allow_pickle=False)
                     for suffix, path in extra_paths.items()} if extra_policy else {}
            if x.ndim != 4 or x.shape[1:] != (15, 8, 8):
                raise ValueError(f"{x_path.name}: expected (N,15,8,8).")
            if y.ndim != 4 or y.shape[1] not in (1, 2) or y.shape[2:] != (8, 8) or len(x) != len(y):
                raise ValueError(f"{y_path.name}: expected aligned (N,1 or 2,8,8) targets.")
            if target_planes is not None and y.shape[1] != target_planes:
                raise ValueError("All source chunks must use the same number of target planes.")
            if extra_policy:
                if any(array.ndim != 1 or len(array) != len(x) for array in extra.values()):
                    raise ValueError("Source metadata must have one value per position.")
                if not np.isin(extra["_promotion"], (0, 2, 3, 4, 5)).all():
                    raise ValueError("Promotion metadata must use 0 or a valid promoted-piece type.")
            target_planes = y.shape[1]
            record = {"chunk_index": chunks[source_index], "rows": len(x), "selected_rows": 0,
                      "input_file": str(x_path), "target_file": str(y_path),
                      "input_sha256": sha256(x_path), "target_sha256": sha256(y_path)}
            if extra_policy:
                record["metadata_files"] = {
                    suffix: {"file": str(path), "sha256": sha256(path)}
                    for suffix, path in extra_paths.items()
                }
            manifest["sources"].append(record)
            manifest["input_rows"] += len(x)
            for start in range(0, len(x), block_rows):
                xb, yb = x[start:start + block_rows], y[start:start + block_rows]
                counts = validate_block(xb, yb)
                chosen = np.flatnonzero((counts >= min_pieces) & (counts <= max_pieces))
                for count, frequency in zip(*np.unique(counts[chosen], return_counts=True)):
                    key = str(count)
                    manifest["piece_counts"][key] = manifest["piece_counts"].get(key, 0) + int(frequency)
                record["selected_rows"] += len(chosen)
                manifest["selected_rows"] += len(chosen)
                while len(chosen):
                    take = chosen[:shard_rows - buffered]
                    buffers[0].append(xb[take].astype(np.bool_))
                    buffers[1].append(yb[take].astype(np.uint8))
                    buffers[2].append(np.column_stack((np.full(len(take), source_index, dtype=np.int64), start + take)))
                    if extra_policy:
                        for suffix in extra_suffixes:
                            extra_buffers[suffix].append(extra[suffix][start + take])
                    buffered += len(take)
                    chosen = chosen[len(take):]
                    if buffered == shard_rows:
                        flush()
            del x, y
            del extra
        if buffered:
            flush()
        if not manifest["selected_rows"]:
            raise ValueError("No positions matched the piece limits; no usable dataset was produced.")
        manifest["status"] = "complete"
        save_manifest()
        return manifest
    except Exception as exc:
        manifest["status"] = "failed"
        manifest["error"] = str(exc)
        save_manifest()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--chunks", type=int, nargs="+", required=True)
    parser.add_argument("--source-id", required=True, help="Dataset identity, version, and source partition.")
    parser.add_argument("--split", choices=("training", "evaluation"), required=True)
    parser.add_argument("--min-pieces", type=int, default=3)
    parser.add_argument("--max-pieces", type=int, default=6)
    parser.add_argument("--shard-rows", type=int, default=100000)
    parser.add_argument("--block-rows", type=int, default=4096)
    args = parser.parse_args()
    result = build_dataset(**vars(args))
    print(json.dumps({key: result[key] for key in ("status", "input_rows", "selected_rows", "piece_counts")}, indent=2))


if __name__ == "__main__":
    main()
