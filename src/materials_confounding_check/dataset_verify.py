"""T008 — strict content verification of a dataset URL.

Status code alone is NOT enough (HTTP 202 from figshare means "request accepted for async
processing", not "here is the file"). This module checks the REAL content:
  1. Content-Type header (must be a data mime: text/csv, application/json, parquet, zip, ...)
  2. first N KB of the body (must look like CSV/JSON/parquet magic, not an HTML landing page
     or a JSON "processing" envelope).
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UrlVerifyResult:
    url: str
    ok: bool
    http_code: int
    content_type: str
    first_bytes_kind: str  # csv | json | parquet | html | other | empty
    first_bytes_preview: str
    note: str


_DATA_MIMES = {
    "text/csv",
    "application/csv",
    "text/plain",
    "application/json",
    "application/octet-stream",
    "application/zip",
    "application/x-parquet",
    "application/vnd.apache.parquet",
}


def _classify_first_bytes(head: bytes) -> str:
    if not head:
        return "empty"
    text = head[:2048]
    # parquet magic: bytes 0..3 == b'PAR1' and end with b'PAR1'
    if head[:4] == b"PAR1" or b"PAR1" in head[-4:]:
        return "parquet"
    stripped = text.lstrip()
    if stripped[:1] in (b"{", b"["):
        return "json"
    # CSV heuristic: contains a comma or tab in the first line
    first_line = text.split(b"\n", 1)[0]
    if b"," in first_line or b"\t" in first_line:
        return "csv"
    if b"<html" in text[:512].lower() or b"<!" in text[:512]:
        return "html"
    return "other"


def verify_dataset_url(url: str, timeout: int = 30, head_kb: int = 8) -> UrlVerifyResult:
    """Download the first `head_kb` KB and report what the URL actually serves.

    Uses curl via subprocess (not urllib) so it behaves like a browser and follows redirects,
    mirroring how a human would fetch the dataset.
    """
    with tempfile.TemporaryDirectory() as td:
        hdr_path = f"{td}/hdr.txt"
        # 1) headers (status + content-type) to a file
        subprocess.run(
            ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0", "-L",
             "-D", hdr_path, "-o", "/dev/null", url],
            capture_output=True, text=True,
        )
        # 2) body via stdout (no Range: some servers return empty on Range requests)
        body = subprocess.run(
            ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0", "-L",
             "--max-time", str(timeout), url],
            capture_output=True,
        )
        header_blob = Path(hdr_path).read_text(errors="replace")
        raw = body.stdout

    http_code = 0
    content_type = ""
    for line in header_blob.splitlines():
        if line.lower().startswith("http/"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                http_code = int(parts[1])
        if line.lower().startswith("content-type:"):
            content_type = line.split(":", 1)[1].strip()

    head = raw[: head_kb * 1024]
    ctype_l = content_type.lower().split(";")[0].strip()
    if ctype_l in ("text/html", "application/xhtml+xml") and not head:
        kind = "html"
    else:
        kind = _classify_first_bytes(head)
    preview = head[:200].decode("utf-8", errors="replace").replace("\n", " ")

    mime_ok = ctype_l in _DATA_MIMES
    ok = mime_ok and kind in ("csv", "json", "parquet") and http_code in (200, 206)
    note = ""
    if not ok:
        if kind == "html":
            note = "URL serves an HTML page (landing/login), not the dataset file."
        elif kind == "empty":
            note = "Empty body — likely an async/accepted endpoint, not the binary."
        elif http_code == 202:
            note = "HTTP 202 = request accepted for processing, not the file (needs async poll)."
        elif not mime_ok:
            note = f"Content-Type '{content_type}' is not a known data mime."
        else:
            note = f"Unexpected first-bytes kind '{kind}'."
    return UrlVerifyResult(
        url=url, ok=ok, http_code=http_code, content_type=content_type,
        first_bytes_kind=kind, first_bytes_preview=preview[:120], note=note,
    )
