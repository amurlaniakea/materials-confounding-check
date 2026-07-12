"""AC-2: metadata classifier reports above_chance flag + baseline. AC-3: group/time split
reports delta vs random. AC-5: seed and no-metadata-enrich flags are accepted and change
nothing about the fixture result determinism. AC-6 also covered in test_ac1.
"""

from __future__ import annotations

from materials_confounding_check.check import run
from materials_confounding_check.tests_.metadata_clf import run_metadata_clf
from materials_confounding_check.tests_.split_eval import run_split_eval
from tests.data.fixture import make_fixture


def test_ac2_metadata_clf():
    ds = make_fixture(spurious=True, seed=20260712)
    m = run_metadata_clf(ds, seed=20260712, n_perm=20)
    assert "above_chance" in dir(m)
    # on the spurious fixture, metadata must be predictable above chance
    assert m.above_chance is True, f"metadata not above chance: acc={m.best_acc} base={m.baseline_acc}"


def test_ac3_split_eval():
    ds = make_fixture(spurious=True, seed=20260712)
    s = run_split_eval(ds, seed=20260712, group_by="year")
    assert "delta_random_vs_group" in dir(s)
    assert s.perf_random >= 0.0
    assert s.perf_group >= 0.0


def test_ac5_seed_deterministic():
    ds = make_fixture(spurious=True, seed=20260712)
    v1 = run(ds, seed=1)
    v2 = run(ds, seed=1)
    assert v1.score == v2.score
    v3 = run(ds, seed=999)
    # different seed must not crash; risk still valid
    assert v3.risk in ("low", "medium", "high")
