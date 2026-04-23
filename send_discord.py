"""Discord webhook sender for TW stock analysis push.

Uses urllib (stdlib only) to avoid external deps.
Reads DISCORD_WEBHOOK_URL from .env in the same folder.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"

DISCORD_CONTENT_LIMIT = 2000
DISCORD_EMBED_TITLE_LIMIT = 256
DISCORD_EMBED_DESC_LIMIT = 4096
# Discord caps the *total* characters across all embeds in a single webhook message
# at 6000. To stay safely under that, send one embed per message.
DISCORD_EMBEDS_PER_MSG = 1


def load_env() -> dict[str, str]:
    if not ENV_FILE.exists():
        raise FileNotFoundError(f"{ENV_FILE} not found")
    data: dict[str, str] = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def post(payload: dict) -> tuple[int, str]:
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        env = load_env()
        url = env.get("DISCORD_WEBHOOK_URL")
    if not url:
        raise RuntimeError("DISCORD_WEBHOOK_URL missing in env / .env")

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "tw-stock-bot/0.1"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def send_text(content: str) -> None:
    for i in range(0, len(content), DISCORD_CONTENT_LIMIT):
        chunk = content[i : i + DISCORD_CONTENT_LIMIT]
        status, body = post({"content": chunk})
        if status >= 300:
            raise RuntimeError(f"Discord returned {status}: {body}")
        time.sleep(0.4)


def send_embeds(embeds: list[dict], content: str | None = None) -> None:
    for i in range(0, len(embeds), DISCORD_EMBEDS_PER_MSG):
        batch = embeds[i : i + DISCORD_EMBEDS_PER_MSG]
        payload: dict = {"embeds": batch}
        if i == 0 and content:
            payload["content"] = content[:DISCORD_CONTENT_LIMIT]
        status, body = post(payload)
        if status >= 300:
            raise RuntimeError(f"Discord returned {status}: {body}")
        time.sleep(0.4)


def test_ping() -> None:
    send_embeds(
        embeds=[
            {
                "title": "TW-Stock-Bot 連線測試",
                "description": "Webhook 設定成功，準備進行台股潛力標的分析推播。",
                "color": 0x00B894,
                "fields": [
                    {"name": "狀態", "value": "OK", "inline": True},
                    {"name": "來源", "value": "Claude Code", "inline": True},
                ],
                "footer": {"text": "送出此訊息代表通道可用"},
            }
        ],
        content="✅ 測試訊息",
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_ping()
        print("sent test ping")
    else:
        print("usage: python send_discord.py test")
