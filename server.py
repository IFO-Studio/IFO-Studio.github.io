#!/usr/bin/env python3
"""Tiny static file server for the portfolio site — always no-cache.

Using python -m http.server left Cloudflare's edge (and browsers) free to
cache CSS/JS for hours via its default heuristics, since that module sends
no Cache-Control header at all. That caused a redesign to look stale for
everyone until the edge cache TTL expired. This tiny handler always sends
Cache-Control: no-store so every deploy is visible immediately.
"""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))

CTYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css",
    ".js": "application/javascript",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            path = "/index.html"
        full_path = os.path.normpath(os.path.join(HERE, path.lstrip("/")))
        if not full_path.startswith(HERE) or not os.path.isfile(full_path):
            self.send_response(404)
            self.end_headers()
            return
        ext = os.path.splitext(full_path)[1]
        ctype = CTYPES.get(ext, "application/octet-stream")
        with open(full_path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8101), Handler).serve_forever()
