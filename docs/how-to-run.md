# How to Run the AI Employee

Complete start/stop/verify instructions for every operating mode.

---

## Running Locally Only (Development / Bronze–Gold)

All components run on the Windows PC. No EC2 required.

**Open three terminals in the vault directory:**

```cmd
cd "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault"
```

**Terminal 1 — Filesystem watcher:**
```cmd
python watchers/filesystem_watcher.py
```

**Terminal 2 — Gmail watcher:**
```cmd
python watchers/gmail_watcher.py
```

**Terminal 3 — Orchestrator:**
```cmd
python orchestrator.py
```

**Terminal 4 (optional) — Claude Code interactive:**
```cmd
claude
```

**To stop:** `Ctrl+C` in each terminal.

---

## Running Cloud Agent Only (Test EC2)

Use this to verify the EC2 setup before enabling two-agent mode.

**SSH into EC2:**
```powershell
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_EC2_IP
```

**Start the Cloud Agent (systemd):**
```bash
sudo systemctl start ai-employee-cloud
sudo systemctl status ai-employee-cloud
```

**Watch live logs:**
```bash
tail -f ~/logs/cloud_agent.log
# or via journald:
journalctl -u ai-employee-cloud -f
```

**Test a single cycle:**
```bash
cd ~/AI_Employee_Vault
python3.13 cloud/cloud_agent.py --dry-run
```

**Stop:**
```bash
sudo systemctl stop ai-employee-cloud
```

---

## Running BOTH — Platinum Mode (Production)

### Step 1 — On AWS EC2 (Cloud Agent)

SSH in:
```powershell
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_EC2_IP
```

Start Odoo (if not already running):
```bash
cd ~/odoo-cloud
docker compose up -d
# Verify containers
docker compose ps
```

Verify Cloud Agent is running:
```bash
sudo systemctl status ai-employee-cloud
# If not running:
sudo systemctl start ai-employee-cloud
```

Verify cron is set up:
```bash
crontab -l | grep AI_Employee
```

Verify Odoo is accessible:
```bash
curl -s http://localhost:8069/web/database/selector | head -3
```

Check last vault sync:
```bash
cd ~/AI_Employee_Vault
git log --oneline -5
```

You can now disconnect from SSH — the Cloud Agent runs autonomously.

---

### Step 2 — On Local PC (Windows)

Open a terminal in the vault:
```cmd
cd "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault"
```

Pull latest from Cloud:
```cmd
scripts\vault_sync.bat
```

Start the Local Agent (continuous mode):
```cmd
python local/local_agent.py
```

Or run a single cycle on demand:
```cmd
python local/local_agent.py --once
```

Open Obsidian and navigate to `/Pending_Approval` to review Cloud drafts:
```
File → Open Vault → AI_Employee_Vault
```

**Optional — also start the Gold-tier orchestrator** (handles `/Social_Media` records and legacy items):
```cmd
python orchestrator.py
```

---

### Step 3 — Set AGENT_ROLE in .env

For the orchestrator to automatically delegate to the right agent:

**Windows PC `.env`:**
```env
AGENT_ROLE=local
```

**EC2 `.env`:**
```env
AGENT_ROLE=cloud
```

With this set, `python orchestrator.py` on each machine will automatically
start the correct agent without needing to call `local_agent.py` or
`cloud_agent.py` directly.

---

## Stopping Everything

### Cloud (SSH into EC2):
```bash
sudo systemctl stop ai-employee-cloud
cd ~/odoo-cloud && docker compose down
```

### Local (Windows):
```
Ctrl+C on local_agent.py
Ctrl+C on orchestrator.py (if running)
Close Claude Code
```

---

## Scheduled Task Mode (Platinum — Unattended)

For fully unattended operation, Task Scheduler handles the Local Agent.
No terminal needs to stay open.

**Setup (one-time, run as Administrator):**
```powershell
# Creates AI-LocalAgent and AI-VaultSync tasks (every 10 min)
# See docs/windows-scheduler-platinum.md for the full PowerShell block
```

**Verify tasks are active:**
```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "AI-*" } |
    Select-Object TaskName, State |
    Format-Table -AutoSize
```

**Run a task immediately:**
```powershell
Start-ScheduledTask -TaskName "AI-LocalAgent"
Start-ScheduledTask -TaskName "AI-VaultSync"
```

---

## Verifying Everything Works

Run through this checklist after starting both agents:

**1. Dashboard.md — all sections populated**
```cmd
type Dashboard.md | findstr "Cloud Status\|Last Sync\|HEALTHY"
```
Expected: `Cloud Status | Running` and `HEALTHY`

**2. Audit log — entries from both agents**
```cmd
python -c "
import json
from pathlib import Path
entries = [json.loads(l) for l in Path('Logs/audit.jsonl').read_text().splitlines() if l.strip()]
components = set(e.get('component','') for e in entries[-50:])
print('Active components:', components)
"
```
Expected: `{'cloud_agent', 'local_agent'}` (or `orchestrator` for Gold mode)

**3. Cloud heartbeat — timestamp within 15 minutes**
```cmd
python -c "
import time, os
from pathlib import Path
f = Path('Signals/cloud_heartbeat.md')
if f.exists():
    age = (time.time() - f.stat().st_mtime) / 60
    print(f'Heartbeat age: {age:.1f} minutes')
    print('OK' if age < 15 else 'WARNING: Cloud agent may be down')
else:
    print('No heartbeat file — Cloud not yet deployed')
"
```

**4. systemd service — active on EC2**
```bash
# Run on EC2:
sudo systemctl is-active ai-employee-cloud
# Expected: active
```

**5. Odoo accessible**
```bash
# Run on EC2:
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069
# Expected: 200 or 303
```

**6. Git log — commits from both agents**
```cmd
git log --oneline -10
```
Expected: mix of `Cloud sync:` and `Local sync:` commits

**7. Run the Platinum demo verification**
```cmd
python tests/platinum_demo.py --mode verify --demo-id YOUR_LAST_DEMO_ID
```
Expected: `PLATINUM DEMO PASSED`

---

## Common Start Sequences

### Fresh start (first time ever):
```
1. EC2: bash cloud/setup_ec2_services.sh
2. EC2: cd ~/odoo-cloud && docker compose up -d
3. EC2: sudo systemctl start ai-employee-cloud
4. Local: scripts\vault_sync.bat
5. Local: python local/local_agent.py --once
6. Local: Open Obsidian, check Dashboard.md
```

### Daily start (normal morning):
```
1. Local: scripts\vault_sync.bat   (get overnight Cloud work)
2. Local: Open Obsidian → /Pending_Approval  (review drafts)
3. Local: Approve/reject items
4. Task Scheduler handles the rest automatically
```

### After EC2 stop/start (IP may have changed if no Elastic IP):
```
1. EC2 console: note new public IP
2. Local: update SSH command with new IP
3. EC2: sudo systemctl start ai-employee-cloud
4. EC2: update git remote if token embedded in URL
```

---

## Dry-Run Mode (Safe Testing)

Every component supports `--dry-run`. Use this to test without any real sends:

```cmd
python orchestrator.py --dry-run
python local/local_agent.py --dry-run --once
python tests/platinum_demo.py --dry-run
```

```bash
# On EC2:
python3.13 cloud/cloud_agent.py --dry-run
```

In dry-run mode:
- Files are created (so you can inspect them)
- Git push/pull are skipped
- No emails are sent
- No social media posts are published
- All actions are logged to `/Logs/audit.jsonl` with `dry_run: true`
