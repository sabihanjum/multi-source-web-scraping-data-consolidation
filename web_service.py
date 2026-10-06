from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from main import run


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = json.dumps({"status": "running", "scraper": "started"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == "__main__":
    Thread(target=run, daemon=True).start()
    port = int(os.environ.get("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()
