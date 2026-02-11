#!/usr/bin/env python3
"""Serve the repo root so landing/ can reference ../docs and ../*.md.

Usage:
  python3 scripts/serve_landing.py
  python3 scripts/serve_landing.py --port 5173 --open

This is intentionally dependency-free.
"""

from __future__ import annotations

import argparse
import http.server
import os
import socketserver
import sys
import threading
import time
import webbrowser


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5173, help="Port to serve on (default: 5173)")
    ap.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind (default: 127.0.0.1)",
    )
    ap.add_argument("--open", action="store_true", help="Open the landing page in your default browser")
    args = ap.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(repo_root)

    landing_path = "/landing/index.html"
    url = f"http://{args.host}:{args.port}{landing_path}"

    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer((args.host, args.port), handler) as httpd:
        httpd.allow_reuse_address = True

        print(f"Serving repo root: {repo_root}")
        print(f"Landing: {url}")
        print("Ctrl+C to stop")

        if args.open:
            # Give the server a moment to start.
            def _open() -> None:
                time.sleep(0.25)
                try:
                    webbrowser.open(url)
                except Exception:
                    pass

            threading.Thread(target=_open, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped")
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
