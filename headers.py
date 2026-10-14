import argparse
import http.server
import json
import socketserver
import urllib.request
from datetime import datetime, timezone

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
    "Cross-Origin-Embedder-Policy",
]


class UAHandler(http.server.BaseHTTPRequestHandler):
    """Servidor HTTP que registra el User-Agent de cada peticion."""

    def _log_request(self):
        entry = {
            "time": datetime.now(timezone.utc).isoformat(),
            "method": self.command,
            "path": self.path,
            "client": self.client_address[0],
            "user_agent": self.headers.get("User-Agent", ""),
            "headers": dict(self.headers.items()),
        }

        print(json.dumps(entry, ensure_ascii=False, indent=2))

        with open("user_agents.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def do_GET(self):
        self._log_request()

        body = b"OK\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_POST = do_GET
    do_HEAD = do_GET

    def log_message(self, fmt, *args):
        return


def check_security_headers(url, timeout=10):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SecurityHeaderChecker/1.0"},
    )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        headers = {k.lower(): v for k, v in response.headers.items()}

        report = {
            "url": response.geturl(),
            "status": response.status,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "headers": {},
        }

        for header in SECURITY_HEADERS:
            report["headers"][header] = headers.get(header.lower())

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Comprueba cabeceras de seguridad y captura User-Agent"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://example.com",
        help="URL a analizar",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Puerto del servidor HTTP",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Interfaz de escucha",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout de la peticion HTTP",
    )

    args = parser.parse_args()

    try:
        report = check_security_headers(args.url, args.timeout)
        print(json.dumps(report, ensure_ascii=False, indent=2))

        with open("security_headers.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    except Exception as exc:
        print(f"[!] No se pudo analizar {args.url}: {exc}")

    print(f"\n[*] Servidor HTTP escuchando en http://{args.host}:{args.port}")
    print("[*] Las cabeceras User-Agent se guardan en user_agents.jsonl")

    with socketserver.ThreadingTCPServer((args.host, args.port), UAHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Servidor detenido")


if __name__ == "__main__":
    main()

