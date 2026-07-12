"""Test 1: predict bibliographic metadata from chemical descriptors.

If a classifier recovers author/journal/year ABOVE chance from the descriptors alone,
there is a bibliographic signal in the dataset. The decision is made against a NULL
DISTRIBUTION of N=100 deterministic metadata permutations (percentile-95 threshold),
NOT a hand-tuned fixed margin. This is the same statistical rigor the tool demands of
the models it audits: a single-sample margin tuned until "it passes" would itself be
a Clever-Hans artifact.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

from materials_confounding_check.models import Dataset


@dataclass
class MetadataClfResult:
    above_chance: bool
    best_acc: float
    baseline_acc: float
    permuted_p95: float  # 95th percentile of the null (permuted-label) accuracy distribution
    n_perm: int
    predicted_field: str


def _eval(y: list[int], Xs: np.ndarray, seed: int) -> float:
    clf = LogisticRegression(max_iter=1000, random_state=seed)
    return float(cross_val_score(clf, Xs, y, cv=3).mean())


def run_metadata_clf(
    dataset: Dataset, seed: int = 20260712, n_perm: int = 100, alpha: float = 0.05
) -> MetadataClfResult:
    X = dataset.feature_matrix()
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    rng = np.random.default_rng(seed)
    n_rows = len(dataset.target)
    perms = [list(rng.permutation(n_rows)) for _ in range(n_perm)]

    candidates: list[tuple[str, list[int]]] = []
    authors = [m.author for m in dataset.metadata]
    uniq_a = sorted(set(authors))
    if len(uniq_a) >= 2:
        candidates.append(("author", [uniq_a.index(a) for a in authors]))
    years = [m.year for m in dataset.metadata]
    uniq_y = sorted(set(years))
    if len(uniq_y) >= 2:
        candidates.append(("year", [uniq_y.index(yr) for yr in years]))

    if not candidates:
        return MetadataClfResult(above_chance=False, best_acc=0.0, baseline_acc=1.0,
                                 permuted_p95=0.0, n_perm=n_perm, predicted_field="")

    best_acc = 0.0
    best_field = ""
    best_perm_p95 = 0.0
    n_classes = 0
    for field_name, y in candidates:
        n_classes = len(set(y))
        real_acc = _eval(y, Xs, seed)
        perm_accs = np.array([_eval([y[i] for i in perm], Xs, seed) for perm in perms])
        thr = float(np.percentile(perm_accs, (1 - alpha) * 100))
        # signal only if real beats the 95th percentile of the null distribution
        if real_acc > thr and real_acc > best_acc:
            best_acc = float(real_acc)
            best_field = field_name
            best_perm_p95 = thr
    baseline_acc = 1.0 / n_classes
    above = best_acc > baseline_acc and best_field != ""
    return MetadataClfResult(
        above_chance=above,
        best_acc=best_acc,
        baseline_acc=baseline_acc,
        permuted_p95=best_perm_p95,
        n_perm=n_perm,
        predicted_field=best_field,
    )
