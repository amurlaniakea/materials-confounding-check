"""Test 3: group/time split vs random split performance drop.

Train with a random split and with a group/time split (by author or by year). A large
drop in performance under group/time split means the model relied on group-specific shortcuts.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import cross_val_predict, GroupKFold

from materials_confounding_check.models import Dataset


@dataclass
class SplitEvalResult:
    perf_random: float
    perf_group: float
    delta_random_vs_group: float  # positive => group split hurts => shortcut suspected
    group_by: str


def _score(y_true, y_pred, classification: bool) -> float:
    if classification:
        return float(roc_auc_score(y_true, y_pred))
    return float(r2_score(y_true, y_pred))


def run_split_eval(dataset: Dataset, seed: int = 20260712, group_by: str = "year") -> SplitEvalResult:
    X = np.array(dataset.feature_matrix(), dtype=float)
    y = np.array(dataset.target, dtype=float)
    classification = set(dataset.target).issubset({0.0, 1.0})

    groups = np.array(
        [getattr(m, group_by) for m in dataset.metadata], dtype=object
    )
    # bucketize continuous year into decades-ish groups so GroupKFold has viable group sizes
    if group_by == "year":
        groups = np.array([(int(g) // 5) * 5 for g in groups], dtype=object)
    uniq = sorted(set(groups))
    # need >=2 groups for GroupKFold
    if len(uniq) < 2:
        return SplitEvalResult(perf_random=0.0, perf_group=0.0, delta_random_vs_group=0.0, group_by=group_by)

    if classification:
        model = LogisticRegression(max_iter=1000, random_state=seed)
        pred_all = cross_val_predict(model, X, y, cv=5, method="predict_proba")[:, 1]
        gkf = GroupKFold(n_splits=min(5, len(uniq)))
        pred_g = cross_val_predict(model, X, y, cv=gkf, groups=groups, method="predict_proba")[:, 1]
    else:
        model = LinearRegression()
        pred_all = cross_val_predict(model, X, y, cv=5)
        gkf = GroupKFold(n_splits=min(5, len(uniq)))
        pred_g = cross_val_predict(model, X, y, cv=gkf, groups=groups)

    perf_random = _score(y, pred_all, classification)
    perf_group = _score(y, pred_g, classification)
    return SplitEvalResult(
        perf_random=float(perf_random),
        perf_group=float(perf_group),
        delta_random_vs_group=float(perf_random - perf_group),
        group_by=group_by,
    )
