"""Download a bounded prefix of one Lichess standard monthly PGN archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path


def download(month: str, output: Path, max_bytes: int):
    if not re.fullmatch(r"20\d\d-(0[1-9]|1[0-2])", month):
        raise ValueError("month must use YYYY-MM")
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(output)
    url = f"https://database.lichess.org/standard/lichess_db_standard_rated_{month}.pgn.zst"
    request = urllib.request.Request(
        url, headers={"Range": f"bytes=0-{max_bytes - 1}",
                      "User-Agent": "Ludus-dataset-pilot/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        expected_range = re.fullmatch(r"bytes 0-(\d+)/(\d+)", response.headers.get("Content-Range", ""))
        if response.status != 206 or not expected_range:
            raise RuntimeError("Source did not honor a bounded HTTP Range request.")
        expected_bytes = int(expected_range.group(1)) + 1
        if expected_bytes > max_bytes:
            raise RuntimeError("Source returned more bytes than requested.")
        output.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        with output.open("xb") as target:
            remaining = expected_bytes
            while remaining:
                block = response.read(min(65536, remaining))
                if not block:
                    raise EOFError("Source ended before the requested prefix was complete.")
                target.write(block)
                digest.update(block)
                remaining -= len(block)
    return {"url": url, "prefix_bytes": output.stat().st_size,
            "archive_bytes": int(expected_range.group(2)),
            "prefix_sha256": digest.hexdigest(), "path": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", default="2017-04")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-bytes", type=int, default=4 * 1024 * 1024)
    args = parser.parse_args()
    print(json.dumps(download(args.month, args.output, args.max_bytes), indent=2))


if __name__ == "__main__":
    main()
