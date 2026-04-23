"""LINE Messaging API sender — push Flex messages to a group.

Reads LINE_CHANNEL_ACCESS_TOKEN and LINE_GROUP_ID_STOCKS from os.environ
first, falls back to .env (same file used by send_discord.py).

One `push` to a groupId = 1 billed message regardless of group size.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from send_discord import load_env

LINE_PUSH_ENDPOINT = "https://api.line.me/v2/bot/message/push"

LINE_MESSAGES_PER_PUSH = 5          # LINE allows up to 5 message objects per push call
LINE_PAYLOAD_BYTE_LIMIT = 25 * 1024  # 25 KB per push


def _config() -> tuple[str, str]:
    env_file = load_env()
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN") or env_file.get("LINE_CHANNEL_ACCESS_TOKEN")
    group_id = os.environ.get("LINE_GROUP_ID_STOCKS") or env_file.get("LINE_GROUP_ID_STOCKS")
    if not token:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN missing in env / .env")
    if not group_id:
        raise RuntimeError("LINE_GROUP_ID_STOCKS missing in env / .env")
    return token, group_id


def _post(payload: dict, token: str) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    if len(body) > LINE_PAYLOAD_BYTE_LIMIT:
        raise ValueError(
            f"LINE payload is {len(body)} bytes, exceeds 25KB push limit. "
            "Split into fewer bubbles or shorter text."
        )
    req = urllib.request.Request(
        LINE_PUSH_ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "tw-stock-bot/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def push_messages(messages: list[dict]) -> int:
    """Send `messages` to the configured group.

    LINE accepts up to 5 message objects per push call; this helper splits
    larger lists into chunks, each chunk counts as 1 push toward quota.
    Returns number of push calls made.
    """
    token, group_id = _config()
    calls = 0
    for i in range(0, len(messages), LINE_MESSAGES_PER_PUSH):
        chunk = messages[i : i + LINE_MESSAGES_PER_PUSH]
        status, body = _post({"to": group_id, "messages": chunk}, token)
        if status >= 300:
            raise RuntimeError(f"LINE push failed ({status}): {body}")
        calls += 1
        time.sleep(0.4)
    return calls


def push_text(text: str) -> None:
    push_messages([{"type": "text", "text": text[:5000]}])


def push_image(image_url: str, preview_url: str | None = None) -> None:
    """Send a LINE image message. URL must be HTTPS and publicly reachable."""
    msg = {
        "type": "image",
        "originalContentUrl": image_url,
        "previewImageUrl": preview_url or image_url,
    }
    push_messages([msg])


def test_ping() -> None:
    push_text("✅ TW-Stock-Bot LINE 連線測試 OK")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_ping()
        print("sent LINE test ping")
    else:
        print("usage: python send_line.py test")
