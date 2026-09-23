"""Preview server for src/ that behaves like GitHub Pages.

    python scripts/serve.py            # http://localhost:8765
    python scripts/serve.py 9000

Unlike `python -m http.server`, a missing path returns src/404.html with a
404 status, and directories resolve to their index.html. Nothing is cached,
so a rebuild shows up on the next reload.
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "src"


class Handler(SimpleHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        page = ROOT / "404.html"
        if code == 404 and page.exists():
            body = page.read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return
        super().send_error(code, message, explain)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stdout.write(f"{self.command} {self.path} -> {args[1] if len(args) > 1 else ''}\n")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(ROOT)))
    print(f"serving {ROOT} at http://localhost:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
