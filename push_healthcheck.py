"""Push healthcheck embeds to Discord.

Reads healthcheck_YYYY-MM-DD.json and sends:
  1 summary embed + N per-holding embeds + 1 disclaimer embed.

Usage:
    export DISCORD_WEBHOOK_URL=$(grep '^DISCORD_WEBHOOK_URL_HEALTHCHECK=' .env | cut -d= -f2-)
    python push_healthcheck.py [healthcheck_YYYY-MM-DD.json]
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import send_discord  # noqa: E402

# ── colour constants ──────────────────────────────────────────────────────────
COLOR_GREEN = 0x00B894   # 加碼 / 續抱
COLOR_YELLOW = 0xFDCB6E  # 中立
COLOR_RED = 0xD63031     # 減碼 / 出場
COLOR_GREY = 0x95A5A6    # ETF / N/A

RATING_COLORS = {
    "🟢": COLOR_GREEN,
    "🟡": COLOR_YELLOW,
    "🔴": COLOR_RED,
}


def color_for_rating(rating: str) -> int:
    for prefix, color in RATING_COLORS.items():
        if rating.startswith(prefix):
            return color
    return COLOR_GREY


def truncate(s: str, limit: int = 1024) -> str:
    if len(s) > limit:
        return s[: limit - 3] + "..."
    return s


# ── embed builders ────────────────────────────────────────────────────────────

def build_summary_embed(meta: dict, holdings: list[dict]) -> dict:
    date = meta["date"]
    taiex = meta.get("taiex", "N/A")
    lines = [f"**加權指數：** {taiex}", ""]
    lines.append("```")
    lines.append(f"{'代號':<8} {'名稱':<10} {'現價':>6} {'目標':>7} {'Upside':>8} {'評等'}")
    lines.append("─" * 56)
    for h in holdings:
        ticker = h["ticker"]
        name = h["name"][:6]
        price = f"NT${h['price']}"
        target = f"NT${h.get('target_base', '—')}" if h.get("target_base") else "—"
        upside = f"{h['upside_pct']:+.1f}%" if h.get("upside_pct") is not None else "N/A"
        rating = h["rating"]
        lines.append(f"{ticker:<8} {name:<10} {price:>6} {target:>7} {upside:>8}  {rating}")
    lines.append("```")
    desc = "\n".join(lines)
    return {
        "title": f"📋 持股健檢 ({date})",
        "description": truncate(desc, 4096),
        "color": COLOR_GREEN,
        "footer": {"text": f"生成時間：{meta.get('generated_at', datetime.now(timezone.utc).isoformat())}"},
    }


def build_holding_embed(i: int, h: dict) -> dict:
    ticker = h["ticker"]
    name = h["name"]
    rating = h["rating"]
    color = color_for_rating(rating)
    holding_type = h.get("type", "stock")

    fields = []

    if holding_type == "ETF":
        ctx = h.get("etf_context", {})
        status_val = (
            f"現價：NT${h['price']}\n"
            f"追蹤指數：{ctx.get('tracked_index', '—')}\n"
            f"TAIEX：{ctx.get('taiex_level', '—')}\n"
            f"近期走勢：{ctx.get('recent_trend', '—')}"
        )
        fields.append({"name": "📊 目前狀態", "value": truncate(status_val), "inline": False})
        fields.append({"name": "⚠️ 槓桿耗損提醒", "value": truncate(ctx.get("leverage_decay_reminder", "—")), "inline": False})
        fields.append({"name": "📐 部位控管", "value": truncate(ctx.get("position_sizing_caution", "—")), "inline": False})
    else:
        upside_str = f"{h['upside_pct']:+.1f}%" if h.get("upside_pct") is not None else "N/A"
        status_val = (
            f"現價：NT${h['price']}\n"
            f"P/E (trailing)：{h.get('pe_trailing', '—')}×\n"
            f"2026 EPS共識：NT${h.get('eps_2026', '—')}"
        )
        target_val = (
            f"Base目標：NT${h.get('target_base', '—')}\n"
            f"Upside：{upside_str}"
        )
        fields.append({"name": "📊 目前狀態", "value": truncate(status_val), "inline": True})
        fields.append({"name": "🎯 目標與Upside", "value": truncate(target_val), "inline": True})

    # Rationale
    fields.append({"name": "💬 評估理由", "value": truncate(h.get("rationale", "—")), "inline": False})

    # Catalysts
    catalysts = h.get("catalysts", [])
    if catalysts:
        fields.append({"name": "🚀 催化劑", "value": truncate("\n".join(f"• {c}" for c in catalysts)), "inline": False})

    # Risks
    risks = h.get("risks", [])
    if risks:
        fields.append({"name": "⚠️ 風險", "value": truncate("\n".join(f"• {r}" for r in risks)), "inline": False})

    # Action
    action = h.get("action", "—")
    fields.append({"name": "🔔 建議動作", "value": truncate(action), "inline": False})

    # Exclusion flags (if any)
    flags = h.get("exclusion_flags", [])
    if flags:
        fields.append({"name": "🚩 排除標記", "value": truncate("\n".join(f"• {f}" for f in flags)), "inline": False})

    return {
        "title": f"#{i} {name} ({ticker}) {rating}",
        "color": color,
        "fields": fields,
        "footer": {"text": truncate(h.get("sources_short", ""), 2048)},
    }


def build_disclaimer_embed() -> dict:
    return {
        "title": "⚠️ 免責聲明",
        "description": (
            "本報告由 AI（Claude Code）自動生成，**僅供參考，不構成投資建議**。\n\n"
            "所有數據（價格、EPS、目標價）均來自公開資訊或 AI 推論整理，未必反映最新市況。"
            "投資人應自行查閱原始法人報告及財務資料，並依個人風險承受度做出判斷。\n\n"
            "**本內容不代表任何金融機構或投顧意見。買賣股票有損失本金之風險。**"
        ),
        "color": 0x636E72,
        "footer": {"text": "AI-generated • Not investment advice • 非投資建議"},
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    json_path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "healthcheck_2026-04-22.json")
    if not json_path.exists():
        raise FileNotFoundError(f"{json_path} not found")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    meta = data["meta"]
    holdings = data["holdings"]

    embeds: list[dict] = []
    embeds.append(build_summary_embed(meta, holdings))
    for i, h in enumerate(holdings, start=1):
        embeds.append(build_holding_embed(i, h))
    embeds.append(build_disclaimer_embed())

    import os
    channels = os.environ.get("PUSH_CHANNELS", "both")
    want_discord = channels in ("discord", "both")
    want_line = channels in ("line", "both")

    if want_discord:
        print(f"discord: sending {len(embeds)} embeds…")
        send_discord.send_embeds(embeds)
        print(f"discord: done — sent {len(embeds)} embeds.")

    if want_line:
        try:
            from line_builders import build_healthcheck_flex
            from send_line import push_messages
            msgs = build_healthcheck_flex(data)
            calls = push_messages(msgs)
            print(f"line: sent {calls} push call(s) ({len(holdings)} holdings)")
        except Exception as e:
            print(f"line: skipped — {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
