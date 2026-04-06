# AI Employee — Full Hackathon Demo Guide
### Bronze → Silver → Gold → Platinum — One Presentation

**Business:** NovaMind Tech Solutions (AI consulting for Pakistani SMEs)
**Total time:** ~20 minutes
**Vault root:** `D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault`

**Screen setup before recording:**
- Left half: Obsidian (vault open)
- Right half: Terminal (in vault root, venv activated)

---

## BEFORE YOU HIT RECORD

Run this once to confirm what is live:
```powershell
python scripts/pre_demo_check.py
```

Start Docker if Odoo is down:
```powershell
docker compose -f odoo-cloud/docker-compose.yml up -d
```

Clean up any leftover demo files from last run:
```powershell
# Clear old test files so folders look clean
rm -f Needs_Action/email/EMAIL_test_demo_*.md
rm -f In_Progress/cloud/EMAIL_test_demo_*.md
rm -f Pending_Approval/email/REPLY_test_demo_*.md
```

---

---

# PART 1 — BRONZE TIER
### "The Foundation: Files as a Message Queue"
*Time: ~3 minutes*

---

### 1.1 — Open the Vault (45 sec)

Open Obsidian. Show the sidebar folder structure.

**Say:**
> "This is the AI Employee — a fully autonomous business assistant built inside an Obsidian vault.
> Every piece of work becomes a Markdown file. The folders are the pipeline.
> No database, no message broker — just files moving through folders, synced by Git."

Click through each folder briefly:
- `Inbox/` — raw items land here
- `Needs_Action/` — AI picks up work from here
- `Done/` — completed tasks go here
- `Dashboard.md` — open this, show the tier badge and folder counts

---

### 1.2 — Show the Rules Engine (30 sec)

Open `Company_Handbook.md`. Scroll to the **Priority Keywords** table.

**Say:**
> "The AI knows the company rules. It reads this handbook to classify every incoming item —
> high, medium, or low priority — before deciding what to do with it."

---

### 1.3 — Show a Completed Task (45 sec)

Open `Done/DONE_EMAIL_service_inquiry_20260405_143000.md` in Obsidian.

**Say:**
> "Here is a completed task. An email came in, the AI read it, classified it,
> drafted a reply, got human approval, sent it, and archived the whole thing here.
> This is the complete lifecycle of one piece of work."

---

---

# PART 2 — SILVER TIER
### "HITL: The AI Asks Before It Acts"
*Time: ~5 minutes*

---

### 2.1 — Drop a New Email into Needs_Action (1 min)

In PowerShell terminal:
```powershell
@"
---
type: email
priority: high
from: ahmed.khan@khanindustries.pk
subject: Interested in AI automation — need pricing and case study
received: 2026-04-06T09:00:00
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
> "In production, the Gmail watcher creates files like this automatically every 2 minutes.
> I'm simulating that here to show you the exact file the AI sees."

Switch to Obsidian — the file appears in the sidebar instantly.

---

### 2.2 — Let Claude Process It (1.5 min)

In Claude Code, type:
```
/file-processing
```

**Narrate as it runs:**
- "Reading the file from Needs_Action"
- "Checking Company_Handbook — keyword 'CEO' and 'pricing' → classifies as HIGH priority"
- "Drafting a reply"
- "It's an outbound email — HITL required — creating approval request in Pending_Approval"
- "Moving the original to Done"
- "Updating Dashboard"

---

### 2.3 — Show the Approval Gate (1 min)

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
> This is enforced at the code level, not by trust."

Now approve it — drag the file from `Pending_Approval/email/` to `Approved/` in Obsidian.

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

Open `Plans/` in Obsidian — show the new PLAN file with checkboxes.

**Say:**
> "For complex tasks, Claude creates a tracked plan. Each step has its own approval
> if needed. You can see exactly where any task is at any moment."

---

---

# PART 3 — GOLD TIER
### "Three Live MCP Servers: Accounting, Email, Social Media"
*Time: ~8 minutes*

---

### 3.1 — Show All Three MCP Servers Connected (1 min)

In Claude Code, type:
```
Check all MCP connections: run odoo_status, check_smtp_status, and social_media_status
```

**Narrate results:**
- Odoo: `connected, version 19.0, uid=2, db=ai_employee_db`
- SMTP: `OK — smtp.gmail.com:587`
- Social Media: FB/IG/Twitter keys configured, `SOCIAL_DRY_RUN=true`

**Say:**
> "Three live MCP servers. Email over Gmail SMTP, Odoo 19 ERP running locally on Docker,
> and Social Media for Facebook, Instagram, and Twitter."

---

### 3.2 — Live Odoo Accounting Sync (1.5 min)

In Claude Code, type:
```
Sync Odoo: search customers, get invoices, get overdue invoices,
get account balances, and update Accounting/Current_Month.md
```

**Narrate as each MCP tool fires:**
- `search_customers` → live customer list
- `get_invoices` → posted invoices with PKR amounts
- `get_overdue_invoices` → any past-due flagged
- `get_account_balances` → 30-account Pakistani Chart of Accounts

Open `Accounting/Current_Month.md` in Obsidian.

**Say:**
> "This runs automatically every day at 7 AM. Odoo is on Docker locally.
> The AI reads live financial data but has ZERO write tools — the MCP server
> exposes read-only tools only. Any write to Odoo goes through Pending_Approval first."

---

### 3.3 — Social Media Post with HITL (1.5 min)

In Claude Code, type:
```
/social-media-manager

Generate a Facebook post for NovaMind Tech Solutions.
Topic: How AI automation is helping Pakistani SMEs cut manual work by 60%.
Brand voice: professional, specific to South Asian market. Save for approval.
```

**Narrate:**
- Claude reads `Business_Goals.md` for brand rules
- Post saved to `Pending_Approval/social/`

Show the file in Obsidian.

Now approve and post:
```bash
mv Pending_Approval/social/APPROVAL_social_post_facebook_*.md Approved/
```

Then in Claude Code:
```
Post the approved Facebook content from the Approved folder
```

**Say:**
> "Facebook is live — real Page token, real post. Twitter is in dry-run mode
> to save API credits during demo. One env var flip makes it live.
> The code path is identical either way."

---

### 3.4 — CEO Briefing (1.5 min)

Open `Briefings/CEO_Briefing_2026-03-12.md` in Obsidian.

Walk through each section slowly:
1. **Executive Summary** — 3 sentences, real numbers
2. **Financial Overview** — revenue, overdue invoices, account balances from Odoo
3. **Task Summary** — items completed, pending, stuck this week
4. **Social Media Performance** — posts per platform
5. **System Health** — all components, last run, error count
6. **Top 3 Recommendations** — priority-ordered actions

**Say:**
> "Every Monday at 7 AM this generates automatically. The CEO opens their laptop
> and this is waiting — no manual reports, no chasing people for numbers.
> It reads Odoo, reads the vault, reads the audit log, and synthesizes it in one shot."

---

### 3.5 — Error Recovery System (1 min)

```bash
python scripts/demo_show_errors.py
```

**Say:**
> "Five severity levels. TRANSIENT errors retry 3 times with 30, 60, 120 second backoff.
> AUTH errors create an URGENT action file for human intervention.
> CRITICAL errors halt the component. The system degrades gracefully —
> if Odoo goes down, Gmail and the file watcher keep running."

---

### 3.6 — The Audit Trail (45 sec)

```bash
python scripts/demo_show_audit.py
```

Point out:
- `actor: claude` vs `actor: human` — every action attributed
- `approval_required: true` entries
- 3000+ entries — everything logged since day one

**Say:**
> "Every action — AI and human — timestamped, component-tagged, with approval status.
> Full compliance audit trail. Right now there are over 3,000 entries in this log."

---

### 3.7 — Ralph Wiggum Loop (45 sec)

```bash
ls .claude/hooks/
```

Show `ralph_stop_check.py` exists. Show `.claude/settings.json`.

Run a quick test:
```
/ralph-loop "Check Needs_Action/email/ for unprocessed files. If empty output <promise>VAULT_CLEAN</promise>" --max-iterations 3 --completion-promise "VAULT_CLEAN"
```

**Say:**
> "This is the stop-hook pattern for autonomous loops. Claude works, tries to exit,
> the hook intercepts — if the completion promise isn't in the output, it re-injects the task.
> Claude keeps running until the job is actually done. We named it Ralph Wiggum —
> persistent despite setbacks."

---

### 3.8 — Scheduler (30 sec)

```bash
scripts\scheduler.bat help
```

Show the 9 commands: `daily`, `odoo-sync`, `linkedin`, `social-batch`, `ceo-briefing`, `weekly-audit`, `health-check`.

**Say:**
> "9 scheduled tasks, all running on Windows Task Scheduler.
> The system operates fully autonomously — 7 AM Odoo sync, 9 AM LinkedIn posts,
> Monday CEO briefing, Sunday weekly audit."

---

---

# PART 4 — PLATINUM TIER
### "Two Agents, One Vault, Zero Coordination Calls"
*Time: ~5 minutes*

---

### Opening line (say this before starting):
> "Platinum tier adds a second agent. A Cloud Agent runs 24/7 on AWS EC2.
> A Local Agent runs here on my Windows PC.
> They never call each other, never share a database —
> they communicate exclusively through this Git-synced vault."

---

### 4.1 — Show the Architecture (30 sec)

Open `Dashboard.md` in Obsidian. Scroll to the **Cloud Agent Status** section.

Then show in terminal:
```bash
ls In_Progress/cloud/
ls In_Progress/local/
ls Signals/
cat Signals/cloud_heartbeat.md
```

**Say:**
> "The Cloud Agent writes a heartbeat every 5 minutes. If Local sees the heartbeat is
> more than 60 minutes old, it creates an URGENT signal. That is the entire
> inter-agent communication protocol — file moves."

---

### 4.2 — Run the Full Platinum Demo Loop (3 min)

**Step A — Cloud side (simulate on EC2 or locally):**
```bash
python tests/platinum_demo.py --mode cloud --demo-id demo_live_$(date +%H%M%S)
```

**Narrate each printed step:**
- "Email arrives from client"
- "Cloud Gmail watcher detects it"
- "Cloud creates EMAIL_*.md in Needs_Action/email/"
- "Claim-by-move — Cloud moves it to In_Progress/cloud/ — it owns this item now"
- "Cloud drafts professional reply with Claude"
- "Draft saved to Pending_Approval/email/ — waiting for human"
- "Cloud git pushes — draft is now in GitHub"

**Step B — Local syncs:**
```bash
scripts\vault_sync.bat
```

Show git pull output — "Fast-forward, files changed."

**Step C — Human reviews in Obsidian:**

Navigate to `Pending_Approval/email/` — open the draft. Read it briefly.

**Say:**
> "Cloud drafted this while my PC was offline. Now I review it in Obsidian."

Drag the file to `Approved/`.

**Step D — Local executes:**
```bash
python local/local_agent.py --once
```

**Narrate output:**
- "Vault sync — pulling latest"
- "Cloud heartbeat OK"
- "Found 1 approved action"
- "Routing: email_reply → Gmail MCP send_email"
- "Email sent — logged — archived"

---

### 4.3 — Verify Everything Completed (45 sec)

```bash
python tests/platinum_demo.py --mode verify --demo-id demo_live_XXXXXX
```

Expected — all green:
```
  [OK]  /Done file present
  [OK]  Audit log: email_sent found
  [OK]  Pending_Approval/email/ — empty
  [OK]  In_Progress/cloud/ — empty

PLATINUM DEMO PASSED
```

Show in Obsidian:
- `Done/` — file is there
- `Pending_Approval/email/` — empty
- `In_Progress/cloud/` — empty

---

### Closing line:
> "Email arrived while Local was offline.
> Cloud drafted it autonomously, synced it through Git.
> I reviewed in Obsidian and approved with one drag.
> Local sent via Gmail MCP, logged every step, archived the task.
> Two agents, zero direct communication, zero missed messages.
> That is the complete Platinum AI Employee."

---

---

# QUICK REFERENCE — COMMANDS IN ORDER

```
# PRE-DEMO
python scripts/pre_demo_check.py
docker compose -f odoo-cloud/docker-compose.yml up -d

# BRONZE / SILVER
(Obsidian) Open Dashboard.md, Company_Handbook.md, Done/ folder
cat > "Needs_Action/email/EMAIL_client_inquiry_TIMESTAMP.md"   ← create test email
/file-processing                                               ← Claude processes it
(Obsidian) Show Pending_Approval, drag to Approved
/task-planner                                                  ← show multi-step plan

# GOLD
Check all MCP connections: run odoo_status, check_smtp_status, and social_media_status
Sync Odoo: search customers, get invoices, get account balances, update Current_Month.md
/social-media-manager  → approve → post
(Obsidian) Open Briefings/CEO_Briefing_2026-03-12.md
python scripts/demo_show_errors.py
python scripts/demo_show_audit.py
/ralph-loop "Check Needs_Action/email/. If empty output <promise>VAULT_CLEAN</promise>"
scripts\scheduler.bat help

# PLATINUM
cat Signals/cloud_heartbeat.md
python tests/platinum_demo.py --mode cloud --demo-id demo_live_XXX
scripts\vault_sync.bat
(Obsidian) Open draft → drag to Approved
python local/local_agent.py --once
python tests/platinum_demo.py --mode verify --demo-id demo_live_XXX
python scripts/demo_show_audit.py
```

---

# IF SOMETHING BREAKS

| Problem | What to do |
|---------|-----------|
| Odoo FAIL | `docker compose -f odoo-cloud/docker-compose.yml up -d` then wait 30 sec |
| Facebook MISSING | Show Twitter dry-run output as proof of the social flow — same code path |
| Gmail MCP fails | Add `--dry-run` to platinum_demo.py — all files created, audit logged |
| EC2 not available | Run `--mode cloud` locally — demo shows same output |
| platinum_demo.py errors | `python tests/platinum_demo.py --dry-run` — identical 18 steps, no external calls |
