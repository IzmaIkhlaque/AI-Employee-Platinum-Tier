# Windows Task Scheduler — Platinum Tier Setup

This document covers the **four new Platinum-tier tasks** that run the Local Agent
and vault sync on your Windows PC.

For the original Gold-tier tasks (daily routine, LinkedIn, CEO briefing, etc.)
see `docs/windows-scheduler-setup.md`.

---

## Prerequisites

Before creating these tasks, verify:

```powershell
# Python is in PATH
python --version

# Claude Code is in PATH
claude --version

# Vault exists
Test-Path "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault"

# Git is in PATH
git --version
```

If any of these fail, fix them before continuing — Task Scheduler runs in a
minimal environment and will fail silently if the binary isn't in the system PATH.

---

## Quick Setup — PowerShell (Recommended)

Open **PowerShell as Administrator** (`Win + S` → PowerShell → right-click → Run as administrator)
and paste this entire block:

```powershell
$vault = "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault"
$python = (Get-Command python).Source
$cmd    = "cmd.exe"

# ── Helper: create a task that repeats every N minutes all day ───────────────
function New-RepeatTask {
    param(
        [string]$Name,
        [string]$Program,
        [string]$Arguments,
        [string]$WorkDir,
        [int]   $RepeatMinutes
    )
    $action   = New-ScheduledTaskAction -Execute $Program `
                    -Argument $Arguments `
                    -WorkingDirectory $WorkDir

    # Base trigger: fires at midnight, then repeats every N minutes for 24 hours
    $trigger  = New-ScheduledTaskTrigger -Daily -At "00:00"
    $trigger.RepetitionInterval = [System.TimeSpan]::FromMinutes($RepeatMinutes)
    $trigger.RepetitionDuration = [System.TimeSpan]::FromHours(24)

    $settings = New-ScheduledTaskSettingsSet `
                    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
                    -StartWhenAvailable `
                    -MultipleInstances IgnoreNew `
                    -RunOnlyIfNetworkAvailable

    $principal = New-ScheduledTaskPrincipal `
                    -UserId $env:USERNAME `
                    -LogonType InteractiveToken `
                    -RunLevel Highest

    Register-ScheduledTask `
        -TaskName  $Name `
        -Action    $action `
        -Trigger   $trigger `
        -Settings  $settings `
        -Principal $principal `
        -Force | Out-Null

    Write-Host "Created: $Name  (every ${RepeatMinutes}min)"
}

# ── Helper: create a one-time daily or weekly task ───────────────────────────
function New-ScheduledAITask {
    param(
        [string]$Name,
        [string]$Arguments,
        [string]$Time,
        [string]$Days
    )
    $action  = New-ScheduledTaskAction -Execute $cmd `
                   -Argument $Arguments `
                   -WorkingDirectory $vault

    if ($Days -eq "Daily") {
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time
    } else {
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Days -At $Time
    }

    $settings = New-ScheduledTaskSettingsSet `
                    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
                    -StartWhenAvailable `
                    -RunOnlyIfNetworkAvailable

    Register-ScheduledTask -TaskName $Name -Action $action `
        -Trigger $trigger -Settings $settings -Force | Out-Null
    Write-Host "Created: $Name  ($Days at $Time)"
}

# ── Task 1: Local Agent — every 10 minutes ───────────────────────────────────
New-RepeatTask `
    -Name           "AI-LocalAgent" `
    -Program        $python `
    -Arguments      "local/local_agent.py --once" `
    -WorkDir        $vault `
    -RepeatMinutes  10

# ── Task 2: Vault Sync — every 10 minutes ────────────────────────────────────
New-RepeatTask `
    -Name           "AI-VaultSync" `
    -Program        $cmd `
    -Arguments      "/c `"$vault\scripts\vault_sync.bat`"" `
    -WorkDir        $vault `
    -RepeatMinutes  10

# ── Task 3: Daily Morning Routine — 8:00 AM ──────────────────────────────────
New-ScheduledAITask `
    -Name      "AI-Daily-Morning-Platinum" `
    -Arguments "/c `"$vault\scripts\scheduler.bat daily`"" `
    -Time      "08:00" `
    -Days      "Daily"

# ── Task 4: CEO Briefing — Monday 7:00 AM ────────────────────────────────────
New-ScheduledAITask `
    -Name      "AI-CEO-Briefing-Platinum" `
    -Arguments "/c `"$vault\scripts\scheduler.bat ceo-briefing`"" `
    -Time      "07:00" `
    -Days      "Monday"

Write-Host ""
Write-Host "All 4 Platinum tasks created."
Write-Host "Verify in Task Scheduler > Task Scheduler Library (look for AI-*)"
```

---

## Task Reference

| Task Name | Program | Trigger | Purpose |
|-----------|---------|---------|---------|
| `AI-LocalAgent` | `python` | Every 10 min | Sync vault, merge updates, execute approved actions |
| `AI-VaultSync` | `cmd` | Every 10 min | git pull + git push (runs even if Local Agent fails) |
| `AI-Daily-Morning-Platinum` | `cmd` | Daily 8:00 AM | Morning Needs_Action check + light Odoo sync |
| `AI-CEO-Briefing-Platinum` | `cmd` | Monday 7:00 AM | Full business intelligence briefing |

> **Note:** `AI-VaultSync` is intentionally separate from `AI-LocalAgent`.
> If the Local Agent Python script crashes, Git sync still runs and Cloud
> can still communicate with Local via the vault.

---

## Manual GUI Steps

Use these if the PowerShell script fails or you prefer clicking.

### Repeat-every-10-minutes trigger (Tasks 1 and 2)

This is the tricky part — Task Scheduler hides the repeat setting inside the
trigger properties.

**Step-by-step for Task 1 (AI-LocalAgent):**

1. `Win + S` → **Task Scheduler** → Open
2. Click **Create Task...** (right panel — NOT "Create Basic Task")
3. **General tab:**
   - Name: `AI-LocalAgent`
   - Check **Run whether user is logged on or not**
   - Check **Run with highest privileges**
   - Configure for: `Windows 10`

4. **Triggers tab → New:**
   - Begin the task: `On a schedule`
   - Settings: `Daily`
   - Start: Today's date, `12:00:00 AM`
   - Recur every: `1` days
   - ✅ **Repeat task every:** `10 minutes`
   - For a duration of: `1 day`
   - ✅ Enabled
   - Click **OK**

5. **Actions tab → New:**
   - Action: `Start a program`
   - Program/script:
     ```
     python
     ```
   - Add arguments:
     ```
     local/local_agent.py --once
     ```
   - Start in:
     ```
     D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault
     ```

6. **Settings tab:**
   - ✅ Run task as soon as possible after a scheduled start is missed
   - ✅ If the running task does not end when requested, force it to stop
   - Stop the task if it runs longer than: `5 minutes`
   - If the task is already running: `Do not start a new instance`

7. Click **OK** → enter your Windows password.

---

**Repeat for Task 2 (AI-VaultSync):**

Same steps, except in **Actions tab**:
- Program/script: `cmd`
- Add arguments:
  ```
  /c "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault\scripts\vault_sync.bat"
  ```

---

**Task 3 (Daily Morning) and Task 4 (CEO Briefing):**

Same steps as the Gold-tier tasks in `docs/windows-scheduler-setup.md`.
Skip the repeat trigger — just set a fixed daily or weekly time.

---

## Verifying Tasks Are Running

```powershell
# List all AI-* tasks and their state
Get-ScheduledTask | Where-Object { $_.TaskName -like "AI-*" } |
    Select-Object TaskName, State, @{N="LastRun";E={(Get-ScheduledTaskInfo $_.TaskName).LastRunTime}} |
    Format-Table -AutoSize
```

Expected output:
```
TaskName                    State   LastRun
--------                    -----   -------
AI-LocalAgent               Ready   3/26/2026 10:00:00 AM
AI-VaultSync                Ready   3/26/2026 10:00:00 AM
AI-Daily-Morning-Platinum   Ready   3/26/2026 8:00:00 AM
AI-CEO-Briefing-Platinum    Ready   3/24/2026 7:00:00 AM
```

Run a task immediately to test it:

```powershell
Start-ScheduledTask -TaskName "AI-LocalAgent"
Start-ScheduledTask -TaskName "AI-VaultSync"
```

Check the last result code (0 = success):

```powershell
(Get-ScheduledTaskInfo "AI-LocalAgent").LastTaskResult
```

---

## Viewing Logs

Local Agent writes to the vault audit log:

```powershell
# Last 20 local_agent actions
python -c "
from utils.audit_logger import AuditLogger
audit = AuditLogger()
for e in audit.get_recent_logs(20):
    if e.get('component') == 'local_agent':
        print(e['ts'][:19], e['action'], e['status'])
"
```

Vault sync log (written by `vault_sync.bat`):

```powershell
# No built-in log in vault_sync.bat — add one by running manually:
cmd /c "D:\Izma folder\...\scripts\vault_sync.bat" 2>&1 | Tee-Object -FilePath memory\scheduler_logs\vault_sync_test.log
```

---

## Troubleshooting

### "python" is not recognized
Task Scheduler uses the system PATH, not your user PATH. Fix:

1. `Win + S` → **Edit the system environment variables** → **Environment Variables**
2. Under **System variables** → select **Path** → **Edit**
3. Click **New** → add the folder containing `python.exe` (e.g. `C:\Python313\`)
4. Click **OK** on all dialogs
5. Restart Task Scheduler (or just log out and back in)

### Task shows "Last Run Result: 0x1" (exit code 1)
The script exited with an error. Check the audit log and error log:

```powershell
Get-Content "Logs\errors.jsonl" | Select-Object -Last 10 | ForEach-Object { $_ | ConvertFrom-Json | Select-Object ts, component, message }
```

### Vault sync fails: "git is not recognized"
Add Git to the system PATH (same process as Python above). Git is usually at
`C:\Program Files\Git\cmd\`.

### Local Agent runs but doesn't process Cloud updates
Check that the vault is connected to GitHub:

```powershell
cd "D:\Izma folder\...\AI_Employee_Vault"
git remote -v
git status
```

If the remote is missing: `git remote add origin https://github.com/IzmaIkhlaque/AI-Employee-Gold-Tier.git`

### Two instances running at the same time
Make sure the task **Settings tab** has:
- "If the task is already running" set to **Do not start a new instance**

This prevents overlap if `local_agent.py --once` takes longer than 10 minutes.

---

## Removing Platinum Tasks

```powershell
# Remove just the Platinum tasks
"AI-LocalAgent","AI-VaultSync","AI-Daily-Morning-Platinum","AI-CEO-Briefing-Platinum" |
    ForEach-Object { Unregister-ScheduledTask -TaskName $_ -Confirm:$false }
```

To remove ALL AI tasks (Gold + Platinum):

```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "AI-*" } |
    Unregister-ScheduledTask -Confirm:$false
```
