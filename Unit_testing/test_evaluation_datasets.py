import tempfile
import unittest
from pathlib import Path

from Backend.model_evaluation.evaluation_datasets import find_evaluation_shards


class EvaluationDatasetTests(unittest.TestCase):
    def test_new_shards_and_legacy_layout(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            modern = root / "datasets" / "april2017-general-eval-v1"
            modern.mkdir(parents=True)
            for number in (1, 0):
                (modern / f"chunk_{number}.npy").touch()
                (modern / f"chunk_{number}_y.npy").touch()
            label, pairs = find_evaluation_shards(root, "paolomostardi/april2017-general-eval-v1")
            self.assertEqual(label, "april2017_general_eval_v1")
            self.assertEqual([pair[0].name for pair in pairs], ["chunk_0.npy", "chunk_1.npy"])
            legacy = root / "datasets" / "eval-training-2013-chunk-9" / "my_processed_chunks" / "2013-01"
            legacy.mkdir(parents=True)
            (legacy / "chunk_6_x.npy").touch()
            (legacy / "chunk_6_y.npy").touch()
            self.assertEqual(find_evaluation_shards(root, "paolomostardi/eval-training-2013-chunk-9")[0], "2013_01")


if __name__ == "__main__":
    unittest.main()
