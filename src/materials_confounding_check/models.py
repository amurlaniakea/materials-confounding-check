"""Canonical data contracts. Defined ONCE here; all modules import from this file.

Following the SDD-audit rule: a dataclass duplicated across modules diverges silently.
`Dataset`/`Metadata`/`ConfoundingVerdict` are the single source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Metadata:
    """Bibliographic metadata for one dataset row (enriched via Crossref)."""

    row_id: str
    author: str = ""
    journal: str = ""
    year: int = 0


@dataclass
class Dataset:
    """A materials-science dataset: chemical descriptors + bibliographic metadata + target."""

    dataset_id: str
    features: dict[str, list[float]]  # descriptor name -> values per row
    metadata: list[Metadata]  # one per row, aligned with features
    target: list[float]  # property to predict, one per row

    def n_rows(self) -> int:
        if not self.features:
            return 0
        return len(next(iter(self.features.values())))

    def feature_matrix(self) -> list[list[float]]:
        """Return [n_rows, n_features] matrix with feature order from `features` keys."""
        keys = list(self.features.keys())
        return [list(row) for row in zip(*[self.features[k] for k in keys])]


@dataclass
class ConfoundingVerdict:
    """Output of the full falsification pipeline."""

    risk: str  # "low" | "medium" | "high"
    score: float  # [0, 1]
    triggered_tests: list[str] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)
