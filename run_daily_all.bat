@echo off
REM Daily TW stock pipeline — 前450名市值 strategy ONLY.
REM Runs fresh web research + dual push (Discord + LINE).
REM Invoked by Windows Task Scheduler twice daily (07:00 and 18:00 Taipei).
REM
REM Register both schedules (run once in elevated cmd):
REM   schtasks /create /tn "tw-stock 07:00" /tr "\"C:\Users\can20\OneDrive\other\work\stocks\run_daily_all.bat\"" /sc daily /st 07:00 /rl LIMITED
REM   schtasks /create /tn "tw-stock 18:00" /tr "\"C:\Users\can20\OneDrive\other\work\stocks\run_daily_all.bat\"" /sc daily /st 18:00 /rl LIMITED
REM Uninstall:
REM   schtasks /delete /tn "tw-stock 07:00" /f
REM   schtasks /delete /tn "tw-stock 18:00" /f

cd /d C:\Users\can20\OneDrive\other\work\stocks
if not exist logs mkdir logs

set STAMP=%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%%time:~3,2%
set LOG=logs\run_%STAMP%.log

echo ======== %STAMP% 前450名市值 run start ======== >> "%LOG%" 2>&1
claude -p --allowedTools "Bash WebSearch WebFetch Read Write Edit Glob Grep" "重新執行本日前450名市值分析與推送" >> "%LOG%" 2>&1
echo ======== %STAMP% run end ======== >> "%LOG%" 2>&1
