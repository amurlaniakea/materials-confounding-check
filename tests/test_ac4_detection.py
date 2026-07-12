"""AC-4: the fixture with injected confounding must be detected (high risk), and the
clean fixture (no injection) must NOT be flagged (low risk). Non-circular: the ground
truth comes from the fixture's own `spurious` flag, not from the tester's rules.

Robustness: the spurious/clean verdict must hold across MULTIPLE seeds (not just the
default 20260712), because a verdict that flips with the seed would mean the null
distribution (percentile-95 over 100 permutations) is itself unstable on this data size.
"""

from __future__ import annotations

import pytest

from materials_confounding_check.check import run
from tests.data.fixture import make_fixture

SEEDS = [20260712, 101, 777, 424242]


@pytest.mark.slow
def test_ac4_spurious_detected_across_seeds():
    for seed in SEEDS:
        ds = make_fixture(spurious=True, seed=seed)
        v = run(ds, seed=seed, n_perm=100)
        assert v.risk in ("medium", "high"), (
            f"[seed {seed}] spurious fixture not flagged: risk={v.risk}, trig={v.triggered_tests}"
        )
        assert len(v.triggered_tests) >= 1, (
            f"[seed {seed}] no test triggered on spurious fixture: {v.triggered_tests}"
        )


@pytest.mark.slow
def test_ac4_clean_not_flagged_across_seeds():
    for seed in SEEDS:
        ds = make_fixture(spurious=False, seed=seed)
        v = run(ds, seed=seed, n_perm=100)
        assert v.risk == "low", (
            f"[seed {seed}] clean fixture wrongly flagged {v.risk}: {v.triggered_tests}"
        )
        assert v.triggered_tests == [], (
            f"[seed {seed}] clean fixture triggered tests: {v.triggered_tests}"
        )


def test_ac4_deterministic():
    ds = make_fixture(spurious=True, seed=20260712)
    v1 = run(ds, seed=20260712, n_perm=20)
    v2 = run(ds, seed=20260712, n_perm=20)
    assert v1.risk == v2.risk
    assert v1.score == v2.score
    assert v1.triggered_tests == v2.triggered_tests
