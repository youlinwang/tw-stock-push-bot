"""One-shot LINE webhook probe to capture a groupId.

Run this, expose :8080 via ngrok / cloudflared, paste that URL into
LINE Developers Console > Messaging API > Webhook URL, then in your
target LINE group have someone @ the bot or send any message. The
script prints the groupId and exits.

Usage:
    python line_probe.py
    (then in another shell)
    ngrok http 8080
    # paste https URL into LINE Console webhook, enable 'Use webhook'
    # in the LINE group, send a message mentioning the bot
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{}')

        try:
            data = json.loads(body)
        except Exception:
            print("non-JSON body:", body[:200])
            return

        for ev in data.get("events", []):
            src = ev.get("source", {})
            kind = src.get("type")
            if kind == "group":
                print("\n=== FOUND groupId ===")
                print(src["groupId"])
                print("=====================\n")
                print("Add to .env:")
                print(f"LINE_GROUP_ID_STOCKS={src['groupId']}")
                sys.stdout.flush()
                # keep running so you can capture multiple events if needed
            elif kind == "room":
                print("roomId:", src.get("roomId"))
            elif kind == "user":
                print("userId (DM, not group):", src.get("userId"))
            else:
                print("event:", json.dumps(ev, ensure_ascii=False)[:400])

    def log_message(self, fmt, *args):
        return  # suppress default noisy logging


def main() -> None:
    port = 8080
    print(f"listening on :{port} — expose via ngrok/cloudflared and paste URL into LINE Console")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
