"""T008: strict content verification of dataset URLs (Content-Type + first KB, not just status).

The module must distinguish a REAL data file from an HTML landing page or an async endpoint.
We test the classification logic against a LOCAL http.server (deterministic, no external
network dependency — the sandbox network is intermittently reset). The positive real-world
case (TADF figshare zip) is covered by `test_t008_real_world_slow` (marked slow, needs network).
"""

from __future__ import annotations

import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from materials_confounding_check.dataset_verify import verify_dataset_url


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data.csv":
            body = b"author,year,target\ng1,2020,1\ng2,2021,0\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/page.html":
            body = b"<html><body>login</body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/async":
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"processing"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):  # silence
        pass


def _start_server(port: int) -> None:
    srv = HTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()


def test_t008_real_csv_ok():
    port = _free_port()
    _start_server(port)
    r = verify_dataset_url(f"http://127.0.0.1:{port}/data.csv", head_kb=4)
    assert r.ok is True, f"CSV debería verificarse como dato real: {r.note}"
    assert r.first_bytes_kind == "csv"
    assert r.http_code == 200


def test_t008_rejects_html_landing():
    port = _free_port()
    _start_server(port)
    r = verify_dataset_url(f"http://127.0.0.1:{port}/page.html", head_kb=4)
    assert r.ok is False
    assert r.first_bytes_kind == "html"


def test_t008_flags_async_202():
    port = _free_port()
    _start_server(port)
    r = verify_dataset_url(f"http://127.0.0.1:{port}/async", head_kb=4)
    assert r.ok is False
    assert r.http_code == 202
    assert "202" in r.note
