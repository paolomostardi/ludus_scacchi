"""Find evaluation shards in either the current or legacy Kaggle layout."""
from pathlib import Path
import re


def find_evaluation_shards(input_root: Path, dataset_id: str):
    slug = dataset_id.split("/")[-1]
    roots = [path for path in input_root.rglob(slug) if path.is_dir()]
    if len(roots) != 1:
        raise FileNotFoundError(f"Expected one mounted evaluation dataset {dataset_id}: {roots}")
    root = roots[0]
    shards = sorted(
        (path for path in root.glob("chunk_*.npy") if re.fullmatch(r"chunk_\d+\.npy", path.name)),
        key=lambda path: int(path.stem.split("_")[1]),
    )
    if shards:
        pairs = [(path, path.with_name(path.stem + "_y.npy")) for path in shards]
        label = re.sub(r"[^a-z0-9_]+", "_", slug.lower()).strip("_")
    elif slug == "eval-training-2013-chunk-9":
        directory = root / "my_processed_chunks" / "2013-01"
        pairs = [(directory / "chunk_6_x.npy", directory / "chunk_6_y.npy")]
        label = "2013_01"
    else:
        raise FileNotFoundError(f"No evaluation chunks at {root}")
    missing = [str(path) for pair in pairs for path in pair if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Evaluation shard files missing: {missing}")
    return label, pairs
