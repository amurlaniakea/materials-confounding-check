"""Test 2: bibliographic fingerprint as the ONLY input, decided against a null distribution.

Train the property model using ONLY the predicted metadata (bibliographic fingerprint) as
input. Compare its performance against the descriptor-based model AND against a NULL
DISTRIBUTION of N=100 deterministic metadata permutations. If the real fingerprint beats the
95th percentile of the permuted null AND approaches the descriptor model, the dataset does not
rule out that the model "cheats" via bibliography. The permutation null replaces the
hand-tuned fixed margin (which would be a Clever-Hans artifact on its own fixture).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import cross_val_predict
from sklearn.preprocessing import StandardScaler

from materials_confounding_check.models import Dataset


@dataclass
class FingerprintResult:
    ratio: float  # perf_fingerprint / perf_chemo
    perf_chemo: float
    perf_fingerprint: float
    perf_fingerprint_permuted_p95: float  # 95th pct of the permuted null distribution
    n_perm: int
    task: str  # "regression" | "classification"


def _is_classification(target: list[float]) -> bool:
    return set(target).issubset({0.0, 1.0})


def _fingerprint_matrix(dataset: Dataset) -> np.ndarray:
    authors = [m.author for m in dataset.metadata]
    uniq_a = sorted(set(authors))
    years = [m.year for m in dataset.metadata]
    uniq_y = sorted(set(years))
    A = np.array([[1.0 if a == ua else 0.0 for ua in uniq_a] for a in authors], dtype=float)
    Yr = np.array([[1.0 if yr == uy else 0.0 for uy in uniq_y] for yr in years], dtype=float)
    return np.hstack([A, Yr])


def run_fingerprint(
    dataset: Dataset, seed: int = 20260712, n_perm: int = 100, alpha: float = 0.05
) -> FingerprintResult:
    Xc = np.array(dataset.feature_matrix(), dtype=float)
    Xc = StandardScaler().fit_transform(Xc)
    y = np.array(dataset.target, dtype=float)
    Xf = _fingerprint_matrix(dataset)
    rng = np.random.default_rng(seed)
    n_rows = len(y)
    perms = [rng.permutation(n_rows) for _ in range(n_perm)]

    classification = _is_classification(dataset.target)
    if classification:
        model_chemo = LogisticRegression(max_iter=1000, random_state=seed)
        model_fp = LogisticRegression(max_iter=1000, random_state=seed)
        pred_c = cross_val_predict(model_chemo, Xc, y, cv=3, method="predict_proba")[:, 1]
        pred_f = cross_val_predict(model_fp, Xf, y, cv=3, method="predict_proba")[:, 1]
        perf_chemo = float(roc_auc_score(y, pred_c))
        perf_fingerprint = float(roc_auc_score(y, pred_f))
        perm_accs = np.array([
            roc_auc_score(y, cross_val_predict(model_fp, Xf[perm], y, cv=3, method="predict_proba")[:, 1])
            for perm in perms
        ])
    else:
        model_chemo = LinearRegression()
        model_fp = LinearRegression()
        pred_c = cross_val_predict(model_chemo, Xc, y, cv=3)
        pred_f = cross_val_predict(model_fp, Xf, y, cv=3)
        perf_chemo = float(r2_score(y, pred_c))
        perf_fingerprint = float(r2_score(y, pred_f))
        perm_accs = np.array([
            r2_score(y, cross_val_predict(model_fp, Xf[perm], y, cv=3))
            for perm in perms
        ])

    thr = float(np.percentile(perm_accs, (1 - alpha) * 100))
    ratio = float(perf_fingerprint / perf_chemo) if perf_chemo > 1e-9 else 0.0
    return FingerprintResult(
        ratio=ratio,
        perf_chemo=perf_chemo,
        perf_fingerprint=perf_fingerprint,
        perf_fingerprint_permuted_p95=thr,
        n_perm=n_perm,
        task="classification" if classification else "regression",
    )
