# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Taiwan-stock research push bot: reads `picks.json` (hand-curated analysis — EPS scenarios, target prices, catalysts, risks) and pushes formatted Discord embeds. Content is in Traditional Chinese.

## Runtime / dependencies

- **Python stdlib only** — no `requirements.txt`, no virtualenv needed. Do not add external packages without a reason; HTTP goes through `urllib.request`.
- `.env` (gitignored) holds `DISCORD_WEBHOOK_URL`. `send_discord.load_env()` is a tiny hand-rolled parser — do not swap in `python-dotenv`.

## Common commands

```bash
python send_discord.py test       # ping the webhook to verify setup
python daily_push.py              # full daily report (summary table + per-pick + disclaimer), reads picks.json
python daily_push.py other.json   # same, different data file
python push_picks.py picks.json   # older format (intro embed + per-pick + disclaimer)
python send_summary.py            # summary-only embed (ranked table, no per-pick detail)
```

No build, no lint, no tests.

## Architecture

Three entry scripts share one transport layer:

- **`send_discord.py`** — transport. `send_embeds(embeds, content=None)` posts to the webhook. Discord caps *total* embed characters per message at 6000, so this module sends **one embed per HTTP request** with a 0.4s sleep between. Do not raise `DISCORD_EMBEDS_PER_MSG` without also checking per-message char totals.
- **`daily_push.py`** — the current/canonical formatter. Builds `[summary_table, *per_pick, disclaimer]`. The 5-tier rating (🟢 首選/🟢 進場/🟡 偏高/🔴 等回/🔴 追高風險) is centralised in `rating_for(upside_pct)` — change thresholds there, not in the embed builders.
- **`push_picks.py`** — older 2-colour formatter kept alongside. Overlaps with `daily_push.py`; prefer editing `daily_push.py` unless specifically asked.
- **`send_summary.py`** — just the ranked table, used standalone.

Data flow: `picks.json` → builder functions (pure, return dict embeds) → `send_embeds()` → Discord.

## `picks.json` schema

Top-level `meta` (date, taiex, ytd, theme, n_picks, generated_at, optional upcoming_catalysts) + `picks[]`. Each pick must have: `ticker`, `name`, `price`, `market_cap_str`, `pe_trailing`, `pe_forward`, `scenarios{bear,base,bull}` (EPS in NT$), `targets{bear,base,bull}` (price in NT$), `upside_base_pct`, `financial_highlight`, `catalysts[]`, `risks[]`, `reason`, `sources_short`. Builders truncate long strings to Discord field limits (1024 chars) — keep this truncation when editing.

## Scheduling

**Authoritative: local Windows Task Scheduler.** `run_daily_all.bat` fires **twice daily** (07:00 + 18:00 Asia/Taipei) and runs the 前450名市值 strategy via `claude -p`. Each run re-fetches web data per **Freshness rule**, rebuilds `picks.json` (top 5), and pushes to Discord + LINE.

- Script: `run_daily_all.bat`. Logs to `logs/run_*.log`.
- Install both schedules once:
  ```
  schtasks /create /tn "tw-stock-0700" /tr "\"<repo>\run_daily_all.bat\"" /sc daily /st 07:00 /rl LIMITED
  schtasks /create /tn "tw-stock-1800" /tr "\"<repo>\run_daily_all.bat\"" /sc daily /st 18:00 /rl LIMITED
  (task names MUST NOT contain ":" — Windows treats colons as path separators and rejects the command)
  ```
- Only 前450名市值 is scheduled. 持股健檢 is ad-hoc. 100元內 / 防禦龍頭 are deprecated.

**Cloud RemoteTriggers — all disabled (do not re-enable)**
- `trig_01CSYskLt78nbARRu5QrRJ8S` (中大型市值) — `enabled: false`
- `trig_01ALQkxLoezW1aBEJxLR5XtF` (100元內) — `enabled: false`
- `trig_018SuYKuBnjow8w6K1n14wfH` (ping-test) — `enabled: false`

The RemoteTrigger tool's `run` action has known dispatch bugs (see Claude Code GitHub issue #43438 — returns HTTP 200 but silently fails to execute). Local Task Scheduler is the sole supported path.

**Legacy `run_daily.bat` + `.local_fallback_enabled`** — superseded by `run_daily_all.bat`. Can be deleted.

## Content conventions

- Currency is NT$ throughout; prices are integers (no decimals), EPS to 2 decimals.
- Every push ends with a disclaimer embed stating this is AI-generated and **not investment advice** — keep it.
- Notification channels: **Discord** (per-strategy webhook) **and LINE** (single group, all strategies share). Dual-push is default; individual strategy pushers honour `--channels discord|line|both` (daily_push.py) or `PUSH_CHANNELS=discord|line|both` env var (push_healthcheck.py / push_defenders.py).
- LINE setup: bot `@667cxjyr` in group `台股研究室`; credentials `LINE_CHANNEL_ACCESS_TOKEN` + `LINE_GROUP_ID_STOCKS` in `.env`. Each strategy compresses to **1 Flex bubble = 1 push = 1 billed message**; under LINE free tier 200 msg/month quota.

## Subagent boundaries

Subagents dispatched to run strategy pipelines (中大型市值 / 100元內 / 防禦龍頭 / 持股健檢) MUST NOT:
- `git commit` / `git push` — artifacts stay in the working tree, the human decides what to commit
- `git reset --hard` / `rm -rf` / any destructive cleanup
- Push to any webhook / API channel not listed in the agent's explicit instructions
- Modify `CLAUDE.md`, `.env`, `daily_push.py`, `send_discord.py`, `send_line.py`, `line_builders.py`, or any cloud trigger config

Subagents MAY: read any file, write strategy output files (`picks*.json`, `defenders_*.json`, `healthcheck_*.json`, `universe_*.txt`, helper build/push scripts), fetch web data, call the pushers listed in their instructions.

## Freshness rule (applies to every strategy)

Every execution of any strategy (中大型市值 / 100元內 / 持股健檢 / 防禦龍頭 / future additions) MUST fetch the latest web data each run — **do not reuse yesterday's cached picks, rank cards, or prices**. Fetch order follows Source priority (法人報告 > 財報 > 法說會 > 新聞). Applies equally to scheduled daily runs and ad-hoc invocations. Cache is acceptable only for slow-moving references (constituent lists, filings older than 1 quarter); rank cards, prices, and picks are always regenerated.

## Selection strategies (named rule-sets)

Multiple named strategies may coexist. Each strategy shares the same rank-card / filter / exclusion / final-selection logic, and differs only in **universe definition** and **output routing** (picks file name + Discord webhook).

| Strategy | Universe | Picks file | Webhook env var |
|---|---|---|---|
| **前450名市值** (default, scheduled 07:00 & 18:00) | 台股當日市值前 450 名（依 TWSE 官方 openapi `t187ap03_L` shares-outstanding × 當日收盤價；排除 ETF / 特別股 / 下市 / 權證） | `picks.json` | `DISCORD_WEBHOOK_URL` (.env) |
| **持股健檢** (ad-hoc) | 使用者臨時提供的持股清單（**僅需股票名稱或 ticker**；不含成本價、持股數、盈虧） | `healthcheck_YYYY-MM-DD.json` | `DISCORD_WEBHOOK_URL_HEALTHCHECK` (.env) |
| ~~**100元內**~~ (deprecated, 2026-04-23) | ~~全台股當日收盤價 < NT$100~~ | — | — |
| ~~**防禦龍頭**~~ (deprecated, 2026-04-23) | ~~TWSE 產業分類子領域~~ | — | — |

Adding a new strategy = add a row here + a universe fetcher + a picks-file name + a webhook entry. No other rule changes.

## Semantic triggers

- **「重新執行本日分析與推送」** / **「重新執行本日前450名市值分析與推送」** — 前450名市值 strategy full pipeline: (1) 從 TWSE 官方 openapi 取當日市值前 450 名作為 universe（以 `t187ap03_L` shares-outstanding × 當日收盤價計算；排除 ETF / 特別股 / 全額交割 / 下市 / 權證）, (2) build rank cards + price sanity check, (3) eligibility filter + exclusion categories + **技術面 & 籌碼面篩選（下述）**, (4) rebuild `picks.json` with **top 5**, (5) `python daily_push.py picks.json --channels both --strategy "前450名市值"`. Do not reuse the existing `picks.json`.
- **「持股健檢」** / **「檢查持股」** / **「幫我評估持股」** — 使用者會附上持股清單（**只有股票名稱或 ticker**；**不詢問、不利用成本價、持股數、盈虧**）。對清單中每檔執行 rank-card + price sanity check + source priority 規則，依據財報、法說、新聞等 tier-1/2/3 來源比較「**現價 vs. 12 個月 Base 目標價**」給出操作建議：
  - **🟢 加碼** — Base upside ≥ +15%、催化劑仍在、無重大利空
  - **🟢 續抱** — Base upside +5% ~ +15%
  - **🟡 中立** — Base upside -5% ~ +5%，估值合理無明顯方向
  - **🔴 減碼** — Base upside -5% ~ -15%，現價接近或略超目標
  - **🔴 獲利了結 / 出場** — Base upside < -15%（現價明顯超越目標），或出現 material bad news / stale target / 基本面轉弱

  ETF / 槓桿 ETF（如 00631L、006208）沒有 EPS/target，標記 `N/A` 並改以追蹤指數現況 + 波動風險/槓桿耗損提示代替評級。輸出 `healthcheck_YYYY-MM-DD.json` 並推送至 `DISCORD_WEBHOOK_URL_HEALTHCHECK`（Discord 頻道「持股健檢」）：summary 表列每檔分類 + 現價 + Base 目標 + upside%，逐檔 embed 附理由 + tier-1/2/3 sources + 催化劑 + 風險 + 建議動作，最後免責。

- **「防禦龍頭」** / **「產業龍頭評估」** / **「幫我選各產業龍頭」** — 使用者會提供一組「證交所產業分類」子領域（例如：半導體、金融保險、電子零組件、生技醫療、食品…）。對**每個子領域**：
  1. 用 TWSE/OTC 產業分類抓取該子領域當日全部成分股為該次 universe（非 0050∪0051，非價<100）。
  2. 對每檔套用既有方法學：rank-card + **price sanity check** + eligibility filter + exclusion categories + source priority（法人報告 > 財報 > 法說會 > 新聞）。
  3. 挑出**一檔**作為該子領域的「潛力代表龍頭」，挑選標準綜合三面向：
     - **基本面穩健度**：近 8 季 EPS 波動小、ROE/現金流正向、負債比健康（防禦性核心）
     - **法人共識 upside**：Base upside % 為正且 data_quality 非 low
     - **產業地位**：市值排名靠前 / 市占率 / 客戶集中度（龍頭門檻）
  4. 若子領域內沒有同時滿足三條件的標的，標註「本領域暫無防禦龍頭」，不湊數。

  產出 `defenders_YYYY-MM-DD.json`（schema 與 picks.json 類似，但多一個 `sector` 欄位標記子領域 + 一個 `runner_ups` 欄位列該領域第 2-3 名落選理由），推送至 `DISCORD_WEBHOOK_URL_DEFENDERS`（Discord 頻道「防禦龍頭」）。Embed 結構：summary 表（sector → 代表檔 → upside% → 評等）+ 逐子領域 embed（含選中理由、runner-ups、風險/催化劑、sources）+ 免責。

- **「重新執行本日100元內分析與推送」** — 100元內 strategy full pipeline: same logic, but universe = all TWSE+OTC tickers with price < NT$100 (snapshot taken same day, filter out 全額交割股、警示股、下市中). Output to `picks_100yuan.json`. Push by setting `DISCORD_WEBHOOK_URL` env var to the value of `DISCORD_WEBHOOK_URL_100YUAN` for that single run, then `python daily_push.py picks_100yuan.json`.

## Pick selection methodology

Applies to any flow that produces a fresh `picks.json` (local run, cloud trigger, subagent pipeline). Rules are methodology-only — no hard-coded tickers or sector quotas.

### Universe
- Default: **台灣50 (0050) + 中型100 (0051)** constituent union (~150 tickers). Override only with explicit user instruction.
- Fetch constituent list from 元大投信 / wantgoo / pocket at run-time; store a dated `universe_YYYY-MM-DD.txt` snapshot for traceability.

### Price sanity check (mandatory at rank-card stage)
Before a ticker enters the shortlist, cross-verify its current price against **at least two independent sources** (e.g. Yahoo 股市 + TWSE MI_INDEX, or goodinfo + cnyes). Reject the card and tag `price_anomaly` if the two sources disagree by >3%, or if the price looks like a factor-of-10/100 artifact (除權息基準、零股欄位誤抓、parse error). This check is especially load-bearing for the **100元內** strategy because a mis-parsed price can wrongly pull a NT$185 ticker into a "price<100" universe. Applies to all strategies.

### Per-ticker rank card (required fields)
For every ticker in the universe produce a card with: `ticker`, `name`, `price` (int NT$), `pe_trailing`, `eps_2026` (2dp), `target_base` (int NT$), `upside_pct = (target_base - price) / price × 100` (1dp), `rating`, `data_quality ∈ {high, med, low}`, `note`, `sources`.

Price and trailing P/E MUST come from the same intra-day snapshot (typically Yahoo Taiwan 股市 or equivalent) to keep them internally consistent. EPS and target must follow the **Source priority** rules below.

### Rating (keyed to Base upside %)
| Band | Rating | Color |
|---|---|---|
| ≥ +20% | 🟢 首選/核心 | 0x00B894 |
| +10 ~ +19.9% | 🟢 進場 | 0x00B894 |
| 0 ~ +9.9% | 🟡 偏高 | 0xFDCB6E |
| -0.1 ~ -10% | 🔴 等回 | 0xD63031 |
| < -10% | 🔴 追高風險 | 0xD63031 |

The canonical implementation is `rating_for(upside_pct)` in `daily_push.py`. Any downstream builder that computes a rating independently MUST stay consistent with this function.

### Technical & chip filter (2026-04-23 onward; 前450名市值 strategy only)

Must pass **both** before entering shortlist:

1. **Technical — entering uptrend but not overheated**
   - 5-day MA crossing above 20-day MA (or already above with positive slope), AND
   - RSI(14) ∈ [50, 70]（過熱排除）, AND
   - 近 5 日累積漲幅 ≤ +15%（急漲排除）, AND
   - 現價距近 60 日高點 ≤ 0%（未破新高）OR 剛突破新高但成交量同步放大

2. **Chip — institutional accumulation yesterday**
   - 前一交易日：**投信買超 > 0** **OR** **外資買超 > 0**（至少一方買進）, AND
   - 前一交易日：**三大法人合計買超 > 0**（自營含避險不得使合計轉負）

資料來源：TWSE MI_INDEX / T86 外資買賣超 / TWT38U 投信買賣超 / TWT43U 自營商 日報。任一資料缺失或值為 null 則視為不通過。

### Eligibility filter (universe → shortlist)
Keep only cards that satisfy **all** of:
1. `rating` starts with 🟢 (首選 or 進場).
2. `data_quality` ∈ {high, med}.
3. `upside_pct ≥ 15%`.
4. Both `eps_2026` and `target_base` are non-null (no bare price-only cards).

### Exclusion categories (shortlist → final picks)
Remove any shortlist entry that falls into any of these categories; do not silently keep them just to fill the slate. Record the reason per excluded ticker for traceability.
- **Stale target**: price has moved well past the consensus target in either direction, or the consensus hasn't been re-marked after a meaningful corporate event.
- **Extreme analyst dispersion**: target range is so wide (>2× min-to-max) that the midpoint carries little signal; treat single-outlier targets as not a consensus.
- **Single-source target**: only one sell-side house or one blogger; sample too thin to count as consensus.
- **Loss-making or pre-revenue base**: EPS around zero or negative; ratio-based targets become unstable.
- **Price / data anomaly**: page returned an obviously wrong price (split/dividend artifact, parse error, zero-volume line).
- **Possible ex-dividend mismatch**: target and price priced under different dividend assumptions; re-anchor before ranking.
- **Target pinned to prior fiscal year**: the cited target is a 2025 figure; without a refreshed 2026 target, the upside% comparison is apples-to-oranges.
- **No 2026 EPS consensus**: only trailing or 2025 EPS available.
- **Target vs. EPS mismatch**: target number exists but without a matching 2026 EPS projection to back it.
- **Cyclical industries with low forward visibility**: airlines, shipping, pure commodity cycles — exclude unless a tier 1-3 source explicitly models the current cycle phase.
- **Material bad news**: 暴雷, 停牌, 董監事事件, SEC/FSC/競爭主管機關調查等。

### Final selection
- Sort remaining picks by `upside_pct` desc.
- Take **top 5** by a blended score: `0.5 × upside_pct_normalised + 0.3 × chip_strength + 0.2 × technical_momentum`. Size mix (大 / 中 / 小) is a tie-breaker, not a hard quota.
- Rebuild `picks.json`; `meta.theme` records the universe + sort key + filter summary; `meta.generated_at` MUST include time to the second (`YYYY-MM-DD HH:MM:SS TST`); each pick's `sources_short` lists tier 1-3 URLs.

### Fresh evaluation, daily
- Do not anchor to yesterday's picks; re-run the pipeline from scratch each day.
- Cache is fine for constituent lists and long-shelf-life filings; do not cache rank cards or final picks.

## Source priority for picks research

All future `picks.json` (whether generated locally or by the cloud trigger) MUST ground every number in **primary sources** in this priority order:

1. **原始法人報告 / sell-side analyst reports** (PDF or IR page) — highest weight for target price, 2026/2027 EPS consensus, scenario fan.
2. **原始財報 / raw financial statements** from 公開資訊觀測站 (MOPS) or company IR — highest weight for trailing P/E, market cap, revenue YoY, gross margin, current-quarter EPS.
3. **原始法說會資料 / investor-conference materials** (presentation deck, transcript, recording notes) — highest weight for forward guidance, catalysts with dates, management commentary, risk disclosure.
4. **News coverage / aggregator summaries** (鉅亨網, 經濟日報, UDN, CMoney, 財報狗, etc.) — lower weight; only as leads or colour commentary on top of (1)-(3), never as the sole citation for a number that will appear in a pushed embed.

WebSearch snippets, TradingView / Yahoo Finance summary fields, and FactSet consensus quoted through news articles all count as tier 4 leads — they indicate *where* to look for (1)-(3), but do not substitute for them.

Every pushed pick should have at least one tier-1/2/3 source behind its price, EPS scenarios, and target. Record the source URLs in `sources_short` (or a richer field if introduced later). When a tier-1/2/3 source cannot be obtained, tag the affected field with `[原文取得失敗、此為推論的回答]` or `[尚未閱讀原文、此為推論的回答]` per the global inference-tag convention — do not silently fall back to tier 4.
