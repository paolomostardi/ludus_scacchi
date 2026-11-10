"""Export validated positions for older CSV consumers; author the JSON catalog."""
import csv
from pathlib import Path

import chess

from Backend.model_evaluation.simple_positions import load_catalog


def main(output_path=None):
    path = Path(output_path) if output_path else Path.cwd() / "Backend/model_evaluation/simple_positions.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog()
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["FEN", "TargetSquare", "ID", "Category", "ExpectedMoves"])
        writer.writeheader()
        for case in catalog["cases"]:
            writer.writerow({"FEN": case["fen"], "TargetSquare": chess.Move.from_uci(case["moves"][0]).from_square,
                             "ID": case["id"], "Category": case["category"], "ExpectedMoves": " ".join(case["moves"])})
    print(f"Exported {len(catalog['cases'])} validated positions to {path}")
    return path


if __name__ == "__main__":
    main()
