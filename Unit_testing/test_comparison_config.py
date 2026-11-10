"""Verify the depth-only experiment reaches the staged Kaggle notebooks."""
import ast
import json
import tempfile
import unittest
from pathlib import Path

from Backend.training_pipeline.configuration import load_config
from Backend.training_pipeline import run_batch


class ComparisonConfigTests(unittest.TestCase):
    def test_depth_only_and_staging(self):
        baseline = load_config()
        path = run_batch.REPO_ROOT / "Backend/training_pipeline/configs/source_resnet_6x64.json"
        comparison = load_config(path)
        self.assertEqual(comparison["architecture"]["parameters"]["residual_blocks"], 6)
        expected = json.loads(json.dumps(baseline))
        expected["architecture"]["parameters"]["residual_blocks"] = 6
        self.assertEqual(comparison, expected)
        args = run_batch.build_parser().parse_args(["--config", str(path)])
        args.run_config = comparison
        args.repository_revision = "a" * 40
        args.training_dataset = comparison["training_dataset"]
        args.evaluation_dataset = comparison["evaluation_dataset"]
        with tempfile.TemporaryDirectory() as directory:
            specs = run_batch.stage_kernels(args, Path(directory))
            for spec in specs.values():
                notebook = json.loads((spec["directory"] / spec["metadata"]["code_file"]).read_text())
                tree = ast.parse(run_batch.notebook_source(notebook["cells"][0]))
                env = ast.literal_eval(tree.body[-1].value.args[0])
                self.assertEqual(json.loads(env["LUDUS_RUN_CONFIG"]), comparison)
                self.assertEqual(env["LUDUS_PIPELINE_MODE"], "training")
            self.assertEqual(specs["fit"]["metadata"]["dataset_sources"], [comparison["training_dataset"]])


if __name__ == "__main__":
    unittest.main()
