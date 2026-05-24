from __future__ import annotations

import argparse
import contextlib
import os
import socket
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def find_free_port(preferred: int) -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex(("127.0.0.1", preferred)) != 0:
            return preferred
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lokalen HTTP-Server für den WinStorePackager Companion starten."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host für den lokalen Server.")
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Bevorzugter Port. Bei Belegung wird ein freier Port gesucht.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Browser nicht automatisch öffnen.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    port = find_free_port(args.port)
    handler = partial(SimpleHTTPRequestHandler, directory=os.fspath(ROOT))
    server = ThreadingHTTPServer((args.host, port), handler)
    url = f"http://{args.host}:{port}/index.html"
    print(f"WinStorePackager Companion läuft unter {url}")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
