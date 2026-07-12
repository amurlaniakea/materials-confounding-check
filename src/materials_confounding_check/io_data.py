"""Dataset ingestion: CSV / JSON / parquet -> Dataset, with pydantic-free structural checks."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import Dataset, Metadata

# columns we expect (case-insensitive matching done by caller)
REQUIRED_FEATURE_HINT = None  # features are any numeric columns except the reserved ones
RESERVED = {"row_id", "author", "journal", "year", "target"}


def read_dataset(path: str | Path, target_col: str = "target") -> Dataset:
    """Read a dataset from CSV/JSON/parquet.

    The file must contain: numeric feature columns, a `target` column, and bibliographic
    metadata columns (`author`, `journal`, `year`). Missing metadata -> ValueError (AC-6),
    unless the caller supplies it separately (not handled here).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"dataset not found: {path}")
    suffix = p.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(p)
    elif suffix == ".json":
        df = pd.read_json(p)
    elif suffix in (".parquet", ".pq"):
        df = pd.read_parquet(p)
    else:
        raise ValueError(f"unsupported dataset format: {suffix} (use .csv/.json/.parquet)")

    return _df_to_dataset(df, target_col=target_col, source=p.name)


def _df_to_dataset(df: pd.DataFrame, target_col: str, source: str) -> Dataset:
    if target_col not in df.columns:
        raise ValueError(f"missing required target column '{target_col}' (AC-6)")
    for col in ("author", "journal", "year"):
        if col not in df.columns:
            raise ValueError(f"missing required metadata column '{col}' (AC-6)")

    feature_cols = [c for c in df.columns if c not in RESERVED and c != target_col]
    if not feature_cols:
        raise ValueError("no feature columns found (AC-6)")

    features: dict[str, list[float]] = {}
    for c in feature_cols:
        vals = df[c].to_numpy(dtype=float).tolist()
        # reject non-finite
        if any(__import__("math").isnan(v) or __import__("math").isinf(v) for v in vals):
            raise ValueError(f"non-finite value in feature column '{c}' (AC-6)")
        features[c] = vals

    metadata: list[Metadata] = []
    for _, row in df.iterrows():
        metadata.append(
            Metadata(
                row_id=str(row.get("row_id", f"r{len(metadata)}")),
                author=str(row["author"]),
                journal=str(row["journal"]),
                year=int(row["year"]),
            )
        )
    target = df[target_col].to_numpy(dtype=float).tolist()
    return Dataset(dataset_id=source, features=features, metadata=metadata, target=target)
