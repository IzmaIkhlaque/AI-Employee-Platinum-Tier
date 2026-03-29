@echo off
::
:: AI Employee Scheduled Tasks — Gold Tier (Windows)
::
:: Usage:
::   scheduler.bat daily           - Morning routine (Needs_Action + Approved + Odoo sync)
::   scheduler.bat odoo-sync       - Sync Odoo accounting to /Accounting/Current_Month.md
::   scheduler.bat linkedin        - Generate LinkedIn post draft -> /Pending_Approval
::   scheduler.bat social-batch    - Generate FB + IG + 2x Twitter drafts -> /Pending_Approval
::   scheduler.bat weekly-audit    - Weekly business audit -> /Briefings/
::   scheduler.bat ceo-briefing    - Monday Morning CEO Briefing -> /Briefings/
::   scheduler.bat health-check    - Verify MCP servers, watchers, error counts
::   scheduler.bat check-approvals - Check /Pending_Approval, /Approved, /Rejected
::   scheduler.bat email-check     - One-shot Gmail poll
::   scheduler.bat status          - Print folder counts and recent logs
::   scheduler.bat help            - Show this message
::

setlocal enabledelayedexpansion

:: ── Configuration ────────────────────────────────────────────────────────────

:: Resolve vault path: parent of the scripts\ folder
set "SCRIPT_DIR=%~dp0"
if not defined VAULT_PATH (
    for %%I in ("%SCRIPT_DIR%..") do set "VAULT_PATH=%%~fI"
)

:: Log directory
set "LOG_DIR=%VAULT_PATH%\memory\scheduler_logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Timestamp for this run (safe for filenames)
for /f "tokens=1-3 delims=/ " %%a in ("%DATE%") do (
    set "D_DD=%%a"
    set "D_MM=%%b"
    set "D_YYYY=%%c"
)
for /f "tokens=1-3 delims=:. " %%a in ("%TIME: =0%") do (
    set "T_HH=%%a"
    set "T_MM=%%b"
    set "T_SS=%%c"
)
set "TS=%D_YYYY%-%D_MM%-%D_DD%_%T_HH%-%T_MM%-%T_SS%"

:: Common log file for this run
set "RUN_LOG=%LOG_DIR%\scheduler_%TS%.log"

:: ── Helpers ──────────────────────────────────────────────────────────────────

:log
    echo [%DATE% %TIME%] %~1
    echo [%DATE% %TIME%] %~1 >> "%RUN_LOG%"
    goto :eof

:: ── Main dispatch ─────────────────────────────────────────────────────────────

call :log "Starting scheduler task: %~1"
call :log "Vault path: %VAULT_PATH%"

if "%~1"=="daily"           goto :cmd_daily
if "%~1"=="odoo-sync"       goto :cmd_odoo_sync
if "%~1"=="linkedin"        goto :cmd_linkedin
if "%~1"=="social-batch"    goto :cmd_social_batch
if "%~1"=="weekly-audit"    goto :cmd_weekly_audit
if "%~1"=="ceo-briefing"    goto :cmd_ceo_briefing
if "%~1"=="health-check"    goto :cmd_health_check
if "%~1"=="check-approvals" goto :cmd_check_approvals
if "%~1"=="email-check"     goto :cmd_email_check
if "%~1"=="status"          goto :cmd_status
if "%~1"=="help"            goto :cmd_help
if "%~1"=="-h"              goto :cmd_help
if "%~1"=="--help"          goto :cmd_help

echo Unknown command: %~1
echo Run "scheduler.bat help" for usage.
exit /b 1

:: ── Commands ─────────────────────────────────────────────────────────────────

:cmd_daily
call :log "Running daily morning routine..."
cd /d "%VAULT_PATH%"
claude --print "Perform your daily morning routine:

1. Check /Needs_Action for any new items and process each one using the file-processing skill
2. Check /Approved for any actions ready to execute and run them
3. Sync accounting data: call the Odoo MCP to fetch recent invoices and payments, append a summary row to /Accounting/Current_Month.md
4. Check /Pending_Approval for items older than 24 hours and flag them in Dashboard.md
5. Update Dashboard.md: refresh folder counts, add a Daily Check entry to Recent Activity, update the Last Updated timestamp
6. Log all actions to /Logs/audit.jsonl using the audit-logger skill

Be thorough but concise. Report what was done." >> "%LOG_DIR%\daily_%TS%.log" 2>&1
call :log "Daily routine completed"
goto :done

:cmd_odoo_sync
call :log "Syncing Odoo accounting data..."
cd /d "%VAULT_PATH%"
claude --print "Sync accounting data from Odoo to the vault:

1. Call the Odoo MCP server:
   - get_invoices (posted, last 30 days)
   - get_overdue_invoices
   - get_payments (last 30 days)
   - get_account_balances
2. Open /Accounting/Current_Month.md and update:
   - Total invoiced this month
   - Total collected this month
   - Outstanding (overdue) balance
   - Top 3 unpaid invoices (client, amount, days overdue)
   - Account balances snapshot
3. If any invoice is overdue > 30 days, create a FINANCE_overdue_*.md in /Needs_Action
4. Log the sync to /Logs/audit.jsonl with action: odoo_sync

Report the totals and any flags." >> "%LOG_DIR%\odoo_sync_%TS%.log" 2>&1
call :log "Odoo sync completed"
goto :done

:cmd_linkedin
call :log "Generating LinkedIn post draft..."
cd /d "%VAULT_PATH%"
claude --print "Generate a LinkedIn post draft using the linkedin-posting skill:

1. Read Business_Goals.md — note the LinkedIn Content Strategy, content pillars, and today's day of the week
2. Check the Content Calendar for today's recommended content type (Mon=Industry Insight, Wed=How-To, Fri=Thought Leadership)
3. Check /Done for recent completed tasks that could inspire the post
4. Draft an engaging post:
   - Under 3000 characters
   - 3–5 relevant hashtags at the end
   - Tone: professional but approachable (per Business_Goals.md brand voice)
   - No emojis unless they add real value
5. Save to /Pending_Approval/PENDING_linkedin_post_YYYYMMDD_HHMMSS.md with frontmatter:
   type: approval_request
   action: social_post
   platform: linkedin
   status: pending
6. Update Dashboard.md Pending Approvals count
7. Log to /Logs/audit.jsonl with action: social_post_drafted

Report the post preview and file path." >> "%LOG_DIR%\linkedin_%TS%.log" 2>&1
call :log "LinkedIn draft generation completed"
goto :done

:cmd_social_batch
call :log "Generating social media content batch..."
cd /d "%VAULT_PATH%"
claude --print "Generate a social media content batch using the social-media-manager skill:

Read Business_Goals.md for brand voice, content themes, and posting guidelines for each platform.

Create 4 separate approval files in /Pending_Approval:

1. Facebook post:
   - Theme: business update, industry news, or client testimonial
   - 150-300 words, 2-3 hashtags
   - Filename: PENDING_facebook_post_YYYYMMDD_HHMMSS.md

2. Instagram caption:
   - Visual-first framing (describe the image concept in ## Image Concept section)
   - 100-150 words, 5-10 hashtags
   - Filename: PENDING_instagram_post_YYYYMMDD_HHMMSS.md

3. Twitter/X post #1:
   - Quick insight or industry take, under 280 characters
   - Filename: PENDING_twitter_post_1_YYYYMMDD_HHMMSS.md

4. Twitter/X post #2:
   - Engagement question or poll idea, under 280 characters
   - Filename: PENDING_twitter_post_2_YYYYMMDD_HHMMSS.md

Each file must have frontmatter:
   type: approval_request
   action: social_post
   platform: [facebook|instagram|twitter]
   status: pending

Update Dashboard.md Pending Approvals count (+4).
Log to /Logs/audit.jsonl with action: social_post_drafted for each.

Report all 4 post previews." >> "%LOG_DIR%\social_batch_%TS%.log" 2>&1
call :log "Social media batch generation completed"
goto :done

:cmd_weekly_audit
call :log "Running weekly business audit..."
cd /d "%VAULT_PATH%"
claude --print "Perform a weekly business audit and save results to /Briefings/:

1. TASK REVIEW:
   - Count /Done items created in the last 7 days (by type: email, file, social, finance)
   - List any items stuck in /Pending_Approval for > 48 hours
   - Check /Plans for incomplete multi-step plans

2. FINANCIAL REVIEW:
   - Read /Accounting/Current_Month.md for current month totals
   - Query Odoo: get_overdue_invoices, get_payments
   - Flag any invoices overdue > 14 days

3. SOCIAL MEDIA REVIEW:
   - Count social posts approved and pending this week
   - Identify which platforms had the most content activity

4. EMAIL ACTIVITY:
   - Read /Logs/audit.jsonl, count email_received and send_success in last 7 days

5. BOTTLENECKS:
   - List top 3 items that slowed down the workflow this week
   - Suggest one process improvement

6. Save to /Briefings/WEEKLY_AUDIT_YYYYMMDD.md
7. Update Dashboard.md with the audit summary
8. Log to /Logs/audit.jsonl with action: weekly_audit_generated

Report the key findings." >> "%LOG_DIR%\weekly_audit_%TS%.log" 2>&1
call :log "Weekly audit completed"
goto :done

:cmd_ceo_briefing
call :log "Generating Monday Morning CEO Briefing..."
cd /d "%VAULT_PATH%"
claude --print "Generate the Monday Morning CEO Briefing using the ceo-briefing skill.

This is the weekly autonomous business intelligence report. Follow the full skill procedure:

1. FINANCIAL OVERVIEW (from Odoo MCP + /Accounting/Current_Month.md):
   - Revenue collected vs target this month
   - Outstanding invoices and overdue amounts
   - Account balances summary

2. TASK SUMMARY (from /Done and /Needs_Action):
   - Items completed this week (count by type)
   - Items pending action
   - Items awaiting approval (how long)

3. SOCIAL MEDIA PERFORMANCE (from /Logs/audit.jsonl + /Social_Media/):
   - Posts published this week per platform
   - Posts still pending approval
   - Any notable engagement data

4. EMAIL ACTIVITY (from /Logs/audit.jsonl):
   - Emails received and actioned this week
   - Average response time estimate
   - Any flagged emails needing CEO attention

5. SYSTEM HEALTH (from /Logs/errors.jsonl + /Logs/audit.jsonl):
   - Error count last 7 days
   - Last successful run per component
   - Any components that need attention

6. RECOMMENDATIONS:
   - Top 3 actions for the CEO this week
   - Priority order with brief rationale

Save to /Briefings/CEO_BRIEFING_YYYYMMDD.md with proper frontmatter.
Update Dashboard.md with briefing status.
Log to /Logs/audit.jsonl with action: ceo_briefing_generated.

Report the executive summary section." >> "%LOG_DIR%\ceo_briefing_%TS%.log" 2>&1
call :log "CEO Briefing generation completed"
goto :done

:cmd_health_check
call :log "Running system health check..."
cd /d "%VAULT_PATH%"
claude --print "Perform a system health check and update Dashboard.md:

1. MCP SERVERS — test each connection:
   - email-mcp: call check_smtp_status
   - odoo: call odoo_status
   - social-media: call social_media_status

2. ERROR LOG — read /Logs/errors.jsonl:
   - Count errors in last 24 hours
   - Count errors in last 7 days
   - Identify most common error component

3. AUDIT LOG — read /Logs/audit.jsonl:
   - Find last successful entry per component (gmail_watcher, filesystem_watcher, orchestrator)
   - Flag any component with no successful entry in > 48 hours

4. WATCHER STATUS:
   - Check if orchestrator_state.json exists and when it was last modified
   - Report last processed file timestamps

5. FOLDER COUNTS — report current counts for:
   Inbox / Needs_Action / Plans / Pending_Approval / Approved / Rejected / Done / Briefings / Accounting

6. Update Dashboard.md System Health section with:
   - Overall status: HEALTHY / DEGRADED / ERROR
   - Last checked timestamp
   - Any components in warning or error state

7. If any MCP server is down or error count > 5 in 24h:
   - Create URGENT_health_alert_YYYYMMDD_HHMMSS.md in /Needs_Action

Log to /Logs/audit.jsonl with action: health_check.

Report the overall health status." >> "%LOG_DIR%\health_check_%TS%.log" 2>&1
call :log "Health check completed"
goto :done

:cmd_check_approvals
call :log "Checking pending approvals..."
cd /d "%VAULT_PATH%"
claude --print "Check the approval workflow status:

1. List all items in /Pending_Approval with their age (created timestamp from frontmatter)
2. Flag any items older than 24 hours as OVERDUE in your report
3. Check /Approved for items ready to execute — if any exist, process them now
4. Check /Rejected for items that need acknowledgment or archiving
5. Update Dashboard.md Pending Approvals section with current counts
6. Log the check to /Logs/audit.jsonl with action: approval_check

Report what needs human attention and what was auto-executed." >> "%LOG_DIR%\approvals_%TS%.log" 2>&1
call :log "Approval check completed"
goto :done

:cmd_email_check
call :log "Running one-shot Gmail check..."
cd /d "%VAULT_PATH%"
if exist "watchers\gmail_watcher.py" (
    python watchers\gmail_watcher.py --vault-path "%VAULT_PATH%" --once 2>> "%LOG_DIR%\email_check_%TS%.log"
    call :log "Email check completed"
) else (
    call :log "ERROR: watchers\gmail_watcher.py not found"
    exit /b 1
)
goto :done

:cmd_status
echo.
echo === AI Employee Status ===
echo.
echo Vault: %VAULT_PATH%
echo.
echo Folder Counts:
for %%F in (Inbox Needs_Action Plans Pending_Approval Approved Rejected Done Briefings Accounting) do (
    set "COUNT=0"
    if exist "%VAULT_PATH%\%%F" (
        for /f %%N in ('dir /b /a-d "%VAULT_PATH%\%%F\*.md" 2^>nul ^| find /c /v ""') do set "COUNT=%%N"
    )
    echo   %-18s !COUNT! >> nul
    echo   %%F: !COUNT!
)
echo.
echo Recent Scheduler Logs:
if exist "%LOG_DIR%" (
    dir /b /o-d "%LOG_DIR%\*.log" 2>nul | findstr /n "." | findstr "^[1-5]:" | for /f "tokens=2 delims=:" %%L in ('findstr /n "."') do echo   %%L
)
echo.
goto :done

:cmd_help
echo.
echo AI Employee Scheduler — Gold Tier
echo.
echo Usage: scheduler.bat ^<command^>
echo.
echo Gold Tier Commands:
echo   daily           - Morning routine: Needs_Action + Approved + Odoo sync
echo   odoo-sync       - Sync Odoo invoices/payments to /Accounting/Current_Month.md
echo   linkedin        - Generate LinkedIn post draft
echo   social-batch    - Generate FB + IG + 2x Twitter drafts (4 files)
echo   weekly-audit    - Weekly business audit saved to /Briefings/
echo   ceo-briefing    - Monday Morning CEO Briefing (full business intelligence)
echo   health-check    - Verify MCP servers, watchers, error counts
echo.
echo Silver Tier Commands (carried over):
echo   check-approvals - Check /Pending_Approval, /Approved, /Rejected
echo   email-check     - One-shot Gmail poll via gmail_watcher.py
echo.
echo Utility:
echo   status          - Print folder counts and recent log files
echo   help            - Show this message
echo.
echo Environment:
echo   VAULT_PATH      - Override vault path (default: parent of scripts\)
echo.
echo Logs: memory\scheduler_logs\
echo.
goto :done

:done
call :log "Task completed: %~1"
endlocal
exit /b 0
