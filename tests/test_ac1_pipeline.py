"""AC-1: full pipeline over a fixture produces a report with the 4 blocks. AC-6: missing
required columns -> clear error, non-zero exit (here ValueError)."""

from __future__ import annotations


import pytest

from materials_confounding_check.check import run
from materials_confounding_check.io_data import read_dataset
from tests.data.fixture import make_fixture


def _write_csv(path, spurious=True):
    import csv

    ds = make_fixture(spurious=spurious, seed=20260712)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["row_id", "d0", "d1", "author", "journal", "year", "target"])
        for i in range(ds.n_rows()):
            d0 = ds.features["d0"][i]
            d1 = ds.features["d1"][i]
            w.writerow([ds.metadata[i].row_id, d0, d1, ds.metadata[i].author,
                        ds.metadata[i].journal, ds.metadata[i].year, ds.target[i]])


def test_ac1_pipeline(tmp_path):
    csv_path = tmp_path / "ds.csv"
    _write_csv(csv_path, spurious=True)
    ds = read_dataset(csv_path)
    v = run(ds, seed=20260712, n_perm=20)
    report = v.report
    for block in ("metadata_clf", "bibliographic_fingerprint", "group_time_split"):
        assert block in report, f"missing report block {block}"
    assert v.risk in ("low", "medium", "high")
    assert 0.0 <= v.score <= 1.0


def test_ac6_missing_column(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("row_id,d0,author,journal,year\nr0,0.1,a,J,2020\n")
    with pytest.raises(ValueError):
        read_dataset(bad)


def test_ac6_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_dataset(str(tmp_path / "nope.csv"))
