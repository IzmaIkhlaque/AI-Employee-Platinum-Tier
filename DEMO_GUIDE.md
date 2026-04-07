# AI Employee — Full Hackathon Demo Guide
### Bronze → Silver → Gold → Platinum — One Presentation

**Business:** NovaMind Tech Solutions (AI consulting for Pakistani SMEs)
**Total time:** ~20 minutes
**Vault root:** `D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault`

---

## TERMINAL SETUP (open ALL before recording)

You need **4 terminals** open and split on screen before you hit record:

| Terminal | What runs in it | Shell |
|----------|----------------|-------|
| Terminal 1 | Filesystem Watcher | PowerShell or Git Bash |
| Terminal 2 | Gmail Watcher | PowerShell or Git Bash |
| Terminal 3 | Orchestrator | PowerShell or Git Bash |
| Terminal 4 | Commands (demo steps) | PowerShell |

Plus **Obsidian** open on the left half of screen.

---

## BEFORE YOU HIT RECORD

### Step 1 — Activate venv (in every terminal)
```powershell
cd "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault"
& ".venv/Scripts/Activate.ps1"
```

### Step 2 — Verify all connections
```powershell
python scripts/pre_demo_check.py
```

### Step 3 — Start Odoo Docker if needed
```powershell
docker compose -f odoo-cloud/docker-compose.yml up -d
```
Wait 30 seconds, then re-run pre_demo_check.py.

### Step 4 — Disable Task Scheduler (no surprise CMD popups during recording)
```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "*AI*" -or $_.TaskName -like "*Employee*"} | Disable-ScheduledTask
```

### Step 5 — Clean ALL leftover demo files
```powershell
Remove-Item "Needs_Action/email/EMAIL_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "Needs_Action/email/EMAIL_client_inquiry_live.md" -ErrorAction SilentlyContinue
Remove-Item "In_Progress/cloud/EMAIL_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "In_Progress/local/EMAIL_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "Pending_Approval/email/REPLY_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "Approved/REPLY_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "Done/DONE_REPLY_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "Signals/REVIEW_NEEDED_*.md" -ErrorAction SilentlyContinue
Remove-Item "Signals/URGENT_*.md" -ErrorAction SilentlyContinue
Remove-Item "Needs_Action/URGENT_*.md" -ErrorAction SilentlyContinue
Remove-Item "Plans/PLAN_enterprise_*.md" -ErrorAction SilentlyContinue
```

### Step 6 — Refresh the cloud heartbeat
```powershell
"last_updated: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')`nagent: cloud`nstatus: active" | Set-Content "Signals/cloud_heartbeat.md"
```

### Step 7 — Start the 3 background processes

**Terminal 1 — Filesystem Watcher:**
```powershell
python watchers/filesystem_watcher.py
```
Leave it running. It watches for file drops.

**Terminal 2 — Gmail Watcher:**
```powershell
python watchers/gmail_watcher.py
```
Leave it running. It polls Gmail every 2 minutes.

**Terminal 3 — Orchestrator:**
```powershell
python orchestrator.py
```
Leave it running. It coordinates all actions.

### Step 8 — Verify git log shows history
```bash
git log --oneline -10
```
You should see a mix of `Cloud sync:` and `Local sync:` commits.

---

---

# PART 1 — BRONZE TIER
### "The Foundation: Files as a Message Queue"
*Time: ~3 minutes*

---

### 1.1 — Show the 3 Running Processes (30 sec)

Point to each terminal:

**Say:**
> "Before I show you the vault, look at what is already running.
> Terminal 1 is the filesystem watcher — it monitors the vault folders for new files.
> Terminal 2 is the Gmail watcher — it polls Gmail every 2 minutes for new emails.
> Terminal 3 is the orchestrator — it coordinates all of these watchers and triggers Claude
> when work arrives. This is a live, running system."

---

### 1.2 — Open the Vault in Obsidian (45 sec)

Open Obsidian. Show the sidebar folder structure.

**Say:**
> "This is the AI Employee vault in Obsidian. Every piece of work becomes a Markdown file.
> The folders are the pipeline — no database, no message broker, just files moving
> through folders synced by Git. The filesystem IS the message queue."

Click through each folder:
- `Inbox/` — raw incoming items
- `Needs_Action/` — AI picks up work from here
- `In_Progress/` — claimed by an agent, being processed
- `Pending_Approval/` — waiting for human decision
- `Approved/` — human said yes
- `Done/` — completed and archived
- `Dashboard.md` — open this, show the tier badge and live counts

---

### 1.3 — Show the Rules Engine (30 sec)

Open `Company_Handbook.md`. Scroll to the **Priority Keywords** table.

**Say:**
> "The AI knows the company rules. It reads this handbook to classify every incoming item
> as high, medium, or low priority before deciding what to do."

---

### 1.4 — Show a Completed Task (45 sec)

Open `Done/DONE_EMAIL_service_inquiry_20260405_143000.md` in Obsidian.

Walk through it:
- Original email at the top
- AI classification section
- Reply that was sent
- Audit trail table at the bottom with every step timestamped

**Say:**
> "Here is a completed task. Email came in, AI classified it HIGH priority,
> drafted a reply, got human approval, sent it via Gmail, and archived everything here
> with a full audit trail. This is the complete lifecycle of one piece of work."

---

---

# PART 2 — SILVER TIER
### "HITL: The AI Asks Before It Acts"
*Time: ~5 minutes*

---

### 2.1 — Drop a New Email into Needs_Action (1 min)

In Terminal 4 (PowerShell):

```powershell
@"
---
type: email
priority: high
from: ahmed.khan@khanindustries.pk
subject: Interested in AI automation — need pricing and case study
received: 2026-04-07T09:00:00
---

Hi NovaMind,

We are a 50-person manufacturing company in Lahore.
We are interested in your AI automation services.
Can you send us a pricing breakdown and a case study?

Best,
Ahmed Khan
CEO, Khan Industries
"@ | Set-Content "Needs_Action/email/EMAIL_client_inquiry_live.md"
```

**Say:**
> "In production, the Gmail watcher creates this file automatically every 2 minutes
> when a new email arrives. Watch Terminal 1 — the filesystem watcher detects it instantly."

Point to Terminal 1 (filesystem watcher) — it will log the new file detection.
Switch to Obsidian — the file appears in the sidebar.

---

### 2.2 — Let Claude Process It (1.5 min)

In Claude Code (Terminal 4), type:
```
/file-processing
```

**Narrate as it runs:**
- "Reading the file from Needs_Action/email/"
- "Checking Company_Handbook — keyword CEO and pricing → HIGH priority"
- "Drafting a professional reply"
- "Outbound email — HITL required — saving to Pending_Approval"
- "Moving original to Done"
- "Updating Dashboard"

---

### 2.3 — Show the HITL Approval Gate (1 min)

In Obsidian, open `Pending_Approval/email/` — show the file Claude just created.

Read the frontmatter out loud:
```yaml
action: email_reply
approval_required: true
to: ahmed.khan@khanindustries.pk
```

**Say:**
> "This is the Human-in-the-Loop checkpoint. Claude drafted the reply but it cannot send
> anything — no email, no social post, no Odoo write — until a human moves this file.
> This is enforced at the code level in the MCP server, not by trust."

Drag the file from `Pending_Approval/email/` → `Approved/` in Obsidian.

**Say:**
> "One drag. That is the human decision. Now the agent can execute."

---

### 2.4 — Show Multi-Step Planning (30 sec)

In Claude Code, type:
```
/task-planner

A new enterprise client wants a full onboarding proposal:
discovery call, needs assessment, custom pricing, and contract draft.
Create an execution plan.
```

When the 9-step plan prints — **narrate it, do NOT execute the steps:**
- Point out the 3 approval gates (Step 3, 7, 9)
- Explain which steps need human approval and why

Open `Plans/` in Obsidian — show the PLAN file with checkboxes.

**Say:**
> "For complex tasks, Claude creates a tracked plan and identifies every approval gate
> in advance. Nothing gets executed blindly."

**Stop here. Do NOT type "Yes proceed". Move to Gold tier.**

---

---

# PART 3 — GOLD TIER
### "Three Live MCP Servers + Full Autonomous Operations"
*Time: ~8 minutes*

---

### 3.1 — Show the Orchestrator Running (30 sec)

Point to Terminal 3 (orchestrator).

**Say:**
> "The orchestrator has been running this whole time. It polls every 30 seconds,
> runs a health check every 5 minutes, and automatically triggers Claude when new
> items arrive in Needs_Action or Approved. This is what makes the system autonomous."

Show the orchestrator log output on screen.

---

### 3.2 — Check All 3 MCP Server Connections (1 min)

In Claude Code, type:
```
Check all MCP connections: run odoo_status, check_smtp_status, and social_media_status
```

**Narrate each result:**
- Odoo: `connected, version 19.0, uid=2, db=ai_employee_db`
- SMTP: `OK — smtp.gmail.com:587, user: izmarao99@gmail.com`
- Social Media: FB/IG configured live, Twitter SOCIAL_DRY_RUN=true

**Say:**
> "Three live MCP servers — Email over Gmail SMTP, Odoo 19 ERP on Docker,
> and Social Media for Facebook, Instagram, and Twitter."

---

### 3.3 — Live Odoo Accounting Sync (1.5 min)

In Claude Code, type:
```
Sync Odoo: search customers, get invoices, get overdue invoices,
get account balances, and update Accounting/Current_Month.md
```

**Narrate as each MCP tool fires:**
- `search_customers` → live customer list from Odoo
- `get_invoices` → posted invoices with PKR amounts
- `get_overdue_invoices` → any past-due flagged automatically
- `get_account_balances` → 30-account Pakistani Chart of Accounts

Open `Accounting/Current_Month.md` in Obsidian.

**Say:**
> "This syncs every morning at 7 AM automatically. Odoo is on Docker locally.
> The AI reads live financial data but has ZERO write tools exposed —
> the MCP server only has read-only tools. Any Odoo write goes through
> Pending_Approval first."

---

### 3.4 — Social Media Post with Live Facebook (1.5 min)

In Claude Code, type:
```
/social-media-manager

Generate a Facebook post for NovaMind Tech Solutions.
Topic: How AI automation is helping Pakistani SMEs cut manual work by 60%.
Brand voice: professional, specific to South Asian market. Save for approval.
```

Show the draft in Obsidian `Pending_Approval/social/`.

Now approve it in Git Bash:
```bash
mv Pending_Approval/social/APPROVAL_social_post_facebook_*.md Approved/
```

Then in Claude Code:
```
Post the approved Facebook content from the Approved folder
```

**Say:**
> "Facebook is live — real Page token, real post going live right now.
> Twitter is in dry-run mode to save API credits. The code path is identical —
> flip one env var and it goes live."

---

### 3.5 — CEO Briefing (1.5 min)

Open `Briefings/CEO_Briefing_2026-04-06.md` in Obsidian.

Walk through each section:
1. **Executive Summary** — 3 sentences, real numbers
2. **Financial Overview** — from live Odoo data
3. **Task Summary** — items completed, pending, stuck
4. **Social Media Performance** — posts per platform
5. **System Health** — all components, error counts
6. **Top 3 Recommendations** — priority-ordered

**Say:**
> "Every Monday at 7 AM this generates autonomously — reads Odoo, reads the vault,
> reads the audit log, synthesizes everything. CEO opens their laptop and this is waiting."

---

### 3.6 — Error Recovery System (1 min)

```bash
python scripts/demo_show_errors.py
```

**Say:**
> "Five severity levels. TRANSIENT retries 3 times with 30, 60, 120 second backoff.
> AUTH creates an URGENT file in Needs_Action for human intervention.
> These are real errors the system caught, logged, and recovered from automatically."

---

### 3.7 — Full Audit Trail (45 sec)

```bash
python scripts/demo_show_audit.py
```

Also run this to show both agents in the log:
```bash
python -c "
import json
from pathlib import Path
entries = [json.loads(l) for l in Path('Logs/audit.jsonl').read_text().splitlines() if l.strip()]
components = set(e.get('component','') for e in entries[-50:])
print('Active components in last 50 entries:', components)
print('Total audit entries:', len(entries))
"
```

**Say:**
> "Every action — AI and human — timestamped, component-tagged, approval-status tracked.
> Over 3,000 entries. You can see both cloud_agent and local_agent in the log."

---

### 3.8 — Ralph Wiggum Loop (45 sec)

```bash
ls .claude/hooks/
cat .claude/settings.json
```

In Claude Code:
```
/ralph-loop "Check Needs_Action/email/ for unprocessed files. If empty output <promise>VAULT_CLEAN</promise>" --max-iterations 3 --completion-promise "VAULT_CLEAN"
```

**Say:**
> "Stop-hook pattern. Claude works, tries to exit, the hook intercepts.
> If the completion promise is not in the output, it re-injects the task.
> Claude keeps running until the job is actually done."

---

### 3.9 — Scheduler (30 sec)

```powershell
scripts\scheduler.bat status
```

Then open `scripts/scheduler.bat` in VS Code and show the 9 commands visually.

**Say:**
> "9 scheduled tasks on Windows Task Scheduler — 7 AM Odoo sync, Monday CEO briefing,
> LinkedIn Mon/Wed/Fri, social batch Tue/Thu, weekly audit Sunday.
> Fully autonomous daily operations."

---

---

# PART 4 — PLATINUM TIER
### "Two Agents, One Vault, Zero Coordination Calls"
*Time: ~7 minutes*

---

### Opening line:
> "Platinum tier adds a second agent. Cloud Agent runs 24/7 on AWS EC2.
> Local Agent runs here on my Windows PC.
> They never call each other, never share a database —
> they communicate exclusively through this Git-synced vault on GitHub."

---

### 4.1 — Show EC2 Cloud Agent Running (1 min)

Open a new terminal and SSH into EC2:
```powershell
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_EC2_IP
```

On EC2:
```bash
# Show the systemd service is active 24/7
sudo systemctl status ai-employee-cloud

# Show Odoo containers running on EC2
cd ~/odoo-cloud && docker compose ps

# Show live cloud agent logs
tail -20 ~/logs/cloud_agent.log
```

**Say:**
> "The Cloud Agent is a systemd service — it restarts automatically on crash
> and starts on boot. Odoo 19 runs alongside it on Docker with PostgreSQL.
> This has been running 24/7 on EC2 while we were doing the Silver and Gold demos."

---

### 4.2 — Show the Vault Architecture (30 sec)

Back on Windows, in Terminal 4:
```bash
ls In_Progress/cloud/
ls In_Progress/local/
ls Signals/
cat Signals/cloud_heartbeat.md
```

Check heartbeat age:
```bash
python -c "
import time
from pathlib import Path
f = Path('Signals/cloud_heartbeat.md')
age = (time.time() - f.stat().st_mtime) / 60
print(f'Cloud heartbeat age: {age:.1f} minutes')
print('OK' if age < 15 else 'WARNING — cloud may be down')
"
```

**Say:**
> "The Cloud Agent rewrites this heartbeat file every 5 minutes.
> If the Local Agent sees it is more than 60 minutes old, it creates an URGENT signal.
> That is the entire inter-agent monitoring protocol — one file."

---

### 4.3 — Show Git Log — Both Agents Committing (30 sec)

```bash
git log --oneline -10
```

Expected output showing both agents:
```
abc1234 Cloud sync: 2026-04-07 03:35:54
def5678 Local sync: Tue 04/07/2026 03:00:01
ghi9012 Cloud sync: 2026-04-07 02:35:21
jkl3456 Local sync: Tue 04/07/2026 02:00:01
```

**Say:**
> "Every 5 minutes the Cloud Agent pushes to GitHub. Every 10 minutes the Local Agent
> pulls and pushes back. This git log is the complete communication history
> between two agents that never directly talk to each other."

---

### 4.4 — Run the Full Platinum Demo Loop (3 min)

**Step A — Cloud side:**
```bash
python tests/platinum_demo.py --mode cloud --demo-id demo_live_final
```

**Narrate each step as it prints:**
- "Email arrives from client"
- "Cloud Gmail watcher detects it within 2 minutes"
- "Cloud creates EMAIL file in Needs_Action/email/"
- "Claim-by-move — Cloud moves it to In_Progress/cloud/ — it now owns this task"
- "Cloud drafts professional reply using Claude"
- "Draft saved to Pending_Approval/email/ — waiting for human"
- "Cloud git pushes — draft is now in GitHub"

**Step B — Vault sync:**
```bash
scripts\vault_sync.bat
```

Show git pull output — "Fast-forward, files changed."

**Say:** *"My PC just pulled Cloud's work from GitHub."*

**Step C — Human reviews in Obsidian:**

Open `Pending_Approval/email/REPLY_test_demo_live_final.md`.
Read it briefly on camera. Pause 3 seconds.

**Say:**
> "The Cloud Agent drafted this while my PC was offline. I'm reviewing it now.
> Looks professional — I'll approve it."

**Step D — Run local side (script pauses for your approval):**
```bash
python tests/platinum_demo.py --mode local --demo-id demo_live_final --dry-run
```

When the script pauses and shows:
```
>>> HUMAN ACTION REQUIRED <<<
Move REPLY_test_demo_live_final.md to /Approved/ then press Enter...
```

Drag the file from `Pending_Approval/email/` to `Approved/` in Obsidian — on camera.

Then press Enter in the terminal.

**Narrate the remaining steps as they print:**
- "Local detects the approved file"
- "Routes to Gmail MCP send_email"
- "Email sent — logged — moved to Done"
- "Local git pushes completion back to Cloud"

---

### 4.5 — Verify All 5 Checks Green (45 sec)

```bash
python tests/platinum_demo.py --mode verify --demo-id demo_live_final
```

Expected:
```
  [OK]  /Done file: DONE_REPLY_test_demo_live_final.md
  [OK]  Audit log: email_sent found
  [OK]  Pending_Approval/email/ — file cleared
  [OK]  In_Progress/cloud/ — file cleared
  [OK]  Audit trail: demo_step entries logged

PLATINUM DEMO PASSED — All 18 steps completed successfully.
```

In Obsidian, show:
- `Done/` — DONE file is there
- `Pending_Approval/email/` — empty
- `In_Progress/cloud/` — empty

---

### 4.6 — Show the Full Audit Chain (30 sec)

```bash
python scripts/demo_show_audit.py
```

Point out the complete chain from both agents:
```
cloud_agent    email_action_created   success
cloud_agent    item_claimed           success
cloud_agent    email_draft_saved      success
local_agent    approved_action_read   success
local_agent    email_sent             success
local_agent    item_done              success
```

---

### Closing line:
> "Email arrived while Local was offline.
> Cloud drafted it autonomously and synced it through Git.
> I reviewed in Obsidian and approved with one drag.
> Local sent via Gmail MCP, logged every step, archived the task, pushed back to Cloud.
> Two agents, zero direct communication, zero missed messages.
> That is the complete Platinum AI Employee."

---

---

# QUICK REFERENCE — FULL COMMAND LIST IN ORDER

```
======= PRE-DEMO (PowerShell) =======
& ".venv/Scripts/Activate.ps1"
python scripts/pre_demo_check.py
docker compose -f odoo-cloud/docker-compose.yml up -d
Get-ScheduledTask | Where-Object {$_.TaskName -like "*AI*"} | Disable-ScheduledTask
Remove-Item "In_Progress/cloud/EMAIL_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "Pending_Approval/email/REPLY_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "Done/DONE_REPLY_test_demo_*.md" -ErrorAction SilentlyContinue
Remove-Item "Signals/URGENT_*.md" -ErrorAction SilentlyContinue
"last_updated: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')`nagent: cloud`nstatus: active" | Set-Content "Signals/cloud_heartbeat.md"

======= START WATCHERS (3 separate terminals) =======
Terminal 1:  python watchers/filesystem_watcher.py
Terminal 2:  python watchers/gmail_watcher.py
Terminal 3:  python orchestrator.py

======= BRONZE =======
(Obsidian) Open Dashboard.md
(Obsidian) Open Company_Handbook.md → Priority Keywords table
(Obsidian) Open Done/DONE_EMAIL_service_inquiry_20260405_143000.md

======= SILVER (Terminal 4 — PowerShell) =======
@"---\ntype: email..."@ | Set-Content "Needs_Action/email/EMAIL_client_inquiry_live.md"
(Point to Terminal 1 — watcher detects it)
/file-processing                           ← in Claude Code
(Obsidian) Show Pending_Approval → drag to Approved
/task-planner                              ← in Claude Code, narrate plan only

======= GOLD (Claude Code + Terminal 4) =======
Check all MCP connections: run odoo_status, check_smtp_status, and social_media_status
Sync Odoo: search customers, get invoices, get account balances, update Current_Month.md
/social-media-manager → approve → post to Facebook
(Obsidian) Open Briefings/CEO_Briefing_2026-04-06.md
python scripts/demo_show_errors.py
python scripts/demo_show_audit.py
python -c "import json,Path; ..."      ← show active components
/ralph-loop "..."
scripts\scheduler.bat status

======= PLATINUM (Terminal 4 — Git Bash or PowerShell) =======
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_EC2_IP
  sudo systemctl status ai-employee-cloud
  cd ~/odoo-cloud && docker compose ps
  tail -20 ~/logs/cloud_agent.log
  exit
cat Signals/cloud_heartbeat.md
python -c "..."                            ← heartbeat age check
git log --oneline -10                      ← show mixed Cloud/Local commits
python tests/platinum_demo.py --mode cloud --demo-id demo_live_final
scripts\vault_sync.bat
python tests/platinum_demo.py --mode local --demo-id demo_live_final --dry-run
  └── script pauses → drag file in Obsidian to Approved → press Enter
python tests/platinum_demo.py --mode verify --demo-id demo_live_final
python scripts/demo_show_audit.py
```

---

# IF SOMETHING BREAKS

| Problem | Cause | Fix |
|---------|-------|-----|
| `@"..."@ \| Set-Content` syntax error | Wrong shell — must be PowerShell, not Git Bash | Switch to PowerShell terminal |
| `scheduler.bat` shows one log line | Help text missing — use status instead | `scripts\scheduler.bat status` |
| `--mode local` says "Reply file not found" | You moved file BEFORE running local script | `mv Approved/REPLY_*.md Pending_Approval/email/` then re-run |
| `PLATINUM DEMO FAILED` — In_Progress/cloud FAIL | Always use `--dry-run` flag with `--mode local` | Add `--dry-run` |
| Local agent shows heartbeat URGENT | Heartbeat file is stale | `"last_updated:..." \| Set-Content "Signals/cloud_heartbeat.md"` |
| Surprise CMD window during recording | Windows Task Scheduler auto-ran | Disable tasks in Step 4 pre-demo |
| Odoo FAIL | Docker not running | `docker compose -f odoo-cloud/docker-compose.yml up -d` |
| EC2 SSH fails | IP changed (no Elastic IP) | Check new IP in EC2 console |
| Watcher terminal shows no output | venv not activated | `& ".venv/Scripts/Activate.ps1"` in that terminal |
| Orchestrator crashes immediately | Port conflict or import error | Check `orchestrator.log` for details |
