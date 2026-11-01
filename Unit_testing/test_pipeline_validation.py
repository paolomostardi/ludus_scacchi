"""Offline checks for staged modes and actual notebook workload boundaries."""
import ast
import contextlib
import io
import json
import os
import sys
import types
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import numpy as np
from Backend.training_pipeline import run_batch

ROOT = Path(__file__).resolve().parents[1]


def source(filename, index):
    nb = json.loads((ROOT / filename).read_text(encoding="utf-8-sig"))
    return "".join(nb["cells"][index]["source"])


class ValidationModeTests(unittest.TestCase):
    def setUp(self):
        # Keep generated fixtures under the ignored project output directory.
        self.work = (ROOT / (".tmp-validation-tests-" + uuid.uuid4().hex[:8])).resolve()
        self.assertTrue(self.work.is_relative_to(ROOT.resolve()))
        self.work.mkdir()

    def test_staged_modes_and_offline_plan(self):
        for mode in ("training", "validation"):
            output = self.work / mode
            with patch.object(sys, "argv", ["runner", "--plan-only", "--pipeline-mode", mode,
                                            "--output-dir", str(output)]), \
                    patch.object(run_batch, "kaggle_preflight") as preflight, \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_batch.main(), 0)
                preflight.assert_not_called()
            run = next(output.iterdir())
            summary = json.loads((run / "batch-summary.json").read_text())
            self.assertEqual(summary["pipeline_mode"], mode)
            self.assertEqual(summary["validation_limits"] is None, mode == "training")
            for stage, filename in (("fit", "fit-model.ipynb"), ("evaluate", "evaluate-model.ipynb")):
                nb = json.loads((run / "staged" / stage / filename).read_text(encoding="utf-8"))
                config = ast.literal_eval(ast.parse("".join(nb["cells"][0]["source"])).body[-1].value.args[0])
                self.assertEqual(config["LUDUS_PIPELINE_MODE"], mode)
                self.assertEqual(config["LUDUS_VALIDATION_FIT_ROWS"], "50000")
                self.assertEqual(config["LUDUS_VALIDATION_EVAL_ROWS"], "1000")
            metadata = json.loads((run / "staged/evaluate/kernel-metadata.json").read_text())
            self.assertEqual(metadata["kernel_sources"], ["paolomostardi/fit-model"])

    def run_fit(self, mode, limit="7"):
        inputs = self.work / "input" / "lichess-bitboards-2013-01"
        inputs.mkdir(parents=True, exist_ok=True)
        (inputs / "chunk_0.npy").touch()
        class Model:
            name = "test-model"
            def __init__(self): self.calls = []
            def fit(self, x, y, **kw): self.calls.append((len(x), len(y), kw))
            def save(self, path): pass
        params = {}
        class Session:
            def __enter__(self): return types.SimpleNamespace(info=types.SimpleNamespace(run_id="test-run"))
            def __exit__(self, *args): pass
        flow = types.SimpleNamespace(start_run=lambda **kw: Session(), log_params=params.update,
                                     log_param=lambda k, v: params.update({k: v}),
                                     log_metric=lambda *a, **kw: None, log_dict=lambda *a: None)
        def load(path, mmap_mode):
            self.assertEqual(mmap_mode, "r")
            shape = (10005, 2, 8, 8) if "_y" in Path(path).name else (10005, 15, 8, 8)
            return np.zeros(shape, dtype=np.uint8)
        model = Model()
        env = {"model": model, "model_config": {"factory": "test-model", "parameters": {}, "artifact_file": "test.keras"},
               "conv_filters": 12, "upsample_factor": 4, "mlflow": flow,
               "np": types.SimpleNamespace(load=load, array=np.array)}
        code = source("fit-model.ipynb", 7).replace("Path('/kaggle/input')", "Path(" + repr(str(inputs.parent)) + ")")
        with patch.dict(os.environ, {"LUDUS_PIPELINE_MODE": mode, "LUDUS_VALIDATION_FIT_ROWS": limit}), \
                contextlib.redirect_stdout(io.StringIO()):
            exec(code, env)
        return model, params, env

    def test_validation_caps_fit_and_uses_one_epoch(self):
        model, params, env = self.run_fit("validation")
        self.assertEqual(model.calls, [(7, 7, {"batch_size": 64, "epochs": 1})])
        self.assertEqual(params["total_training_rows"], 7)
        self.assertEqual(env["training_manifest"]["chunks"][0]["sampled_out_rows"], 9998)
        self.assertEqual(params["end_chunk"], 0)

    def test_training_preserves_full_chunks_epochs_and_holdout(self):
        model, params, env = self.run_fit("training", limit="1")
        self.assertEqual([call[0] for call in model.calls], [10005]*4 + [5])
        self.assertTrue(all(call[2]["epochs"] == 3 for call in model.calls))
        self.assertEqual(params["total_training_rows"], 40025)
        self.assertEqual(env["training_manifest"]["chunks"][-1]["excluded_rows"], 10000)

    def test_evaluation_caps_before_label_processing(self):
        code = source("Backend/kaggle/notebooks/evaluate-model.ipynb", 9)
        settings = code.split("from Backend.data_pipeline", 1)[0]
        loading = code[code.index("x = np.load(x_path"):code.index("create_simple.main()")]
        for mode, expected in (("training", 20), ("validation", 3)):
            fake = types.SimpleNamespace(load=lambda path, **kw: np.zeros((20, 15, 8, 8)) if path == "x" else np.zeros((20, 2, 8, 8)))
            env = {"np": fake, "x_path": "x", "y_path": "y"}
            with patch.dict(os.environ, {"LUDUS_PIPELINE_MODE": mode, "LUDUS_VALIDATION_EVAL_ROWS": "3"}):
                exec(settings + loading, env)
            self.assertEqual(len(env["x"]), expected)
            self.assertEqual(len(env["y"]), expected)

    def test_invalid_limits_stop_before_submission(self):
        with patch.object(sys, "argv", ["runner", "--plan-only", "--validation-fit-rows", "0"]):
            with self.assertRaises(SystemExit): run_batch.main()
        with self.assertRaises(ValueError): self.run_fit("validation", limit="0")


if __name__ == "__main__":
    unittest.main()
