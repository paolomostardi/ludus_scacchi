"""Local position authoring, validation and model diagnostics."""
import argparse
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import chess

from Backend.model_evaluation.simple_positions import (
    CATALOG, audit_catalog, catalog_identity, load_catalog, normalize_case, prepare, score_predictions,
)


def save_case(path, case):
    catalog = load_catalog(path)
    case = normalize_case(case)
    if any(c["id"] == case["id"] or c["fen"].split()[:4] == case["fen"].split()[:4] for c in catalog["cases"]):
        raise ValueError("This ID or board position already exists.")
    catalog["cases"].append(case)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return case


def serve(path, port):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, payload, status=200):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/":
                data = Path(__file__).with_name("position_editor.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(data)
            elif self.path == "/api/catalog":
                catalog = load_catalog(path)
                self.respond({"identity": catalog_identity(catalog), "cases": catalog["cases"]})
            else:
                self.respond({"error": "Not found"}, 404)

        def do_POST(self):
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}:
                return self.respond({"error": "Use the local editor origin."}, 403)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 65536 or self.headers.get_content_type() != "application/json":
                    raise ValueError("Expected a JSON request of at most 64 KiB.")
                payload = json.loads(self.rfile.read(length))
                if self.path == "/api/board":
                    board = chess.Board(payload["fen"])
                    return self.respond({"fen": board.fen(), "valid": board.is_valid(),
                        "pieces": {chess.square_name(s): p.symbol() for s, p in board.piece_map().items()},
                        "legal_moves": [m.uci() for m in board.legal_moves]})
                if self.path not in {"/api/preview", "/api/add"}:
                    return self.respond({"error": "Not found"}, 404)
                case = normalize_case(payload)
                if self.path == "/api/add":
                    case = save_case(path, case)
                self.respond({"case": case, "san": [chess.Board(case["fen"]).san(chess.Move.from_uci(m)) for m in case["moves"]]})
            except (ValueError, KeyError, TypeError) as exc:
                self.respond({"error": str(exc)}, 400)

    # One request at a time prevents competing add requests from losing an edit.
    from http.server import HTTPServer
    print(f"Position editor: http://127.0.0.1:{port} (Ctrl+C to stop)", flush=True)
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    commands = parser.add_subparsers(dest="command", required=True)
    editor = commands.add_parser("serve")
    editor.add_argument("--port", type=int, default=8765)
    commands.add_parser("audit")
    add = commands.add_parser("add")
    add.add_argument("--id", required=True)
    add.add_argument("--fen", required=True)
    add.add_argument("--moves", nargs="+", required=True)
    add.add_argument("--category", choices=("mate_in_1", "free_queen", "other"), required=True)
    add.add_argument("--rationale", required=True)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--model", type=Path, required=True)
    evaluate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "serve":
        return serve(args.catalog, args.port)
    if args.command == "add":
        return print(json.dumps(save_case(args.catalog, {key: getattr(args, key) for key in ("id", "fen", "moves", "category", "rationale")}), indent=2))
    catalog = load_catalog(args.catalog)
    if args.command == "audit":
        return print(json.dumps(audit_catalog(catalog), indent=2))
    import keras
    model = keras.models.load_model(args.model, compile=False)
    x, _ = prepare(catalog)
    report = score_predictions(catalog, model.predict(x, batch_size=128, verbose=0))
    report["model_file"] = str(args.model.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"dataset": report["dataset"], "metrics": report["metrics"],
                      "by_category": report["by_category"], "orientation_top1_accuracy": report["orientation_top1_accuracy"]}, indent=2))


if __name__ == "__main__":
    main()
