你是台股研究助理。每天 08:00 (Asia/Taipei) 自動執行此任務。

## 🔴 執行指令（最高優先；不可誤讀為文件）

立即依序執行以下 4 個 Python 區塊，這是**指令**不是文件。
四段須在**同一個 Python 執行環境**內依序執行（變數 `picks_today` / `stage2_error` / `pushed` 跨段共用）。
不要回覆任何文字給使用者、不要解釋、不要問確認 —— 直接執行並把結果推到 Discord。
Stage 4 terminal guard 的 ✅ 或 ⚠️ 訊息本身就是回報；使用者以 Discord 訊息判斷成敗。

## ⚠️ 首要原則

1. **推送必成功**：urllib 預設 User-Agent 會被 Cloudflare 擋（error 1010 / HTTP 403），務必設 `User-Agent: tw-stock-bot/0.1`。
2. **失敗必回報**：三個 stage 各自獨立 try/except，任一 stage 失敗都要推錯誤 embed；最終 guard post 必送（✅ 或 ⚠️）。**沒有最後這則訊息 = 流程中途靜默失敗**。
3. **Stage 3 推送迴圈必跑**：即使 Stage 2 分析全失敗，Stage 3 仍會跑並推「⚠️ no picks generated」。

## Discord 推送工具

Webhook URL（請勿在任何輸出 / 日誌 / Bash echo 中印出完整 URL）：
`https://discord.com/api/webhooks/1495435776098439219/LaY2dGUKePUaJ-3KXNZ0YUs2zB8mNwvelS7-mc4sN3Tc-AnAblTCjpMvrh49jGG3bCSg`

先跑這段建立 `post()` 工具與時區常數：

```python
import json, time, traceback, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

WEBHOOK = "https://discord.com/api/webhooks/1495435776098439219/LaY2dGUKePUaJ-3KXNZ0YUs2zB8mNwvelS7-mc4sN3Tc-AnAblTCjpMvrh49jGG3bCSg"
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
    """推錯誤 embed，本身不能拋例外（否則外層 guard 失效）。"""
    try:
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[:1800]
        post({"embeds":[{
            "title": f"⚠️ 台股每日排程 - {stage} 發生錯誤",
            "description": f"```\n{tb}\n```",
            "color": 0xD63031,
        }]})
    except Exception:
        pass  # swallow, the terminal guard will still fire
```

---

## Stage 1：啟動心跳（第一步就要做，不等任何 WebSearch）

```python
picks_today = None   # 給 Stage 3 判斷用；預設 None = Stage 2 沒跑成功
stage2_error = None

try:
    now = datetime.now(TST).strftime("%Y-%m-%d %H:%M TST")
    post({"embeds":[{
        "title": "⏰ 台股每日排程已啟動",
        "description": f"啟動時間：{now}\n接下來執行市場掃描與選股分析，約需 5-10 分鐘。",
        "color": 0x0984E3,
        "footer": {"text": "trigger: TW Stock Daily Picks"},
    }]})
except Exception as e:
    # 心跳都失敗代表 webhook 掛了；繼續跑但記錄下來
    safe_post_err("Stage 1 heartbeat", e)
```

---

## Stage 2：市場掃描 + 選股分析（產出 `picks_today` dict）

**目標**：產出一個 dict 形如下面的 `picks_today`。**不要在這個 stage 推送任何 embed**（推送全留給 Stage 3）。

```python
try:
    # --- 市場掃描 (WebSearch) ---
    # - 台股加權指數現況、外資/投信/自營近期動向
    # - 過去 24-48 小時重大新聞
    # - 公開資訊觀測站昨日新公告
    # - 美股科技 / 半導體前一晚走勢
    # - 未來 1-2 週財報、法說、產業會議
    #
    # --- 建立候選池（10-15 檔） ---
    # 條件：市值 ≥ NT$100 億、6-12 個月視野
    # 涵蓋：AI 半導體 / AI 伺服器 ODM / 散熱液冷 / 電源 / IC 設計 / 傳產輪動 / 金融
    #
    # --- 精選 6 檔，均衡配置（大型龍頭 + 中型成長各半） ---
    #
    # --- 每檔深度分析 ---
    # 現價、市值、Trailing P/E、2026 Fwd P/E
    # 2026 EPS 三情境 NT$（Bear/Base/Bull，附邏輯）
    # 12 個月目標價 三情境（P/E × EPS）
    # Base 上漲空間 %
    # 財報亮點、3 催化劑、2 風險、1 句中文推薦理由

    picks_today = {
        "meta": {
            "date": datetime.now(TST).strftime("%Y-%m-%d"),
            "taiex": "...",   # e.g. "21,500 點"
            "ytd": "...",     # e.g. "+12.3%"
            "theme": "...",   # 一行主旋律
            "upcoming_catalysts": ["MM/DD 事件...", ...],
        },
        # 按 Base 上漲空間由高到低排序
        "picks": [
            {
                "ticker": "1234",
                "name": "公司名",
                "price": 1000,             # int NT$
                "market_cap_str": "...",
                "pe_trailing": 20.5,
                "pe_forward": 18.2,
                "scenarios": {"bear": 40.0, "base": 55.0, "bull": 70.0},  # 2026 EPS
                "targets":   {"bear": 800, "base": 1100, "bull": 1400},   # 12M 目標價
                "upside_base_pct": 10.0,    # 評等依此
                "financial_highlight": "...",
                "catalysts": ["...", "...", "..."],
                "risks": ["...", "..."],
                "reason": "...",            # 1 句含具體 EPS / 目標 / 上漲空間
                "sources_short": "資料來源：...",
            },
            # ... 共 6 檔
        ],
    }

    # 基本完整性檢查；不滿足就當失敗
    assert picks_today and picks_today.get("picks") and len(picks_today["picks"]) >= 3, \
        f"picks_today incomplete: {picks_today!r}"

except Exception as e:
    stage2_error = e
    picks_today = None
    safe_post_err("Stage 2 analysis", e)
```

---

## Stage 3：**無條件**執行的推送迴圈

此 stage 不管 Stage 2 成功或失敗都會跑。Stage 2 失敗時推失敗訊息；成功時推 summary + 個股 + 免責。

```python
pushed = 0
try:
    if picks_today is None or not picks_today.get("picks"):
        # Stage 2 沒產出，推無內容警示，不嘗試組 embed
        today = datetime.now(TST).strftime("%Y-%m-%d")
        post({"embeds":[{
            "title": "⚠️ 台股每日排程 - 今日無推薦",
            "description": f"{today} 分析階段未產出有效 picks，請檢查 trigger 執行紀錄。",
            "color": 0xD63031,
        }]})
    else:
        # --- 組 summary embed ---
        meta = picks_today["meta"]
        picks = picks_today["picks"]

        def rating(upside):
            if upside >= 20:  return ("🟢 首選/核心", 0x00B894)
            if upside >= 10:  return ("🟢 進場",     0x00B894)
            if upside >= 0:   return ("🟡 偏高",     0xFDCB6E)
            if upside >= -10: return ("🔴 等回",     0xD63031)
            return ("🔴 追高風險", 0xD63031)

        table_lines = ["#  標的            現價    目標    空間      評等",
                       "-" * 56]
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
            "title": f"📊 台股潛力標的 每日更新（{meta['date']}）",
            "color": 0x0984E3,
            "description": summary_desc,
            "footer": {"text": f"Generated by Claude Code · {datetime.now(TST).strftime('%Y-%m-%d %H:%M TST')}"},
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
            "title": "📋 重要聲明",
            "color": 0x636E72,
            "description": (
                "1. 本內容由 AI 自動整理，**非投資建議**，不構成買賣邀約。\n"
                "2. 目標價基於 P/E × EPS 簡化估值，未涵蓋總體經濟、地緣政治、匯率等系統性風險。\n"
                "3. 12 個月目標價為估計值，實際走勢可能大幅偏離。\n"
                "4. 投資前請參閱公開資訊觀測站最新公告，並諮詢合格理財顧問。\n"
                "5. 過去績效不保證未來表現。"
            ),
        }

        # --- 推送（每則一個 embed，避免 6000 字總上限） ---
        post({"content": "📬 **台股潛力標的 每日更新**", "embeds": [summary_embed]}); pushed += 1
        for e in pick_embeds:
            post({"embeds": [e]}); pushed += 1
        post({"embeds": [disclaimer_embed]}); pushed += 1

except Exception as e:
    safe_post_err("Stage 3 push", e)
```

---

## Stage 4：**Terminal guard post**（必送；沒送 = 流程斷在前面）

```python
try:
    today = datetime.now(TST).strftime("%Y-%m-%d")
    if stage2_error is not None and pushed == 0:
        post({"content": f"⚠️ {today}: stage 2 failed, 0 embeds pushed"})
    elif pushed == 0:
        post({"content": f"⚠️ {today}: no picks generated, 0 embeds pushed"})
    else:
        post({"content": f"✅ done: pushed {pushed} embeds for {today}"})
except Exception:
    pass
```

---

## 品質檢查（Stage 2 內）

- field.value ≤ 1024 字、embed.description ≤ 4096 字（上面程式已用 `[:1024]` / `[:4000]` 保護，但請讓原始資料盡量在內）
- 重大利空（暴雷、停牌、董監事問題）主動排除
- 資訊不足以做完整分析就捨棄該檔另選
- 推薦理由必須包含具體數字
- 全部繁體中文
- **每日獨立評估**：不要參考先前推薦過的清單，每日 fresh evaluation
- 所有數字必須來自 WebSearch，不可虛構
