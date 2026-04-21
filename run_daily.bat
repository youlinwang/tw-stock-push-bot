@echo off
REM Local fallback for TW Stock Daily Picks push.
REM Gated by flag file: only runs if .local_fallback_enabled exists.
REM
REM To enable (after confirming cloud trigger failed):
REM   echo enabled > C:\Users\can20\Documents\Claude\stocks\.local_fallback_enabled
REM   schtasks /Create /TN "TW_Stock_Daily_Push" /TR "C:\Users\can20\Documents\Claude\stocks\run_daily.bat" /SC DAILY /ST 08:30 /F
REM To disable:
REM   del C:\Users\can20\Documents\Claude\stocks\.local_fallback_enabled
REM
REM Logs: run_daily.log next to this script.

cd /d "%~dp0"

if not exist ".local_fallback_enabled" (
    echo [%date% %time%] fallback disabled, skipping >> run_daily.log
    exit /b 0
)

echo [%date% %time%] fallback firing >> run_daily.log
"C:\Python314\python.exe" daily_push.py picks.json >> run_daily.log 2>&1
echo [%date% %time%] exit=%errorlevel% >> run_daily.log
