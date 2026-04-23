"""Flex Message builders for LINE — mirror daily_push.py Discord embeds.

One push = one Flex Carousel message covering the whole daily report
(summary bubble + pick bubbles + disclaimer bubble). Fits in <25KB and
counts as 1 billed message regardless of group size.

Carousel hard limit: 10 bubbles per carousel. 1 summary + 6 picks + 1
disclaimer = 8 bubbles, comfortably under the cap.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from daily_push import rating_for, fmt_num, fmt_pct


_COLOR_MAP = {
    0x00B894: "#00B894",
    0xFDCB6E: "#FDCB6E",
    0xD63031: "#D63031",
    0x0984E3: "#0984E3",
    0x636E72: "#636E72",
}


def _hex(rgb_int: int) -> str:
    return _COLOR_MAP.get(rgb_int, f"#{rgb_int:06X}")


def _text(text, **kw) -> dict:
    # Coerce to string; LINE rejects non-string `text` or empty string.
    if isinstance(text, list):
        text = " / ".join(str(x) for x in text)
    elif text is None:
        text = ""
    else:
        text = str(text)
    safe = text if text else " "
    base = {"type": "text", "text": safe, "wrap": True, "size": "sm"}
    base.update(kw)
    return base


def _sep(margin: str = "md") -> dict:
    return {"type": "separator", "margin": margin}


def _row(label: str, value: str, value_weight: str = "regular") -> dict:
    return {
        "type": "box",
        "layout": "baseline",
        "spacing": "sm",
        "contents": [
            {"type": "text", "text": label, "size": "sm", "color": "#8898A2", "flex": 3},
            {"type": "text", "text": value, "size": "sm", "weight": value_weight, "flex": 6, "wrap": True},
        ],
    }


def summary_bubble(meta: dict, picks: list[dict]) -> dict:
    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _hex(0x0984E3),
        "paddingAll": "md",
        "contents": [
            _text(f"📊 {meta.get('strategy', '台股')} 每日更新", color="#FFFFFF", weight="bold", size="md"),
            _text(meta["date"], color="#D6EAFF", size="xs"),
        ],
    }
    rows: list[dict] = [
        _row("大盤", f"{meta['taiex']} / YTD {meta['ytd']}"),
        _row("主軸", meta["theme"][:60]),
        _sep(),
        _text("推薦排序（按 Base upside%）", weight="bold", size="sm"),
    ]
    for i, p in enumerate(picks, start=1):
        rating, _, _ = rating_for(p["upside_base_pct"])
        line = (
            f"{i}. {p['name']} ({p['ticker']})  "
            f"{p['price']:,.0f}→{p['targets']['base']:,.0f}  "
            f"{fmt_pct(p['upside_base_pct'])}  {rating}"
        )
        rows.append(_text(line, size="xs"))

    upcoming = meta.get("upcoming_catalysts")
    if upcoming:
        rows.append(_sep())
        rows.append(_text("📌 近期事件", weight="bold", size="sm"))
        items = upcoming if isinstance(upcoming, list) else [upcoming]
        for ev in items[:5]:
            rows.append(_text(f"• {ev}", size="xs"))

    body = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": rows}
    return {"type": "bubble", "size": "mega", "header": header, "body": body}


def pick_bubble(idx: int, p: dict) -> dict:
    rating, action, color = rating_for(p["upside_base_pct"])
    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _hex(color),
        "paddingAll": "md",
        "contents": [
            _text(f"#{idx}  {p['name']} ({p['ticker']})", color="#FFFFFF", weight="bold", size="md"),
            _text(rating, color="#FFFFFF", size="xs"),
        ],
    }
    targets = p["targets"]
    scenarios = p["scenarios"]

    rows = [
        _row("現價", f"NT${fmt_num(p['price'])}", value_weight="bold"),
        _row("市值", p["market_cap_str"]),
        _row("Trailing P/E", f"{fmt_num(p['pe_trailing'], 1)}x"),
        _row("Fwd P/E", f"{fmt_num(p['pe_forward'], 1)}x"),
        _sep(),
        _row("Base 目標", f"NT${fmt_num(targets['base'])}  ({fmt_pct(p['upside_base_pct'])})", value_weight="bold"),
        _row("Bear / Bull", f"{fmt_num(targets['bear'])} / {fmt_num(targets['bull'])}"),
        _row("EPS Base", f"NT${fmt_num(scenarios['base'])}"),
        _sep(),
        _text("🔥 財報亮點", weight="bold", size="sm"),
        _text(p["financial_highlight"][:300], size="xs"),
        _text("⚡ 催化劑", weight="bold", size="sm", margin="md"),
        *[_text(f"• {c[:120]}", size="xs") for c in p["catalysts"][:3]],
        _text("⚠️ 風險", weight="bold", size="sm", margin="md"),
        *[_text(f"• {r[:120]}", size="xs") for r in p["risks"][:2]],
        _sep(),
        _text(f"💡 {action}", weight="bold", size="sm"),
        _text(p["reason"][:300], size="xs"),
    ]
    body = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": rows}
    footer = {
        "type": "box",
        "layout": "vertical",
        "contents": [_text(p.get("sources_short", "")[:200], size="xxs", color="#8898A2")],
    }
    return {"type": "bubble", "size": "mega", "header": header, "body": body, "footer": footer}


def disclaimer_bubble() -> dict:
    body = {
        "type": "box",
        "layout": "vertical",
        "contents": [
            _text("📋 重要聲明", weight="bold", size="md"),
            _sep(),
            _text("本內容由 AI 自動整理，非投資建議，不構成買賣邀約。", size="xs"),
            _text("目標價基於 P/E × EPS 簡化估值，未涵蓋總體/地緣/匯率風險。", size="xs"),
            _text("12 個月目標價為估計值，實際走勢可能大幅偏離。", size="xs"),
            _text("投資前請參閱公開資訊觀測站公告並諮詢合格理財顧問。", size="xs"),
            _text("過去績效不保證未來表現。", size="xs"),
        ],
    }
    return {"type": "bubble", "size": "mega", "body": body}


def _rating_color_hex(rating: str) -> str:
    if rating.startswith("🟢"):
        return _hex(0x00B894)
    if rating.startswith("🟡"):
        return _hex(0xFDCB6E)
    if rating.startswith("🔴"):
        return _hex(0xD63031)
    return _hex(0x95A5A6)


def healthcheck_summary_bubble(meta: dict, holdings: list[dict]) -> dict:
    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _hex(0x0984E3),
        "paddingAll": "md",
        "contents": [
            _text("📋 持股健檢", color="#FFFFFF", weight="bold", size="md"),
            _text(meta["date"], color="#D6EAFF", size="xs"),
        ],
    }
    rows = [_row("TAIEX", meta.get("taiex", "—")), _sep()]
    for h in holdings:
        up = h.get("upside_pct")
        up_str = f"{up:+.1f}%" if up is not None else "N/A"
        tgt = h.get("target_base")
        tgt_str = f"→{tgt}" if tgt is not None else ""
        rows.append(
            _text(
                f"{h['name']} ({h['ticker']})  {h['price']}{tgt_str}  {up_str}  {h['rating']}",
                size="xs",
            )
        )
    body = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": rows}
    return {"type": "bubble", "size": "mega", "header": header, "body": body}


def holding_bubble(i: int, h: dict) -> dict:
    rating = h["rating"]
    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _rating_color_hex(rating),
        "paddingAll": "md",
        "contents": [
            _text(f"#{i}  {h['name']} ({h['ticker']})", color="#FFFFFF", weight="bold", size="md"),
            _text(rating, color="#FFFFFF", size="xs"),
        ],
    }
    up = h.get("upside_pct")
    up_str = f"{up:+.1f}%" if up is not None else "N/A"
    rows = [
        _row("現價", f"NT${h['price']}", value_weight="bold"),
        _row("PE (TTM)", str(h.get("pe_trailing", "—"))),
        _row("2026 EPS", str(h.get("eps_2026", "—"))),
        _row("Base 目標", f"NT${h.get('target_base', '—')}  ({up_str})", value_weight="bold"),
        _sep(),
        _text("💬 評估理由", weight="bold", size="sm"),
        _text(str(h.get("rationale", ""))[:300], size="xs"),
    ]
    if h.get("catalysts"):
        rows.append(_text("🚀 催化劑", weight="bold", size="sm", margin="md"))
        for c in h["catalysts"][:3]:
            rows.append(_text(f"• {str(c)[:120]}", size="xs"))
    if h.get("risks"):
        rows.append(_text("⚠️ 風險", weight="bold", size="sm", margin="md"))
        for r in h["risks"][:2]:
            rows.append(_text(f"• {str(r)[:120]}", size="xs"))
    if h.get("action"):
        rows.append(_sep())
        rows.append(_text(f"🔔 {str(h['action'])[:300]}", weight="bold", size="sm"))
    body = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": rows}
    footer = {
        "type": "box",
        "layout": "vertical",
        "contents": [_text(str(h.get("sources_short", ""))[:200], size="xxs", color="#8898A2")],
    }
    return {"type": "bubble", "size": "mega", "header": header, "body": body, "footer": footer}


def _compact_holding_section(i: int, h: dict) -> list[dict]:
    rating = h["rating"]
    up = h.get("upside_pct")
    up_str = f"{up:+.1f}%" if up is not None else "N/A"
    tgt = h.get("target_base")
    tgt_str = f"→ NT${tgt}" if tgt is not None else ""
    rationale = str(h.get("rationale", ""))[:90]
    action = str(h.get("action", ""))[:80]
    return [
        _sep(),
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                _text(f"#{i} {h['name']} ({h['ticker']})", weight="bold", size="sm", flex=6),
                _text(rating, size="xs", align="end", color=_rating_color_hex(rating), flex=4),
            ],
        },
        _text(f"NT${h['price']}  {tgt_str}  {up_str}", size="xs"),
        _text(rationale, size="xxs", color="#556677"),
        _text(f"🔔 {action}" if action else " ", size="xxs", color="#444444"),
    ]


def build_healthcheck_flex(data: dict) -> list[dict]:
    meta = data["meta"]
    holdings = data["holdings"]

    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _hex(0x0984E3),
        "paddingAll": "md",
        "contents": [
            _text("📋 持股健檢", color="#FFFFFF", weight="bold", size="md"),
            _text(meta["date"], color="#D6EAFF", size="xs"),
        ],
    }
    body_contents = [_text(f"TAIEX {meta.get('taiex','—')}", size="xs")]
    for i, h in enumerate(holdings, start=1):
        body_contents.extend(_compact_holding_section(i, h))
    body_contents.append(_sep("lg"))
    body_contents.append(_text("AI 生成，非投資建議。", size="xxs", color="#8898A2"))

    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": header,
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": body_contents},
    }
    return [{
        "type": "flex",
        "altText": f"持股健檢 {meta['date']}",
        "contents": bubble,
    }]


def defenders_summary_bubble(meta: dict, sectors: list[dict]) -> dict:
    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _hex(0x2C3E50),
        "paddingAll": "md",
        "contents": [
            _text("🛡️ 防禦龍頭", color="#FFFFFF", weight="bold", size="md"),
            _text(meta["date"], color="#D6EAFF", size="xs"),
        ],
    }
    n_leaders = sum(1 for s in sectors if s.get("leader"))
    n_none = len(sectors) - n_leaders
    rows = [
        _row("TAIEX", str(meta.get("taiex_close") or meta.get("taiex", "—"))),
        _row("覆蓋 / 選出", f"{len(sectors)} 類 / {n_leaders} 龍頭 / {n_none} 暫無"),
        _sep(),
    ]
    for s in sectors:
        ldr = s.get("leader")
        if ldr:
            up = ldr.get("upside_base_pct") or ldr.get("upside_pct", 0)
            rows.append(
                _text(
                    f"{s['sector']} → {ldr['name']} ({ldr['ticker']})  {up:+.1f}%  {ldr.get('rating','')}",
                    size="xs",
                )
            )
        else:
            rows.append(_text(f"{s['sector']} → 暫無", size="xs", color="#8898A2"))
    body = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": rows}
    return {"type": "bubble", "size": "mega", "header": header, "body": body}


def sector_bubble(s: dict) -> dict:
    ldr = s["leader"]
    rating = ldr.get("rating", "")
    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _rating_color_hex(rating),
        "paddingAll": "md",
        "contents": [
            _text(f"🛡️ {s['sector']}", color="#FFFFFF", size="xs"),
            _text(f"{ldr['name']} ({ldr['ticker']})", color="#FFFFFF", weight="bold", size="md"),
            _text(rating, color="#FFFFFF", size="xs"),
        ],
    }
    up = ldr.get("upside_base_pct") or ldr.get("upside_pct", 0)
    rows = [
        _row("現價", f"NT${ldr.get('price','—')}", value_weight="bold"),
        _row("市值", str(ldr.get("market_cap_str", "—"))),
        _row("PE (TTM)", str(ldr.get("pe_trailing", "—"))),
        _row("Base 目標", f"NT${ldr.get('target_base','—')}  ({up:+.1f}%)", value_weight="bold"),
        _sep(),
        _text("💬 選中理由", weight="bold", size="sm"),
        _text(str(ldr.get("reason") or ldr.get("rationale", ""))[:280], size="xs"),
    ]
    if ldr.get("catalysts"):
        rows.append(_text("🚀 催化劑", weight="bold", size="sm", margin="md"))
        for c in ldr["catalysts"][:2]:
            rows.append(_text(f"• {str(c)[:100]}", size="xs"))
    if ldr.get("risks"):
        rows.append(_text("⚠️ 風險", weight="bold", size="sm", margin="md"))
        for r in ldr["risks"][:2]:
            rows.append(_text(f"• {str(r)[:100]}", size="xs"))
    body = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": rows}
    return {"type": "bubble", "size": "mega", "header": header, "body": body}


def _compact_sector_row(s: dict) -> dict:
    ldr = s.get("leader")
    if not ldr:
        return _text(f"{s['sector']} → 暫無", size="xxs", color="#8898A2")
    up = ldr.get("upside_base_pct") or ldr.get("upside_pct", 0)
    return {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            _text(s["sector"], size="xxs", color="#556677", flex=3),
            _text(f"{ldr['name']}({ldr['ticker']})", size="xs", weight="bold", flex=5),
            _text(f"{up:+.1f}%", size="xs", align="end", color=_rating_color_hex(ldr.get("rating","")), flex=2),
        ],
    }


def build_defenders_flex(data: dict) -> list[dict]:
    """Single compact bubble — all sectors in one row table."""
    meta = data["meta"]
    sectors = data["sectors"]
    leaders = [s for s in sectors if s.get("leader")]

    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _hex(0x2C3E50),
        "paddingAll": "md",
        "contents": [
            _text("🛡️ 防禦龍頭", color="#FFFFFF", weight="bold", size="md"),
            _text(meta["date"], color="#D6EAFF", size="xs"),
        ],
    }
    taiex = str(meta.get("taiex_close") or meta.get("taiex", "—"))
    body_contents = [
        _text(f"TAIEX {taiex}  |  {len(sectors)} 類  |  龍頭 {len(leaders)}  |  暫無 {len(sectors)-len(leaders)}", size="xs"),
        _sep(),
        _text("✅ 選出的龍頭", weight="bold", size="sm"),
    ]
    for s in sectors:
        if s.get("leader"):
            body_contents.append(_compact_sector_row(s))
    body_contents.append(_sep("md"))
    body_contents.append(_text("— 暫無符合 —", weight="bold", size="sm", color="#8898A2"))
    none_list = [s["sector"] for s in sectors if not s.get("leader")]
    body_contents.append(_text("、".join(none_list) if none_list else "（無）", size="xxs", color="#8898A2"))
    body_contents.append(_sep("lg"))
    body_contents.append(_text("AI 生成，非投資建議。EPS/目標價均為 tier-4 推論。", size="xxs", color="#8898A2"))

    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": header,
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": body_contents},
    }
    return [{
        "type": "flex",
        "altText": f"防禦龍頭 {meta['date']}",
        "contents": bubble,
    }]


def _full_pick_section(i: int, p: dict) -> list[dict]:
    """Per-pick full-detail section. Targets ~2KB."""
    rating, action, color = rating_for(p["upside_base_pct"])
    up = p["upside_base_pct"]
    t = p["targets"]
    s = p["scenarios"]
    rows = [
        _sep("md"),
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                _text(f"#{i} {p['name']} ({p['ticker']})", weight="bold", size="md", flex=6),
                _text(rating, size="xs", align="end", color=_rating_color_hex(rating), flex=4),
            ],
        },
        _row("現價", f"NT${p['price']}  /  市值 {p.get('market_cap_str','—')}"),
        _row("P/E", f"TTM {p.get('pe_trailing','—')}x  /  Fwd {p.get('pe_forward','—')}x"),
        _row("目標 (Bear/Base/Bull)", f"{t['bear']} / **{t['base']}** / {t['bull']}"),
        _row("Base Upside", f"{fmt_pct(up)}"),
        _row("EPS 2026 三情境", f"{fmt_num(s['bear'])} / **{fmt_num(s['base'])}** / {fmt_num(s['bull'])}"),
        _text("🔥 財報亮點", weight="bold", size="xs", margin="sm"),
        _text(str(p.get("financial_highlight",""))[:180], size="xxs", color="#333333"),
        _text("⚡ 催化劑", weight="bold", size="xs", margin="sm"),
    ]
    for c in p.get("catalysts", [])[:3]:
        rows.append(_text(f"• {str(c)[:90]}", size="xxs", color="#333333"))
    rows.append(_text("⚠️ 風險", weight="bold", size="xs", margin="sm"))
    for r in p.get("risks", [])[:2]:
        rows.append(_text(f"• {str(r)[:90]}", size="xxs", color="#333333"))
    tech = p.get("technical") or {}
    chip = p.get("chip_prev_day") or {}
    if tech:
        tech_line = (
            f"MA5 {tech.get('ma5','—')} / MA20 {tech.get('ma20','—')} "
            f"／ RSI14 {tech.get('rsi14','—')} ／ 5d {tech.get('ret5d_pct','—')}% "
            f"／ 60dH {tech.get('high60d','—')}"
        )
        rows.append(_text("📊 技術面", weight="bold", size="xs", margin="sm"))
        rows.append(_text(tech_line, size="xxs", color="#333333"))
    if chip:
        chip_line = (
            f"外資 {chip.get('foreign_net','—')}｜投信 {chip.get('trust_net','—')}｜"
            f"自營 {chip.get('dealer_net','—')}｜合計 {chip.get('combined_net','—')} (張)"
        )
        rows.append(_text("💰 籌碼（前日）", weight="bold", size="xs", margin="sm"))
        rows.append(_text(chip_line, size="xxs", color="#333333"))
    rows.append(_text(f"💡 {action}", weight="bold", size="xs", margin="sm"))
    rows.append(_text(str(p.get("reason",""))[:180], size="xxs", color="#333333"))
    ss = p.get("sources_short", "")
    if isinstance(ss, list):
        ss = " / ".join(str(x) for x in ss)
    if ss:
        rows.append(_text(str(ss)[:120], size="xxs", color="#8898A2", margin="xs"))
    return rows


def build_picks_flex(data: dict, strategy_label: str) -> list[dict]:
    """Single mega bubble — summary table + full details of all picks + disclaimer."""
    meta = data["meta"]
    picks = data["picks"]
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S TST")

    header = {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": _hex(0x0984E3),
        "paddingAll": "md",
        "contents": [
            _text(f"📊 {strategy_label} 每日更新", color="#FFFFFF", weight="bold", size="md"),
            _text(f"{meta['date']}  ⏰ {now}", color="#D6EAFF", size="xs"),
        ],
    }

    body_contents = [
        _text(f"大盤 {meta.get('taiex','—')}  YTD {meta.get('ytd','—')}", size="xs"),
        _text(str(meta.get("theme", ""))[:120], size="xxs", color="#8898A2"),
        _sep("md"),
        _text("🧭 篩選機制", weight="bold", size="sm"),
        _text("① 宇宙池：TWSE+OTC 市值前 450（排除 ETF/特別/下市/權證）", size="xxs", color="#556677"),
        _text("② 技術 - 趨勢轉多：5MA 上穿 20MA 且 RSI(14)≥50（確認上升趨勢啟動）", size="xxs", color="#556677"),
        _text("② 技術 - 未過熱：RSI(14)≤70 + 近 5 日漲幅≤15% + 未顯著過 60 日高點（避免追高）", size="xxs", color="#556677"),
        _text("③ 籌碼（前日）：投信 OR 外資買超 > 0 且 三大法人合計買超 > 0（機構加碼）", size="xxs", color="#556677"),
        _text("④ 基本面：2026 EPS 共識 + tier-1/2/3 目標價 + Base upside≥15% + data_quality 非 low", size="xxs", color="#556677"),
        _text("排除：stale/extreme dispersion/single-source/loss/price anomaly/cyclical/bad news", size="xxs", color="#556677"),
        _text("⑤ 排序：blended = 0.5×upside + 0.3×chip + 0.2×tech，取 top 5（不足不湊）", size="xxs", color="#556677"),
        _sep("md"),
        _text("📋 推薦總表", weight="bold", size="sm"),
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                _text("#", size="xxs", color="#8898A2", flex=1),
                _text("標的", size="xxs", color="#8898A2", flex=5),
                _text("現價", size="xxs", color="#8898A2", align="end", flex=3),
                _text("目標", size="xxs", color="#8898A2", align="end", flex=3),
                _text("Upside", size="xxs", color="#8898A2", align="end", flex=3),
            ],
        },
    ]
    for i, p in enumerate(picks, start=1):
        rating, _, _ = rating_for(p["upside_base_pct"])
        body_contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                _text(str(i), size="xxs", flex=1),
                _text(f"{p['name']}({p['ticker']})", size="xxs", weight="bold", flex=5),
                _text(str(p['price']), size="xxs", align="end", flex=3),
                _text(str(p['targets']['base']), size="xxs", align="end", flex=3),
                _text(f"{p['upside_base_pct']:+.1f}%", size="xxs", align="end",
                      color=_rating_color_hex(rating), flex=3),
            ],
        })

    for i, p in enumerate(picks, start=1):
        body_contents.extend(_full_pick_section(i, p))

    body_contents.append(_sep("lg"))
    body_contents.append(_text("AI 自動整理，非投資建議。目標價為 12 個月估值；投資前請參閱公開資訊觀測站公告。",
                               size="xxs", color="#8898A2"))

    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": header,
        "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": body_contents},
    }
    return [{
        "type": "flex",
        "altText": f"{strategy_label} 每日更新 {meta['date']} {now[11:19]}",
        "contents": bubble,
    }]
