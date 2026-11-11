"""Offline tests of filtering, source traceability, and rejected corrupt input."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from Backend.data_pipeline.build_endgames import build_dataset, sha256


class EndgameDatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        self.output = self.root / "output"
        self.x = np.zeros((6, 15, 8, 8), dtype=bool)
        self.y = np.zeros((6, 2, 8, 8), dtype=np.uint8)
        # Three through eight pieces, and a source square owned by the active side.
        for i in range(6):
            self.x[i, 5, 7, 4] = self.x[i, 11, 0, 4] = True
            self.x[i, 0, 6, :i + 1] = True
            self.x[i, 14] = True
            self.y[i, 0, 6, 0] = self.y[i, 1, 5, 0] = 1

    def write(self, index=0):
        np.save(self.inputs / f"chunk_{index}.npy", self.x)
        np.save(self.inputs / f"chunk_{index}_y.npy", self.y)

    def build(self, **kwargs):
        return build_dataset(self.inputs, self.output, source_id="fixture-v1",
                             split="training", **{"chunks": [0], **kwargs})

    def test_selection_shards_and_provenance(self):
        self.write()
        self.write(1)
        result = self.build(chunks=[0, 1], shard_rows=3, block_rows=2)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["selected_rows"], 8)
        self.assertEqual(result["piece_counts"], {"3": 2, "4": 2, "5": 2, "6": 2})
        self.assertEqual([s["rows"] for s in result["shards"]], [3, 3, 2])
        for shard in result["shards"]:
            i = shard["index"]
            x = np.load(self.output / f"chunk_{i}.npy")
            y = np.load(self.output / f"chunk_{i}_y.npy")
            rows = np.load(self.output / f"chunk_{i}_source_rows.npy")
            np.testing.assert_array_equal(x, self.x[rows[:, 1]])
            np.testing.assert_array_equal(y, self.y[rows[:, 1]])
            for name, info in shard["files"].items():
                self.assertEqual(sha256(self.output / name), info["sha256"])
        self.assertEqual(result["sources"][0]["input_sha256"], sha256(self.inputs / "chunk_0.npy"))

    def test_black_to_move_and_piece_boundaries(self):
        self.x[:, 14] = False
        self.y[:, 0] = 0
        self.y[:, 0, 0, 4] = 1
        self.write()
        result = self.build(min_pieces=4, max_pieces=5)
        self.assertEqual(result["selected_rows"], 2)

    def test_invalid_values_kings_overlap_labels_and_turn(self):
        originals = self.x.copy(), self.y.copy()
        for corruption in ("nan", "king", "overlap", "label", "ownership", "turn", "length"):
            with self.subTest(corruption=corruption):
                self.x, self.y = originals[0].astype(float), originals[1].copy()
                self.output = self.root / corruption
                if corruption == "nan": self.x[0, 0, 0, 0] = np.nan
                if corruption == "king": self.x[0, 5] = 0
                if corruption == "overlap": self.x[0, 1, 6, 0] = 1
                if corruption == "label": self.y[0, 0] = 0
                if corruption == "ownership": self.y[0, 0] = self.x[0, 11]
                if corruption == "turn": self.x[0, 14, 0, 0] = 0
                if corruption == "length": self.y = self.y[:-1]
                self.write()
                with self.assertRaises(ValueError): self.build()
                self.assertEqual(json.loads((self.output / "dataset_manifest.json").read_text())["status"], "failed")

    def test_empty_selection_and_existing_destination(self):
        self.write()
        with self.assertRaisesRegex(ValueError, "No positions"):
            self.build(min_pieces=9, max_pieces=10)
        with self.assertRaises(FileExistsError): self.build()

    def test_duplicate_and_missing_chunks(self):
        self.write()
        with self.assertRaises(ValueError): self.build(chunks=[0, 0])
        with self.assertRaises(FileNotFoundError): self.build(chunks=[1])
        self.assertFalse(self.output.exists())

    def test_optional_game_and_promotion_metadata_follows_selected_rows(self):
        self.write()
        keys = np.asarray([bytes([i + 1]) * 32 for i in range(6)], dtype="S32")
        ply = np.arange(1, 7, dtype=np.uint16)
        promotion = np.asarray([0, 0, 0, 5, 0, 0], dtype=np.uint8)
        for suffix, values in (("_game_keys", keys), ("_ply", ply),
                               ("_promotion", promotion)):
            np.save(self.inputs / f"chunk_0{suffix}.npy", values)
        result = self.build(shard_rows=3, block_rows=2)
        self.assertEqual(result["selected_rows"], 4)
        for shard in result["shards"]:
            i = shard["index"]
            rows = np.load(self.output / f"chunk_{i}_source_rows.npy")[:, 1]
            for suffix, values in (("_game_keys", keys), ("_ply", ply),
                                   ("_promotion", promotion)):
                np.testing.assert_array_equal(np.load(self.output / f"chunk_{i}{suffix}.npy"), values[rows])


if __name__ == "__main__":
    unittest.main()
