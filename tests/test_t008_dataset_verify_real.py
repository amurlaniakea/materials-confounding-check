"""T008 real-world positive case (needs external network; marked slow)."""

from __future__ import annotations

import pytest

from materials_confounding_check.dataset_verify import verify_dataset_url

# TADF real (confirmed via figshare API: article 24004182, file 43183206, zip ~5MB)
TADF_URL = "https://ndownloader.figshare.com/files/43183206"


@pytest.mark.slow
def test_t008_real_world_tadf_zip():
    r = verify_dataset_url(TADF_URL, head_kb=8)
    assert r.ok is True, f"TADF debería verificarse como dato real: {r.note}"
    assert r.http_code in (200, 206)
