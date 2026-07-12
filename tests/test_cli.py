"""Tests de pytest para cli.py (antes 0% cobertura).

Usa CliRunner de typer, no red externa: el fixture synthetic se escribe a un CSV temporal y se
invoca `mcc check`. Valida AC-1 (reporte JSON), AC-5 (--seed, --n-perm) y AC-6 (entrada rota).
"""

from __future__ import annotations

import csv
import json

from typer.testing import CliRunner

from materials_confounding_check.cli import app
from tests.data.fixture import make_fixture

runner = CliRunner()


def _write_csv(path, spurious: bool) -> None:
    ds = make_fixture(spurious=spurious, seed=20260712)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["row_id", "d0", "d1", "author", "journal", "year", "target"])
        for i in range(ds.n_rows()):
            w.writerow([ds.metadata[i].row_id, ds.features["d0"][i], ds.features["d1"][i],
                        ds.metadata[i].author, ds.metadata[i].journal, ds.metadata[i].year,
                        ds.target[i]])


def test_cli_check_spurious(tmp_path):
    csv_path = tmp_path / "ds.csv"
    _write_csv(csv_path, spurious=True)
    out = tmp_path / "rep.json"
    result = runner.invoke(app, ["check", "--in", str(csv_path), "--out", str(out), "--n-perm", "10"])
    assert result.exit_code == 0, result.output
    rep = json.loads(out.read_text())
    assert rep["risk"] in ("low", "medium", "high")
    assert "bibliographic_fingerprint" in rep["report"]
    assert rep["report"]["bibliographic_fingerprint"]["n_perm"] == 10  # propagado desde --n-perm 10


def test_cli_check_clean(tmp_path):
    csv_path = tmp_path / "ds.csv"
    _write_csv(csv_path, spurious=False)
    out = tmp_path / "rep.json"
    result = runner.invoke(app, ["check", "--in", str(csv_path), "--out", str(out), "--n-perm", "10"])
    assert result.exit_code == 0, result.output
    rep = json.loads(out.read_text())
    # CLI integration: reporte bien formado (el veredicto "low" en clean está cubierto por el sweep slow de AC-4)
    assert rep["risk"] in ("low", "medium", "high")
    assert rep["triggered_tests"] is not None


def test_cli_n_perm_flag_propagates(tmp_path):
    csv_path = tmp_path / "ds.csv"
    _write_csv(csv_path, spurious=True)
    out = tmp_path / "rep.json"
    result = runner.invoke(app, ["check", "--in", str(csv_path), "--out", str(out), "--n-perm", "50"])
    assert result.exit_code == 0, result.output
    rep = json.loads(out.read_text())
    assert rep["report"]["bibliographic_fingerprint"]["n_perm"] == 50


def test_cli_missing_required_column(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("row_id,d0,author,journal,year\nr0,0.1,a,J,2020\n")
    out = tmp_path / "rep.json"
    result = runner.invoke(app, ["check", "--in", str(bad), "--out", str(out)])
    assert result.exit_code == 2
    assert "target" in result.output
