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

Daily push runs from a **cloud RemoteTrigger** (cron `0 0 * * *` UTC ≈ 08:04 Taipei) that executes a self-contained prompt — it does not call these scripts. The cloud prompt's `post()` helper MUST set `User-Agent: tw-stock-bot/0.1`; Python's default UA is blocked by Cloudflare with HTTP 403 (error 1010) and fails silently. See `SCHEDULE_RUNBOOK.md` for the full incident history.

`run_daily.bat` + `.local_fallback_enabled` flag file is the **local Windows Task Scheduler fallback** (08:30 Taipei), gated so it only fires when the flag file exists. It runs `daily_push.py picks.json` against whatever `picks.json` currently holds — no fresh analysis. Enable/disable commands are in `SCHEDULE_RUNBOOK.md`.

## Content conventions

- Currency is NT$ throughout; prices are integers (no decimals), EPS to 2 decimals.
- Every push ends with a disclaimer embed stating this is AI-generated and **not investment advice** — keep it.
- Default notification channel is **Discord webhook** (user preference: no LINE, no OAuth flows).

## Pick selection methodology

Applies to any flow that produces a fresh `picks.json` (local run, cloud trigger, subagent pipeline). Rules are methodology-only — no hard-coded tickers or sector quotas.

### Universe
- Default: **台灣50 (0050) + 中型100 (0051)** constituent union (~150 tickers). Override only with explicit user instruction.
- Fetch constituent list from 元大投信 / wantgoo / pocket at run-time; store a dated `universe_YYYY-MM-DD.txt` snapshot for traceability.

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
- Take **top 6**, balanced across **大型龍頭 vs 中型成長** (roughly half-half); if the top 6 by pure upside is lopsided, substitute from lower-ranked eligible picks to restore balance rather than drop the size mix rule.
- Rebuild `picks.json` in the schema documented above; `meta.theme` records the universe and the sort key; each pick's `sources_short` lists tier 1-3 URLs (tag otherwise per **Source priority**).

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
