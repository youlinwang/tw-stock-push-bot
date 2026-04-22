"""Local dry-run of the cloud trigger's 4-stage Python logic.
Uses mock picks_today (no WebSearch). Loads webhook from .env."""
import json, time, traceback, urllib.request, urllib.error, os
from datetime import datetime, timezone, timedelta
from send_discord import load_env

WEBHOOK = load_env()["DISCORD_WEBHOOK_URL"]
TST = timezone(timedelta(hours=8))

def post(payload, tries=3):
    body = json.dumps(payload).encode("utf-8")
    last_err = None
    for attempt in range(tries):
        req = urllib.request.Request(
            WEBHOOK, data=body,
            headers={"Content-Type": "application/json", "User-Agent": "tw-stock-bot/0.1"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=15).read()
            time.sleep(0.4)
            return
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Discord post failed after {tries} tries: {last_err}")

def safe_post_err(stage, exc):
    try:
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[:1800]
        post({"embeds":[{
            "title": f"⚠️ 台股每日排程 - {stage} 發生錯誤",
            "description": f"```\n{tb}\n```",
            "color": 0xD63031,
        }]})
    except Exception:
        pass

# ===== Stage 1: heartbeat =====
picks_today = None
stage2_error = None
try:
    now = datetime.now(TST).strftime("%Y-%m-%d %H:%M TST")
    post({"embeds":[{
        "title": "⏰ 台股每日排程已啟動 [LOCAL DRY-RUN]",
        "description": f"啟動時間：{now}\n本機驗證 — mock picks_today，無 WebSearch。",
        "color": 0x0984E3,
        "footer": {"text": "trigger: TW Stock Daily Picks (dry-run)"},
    }]})
except Exception as e:
    safe_post_err("Stage 1 heartbeat", e)

# ===== Stage 2: mock analysis =====
try:
    picks_today = {
        "meta": {
            "date": datetime.now(TST).strftime("%Y-%m-%d"),
            "taiex": "21,500 點",
            "ytd": "+12.3%",
            "theme": "[DRY-RUN] 這是本機測試訊息，非真實推薦",
            "upcoming_catalysts": ["MM/DD 測試事件 A", "MM/DD 測試事件 B"],
        },
        "picks": [
            {
                "ticker": "2330", "name": "台積電", "price": 1100,
                "market_cap_str": "NT$28.5 兆", "pe_trailing": 25.0, "pe_forward": 20.0,
                "scenarios": {"bear": 45.0, "base": 55.0, "bull": 65.0},
                "targets":   {"bear": 900,  "base": 1250, "bull": 1500},
                "upside_base_pct": 13.6,
                "financial_highlight": "[MOCK] 2025 Q4 營收年增 25%，毛利率 58%。",
                "catalysts": ["[MOCK] N2 量產 2026 H2", "[MOCK] AI 加速器訂單", "[MOCK] CoWoS 擴產"],
                "risks": ["[MOCK] 匯率", "[MOCK] 地緣政治"],
                "reason": "[MOCK] 2026 EPS base 55 × 22x = 1250，上漲空間 13.6%。",
                "sources_short": "[MOCK] 本機測試，非實際資料來源",
            },
            {
                "ticker": "2454", "name": "聯發科", "price": 1400,
                "market_cap_str": "NT$2.3 兆", "pe_trailing": 18.0, "pe_forward": 15.5,
                "scenarios": {"bear": 80.0, "base": 95.0, "bull": 110.0},
                "targets":   {"bear": 1200, "base": 1600, "bull": 1900},
                "upside_base_pct": 14.3,
                "financial_highlight": "[MOCK] 旗艦 SoC 佔比提升。",
                "catalysts": ["[MOCK] 天璣 9500", "[MOCK] AI edge", "[MOCK] 車用"],
                "risks": ["[MOCK] 手機需求", "[MOCK] 高通競爭"],
                "reason": "[MOCK] Base EPS 95 × 16.8x ≈ 1600，上漲空間 14.3%。",
                "sources_short": "[MOCK] 本機測試",
            },
            {
                "ticker": "3231", "name": "緯創", "price": 180,
                "market_cap_str": "NT$5200 億", "pe_trailing": 22.0, "pe_forward": 16.0,
                "scenarios": {"bear": 10.0, "base": 12.5, "bull": 15.0},
                "targets":   {"bear": 150, "base": 220, "bull": 270},
                "upside_base_pct": 22.2,
                "financial_highlight": "[MOCK] AI 伺服器佔比突破 40%。",
                "catalysts": ["[MOCK] NVDA GB300 出貨", "[MOCK] HBM 擴產", "[MOCK] 液冷導入"],
                "risks": ["[MOCK] 毛利稀釋", "[MOCK] 客戶集中"],
                "reason": "[MOCK] Base EPS 12.5 × 17.6x ≈ 220，上漲空間 22.2%。",
                "sources_short": "[MOCK] 本機測試",
            },
        ],
    }
    assert picks_today and picks_today.get("picks") and len(picks_today["picks"]) >= 3
except Exception as e:
    stage2_error = e
    picks_today = None
    safe_post_err("Stage 2 analysis", e)

# ===== Stage 3: unconditional push loop =====
pushed = 0
try:
    if picks_today is None or not picks_today.get("picks"):
        today = datetime.now(TST).strftime("%Y-%m-%d")
        post({"embeds":[{
            "title": "⚠️ 台股每日排程 - 今日無推薦",
            "description": f"{today} 分析階段未產出有效 picks。",
            "color": 0xD63031,
        }]})
    else:
        meta = picks_today["meta"]
        picks = picks_today["picks"]

        def rating(upside):
            if upside >= 20:  return ("🟢 首選/核心", 0x00B894)
            if upside >= 10:  return ("🟢 進場",     0x00B894)
            if upside >= 0:   return ("🟡 偏高",     0xFDCB6E)
            if upside >= -10: return ("🔴 等回",     0xD63031)
            return ("🔴 追高風險", 0xD63031)

        table_lines = ["#  標的            現價    目標    空間      評等", "-" * 56]
        for i, p in enumerate(picks, 1):
            label, _ = rating(p["upside_base_pct"])
            table_lines.append(
                f"{i}  {p['name']:<8}{p['ticker']:>6} {p['price']:>6} "
                f"{p['targets']['base']:>6} {p['upside_base_pct']:+6.1f}%  {label}"
            )
        table = "\n".join(table_lines)
        events = "\n".join(f"• {x}" for x in meta.get("upcoming_catalysts", [])) or "（無）"

        summary_desc = (
            f"📅 **報告日期**：{meta['date']}\n"
            f"📈 **大盤狀態**：TAIEX {meta['taiex']}　YTD {meta['ytd']}\n"
            f"🎯 **主軸**：{meta['theme']}\n\n"
            f"## 推薦排序（按 Base 上漲空間）\n```\n{table}\n```\n"
            f"**評等說明**\n🟢 ≥ 10% 空間可現價分批進場　🟡 估值偏高建議分批承接　🔴 建議等回檔\n\n"
            f"👇 各檔詳細見以下 {len(picks)} 則 embed\n\n"
            f"📌 **近期關注事件**\n{events}"
        )[:4000]

        summary_embed = {
            "title": f"📊 台股潛力標的 每日更新（{meta['date']}）[DRY-RUN]",
            "color": 0x0984E3,
            "description": summary_desc,
            "footer": {"text": f"Generated by Claude Code · {datetime.now(TST).strftime('%Y-%m-%d %H:%M TST')} · LOCAL DRY-RUN"},
        }

        pick_embeds = []
        for i, p in enumerate(picks, 1):
            label, color = rating(p["upside_base_pct"])
            pick_embeds.append({
                "title": f"#{i}  {p['name']} ({p['ticker']})  {label}",
                "color": color,
                "fields": [
                    {"name": "💰 目前狀態", "inline": True,
                     "value": (f"現價 NT${p['price']}\n市值 {p['market_cap_str']}\n"
                               f"Trailing P/E {p['pe_trailing']}\nFwd P/E {p['pe_forward']}")[:1024]},
                    {"name": "🎯 目標價（12個月）", "inline": True,
                     "value": (f"Bear {p['targets']['bear']}\n"
                               f"**Base {p['targets']['base']} (+{p['upside_base_pct']:.1f}%)**\n"
                               f"Bull {p['targets']['bull']}\n評等 {label}")[:1024]},
                    {"name": "📈 2026 EPS 三情境 (NT$)", "inline": False,
                     "value": (f"Bear {p['scenarios']['bear']:.2f} ｜ "
                               f"**Base {p['scenarios']['base']:.2f}** ｜ "
                               f"Bull {p['scenarios']['bull']:.2f}")[:1024]},
                    {"name": "🔥 近期財報亮點", "inline": False, "value": p["financial_highlight"][:1024]},
                    {"name": "⚡ 催化劑", "inline": False,
                     "value": "\n".join(f"• {c}" for c in p["catalysts"])[:1024]},
                    {"name": "⚠️ 主要風險", "inline": False,
                     "value": "\n".join(f"• {r}" for r in p["risks"])[:1024]},
                    {"name": "💡 推薦理由（建議動作）", "inline": False, "value": p["reason"][:1024]},
                ],
                "footer": {"text": p.get("sources_short", "")[:2048]},
            })

        disclaimer_embed = {
            "title": "📋 重要聲明 [DRY-RUN]",
            "color": 0x636E72,
            "description": (
                "本則為本機測試，非真實推薦。正式推送請以雲端 trigger 為準。\n\n"
                "1. 本內容由 AI 自動整理，**非投資建議**。\n"
                "2. 目標價基於 P/E × EPS 簡化估值。\n"
                "3. 12 個月目標價為估計值。\n"
                "4. 投資前請諮詢合格理財顧問。\n"
                "5. 過去績效不保證未來表現。"
            ),
        }

        post({"content": "📬 **[DRY-RUN] 台股潛力標的 每日更新**", "embeds": [summary_embed]}); pushed += 1
        for e in pick_embeds:
            post({"embeds": [e]}); pushed += 1
        post({"embeds": [disclaimer_embed]}); pushed += 1

except Exception as e:
    safe_post_err("Stage 3 push", e)

# ===== Stage 4: terminal guard =====
try:
    today = datetime.now(TST).strftime("%Y-%m-%d")
    if stage2_error is not None and pushed == 0:
        post({"content": f"⚠️ {today} [DRY-RUN]: stage 2 failed, 0 embeds pushed"})
    elif pushed == 0:
        post({"content": f"⚠️ {today} [DRY-RUN]: no picks generated, 0 embeds pushed"})
    else:
        post({"content": f"✅ [DRY-RUN] done: pushed {pushed} embeds for {today}"})
except Exception:
    pass

print(f"pushed={pushed}, stage2_error={stage2_error}")
