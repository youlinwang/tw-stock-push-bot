# 台股每日排程 Runbook

## 現況（2026-04-20 16:25 後）

| 項目 | 狀態 |
|---|---|
| 雲端 trigger `trig_01CSYskLt78nbARRu5QrRJ8S` | ✅ 已修復並更新 |
| 觸發時間 | cron `0 0 * * *` UTC = 每日 08:04 (Taipei，帶 jitter) |
| 下次排程 | 2026-04-21 08:04 Taipei |
| Webhook 健康 | ✅ 本機驗證 204 |
| 手動 run 今日測試 | ❌ API 回 200 但 sandbox 14 分鐘未送任何訊息 → 無法當日驗證 |

## 今日早上沒有推送的根因

原 trigger prompt 內的 Python snippet 用 `urllib` POST Discord 時**只設 `Content-Type`**、沒設 `User-Agent`，Python 的預設 UA `Python-urllib/X.Y` 被 Discord 前面的 Cloudflare 以 **error 1010 / HTTP 403** 擋下，Agent 沒有錯誤處理 → 靜默失敗 → 全日無推送。

## 已修復（已 RemoteTrigger.update 到雲端）

新 prompt 的 `post()` 函式：
1. **強制 `User-Agent: tw-stock-bot/0.1`**（解決 CF 擋 bot signature）
2. **自動重試 3 次** 搭配指數 backoff
3. **Step 0 啟動心跳**：agent 第一個動作就送「⏰ 台股每日排程已啟動」embed，不等任何 WebSearch
4. **整個分析包在 try/except**：失敗時推「⚠️ 台股每日排程發生錯誤」含 traceback
5. **完成訊息**：成功結束後推「✅ done: pushed 8 embeds」

## 明早 08:05 Taipei 的驗證 SOP

打開 Discord tw-stock-bot 頻道，按以下順序檢查：

| 預期看到 | 代表 |
|---|---|
| 🟢 「⏰ 台股每日排程已啟動」embed（08:04 左右） | sandbox 能送 Discord，心跳 OK |
| 🟢 「📬 台股潛力標的 每日更新」+ 6 檔個股 + 免責 | 完整分析成功（08:10~08:15） |
| 🟢 「✅ done: pushed 8 embeds for 2026-04-21」 | 流程全程無錯 |
| 🟡 只有心跳、沒有分析 | sandbox 網路 OK、但分析/推送中途錯 → 看「⚠️ 錯誤」embed 的 traceback |
| 🔴 什麼都沒有 | sandbox 完全無法送 Discord → **啟用本機備援（下面一行）** |

## 若明早 08:15 仍無任何訊息 → 啟用本機備援

一條命令啟用：

```cmd
echo enabled > C:\Users\can20\Documents\Claude\stocks\.local_fallback_enabled && schtasks /Create /TN "TW_Stock_Daily_Push" /TR "C:\Users\can20\Documents\Claude\stocks\run_daily.bat" /SC DAILY /ST 08:30 /F
```

- 會每日 08:30 Taipei 本機執行 `daily_push.py picks.json`
- 受 `.local_fallback_enabled` flag file 保護，刪檔即停用
- 只會推送目前 `picks.json` 內容（無每日 fresh 分析；需每日 fresh 時請另外更新 picks.json）
- Log 寫在 `run_daily.log`

停用備援：
```cmd
del C:\Users\can20\Documents\Claude\stocks\.local_fallback_enabled
schtasks /Delete /TN "TW_Stock_Daily_Push" /F
```

## 如果雲端和本機都得並存

本機備援設 08:30 > 雲端 08:04 有 26 分鐘差；若雲端成功就在雲端訊息後 26 分鐘多一份靜態推送（可接受，或把 `.local_fallback_enabled` 刪掉）。
