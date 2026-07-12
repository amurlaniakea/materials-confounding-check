"""Tests de pytest para metadata.py (antes 0% cobertura).

metadata.py es un hook offline: enrich_metadata NO fabrica metadata (integridad) y soporta
modo offline. No usa red externa.
"""

from __future__ import annotations

from materials_confounding_check.metadata import enrich_metadata


def test_offline_returns_rows_unchanged():
    rows = [{"doi": "10.1/x", "author": "A", "journal": "J", "year": 2020}]
    out = enrich_metadata(rows, offline=True)
    assert out == rows  # no transforma, no crashea


def test_online_does_not_fabricate_metadata():
    # sin red/Crossref conectado, el hook debe devolver las rows sin inventar campos
    rows = [{"doi": "10.1/x"}]
    out = enrich_metadata(rows, offline=False)
    assert isinstance(out, list)
    assert len(out) == 1
    # no se inventó author/journal/year
    assert "author" not in out[0]
    assert "journal" not in out[0]
    assert "year" not in out[0]


def test_preserves_existing_fields():
    rows = [{"author": "A", "journal": "J", "year": 2021}]
    out = enrich_metadata(rows, offline=False)
    assert out[0]["author"] == "A"
    assert out[0]["journal"] == "J"
    assert out[0]["year"] == 2021
