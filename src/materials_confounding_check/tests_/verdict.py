"""Test 4: assemble the confounding verdict from the three upstream signals."""

from __future__ import annotations

from dataclasses import dataclass

from materials_confounding_check.tests_.fingerprint import FingerprintResult
from materials_confounding_check.tests_.metadata_clf import MetadataClfResult
from materials_confounding_check.tests_.split_eval import SplitEvalResult


@dataclass
class VerdictResult:
    risk: str  # "low" | "medium" | "high"
    score: float  # [0, 1]
    triggered_tests: list[str]


# thresholds (documented; adjustable)
ABOVE_CHANCE_MARGIN = 0.05
FINGERPRINT_RATIO_WARN = 0.5  # fingerprint perf >= 50% of chemo perf => suspicious
SPLIT_DELTA_WARN = 0.10  # >0.10 drop under group split => shortcut suspected


def run_verdict(
    m: MetadataClfResult,
    f: FingerprintResult,
    s: SplitEvalResult,
) -> VerdictResult:
    triggered: list[str] = []
    signals = 0.0

    if m.above_chance:
        triggered.append("metadata_clf")
        signals += 1.0
    if f.ratio >= FINGERPRINT_RATIO_WARN and f.perf_fingerprint > f.perf_fingerprint_permuted_p95:
        triggered.append("bibliographic_fingerprint")
        signals += 1.0
    if s.delta_random_vs_group >= SPLIT_DELTA_WARN:
        triggered.append("group_time_split_drop")
        signals += 1.0

    # score: normalized count of triggered signals, weighted by intensity
    intensity = 0.0
    if m.above_chance:
        intensity += min(1.0, (m.best_acc - m.baseline_acc) / 0.3)
    if f.ratio >= FINGERPRINT_RATIO_WARN:
        intensity += min(1.0, f.ratio)
    if s.delta_random_vs_group >= SPLIT_DELTA_WARN:
        intensity += min(1.0, s.delta_random_vs_group / 0.3)
    score = round(min(1.0, intensity / 3.0), 3)

    if len(triggered) >= 2:
        risk = "high"
    elif len(triggered) == 1:
        risk = "medium"
    else:
        risk = "low"
    return VerdictResult(risk=risk, score=score, triggered_tests=triggered)
