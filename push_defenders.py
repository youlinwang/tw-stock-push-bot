"""Push defenders_2026-04-22.json to Discord via DISCORD_WEBHOOK_URL_DEFENDERS.

Usage:
    export DISCORD_WEBHOOK_URL=$(grep '^DISCORD_WEBHOOK_URL_DEFENDERS=' .env | cut -d= -f2-)
    python push_defenders.py [defenders_2026-04-22.json]

Reads defenders JSON, builds embeds, calls send_discord.send_embeds().
- 1 summary embed (sector table)
- 1 per-sector embed for each sector with a leader
- 1 disclaimer embed
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import send_discord

TRUNCATE = 1024  # Discord field value limit


def trunc(s: str, limit: int = TRUNCATE) -> str:
    s = str(s)
    return s if len(s) <= limit else s[: limit - 3] + "..."


def rating_color(rating: str) -> int:
    if rating and rating.startswith("🟢"):
        return 0x00B894
    if rating and rating.startswith("🟡"):
        return 0xFDCB6E
    return 0xD63031


def build_summary_embed(meta: dict, sectors: list[dict]) -> dict:
    date = meta.get("date", "")
    taiex = meta.get("taiex_close") or meta.get("taiex", "")
    n_sectors = meta.get("sectors_fetched") or meta.get("n_sectors", 0)
    n_leaders = meta.get("n_leaders") or meta.get("n_leaders_picked", 0)
    n_no = meta.get("n_no_leader", 0)

    lines = []
    for s in sectors:
        sector_name = s["sector"]
        ldr = s.get("leader")
        if ldr:
            ticker = ldr["ticker"]
            name = ldr["name"]
            upside = ldr.get("upside_pct", 0)
            rating = ldr.get("rating", "")
            lines.append(f"`{sector_name}` → **{ticker} {name}** | {upside:+.1f}% {rating}")
        else:
            reason_short = (s.get("reason_no_leader") or "暫無符合者")[:60]
            lines.append(f"`{sector_name}` → 暫無 _(_{reason_short[:40]}_)_")

    # Discord description limit: 4096 chars. Split if needed.
    desc_header = (
        f"**加權指數：{taiex}** | 覆蓋 {n_sectors} 類 | 選出龍頭 {n_leaders} 個 | 暫無 {n_no} 類\n"
        f"策略：三軸篩選（基本面穩健度 × 法人共識upside × 產業地位）\n\n"
    )
    body = "\n".join(lines)
    description = desc_header + body
    if len(description) > 4096:
        description = description[:4090] + "..."

    return {
        "title": f"🛡️ 防禦龍頭 ({date})",
        "description": description,
        "color": 0x2C3E50,
        "footer": {"text": "所有目標價與EPS 2026估值均為tier-4推論，未取得原始法人報告PDF。非投資建議。"},
    }


def build_sector_embed(s: dict) -> dict:
    ldr = s["leader"]
    sector = s["sector"]
    ticker = ldr["ticker"]
    name = ldr["name"]
    price = ldr.get("price", "")
    mktcap = ldr.get("market_cap_str", "")
    pe_tr = ldr.get("pe_trailing", "")
    pe_fw = ldr.get("pe_forward", "")
    eps_ttm = ldr.get("eps_ttm", "")
    eps_2026 = ldr.get("eps_2026", "")
    target = ldr.get("target_base", "")
    upside = ldr.get("upside_base_pct") or ldr.get("upside_pct", 0)
    rating = ldr.get("rating", "")
    rationale = ldr.get("reason") or ldr.get("rationale", "")
    catalysts = ldr.get("catalysts", [])
    risks = ldr.get("risks", [])
    sources_raw = ldr.get("sources_short", "")
    sources = "\n".join(sources_raw) if isinstance(sources_raw, list) else str(sources_raw)
    data_quality = ldr.get("data_quality", "")
    runner_ups = s.get("runner_ups", [])
    color = rating_color(rating)

    # Target/upside field
    upside_str = f"目標：{target} NT$ | Base upside：{upside:+.1f}% | EPS TTM：{eps_ttm} | EPS 2026(估)：{eps_2026}"

    # Runner-ups
    ru_lines = []
    for ru in runner_ups:
        reason_ru = ru.get('reason_excluded') or ru.get('reason_not_picked', '')
        ru_lines.append(f"• {ru.get('ticker','')} {ru.get('name','')}: {reason_ru}")
    ru_text = "\n".join(ru_lines) if ru_lines else "（無）"

    fields = [
        {
            "name": "目前狀態",
            "value": trunc(f"現價：NT${price} | 市值：{mktcap} | PE(TTM)：{pe_tr} | data_quality：{data_quality}"),
            "inline": False,
        },
        {
            "name": "目標與 Upside",
            "value": trunc(upside_str),
            "inline": False,
        },
        {
            "name": "選中理由（三面向）",
            "value": trunc(rationale or ldr.get("financial_highlight", "")),
            "inline": False,
        },
        {
            "name": "催化劑",
            "value": trunc("\n".join(f"• {c}" for c in catalysts) if catalysts else "（無）"),
            "inline": True,
        },
        {
            "name": "風險",
            "value": trunc("\n".join(f"• {r}" for r in risks) if risks else "（無）"),
            "inline": True,
        },
        {
            "name": "落選者（runner-ups）",
            "value": trunc(ru_text),
            "inline": False,
        },
    ]

    return {
        "title": trunc(f"🛡️ {sector} — {name} ({ticker})  {rating}", 256),
        "color": color,
        "fields": fields,
        "footer": {"text": trunc(sources, 2048)},
    }


def build_disclaimer_embed() -> dict:
    return {
        "title": "⚠️ 免責聲明",
        "description": (
            "本報告由 AI（Claude）自動生成，所有分析、目標價、EPS估值均來自公開資料整理或推論，"
            "**未必經過原始法人報告PDF核實（所有目標價與EPS 2026均為tier-4推論）**。\n\n"
            "本內容**不構成投資建議**，不代表任何金融機構意見。\n"
            "投資人應獨立判斷並自行承擔投資風險。\n\n"
            "_此為 AI 生成內容，請謹慎參考。_"
        ),
        "color": 0x636E72,
    }


def main(json_path: str) -> None:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    meta = data["meta"]
    sectors = data["sectors"]

    embeds: list[dict] = []

    # 1. Summary embed
    embeds.append(build_summary_embed(meta, sectors))

    # 2. Per-sector embeds (only sectors with a leader)
    for s in sectors:
        if s.get("leader") is not None:
            embeds.append(build_sector_embed(s))

    # 3. Disclaimer
    embeds.append(build_disclaimer_embed())

    print(f"Pushing {len(embeds)} embeds ({1} summary + {len(embeds)-2} sector + 1 disclaimer)...")

    # Set webhook URL from env before calling (caller should have exported DISCORD_WEBHOOK_URL)
    # If not set, try to load DISCORD_WEBHOOK_URL_DEFENDERS from .env
    if not os.environ.get("DISCORD_WEBHOOK_URL"):
        env_file = ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DISCORD_WEBHOOK_URL_DEFENDERS="):
                    val = line.split("=", 1)[1].strip()
                    os.environ["DISCORD_WEBHOOK_URL"] = val
                    print("Loaded DISCORD_WEBHOOK_URL_DEFENDERS from .env")
                    break

    channels = os.environ.get("PUSH_CHANNELS", "both")
    want_discord = channels in ("discord", "both")
    want_line = channels in ("line", "both")

    if want_discord:
        send_discord.send_embeds(embeds)
        print(f"discord: {len(embeds)} embeds sent.")

    if want_line:
        try:
            from line_builders import build_defenders_flex
            from send_line import push_messages
            msgs = build_defenders_flex(data)
            calls = push_messages(msgs)
            print(f"line: sent {calls} push call(s) ({sum(1 for s in sectors if s.get('leader'))} leaders)")
        except Exception as e:
            print(f"line: skipped — {type(e).__name__}: {e}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "defenders_2026-04-22.json"
    main(path)
