"""Render picks.json into a single tall PNG card for LINE image push.

Layout:
  ┌─ Header (blue bar): 策略 + 日期 + 時間 ─┐
  │  大盤狀態 / 主軸                        │
  │  篩選機制（四面向）                      │
  │  ─── 推薦總表（表格）───                 │
  │  #1 pick full card                      │
  │  #2 pick full card                      │
  │  ...                                    │
  │  免責聲明                                │
  └────────────────────────────────────────┘

Output: PNG at `docs/img/{date}_{HHMM}.png` (repo-relative). Caller is
responsible for making the file reachable over HTTPS (e.g. pushing to
the GitHub repo so raw.githubusercontent.com can serve it).

Usage:
    python render_picks_image.py picks.json "前450名市值" [output_path]
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT_REG = "C:/Windows/Fonts/msjh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msjhbd.ttc"
TST = timezone(timedelta(hours=8))

W = 1080
PAD = 36
LINE_GAP = 6

C_BG = (250, 251, 253)
C_HEADER = (9, 132, 227)
C_HEADER_TXT = (255, 255, 255)
C_TXT = (26, 32, 44)
C_MUTED = (113, 128, 150)
C_CARD_BG = (255, 255, 255)
C_CARD_BORDER = (226, 232, 240)
C_GREEN = (0, 184, 148)
C_YELLOW = (253, 203, 110)
C_RED = (214, 48, 49)
C_ACCENT = (45, 55, 72)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def rating_for(upside: float):
    if upside >= 20:
        return "🟢 首選/核心", C_GREEN
    if upside >= 10:
        return "🟢 進場", C_GREEN
    if upside >= 0:
        return "🟡 偏高", C_YELLOW
    if upside >= -10:
        return "🔴 等回", C_RED
    return "🔴 追高風險", C_RED


def fmt_num(x, d=2):
    try:
        return f"{float(x):,.{d}f}"
    except Exception:
        return str(x)


def draw_multiline(draw, xy, text, fnt, fill, max_w, line_gap=LINE_GAP):
    """Draw text with word wrap + \n respect. Returns final y."""
    x, y = xy
    for paragraph in text.split("\n"):
        if not paragraph:
            y += fnt.size + line_gap
            continue
        words: list[str] = []
        buf = ""
        for ch in paragraph:
            trial = buf + ch
            bbox = draw.textbbox((0, 0), trial, font=fnt)
            if bbox[2] - bbox[0] > max_w and buf:
                words.append(buf)
                buf = ch
            else:
                buf = trial
        if buf:
            words.append(buf)
        for w in words:
            draw.text((x, y), w, font=fnt, fill=fill)
            y += fnt.size + line_gap
    return y


def text_h(draw, text, fnt, max_w, line_gap=LINE_GAP):
    y = 0
    for paragraph in text.split("\n"):
        if not paragraph:
            y += fnt.size + line_gap
            continue
        buf = ""
        count = 0
        for ch in paragraph:
            trial = buf + ch
            bbox = draw.textbbox((0, 0), trial, font=fnt)
            if bbox[2] - bbox[0] > max_w and buf:
                count += 1
                buf = ch
            else:
                buf = trial
        count += 1 if buf else 0
        y += count * (fnt.size + line_gap)
    return y


def render(data: dict, strategy_label: str, output: Path) -> Path:
    meta = data["meta"]
    picks = data["picks"]
    now = datetime.now(TST)
    now_str = now.strftime("%Y-%m-%d %H:%M:%S TST")

    # fonts
    F_TITLE = font(40, bold=True)
    F_SUB = font(22)
    F_H2 = font(26, bold=True)
    F_H3 = font(22, bold=True)
    F_BODY = font(20)
    F_BODY_B = font(20, bold=True)
    F_SMALL = font(17)
    F_TINY = font(15)

    content_w = W - 2 * PAD

    # compute height — multi-pass, render twice to size first
    def layout(dry: bool, img=None, draw=None):
        y = 0
        if not dry:
            # background
            draw.rectangle((0, 0, W, y + 150), fill=C_HEADER)
        # header
        hy = 30
        if not dry:
            draw.text((PAD, hy), f"📊 {strategy_label} 每日更新", font=F_TITLE, fill=C_HEADER_TXT)
        hy += F_TITLE.size + 10
        if not dry:
            draw.text((PAD, hy), f"{meta['date']}  ⏰ {now_str}", font=F_SUB, fill=(214, 234, 255))
        hy += F_SUB.size + 20
        y = max(150, hy)

        # market / theme block
        y += 20
        if not dry:
            draw.text((PAD, y), f"📈 大盤 {meta.get('taiex','—')}  YTD {meta.get('ytd','—')}",
                      font=F_BODY_B, fill=C_TXT)
        y += F_BODY_B.size + LINE_GAP
        if not dry:
            y = draw_multiline(draw, (PAD, y), f"🎯 {meta.get('theme','')}", F_SMALL, C_MUTED,
                               content_w)
        else:
            y += text_h(None, f"🎯 {meta.get('theme','')}", F_SMALL, content_w)

        # methodology card
        y += 24
        methodology_lines = [
            ("🧭 篩選機制（四面向漏斗）", F_H3, C_ACCENT),
            ("① 宇宙池：TWSE+OTC 當日市值前 450 名（排除 ETF/特別股/全額交割/下市/權證）。限制範圍於主要流動性標的。", F_SMALL, C_TXT),
            ("② 技術 - 趨勢轉多：5MA 上穿 20MA（或已在上方且斜率向上）＋ RSI(14) ≥ 50。確認上升趨勢啟動。", F_SMALL, C_TXT),
            ("② 技術 - 未過熱：RSI(14) ≤ 70 ＋ 近 5 日漲幅 ≤ +15% ＋ 未顯著過 60 日高點。避免追高。", F_SMALL, C_TXT),
            ("③ 籌碼（前一交易日）：投信或外資買超 > 0 ＋ 三大法人合計買超 > 0（含自營避險）。確認機構資金淨流入。", F_SMALL, C_TXT),
            ("④ 基本面：2026 EPS 法人共識 ＋ 目標價 tier 1-3 來源（法人報告 > 財報 > 法說會 > 新聞）＋ Base upside ≥ 15%。", F_SMALL, C_TXT),
            ("排除：stale target / extreme dispersion / single-source / loss-making / price anomaly / cyclical / material bad news 等 11 類。", F_TINY, C_MUTED),
            ("⑤ 最終排序：blended = 0.5×upside + 0.3×chip + 0.2×tech；取 top 5（若符合不足 5 檔不湊數）。", F_SMALL, C_TXT),
        ]
        card_y0 = y
        cy = y + 16
        for text, f, color in methodology_lines:
            if not dry:
                cy = draw_multiline(draw, (PAD + 16, cy), text, f, color, content_w - 32)
            else:
                cy += text_h(None, text, f, content_w - 32)
            cy += 2
        cy += 16
        if not dry:
            draw.rounded_rectangle((PAD, card_y0, W - PAD, cy), radius=12,
                                   outline=C_CARD_BORDER, width=2, fill=C_CARD_BG)
            # redraw text on top
            dy = card_y0 + 16
            for text, f, color in methodology_lines:
                dy = draw_multiline(draw, (PAD + 16, dy), text, f, color, content_w - 32)
                dy += 2
        y = cy + 24

        # summary table
        if not dry:
            draw.text((PAD, y), "📋 推薦總表", font=F_H2, fill=C_ACCENT)
        y += F_H2.size + 14
        table_y0 = y
        cols = [(0.08, "#"), (0.34, "標的"), (0.18, "現價"), (0.18, "目標"), (0.22, "Upside / 評等")]
        col_x = [PAD + int(sum(c[0] for c in cols[:i]) * content_w) for i in range(len(cols) + 1)]
        # header row
        if not dry:
            draw.rectangle((PAD, y, W - PAD, y + 36), fill=(237, 242, 247))
            for i, (_, label) in enumerate(cols):
                draw.text((col_x[i] + 10, y + 8), label, font=F_BODY_B, fill=C_ACCENT)
        y += 36
        for i, p in enumerate(picks, 1):
            row_h = 40
            up = p["upside_base_pct"]
            r_label, r_color = rating_for(up)
            if not dry:
                if i % 2 == 0:
                    draw.rectangle((PAD, y, W - PAD, y + row_h), fill=(248, 250, 253))
                draw.text((col_x[0] + 10, y + 10), str(i), font=F_BODY, fill=C_TXT)
                draw.text((col_x[1] + 10, y + 10), f"{p['name']} ({p['ticker']})", font=F_BODY_B, fill=C_TXT)
                draw.text((col_x[2] + 10, y + 10), f"NT${p['price']}", font=F_BODY, fill=C_TXT)
                draw.text((col_x[3] + 10, y + 10), f"NT${p['targets']['base']}", font=F_BODY, fill=C_TXT)
                draw.text((col_x[4] + 10, y + 10), f"{up:+.1f}%  {r_label}", font=F_BODY_B, fill=r_color)
            y += row_h
        if not dry:
            draw.rectangle((PAD, table_y0 - 1, W - PAD, y + 1), outline=C_CARD_BORDER, width=2)
        y += 30

        # per-pick cards
        for i, p in enumerate(picks, 1):
            up = p["upside_base_pct"]
            r_label, r_color = rating_for(up)
            card_y = y
            cy2 = y + 18
            # title
            if not dry:
                draw.text((PAD + 16, cy2), f"#{i}  {p['name']} ({p['ticker']})", font=F_H3, fill=C_ACCENT)
                bbox = draw.textbbox((0, 0), r_label, font=F_BODY_B)
                draw.text((W - PAD - 16 - (bbox[2] - bbox[0]), cy2 + 2), r_label, font=F_BODY_B, fill=r_color)
            cy2 += F_H3.size + 12

            detail_lines = [
                (f"💰 現價 NT${p['price']}　市值 {p.get('market_cap_str','—')}　Trailing P/E {p.get('pe_trailing','—')}　Fwd P/E {p.get('pe_forward','—')}", F_SMALL),
                (f"🎯 目標 Bear {p['targets']['bear']}  /  Base {p['targets']['base']} ({up:+.1f}%)  /  Bull {p['targets']['bull']}", F_SMALL),
                (f"📈 2026 EPS  Bear {fmt_num(p['scenarios']['bear'])} / Base {fmt_num(p['scenarios']['base'])} / Bull {fmt_num(p['scenarios']['bull'])}", F_SMALL),
            ]
            tech = p.get("technical") or {}
            chip = p.get("chip_prev_day") or {}
            if tech:
                detail_lines.append((
                    f"📊 技術 MA5 {tech.get('ma5','—')} / MA20 {tech.get('ma20','—')}　RSI(14) {tech.get('rsi14','—')}　5d {tech.get('ret5d_pct','—')}%　60dH {tech.get('high60d','—')}",
                    F_TINY))
            if chip:
                detail_lines.append((
                    f"💰 前日籌碼  外資 {chip.get('foreign_net','—')}／投信 {chip.get('trust_net','—')}／自營 {chip.get('dealer_net','—')}／合計 {chip.get('combined_net','—')} 張",
                    F_TINY))

            for txt, fnt in detail_lines:
                if not dry:
                    cy2 = draw_multiline(draw, (PAD + 16, cy2), txt, fnt, C_TXT, content_w - 32)
                else:
                    cy2 += text_h(None, txt, fnt, content_w - 32)
                cy2 += 4

            # rich fields
            if p.get("financial_highlight"):
                txt = f"🔥 財報亮點：{str(p['financial_highlight'])[:260]}"
                if not dry:
                    cy2 = draw_multiline(draw, (PAD + 16, cy2), txt, F_TINY, C_TXT, content_w - 32)
                else:
                    cy2 += text_h(None, txt, F_TINY, content_w - 32)
                cy2 += 4
            if p.get("catalysts"):
                bullets = "⚡ 催化劑：" + "；".join(str(c) for c in p["catalysts"][:3])[:320]
                if not dry:
                    cy2 = draw_multiline(draw, (PAD + 16, cy2), bullets, F_TINY, C_TXT, content_w - 32)
                else:
                    cy2 += text_h(None, bullets, F_TINY, content_w - 32)
                cy2 += 4
            if p.get("risks"):
                bullets = "⚠️ 風險：" + "；".join(str(r) for r in p["risks"][:2])[:260]
                if not dry:
                    cy2 = draw_multiline(draw, (PAD + 16, cy2), bullets, F_TINY, C_TXT, content_w - 32)
                else:
                    cy2 += text_h(None, bullets, F_TINY, content_w - 32)
                cy2 += 4
            if p.get("reason"):
                txt = f"💡 推薦理由：{str(p['reason'])[:280]}"
                if not dry:
                    cy2 = draw_multiline(draw, (PAD + 16, cy2), txt, F_SMALL, C_ACCENT, content_w - 32)
                else:
                    cy2 += text_h(None, txt, F_SMALL, content_w - 32)
                cy2 += 4
            ss = p.get("sources_short", "")
            if isinstance(ss, list):
                ss = "；".join(str(x) for x in ss)
            if ss:
                txt = f"🔗 {str(ss)[:180]}"
                if not dry:
                    cy2 = draw_multiline(draw, (PAD + 16, cy2), txt, F_TINY, C_MUTED, content_w - 32)
                else:
                    cy2 += text_h(None, txt, F_TINY, content_w - 32)

            cy2 += 18
            if not dry:
                # left rating color bar
                draw.rectangle((PAD, card_y, PAD + 6, cy2), fill=r_color)
                draw.rounded_rectangle((PAD, card_y, W - PAD, cy2), radius=10,
                                       outline=C_CARD_BORDER, width=1)
            y = cy2 + 16

        # disclaimer
        y += 14
        if not dry:
            draw.text((PAD, y),
                      "📋 AI 自動整理，非投資建議。目標價為 12 個月估值；投資前請參閱公開資訊觀測站公告並諮詢合格顧問。",
                      font=F_TINY, fill=C_MUTED)
        y += F_TINY.size + 30
        return y

    # dry pass to get height (use a throwaway draw for text metrics)
    tmp_img = Image.new("RGB", (W, 8), C_BG)
    tmp_draw = ImageDraw.Draw(tmp_img)
    # inject tmp_draw into text_h via closure: rewrite text_h calls to use tmp_draw
    # easier: temporarily shadow text_h with a partial
    orig_text_h = globals()["text_h"]

    def _th(_none, text, fnt, max_w, line_gap=LINE_GAP):
        return orig_text_h(tmp_draw, text, fnt, max_w, line_gap)

    globals()["text_h"] = _th
    try:
        total_h = layout(dry=True)
    finally:
        globals()["text_h"] = orig_text_h

    # render
    img = Image.new("RGB", (W, total_h), C_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 150), fill=C_HEADER)
    layout(dry=False, img=img, draw=draw)

    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, format="PNG", optimize=True)
    return output


if __name__ == "__main__":
    picks_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "picks.json"
    label = sys.argv[2] if len(sys.argv) > 2 else "前450名市值"
    now = datetime.now(TST)
    default_out = ROOT / "docs" / "img" / f"{now:%Y-%m-%d}_{now:%H%M}.png"
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else default_out
    data = json.loads(picks_path.read_text(encoding="utf-8"))
    result = render(data, label, out)
    print(f"rendered: {result}")
