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
