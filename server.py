#!/usr/bin/env python3
"""
Erica's Kitchen — local server
Run: python3 server.py
Then open: http://localhost:8080
"""
import http.server, urllib.request, urllib.error, json, os, sys

PORT = 8080
DIR  = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/proxy":
            self._proxy()
        else:
            self.send_error(404)

    def _proxy(self):
        length  = int(self.headers.get("Content-Length", 0))
        body    = self.rfile.read(length)
        api_key = self.headers.get("x-api-key", "")
        antv    = self.headers.get("anthropic-version", "2023-06-01")
        beta    = self.headers.get("anthropic-beta", "")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": antv,
                **({"anthropic-beta": beta} if beta else {}),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, x-api-key, anthropic-version, anthropic-beta")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def log_message(self, fmt, *args):
        print(f"  {args[0]} {args[1]}")

if __name__ == "__main__":
    os.chdir(DIR)
    print(f"🍳  Erica's Kitchen running at http://localhost:{PORT}")
    print(f"    Press Ctrl+C to stop.\n")
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as s:
        try:
            s.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped.")
