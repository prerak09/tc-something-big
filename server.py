"""Serves the teaser site and records guesses.

    python3 server.py            # http://localhost:8000
    python3 server.py 9000       # custom port

Guesses are appended to data/guesses.csv with a server-side timestamp, so
"fastest" can be judged fairly. The data/ folder is never served to visitors.
"""
import csv
import json
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CSV_PATH = DATA / "guesses.csv"
LOCK = threading.Lock()
LAST_POST = {}  # ip -> monotonic time, for a light rate limit


def save_guess(name, guess, ip):
    DATA.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    with LOCK:
        new = not CSV_PATH.exists()
        with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["received_at_utc", "name", "guess", "ip"])
            w.writerow([now, name, guess, ip])
    return now


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def _blocked(self):
        p = self.path.split("?", 1)[0].lower()
        return p.startswith("/data") or p.endswith((".py", ".csv"))

    def do_GET(self):
        if self._blocked():
            return self.send_error(404)
        return super().do_GET()

    def do_HEAD(self):
        if self._blocked():
            return self.send_error(404)
        return super().do_HEAD()

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/guess":
            return self._json(404, {"error": "not found"})
        ip = self.client_address[0]
        t = time.monotonic()
        if t - LAST_POST.get(ip, -99) < 5:
            return self._json(429, {"error": "Slow down a little and try again."})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 2048:
                raise ValueError
            data = json.loads(self.rfile.read(n) or b"{}")
            name = " ".join(str(data.get("name", "")).split())[:40]
            guess = " ".join(str(data.get("guess", "")).split())[:120]
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"error": "Bad request."})
        if not name or not guess:
            return self._json(400, {"error": "Please fill in both fields."})
        LAST_POST[ip] = t
        at = save_guess(name, guess, ip)
        return self._json(200, {"ok": True, "at": at})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Serving on http://localhost:{port}  (guesses -> {CSV_PATH})")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
