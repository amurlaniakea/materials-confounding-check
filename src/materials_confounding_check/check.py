"""Orchestration: run the four falsification tests and produce a ConfoundingVerdict."""

from __future__ import annotations

from materials_confounding_check.models import ConfoundingVerdict, Dataset
from materials_confounding_check.tests_.fingerprint import run_fingerprint
from materials_confounding_check.tests_.metadata_clf import run_metadata_clf
from materials_confounding_check.tests_.split_eval import run_split_eval
from materials_confounding_check.tests_.verdict import run_verdict


def run(dataset: Dataset, seed: int = 20260712, group_by: str = "year", n_perm: int = 100) -> ConfoundingVerdict:
    m = run_metadata_clf(dataset, seed=seed, n_perm=n_perm)
    f = run_fingerprint(dataset, seed=seed, n_perm=n_perm)
    s = run_split_eval(dataset, seed=seed, group_by=group_by)
    v = run_verdict(m, f, s)
    return ConfoundingVerdict(
        risk=v.risk,
        score=v.score,
        triggered_tests=v.triggered_tests,
        report={
            "metadata_clf": {
                "above_chance": m.above_chance,
                "best_acc": round(m.best_acc, 3),
                "baseline_acc": round(m.baseline_acc, 3),
                "predicted_field": m.predicted_field,
            },
            "bibliographic_fingerprint": {
                "ratio": round(f.ratio, 3),
                "perf_chemo": round(f.perf_chemo, 3),
                "perf_fingerprint": round(f.perf_fingerprint, 3),
                "perf_fingerprint_permuted_p95": round(f.perf_fingerprint_permuted_p95, 3),
                "n_perm": f.n_perm,
                "task": f.task,
            },
            "group_time_split": {
                "group_by": s.group_by,
                "perf_random": round(s.perf_random, 3),
                "perf_group": round(s.perf_group, 3),
                "delta_random_vs_group": round(s.delta_random_vs_group, 3),
            },
        },
    )
