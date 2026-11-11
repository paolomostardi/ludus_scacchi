"""Stream a Lichess PGN (or a bounded .zst prefix) into split bitboard shards.

This is a data-mining command, independent of Kaggle training orchestration.
For a prefix pilot pass --partial: the last incomplete PGN is discarded.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

import chess
import chess.pgn
import numpy as np

from Backend.data_pipeline.from_PGN_generate_bitboards import (
    from_chess_board_create_bit_boards,
    from_chess_move_create_bitboard,
)

SOURCE_NAME = "lichess_db_standard_rated_2017-04.pgn.zst"
SOURCE_SHA256 = "559222b0e933bc02281643724fbd9bd46690074b10d784c4f264e0bff6c5992c"
CLOCK_PATTERN = re.compile(r"\[%clk\s+\d+:\d\d:\d\d(?:\.\d+)?\]")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pgn_blocks(stream, *, partial: bool):
    """Yield only complete games, bounded by the next Event header."""
    lines = []
    try:
        for line in stream:
            if line.startswith("[Event ") and lines:
                yield "".join(lines)
                lines = []
            lines.append(line)
    except Exception as exc:
        if not partial:
            raise
        # A truncated zstd prefix can end in the middle of the last game.
        if "zstandard" not in type(exc).__module__.lower() and not isinstance(exc, EOFError):
            raise
    if lines and not partial:
        yield "".join(lines)


def initial_clock(header: str) -> float | None:
    match = re.fullmatch(r"(\d+)\+(\d+)", header or "")
    if not match or int(match.group(1)) <= 0:
        return None
    return float(match.group(1))


def rating(header: str) -> int | None:
    try:
        value = int(header)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def event_class(header: str) -> str | None:
    event = (header or "").casefold()
    for label in ("ultrabullet", "bullet", "blitz", "rapid", "classical", "correspondence"):
        if re.search(rf"\b{label}\b", event):
            return label
    return None


def game_key(game: chess.pgn.Game) -> bytes:
    site = game.headers.get("Site", "")
    # Lichess's Site header contains the stable game ID. Reject missing IDs
    # rather than silently split on a mutable PGN body.
    if not re.fullmatch(r"https?://lichess\.org/[A-Za-z0-9]{8}(?:/[A-Za-z0-9]+)?", site):
        raise ValueError(f"Missing or unsupported Lichess game Site: {site!r}")
    return hashlib.sha256(site.split("/")[3][:8].encode("ascii")).digest()


def game_split(key: bytes, *, eval_percent: int) -> str:
    if not 1 <= eval_percent <= 50:
        raise ValueError("eval_percent must be between 1 and 50")
    return "evaluation" if int.from_bytes(key[:8], "big") % 100 < eval_percent else "training"


class ShardWriter:
    def __init__(self, root: Path, split: str, shard_rows: int):
        self.root = root / split
        self.root.mkdir(parents=True, exist_ok=False)
        self.shard_rows = shard_rows
        self.buffers = ([], [], [], [], [])
        self.shards = []
        self.rows = 0

    def append(self, x, y, key: bytes, ply: int, promotion: int = 0):
        for buffer, item in zip(self.buffers, (x, y, key, ply, promotion)):
            buffer.append(item)
        self.rows += 1
        if len(self.buffers[0]) == self.shard_rows:
            self.flush()

    def flush(self):
        if not self.buffers[0]:
            return
        index = len(self.shards)
        arrays = (
            np.asarray(self.buffers[0], dtype=np.bool_),
            np.asarray(self.buffers[1], dtype=np.uint8),
            np.asarray(self.buffers[2], dtype="S32"),
            np.asarray(self.buffers[3], dtype=np.uint16),
            np.asarray(self.buffers[4], dtype=np.uint8),
        )
        entry = {"index": index, "rows": len(arrays[0]), "files": {}}
        for array, suffix in zip(arrays, ("", "_y", "_game_keys", "_ply", "_promotion")):
            name = f"chunk_{index}{suffix}.npy"
            path = self.root / name
            np.save(path, array, allow_pickle=False)
            entry["files"][name] = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
        self.shards.append(entry)
        for buffer in self.buffers:
            buffer.clear()


def mine(input_path: Path, output_dir: Path, *, partial: bool = False,
         min_rating: int = 1450, max_rating: int = 1550,
         min_clock: float = 15, eval_percent: int = 20,
         shard_rows: int = 10000, max_games: int | None = None):
    input_path = Path(input_path).resolve()
    output_dir = Path(output_dir).resolve()
    if not input_path.is_file() or output_dir.exists():
        raise FileNotFoundError(input_path) if not input_path.is_file() else FileExistsError(output_dir)
    if not (0 < min_rating <= max_rating and min_clock >= 0 and shard_rows > 0):
        raise ValueError("Invalid filter or shard size")
    if max_games is not None and max_games < 1:
        raise ValueError("max_games must be positive")
    game_split(b"\0" * 32, eval_percent=eval_percent)

    output_dir.mkdir(parents=True)
    writers = {split: ShardWriter(output_dir, split, shard_rows)
               for split in ("training", "evaluation")}
    counts = Counter()
    manifest = {
        "schema_version": 1, "status": "building", "source_file": input_path.name,
        "source_bytes": input_path.stat().st_size, "source_sha256": file_sha256(input_path),
        "source_complete": not partial and max_games is None,
        "max_games": max_games,
        "expected_full_archive_sha256": SOURCE_SHA256 if input_path.name.startswith(SOURCE_NAME) else None,
        "selection": {"min_rating": min_rating, "max_rating": max_rating,
                      "rating_is_mover": True, "exclude_bullet": True,
                      "min_before_move_clock_seconds": min_clock},
        "split_policy": f"SHA-256(Lichess game ID), first 8 bytes modulo 100; <{eval_percent} evaluation",
        "encoding": "Ludus 15x8x8 inputs and 2x8x8 played-move targets",
        "shard_rows": shard_rows, "counts": {}, "splits": {},
    }

    def save_manifest(status):
        manifest["status"] = status
        manifest["counts"] = dict(sorted(counts.items()))
        manifest["splits"] = {split: {"rows": writer.rows, "shards": writer.shards}
                              for split, writer in writers.items()}
        (output_dir / "dataset_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    save_manifest("building")
    try:
        with input_path.open("rb") as raw:
            if ".zst" in input_path.suffixes:
                import zstandard as zstd
                binary = zstd.ZstdDecompressor().stream_reader(raw)
            else:
                binary = raw
            with io.TextIOWrapper(binary, encoding="utf-8", errors="strict") as stream:
                for block in pgn_blocks(stream, partial=partial):
                    if max_games is not None and counts["games_scanned"] >= max_games:
                        break
                    counts["games_scanned"] += 1
                    game = chess.pgn.read_game(io.StringIO(block))
                    if game is None or game.errors:
                        counts["games_parse_failed"] += 1
                        continue
                    try:
                        key = game_key(game)
                    except ValueError:
                        counts["games_missing_id"] += 1
                        continue
                    category = event_class(game.headers.get("Event", ""))
                    if category in ("bullet", "ultrabullet"):
                        counts["games_bullet"] += 1
                        continue
                    if category is None:
                        counts["games_unknown_event"] += 1
                        continue
                    counts[f"games_event_{category}"] += 1
                    clock0 = initial_clock(game.headers.get("TimeControl", ""))
                    if clock0 is None:
                        counts["games_missing_initial_clock"] += 1
                        continue
                    split = game_split(key, eval_percent=eval_percent)
                    counts[f"games_{split}"] += 1
                    last_clock = {chess.WHITE: clock0, chess.BLACK: clock0}
                    mover_rating = {chess.WHITE: rating(game.headers.get("WhiteElo")),
                                    chess.BLACK: rating(game.headers.get("BlackElo"))}
                    board = game.board()
                    for ply, node in enumerate(game.mainline(), start=1):
                        color = board.turn
                        before = last_clock[color]
                        after = node.clock() if CLOCK_PATTERN.search(node.comment) else None
                        counts["moves_scanned"] += 1
                        if after is None:
                            counts["moves_missing_after_clock"] += 1
                        if mover_rating[color] is not None and min_rating <= mover_rating[color] <= max_rating:
                            counts["moves_rating_match"] += 1
                            if before is None:
                                counts["moves_missing_before_clock"] += 1
                            elif before < min_clock:
                                counts["moves_low_clock"] += 1
                            else:
                                x = from_chess_board_create_bit_boards(board)
                                y = from_chess_move_create_bitboard(node.move)
                                writers[split].append(x, y, key, ply, node.move.promotion or 0)
                                counts[f"rows_{split}"] += 1
                        last_clock[color] = after
                        board.push(node.move)
        for writer in writers.values():
            writer.flush()
        save_manifest("complete")
        return manifest
    except Exception as exc:
        manifest["error"] = str(exc)
        save_manifest("failed")
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--partial", action="store_true")
    parser.add_argument("--min-rating", type=int, default=1450)
    parser.add_argument("--max-rating", type=int, default=1550)
    parser.add_argument("--min-clock", type=float, default=15)
    parser.add_argument("--eval-percent", type=int, default=20)
    parser.add_argument("--shard-rows", type=int, default=10000)
    parser.add_argument("--max-games", type=int)
    args = parser.parse_args()
    result = mine(args.input, args.output_dir, partial=args.partial,
                  min_rating=args.min_rating, max_rating=args.max_rating,
                  min_clock=args.min_clock, eval_percent=args.eval_percent,
                  shard_rows=args.shard_rows, max_games=args.max_games)
    print(json.dumps({"status": result["status"], "counts": result["counts"],
                      "splits": {k: v["rows"] for k, v in result["splits"].items()}}, indent=2))


if __name__ == "__main__":
    main()
