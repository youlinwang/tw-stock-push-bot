"""Push the ranked summary table to Discord as a single embed."""
from __future__ import annotations

import json
from pathlib import Path

from send_discord import send_embeds

ROOT = Path(__file__).resolve().parent
PICKS = ROOT / "picks.json"

RATING = {
    "+36": "🟢 首選",
    "+30": "🟢 核心",
    "+19": "🟢 進場",
    "+10": "🟡 偏高",
    "-9": "🔴 等回",
    "-10": "🔴 追高",
}


def fmt_row(idx: int, p: dict) -> str:
    up = p["upside_base_pct"]
    up_str = f"{up:+.0f}%"
    key = f"{up:+.0f}".replace("+0", "+").rstrip("%")
    rating = RATING.get(f"{up:+.0f}", "—")
    price = f"{p['price']:>5,.0f}"
    target = f"{p['targets']['base']:>5,.0f}"
    name_code = f"{p['name']} {p['ticker']}"
    return f"{idx}. {name_code:<10} {price}  →  {target}  {up_str:>6}  {rating}"


def main() -> None:
    data = json.loads(PICKS.read_text(encoding="utf-8"))
    picks = data["picks"]

    lines = ["```", f"{'#':<3}{'標的':<12}{'現價':>6}     {'目標':>6}   {'空間':>6}   評等"]
    lines.append("-" * 56)
    for i, p in enumerate(picks, start=1):
        up = p["upside_base_pct"]
        up_str = f"{up:+.0f}%"
        rating = RATING.get(f"{up:+.0f}", "—")
        name_code = f"{p['name']} {p['ticker']}"
        lines.append(
            f"{i:<3}{name_code:<12}{p['price']:>6,.0f}  →  {p['targets']['base']:>6,.0f}   {up_str:>6}   {rating}"
        )
    lines.append("```")
    table = "\n".join(lines)

    embed = {
        "title": "📋 推薦排序速覽（按 Base 上漲空間）",
        "description": (
            f"{table}\n\n"
            "🟢 = base case 仍有 ≥15% 空間，可現價分批進場\n"
            "🟡 = 已大幅 re-rate，建議分批承接\n"
            "🔴 = 估值偏高，建議等回檔（緯參考 picks 內建議價位）\n\n"
            "完整三情境 EPS / 目標價 / 催化劑見前面 6 則 embed。"
        ),
        "color": 0x0984E3,
        "footer": {"text": "本內容為 AI 整理之研究筆記，非投資建議"},
    }
    send_embeds(embeds=[embed])
    print("sent summary embed")


if __name__ == "__main__":
    main()
