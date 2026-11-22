"""Pinned comparison inputs for Ludus source-square experiments."""

SUITE_ID = "ludus-heldout-v2"
DATASETS = (
    {"id": "paolomostardi/ludus-1500-2017-04-general-eval-v1", "version": 1, "rows": 111_276,
     "manifest_sha256": "978268932412f2926579d776b58cd1daa00ddd31332cc2d3db8ad5c63bc05269"},
    {"id": "paolomostardi/ludus-1500-2017-04-endgame-eval-v1", "version": 1, "rows": 3_107,
     "manifest_sha256": "7a27c858adbb29efc673b6b1b87dea5b7848d5fc2140219a062e8dc2aaa2dfbf"},
    {"id": "paolomostardi/ludus-1500-2017-04-endgame-eval-v2", "version": 1, "rows": 10_000,
     "manifest_sha256": "05f2484592b6a1550715255375048baf0b9bc2b678fda84fa73a40e8f3aeffbb"},
    {"id": "paolomostardi/ludus-2013-01-overlap-clean-eval-v1", "version": 2, "rows": 293_892,
     "manifest_sha256": "3eab28eb1c318c7af7fae504be38c9ca084d194d1cb06f6489fdc4c3d772f48d"},
    {"id": "paolomostardi/ludus-2000-general-eval-v1", "version": 1, "rows": 10_000,
     "manifest_sha256": "52d441e10fc82d39acf88d9601a5b2e67aeee76413ba006c2a81523fec4d8dbe"},
)
SIMPLE = {"id": "simple_v2", "rows": 201,
          "sha256": "64b176f3326f5798b3917c52d2e4635eb3d56f7d4b66b9cbcd586d099d3b09d8"}


def suite_for(dataset_ids):
    """Return the standard suite only when configured with all its inputs."""
    if set(dataset_ids) == {dataset["id"] for dataset in DATASETS}:
        return {"id": SUITE_ID, "datasets": DATASETS, "simple": SIMPLE}
    return None
