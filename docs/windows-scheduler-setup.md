# Windows Task Scheduler Setup

Configure Windows Task Scheduler to run AI Employee tasks automatically.

---

## Prerequisites

- Claude Code (`claude`) installed and in system PATH
- Python installed and in system PATH
- `VAULT_PATH` resolvable (the `.bat` auto-detects it from its own location)
- All MCP servers registered (`claude mcp list` shows `email-mcp`, `odoo`, `social-media`)

Verify Claude is accessible:

```cmd
claude --version
```

---

## Quick Setup (All Tasks)

Open **PowerShell as Administrator** and run the block below. It creates all 7 tasks at once.

```powershell
$vault = "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault"
$bat   = "$vault\scripts\scheduler.bat"

# Helper: create one scheduled task
function New-AITask {
    param($Name, $Arg, $Time, $Days)
    $action  = New-ScheduledTaskAction -Execute "cmd.exe" `
                   -Argument "/c `"$bat $Arg`"" `
                   -WorkingDirectory $vault
    if ($Days -eq "Daily") {
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time
    } else {
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Days -At $Time
    }
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
                    -StartWhenAvailable -RunOnlyIfNetworkAvailable
    Register-ScheduledTask -TaskName $Name -Action $action `
        -Trigger $trigger -Settings $settings -Force | Out-Null
    Write-Host "Created: $Name"
}

New-AITask "AI-Daily-Morning"  "daily"           "08:00" "Daily"
New-AITask "AI-Odoo-Sync"      "odoo-sync"       "07:00" "Daily"
New-AITask "AI-LinkedIn"       "linkedin"        "09:00" "Monday,Wednesday,Friday"
New-AITask "AI-Social-Batch"   "social-batch"    "10:00" "Tuesday,Thursday"
New-AITask "AI-Weekly-Audit"   "weekly-audit"    "18:00" "Sunday"
New-AITask "AI-CEO-Briefing"   "ceo-briefing"    "07:00" "Monday"
New-AITask "AI-Health-Check"   "health-check"    "06:00" "Daily"

Write-Host ""
Write-Host "All tasks created. Verify in Task Scheduler > Task Scheduler Library."
```

> **Note:** If your vault path contains spaces (it does), the PowerShell script above handles quoting automatically. If you use the GUI instead, see the manual steps below.

---

## Task Reference Table

| Task Name | Command | Trigger | What it does |
|-----------|---------|---------|--------------|
| `AI-Odoo-Sync` | `odoo-sync` | Daily 7:00 AM | Sync invoices/payments → `/Accounting/Current_Month.md` |
| `AI-CEO-Briefing` | `ceo-briefing` | **Monday 7:00 AM** | Full business intelligence briefing → `/Briefings/` |
| `AI-Daily-Morning` | `daily` | Daily 8:00 AM | Process Needs_Action + Approved + light Odoo check |
| `AI-LinkedIn` | `linkedin` | Mon/Wed/Fri 9:00 AM | Draft LinkedIn post → `/Pending_Approval` |
| `AI-Social-Batch` | `social-batch` | Tue/Thu 10:00 AM | Draft FB + IG + 2× Twitter → `/Pending_Approval` |
| `AI-Health-Check` | `health-check` | Daily 6:00 AM | Verify MCP servers + error counts + watcher status |
| `AI-Weekly-Audit` | `weekly-audit` | Sunday 6:00 PM | Full week review → `/Briefings/` |

**Execution order on Monday:** Odoo-Sync (7:00) → CEO-Briefing (7:00, after sync) → Daily-Morning (8:00) → LinkedIn (9:00)

---

## Manual GUI Steps

Use these if you prefer the Task Scheduler GUI or the PowerShell script fails.

### Step 1 — Open Task Scheduler

`Win + S` → type **Task Scheduler** → Open

### Step 2 — Create a new task

1. Click **Create Task...** (not "Create Basic Task") in the right panel
2. **General tab:**
   - Name: e.g. `AI-Daily-Morning`
   - Check **Run whether user is logged on or not**
   - Check **Run with highest privileges**

3. **Triggers tab → New:**
   - Set the schedule from the table above
   - Ensure **Enabled** is checked

4. **Actions tab → New:**
   - Action: `Start a program`
   - Program/script: `cmd.exe`
   - Add arguments:
     ```
     /c "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault\scripts\scheduler.bat daily"
     ```
   - Start in:
     ```
     D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault
     ```

5. **Settings tab:**
   - Check **Run task as soon as possible after a scheduled start is missed**
   - Set **Stop the task if it runs longer than:** `1 hour`

6. Click **OK** and enter your Windows password when prompted.

Repeat for each task in the table.

---

## Running Tasks Manually

Open a Command Prompt in the vault directory and run any task on demand:

```cmd
cd /d "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault"

scripts\scheduler.bat daily
scripts\scheduler.bat odoo-sync
scripts\scheduler.bat linkedin
scripts\scheduler.bat social-batch
scripts\scheduler.bat weekly-audit
scripts\scheduler.bat ceo-briefing
scripts\scheduler.bat health-check
scripts\scheduler.bat check-approvals
scripts\scheduler.bat email-check
scripts\scheduler.bat status
```

---

## Viewing Logs

Each task run creates a timestamped log:

```
memory\scheduler_logs\
  scheduler_2026-03-02_08-00-00.log   ← main run log
  daily_2026-03-02_08-00-00.log       ← Claude output for that task
  ceo_briefing_2026-03-03_07-00-00.log
  ...
```

View recent logs from Command Prompt:

```cmd
dir /b /o-d "memory\scheduler_logs\*.log" | more
```

Or check the audit trail:

```cmd
python -c "
from utils.audit_logger import AuditLogger
audit = AuditLogger()
for entry in audit.get_recent_logs(20):
    print(entry['ts'][:19], entry['component'], entry['action'], entry['status'])
"
```

---

## Verifying Tasks Are Registered

```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "AI-*" } |
    Select-Object TaskName, State |
    Format-Table -AutoSize
```

Expected output:

```
TaskName          State
--------          -----
AI-CEO-Briefing   Ready
AI-Daily-Morning  Ready
AI-Health-Check   Ready
AI-LinkedIn       Ready
AI-Odoo-Sync      Ready
AI-Social-Batch   Ready
AI-Weekly-Audit   Ready
```

---

## Troubleshooting

### Task runs but Claude does nothing

Check that `claude` is in the system PATH for the user account the task runs under:

```cmd
where claude
```

If not found, add the Claude Code install directory to the **system** PATH (not user PATH), or use the full path to `claude.exe` in the task action.

### "The system cannot find the path specified"

The vault path contains spaces. Make sure the entire path in the task action argument is wrapped in double quotes:

```
/c "D:\Izma folder\...\scheduler.bat daily"
```

### Task shows "Last Run Result: 0x1"

Exit code 1 means an unknown command or missing file. Open the log:

```cmd
type "memory\scheduler_logs\scheduler_*.log" | more
```

### Task runs as SYSTEM and can't reach localhost:8069 (Odoo)

Odoo Docker must be running. The task needs network access. In Task Scheduler → Settings tab, ensure **Run only if the following network connection is available** is unchecked (or set to `Any connection`).

Start Odoo before running accounting tasks:

```cmd
cd /d D:\odoo-local
docker compose up -d
```

### Claude API rate limit during social-batch

The `social-batch` task generates 4 API calls. If you hit rate limits, add a delay between calls by splitting into two separate tasks (Facebook+Instagram, then Twitter×2) on different triggers.

---

## Disabling / Removing Tasks

```powershell
# Disable one task
Disable-ScheduledTask -TaskName "AI-Social-Batch"

# Remove all AI tasks
Get-ScheduledTask | Where-Object { $_.TaskName -like "AI-*" } |
    Unregister-ScheduledTask -Confirm:$false
```
