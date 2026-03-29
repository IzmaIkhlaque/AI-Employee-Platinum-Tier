@echo off
echo [%date% %time%] Starting vault sync...
cd /d "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault"

REM Pull Cloud changes first
git pull origin main --no-edit
if %errorlevel% neq 0 (
    echo [%date% %time%] ERROR: git pull failed. Check for conflicts.
    exit /b 1
)

REM Push Local changes
git add -A
git commit -m "Local sync: %date% %time%" 2>nul
git push origin main
if %errorlevel% neq 0 (
    echo [%date% %time%] ERROR: git push failed.
    exit /b 1
)

echo [%date% %time%] Sync complete.
