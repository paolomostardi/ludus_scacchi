"""Validated source-square benchmark and prediction diagnostics."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import chess
import numpy as np

from Backend.data_pipeline import from_PGN_generate_bitboards as encoder

CATALOG = Path(__file__).with_name("simple_positions.json")


def obvious_moves(board, category):
    result = []
    for move in board.legal_moves:
        after = board.copy()
        after.push(move)
        if category == "mate_in_1" and after.is_checkmate():
            result.append(move)
        elif category == "free_queen":
            victim = board.piece_at(move.to_square)
            if victim and victim.piece_type == chess.QUEEN and not after.is_attacked_by(after.turn, move.to_square):
                result.append(move)
    return result


def normalize_case(case):
    board = chess.Board(case["fen"])
    if not board.is_valid() or board.is_game_over():
        raise ValueError("Position must be legal and have a move to play.")
    category = case["category"]
    if category not in {"mate_in_1", "free_queen", "other"}:
        raise ValueError("Unknown category.")
    supplied = case.get("moves", [])
    if isinstance(supplied, str):
        supplied = supplied.replace(",", " ").split()
    if not supplied:
        raise ValueError("Enter at least one expected move in SAN or UCI.")
    moves = []
    for text in supplied:
        try:
            move = chess.Move.from_uci(text)
        except ValueError:
            move = board.parse_san(text)
        piece = board.piece_at(move.from_square)
        if piece and piece.piece_type == chess.PAWN and chess.square_rank(move.to_square) in (0, 7) and not move.promotion:
            raise ValueError(f"Choose a promotion piece: {text}q (queen), {text}r (rook), {text}b (bishop), or {text}n (knight).")
        if move not in board.legal_moves:
            raise ValueError(f"Illegal move: {text}")
        moves.append(move)
    if category != "other":
        solutions = obvious_moves(board, category)
        if not solutions or not set(moves) <= set(solutions):
            raise ValueError("Expected move does not satisfy the chosen theme.")
        # Accept every source that delivers mate/captures the undefended queen.
        moves = solutions
    result = dict(case)
    result["fen"] = board.fen()
    result["moves"] = sorted({move.uci() for move in moves})
    for key in ("id", "rationale"):
        if not isinstance(result.get(key), str) or not result[key].strip():
            raise ValueError(f"{key} is required.")
    result.setdefault("base_id", result["id"])
    result.setdefault("variant", "original")
    return result


def load_catalog(path=CATALOG):
    catalog = json.loads(Path(path).read_text(encoding="utf-8"))
    if catalog.get("schema_version") != 2 or not catalog.get("cases"):
        raise ValueError("Expected a nonempty schema-version-2 catalog.")
    cases = [normalize_case(case) for case in catalog["cases"]]
    ids, positions = set(), set()
    for case in cases:
        key = " ".join(case["fen"].split()[:4])
        if case["id"] in ids or key in positions:
            raise ValueError("Duplicate position ID or board position.")
        ids.add(case["id"])
        positions.add(key)
    catalog["cases"] = cases
    return catalog


def catalog_identity(catalog):
    data = json.dumps(catalog, sort_keys=True, separators=(",", ":")).encode()
    return {"version": catalog["version"], "sha256": hashlib.sha256(data).hexdigest(),
            "sample_count": len(catalog["cases"]),
            "base_position_count": len({case["base_id"] for case in catalog["cases"]})}


def expected_indices(case):
    return sorted({encoder.chess_square_to_source_index(chess.Move.from_uci(move).from_square)
                   for move in case["moves"]})


def audit_catalog(catalog):
    cases = catalog["cases"]
    return {"dataset": catalog_identity(catalog),
            "side_to_move": dict(Counter("white" if chess.Board(c["fen"]).turn else "black" for c in cases)),
            "categories": dict(Counter(c["category"] for c in cases)),
            "piece_counts": dict(sorted(Counter(len(chess.Board(c["fen"]).piece_map()) for c in cases).items())),
            "cases_with_multiple_accepted_sources": sum(len(expected_indices(c)) > 1 for c in cases),
            "cases_with_only_one_legal_source": sum(len({m.from_square for m in chess.Board(c["fen"]).legal_moves}) == 1 for c in cases)}


def prepare(catalog):
    cases = catalog["cases"]
    x = np.stack([encoder.from_chess_board_create_bit_boards(chess.Board(case["fen"])) for case in cases])
    # Representative one-hot labels for compatibility. Set-aware scoring below
    # gives credit to any accepted source when a position has several solutions.
    y = np.zeros((len(cases), 64), dtype=np.float32)
    for row, case in enumerate(cases):
        y[row, expected_indices(case)[0]] = 1
    return x, y


def score_predictions(catalog, probabilities):
    probabilities = np.asarray(probabilities, dtype=float)
    if probabilities.shape != (len(catalog["cases"]), 64):
        raise ValueError("Expected one 64-square prediction for every position.")
    if not np.isfinite(probabilities).all() or (probabilities < 0).any() or not np.allclose(probabilities.sum(axis=1), 1, atol=1e-4):
        raise ValueError("Predictions must be finite normalized probabilities.")
    rows = []
    orientations = {"identity": 0, "flip_files": 0, "flip_ranks": 0, "rotate_180": 0}
    for case, p in zip(catalog["cases"], probabilities):
        board = chess.Board(case["fen"])
        expected = expected_indices(case)
        order = np.argsort(-p, kind="stable")
        legal = {encoder.chess_square_to_source_index(move.from_square) for move in board.legal_moves}
        masked = next(int(i) for i in order if i in legal)
        best = int(order[0])
        for name, transform in (("identity", lambda i: i), ("flip_files", lambda i: i ^ 7),
                                ("flip_ranks", lambda i: i ^ 56), ("rotate_180", lambda i: i ^ 63)):
            orientations[name] += int(best in {transform(i) for i in expected})
        def square(index):
            return chess.square_name(encoder.source_index_to_chess_square(int(index)))
        mass = min(1.0, float(p[expected].sum()))
        rows.append({"id": case["id"], "base_id": case["base_id"], "category": case["category"],
                     "fen": case["fen"], "rationale": case["rationale"], "expected_moves": case["moves"],
                     "expected_moves_san": [board.san(chess.Move.from_uci(move)) for move in case["moves"]],
                     "expected_sources": [square(i) for i in expected], "predicted_source": square(best),
                     "correct": best in expected, "top3_correct": bool(set(order[:3]) & set(expected)),
                     "expected_probability": mass, "best_expected_rank": min(int(np.where(order == i)[0][0]) + 1 for i in expected),
                     "loss": float(-np.log(max(mass, np.finfo(float).tiny))),
                     "legal_source_probability": float(p[list(legal)].sum()),
                     "predicted_source_is_legal": best in legal,
                     "legal_masked_source": square(masked), "legal_masked_correct": masked in expected,
                     "top5": [{"square": square(i), "probability": float(p[i])} for i in order[:5]]})
    def summary(selected):
        return {"accuracy": float(np.mean([r["correct"] for r in selected])),
                "top3_accuracy": float(np.mean([r["top3_correct"] for r in selected])),
                "loss": float(np.mean([r["loss"] for r in selected])), "sample_count": len(selected),
                "legal_masked_accuracy": float(np.mean([r["legal_masked_correct"] for r in selected]))}
    return {"dataset": catalog_identity(catalog), "metrics": summary(rows),
            "loss_definition": "negative log of summed probability on accepted source squares",
            "source_only_limitation": "Correct source does not establish the destination or move quality.",
            "by_category": {name: summary([r for r in rows if r["category"] == name])
                            for name in sorted({r["category"] for r in rows})},
            "orientation_top1_accuracy": {name: count / len(rows) for name, count in orientations.items()},
            "positions": rows}
