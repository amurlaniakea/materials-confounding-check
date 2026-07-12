"""Bibliographic metadata enrichment via Crossref, with local cache and offline mode."""

from __future__ import annotations

import json
from pathlib import Path

CACHE_PATH = Path.home() / ".cache" / "mcc" / "crossref_cache.json"


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def enrich_metadata(rows: list[dict], offline: bool = False, mailto: str | None = None) -> list[dict]:
    """Given rows with at least a `doi` or `title`, fill author/journal/year.

    In offline mode (or on any network failure) returns rows unchanged (caller must already
    have metadata, or the pipeline will flag missing metadata). This keeps the tool usable
    without network and avoids hard failures on Crossref rate limits.
    """
    if offline:
        return rows
    # NOTE: real Crossref call is deferred; for the MVP we rely on metadata already present
    # in the dataset. The enrichment hook exists so Fase 2 can auto-fill from DOIs.
    # We do NOT fabricate metadata. If a row lacks author/journal/year, leave it; the
    # validator (AC-6) will reject rows missing required metadata unless offline+present.
    return rows
