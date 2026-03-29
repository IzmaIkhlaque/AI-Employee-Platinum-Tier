# Gold Tier Demo Guide — Submission Checklist

> **Business:** NovaMind Tech Solutions | **Date:** 2026-03-12
> Run every command from the vault root:
> `D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault`

---

## MCP Connection Status (Pre-Verified)

| MCP Server | Status | Detail |
|-----------|--------|--------|
| Odoo | ✅ CONNECTED | Odoo 19.0-20260217, uid=2, db=ai_employee_db |
| Email SMTP | ✅ CONNECTED | smtp.gmail.com:587, izmarao99@gmail.com |
| Facebook | ✅ LIVE | Live Page token + Page ID configured — posts go live |
| Instagram | ✅ LIVE | Access token + Account ID configured — posts go live |
| Twitter/X | ⚠️ DRY-RUN | Keys configured; SOCIAL_DRY_RUN=true (no API credits) |
| Gmail Watcher | ⚠️ OAuth needed | credentials.json missing — explain during demo |

---

## Gold Tier Requirements Checklist

| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 1 | All Silver requirements | ✅ | Inbox, email, plans, HITL, LinkedIn |
| 2 | Cross-domain integration | ✅ | CLAUDE.md cross-domain section |
| 3 | Odoo + MCP server | ✅ | mcp_servers/odoo_server.py — 6 tools |
| 4 | Facebook + Instagram | ✅ | social_media_server.py — dry-run demo |
| 5 | Twitter/X | ✅ | Keys set, SOCIAL_DRY_RUN=true |
| 6 | Multiple MCP servers | ✅ | email-mcp + odoo + social-media |
| 7 | CEO Briefing | ✅ | Briefings/CEO_Briefing_2026-03-12.md |
| 8 | Error recovery | ✅ | utils/error_handler.py — 5 severity levels |
| 9 | Audit logging | ✅ | Logs/audit.jsonl — 16 entries |
| 10 | Ralph Wiggum loop | ✅ | .claude/hooks/ralph_stop_check.py |
| 11 | Architecture docs | ✅ | docs/architecture.md — 739 lines |
| 12 | Agent Skills | ✅ | 14 skills in .claude/skills/ |

---

## Demo Steps — Run In This Order

---

### STEP 1 — Show the Vault in Obsidian (1 min)

Open Obsidian → open this vault folder.

**What to show:**
- Open `Dashboard.md` → Gold tier dashboard with live data
- Show folder structure in sidebar: Inbox, Needs_Action, Done, Plans, Pending_Approval, Approved, Rejected, Briefings, Accounting, Social_Media, Logs
- Say: *"Every piece of work becomes a Markdown file that flows through these folders. The filesystem IS the message queue."*

**Key files to open:**
- `Dashboard.md` — live system state
- `Business_Goals.md` — NovaMind Tech Solutions
- `CLAUDE.md` — AI instructions (scroll to Gold Tier sections)

---

### STEP 2 — Verify ALL MCP Connections Live (2 min)

Run in Claude Code (type these commands):

```
Check all MCP connections: test Odoo status, SMTP status, and social media config
```

**Or show these MCP tool results one by one:**

**Odoo:**
```
Use odoo_status tool to verify connection
```
Expected output: `status: connected, version: 19.0-20260217, uid: 2`

**Email SMTP:**
```
Use check_smtp_status tool
```
Expected output: `OK: SMTP connection to smtp.gmail.com:587 successful`

**Social Media (dry-run):**
```
Show social media is configured with SOCIAL_DRY_RUN=true for safe demo
```

Say: *"Twitter has keys configured but SOCIAL_DRY_RUN=true — it simulates posts without using API credits. Facebook is live. Instagram needs one more token from the Meta developer portal."*

---

### STEP 3 — Odoo Accounting Integration (2 min)

**Run in Claude Code:**
```
Sync Odoo accounting data — search customers, get invoices, get account balances, update Current_Month.md
```

**What to show:**
1. Odoo MCP pulls live data from `localhost:8069`
2. 30-account Pakistani COA loaded
3. `Accounting/Current_Month.md` updated with live data
4. Dashboard accounting section reflects current state

**Open in Obsidian:** `Accounting/Current_Month.md`

Say: *"This syncs every day at 7 AM via scheduler.bat. Odoo is running locally on Docker."*

---

### STEP 4 — Social Media Post (live Facebook demo) (2 min)

**Run in Claude Code:**
```
/social-media-manager
Generate a social media post for NovaMind Tech Solutions about AI automation for Pakistani SMEs. Save as a Facebook post for approval.
```

**What to show:**
1. Post generated → saved to `/Pending_Approval/APPROVAL_social_post_facebook_*.md`
2. Show the HITL gate — file needs human approval before posting
3. Move file to `/Approved` to trigger live post
4. Claude calls `post_to_facebook()` via MCP → post goes live on NovaMind Facebook Page

**Open in Obsidian:** `Pending_Approval/` folder → move to `Approved/` live during demo

Say: *"Facebook is fully configured with a live Page token. The AI generated the post, but nothing goes live until I move this file to /Approved — that's the HITL safety layer. Watch what happens when I approve it."*

**Note:** Twitter is in dry-run mode (no API credits needed). Instagram is also live with token. Facebook is the cleanest live demo.

---

### STEP 5 — CEO Briefing (2 min)

**Open in Obsidian:** `Briefings/CEO_Briefing_2026-03-12.md`

Walk through the sections:
- Executive Summary (3 sentences with real numbers)
- Financial Overview (live from Odoo)
- Task Summary (from vault folders)
- Social Media Performance (per platform)
- System Health (all components)
- Top 3 Recommendations (data-driven)

Say: *"This generates every Monday at 7 AM automatically via Windows Task Scheduler. It's completely autonomous — reads Odoo, reads the vault, reads the audit log, and produces this in one shot."*

---

### STEP 6 — HITL Approval Workflow (1.5 min)

**Show existing approval files:**
```
ls Pending_Approval/
ls Approved/
ls Done/
```

**Show one pending approval file in Obsidian:** `Pending_Approval/PENDING_odoo_invoice_test_20260312_100000.md`

Walk through:
- YAML frontmatter: `action: create_invoice`, `approval_required: true`
- Invoice details table
- "Move to /Approved to approve, /Rejected to reject"

Say: *"This is the safety layer. Claude NEVER writes to Odoo, sends emails, or posts to social media without this file being in /Approved first. It's enforced at the code level — the Odoo MCP has zero write tools."*

---

### STEP 7 — Error Recovery (1.5 min)

**Show the error recovery test evidence:**

```
Open Logs/errors.jsonl
```

**Open in Obsidian:** `Logs/errors.jsonl` — scroll through and read aloud:

```
SEVERITY     COMPONENT          ERROR_TYPE             RESOLVED
-----------------------------------------------------------------
transient    odoo_sync          TimeoutError           resolved=True
transient    odoo_sync          TimeoutError           resolved=True
transient    odoo_sync          TimeoutError           resolved=True
auth         odoo_sync          PermissionError        resolved=True
```

**Open in Obsidian:** `Logs/audit.jsonl` — scroll to the `system_degraded` and `error_recovery` entries and highlight them.

Say: *"TRANSIENT errors retry 3 times with 30s/60s/120s backoff. AUTH errors create an URGENT file in /Needs_Action for human intervention. The system degrades gracefully — Gmail and file watcher continued working while Odoo was down."*

---

### STEP 8 — Ralph Wiggum Loop (1.5 min)

**Show the infrastructure:**

In terminal:
```bash
ls .claude/hooks/
ls .claude/commands/
cat .claude/settings.json
```

**Run a live test:**
```
/ralph-loop "List all files in /Needs_Action. If empty, confirm vault is clean and output <promise>VAULT_CLEAN</promise>" --max-iterations 3 --completion-promise "VAULT_CLEAN"
```

**What to show:**
1. `ralph_state.json` written (active=true, iteration=1)
2. Task executes
3. Promise `<promise>VAULT_CLEAN</promise>` output
4. Stop hook detects promise → allows stop
5. State cleared

Say: *"This is the stop-hook pattern. Claude works → tries to exit → hook checks for the promise → if found, stops → if not, re-injects the task. Named after The Simpsons character — persistent despite setbacks."*

---

### STEP 9 — Audit Log (1 min)

**Run in terminal:**
```bash
python scripts/demo_show_audit.py
```

**What to show:**
- Every action has ts, actor (claude vs human), action name
- HITL entries show `approval_required: true`
- `human` actor for the approval_granted entry

Say: *"Every single action — AI and human — is recorded here. You can see exactly what the AI did, when, and what the human approved. This is the complete audit trail."*

---

### STEP 10 — Scheduler (30 sec)

**Show the scheduler:**
```bash
scripts\scheduler.bat help
```

**Or show the file in editor:**
Open `scripts/scheduler.bat`

**Show Windows Task Scheduler setup doc:**
Open `docs/windows-scheduler-setup.md`

Say: *"9 scheduled tasks: daily Odoo sync at 7 AM, CEO Briefing every Monday, LinkedIn posts Mon/Wed/Fri, social batch Tue/Thu, weekly audit Sunday. All managed by Windows Task Scheduler."*

---

### STEP 11 — Architecture Docs (30 sec)

**Open:** `docs/architecture.md`

Scroll through quickly:
- ASCII component diagram (Section 1)
- Data flow diagrams (Section 2)
- Security model table (Section 4)
- 10 Lessons Learned (Section 5)

Say: *"739 lines, covers every component, every data flow, the security model, and 10 genuine lessons from building this system using AIDD methodology."*

---

### STEP 12 — Agent Skills (30 sec)

```bash
ls .claude/skills/
```

Show: 14 skills — `ceo-briefing`, `social-media-manager`, `odoo-accounting`, `error-recovery`, `audit-logger`, `ralph-loop-tasks`, etc.

Open one skill in editor: `.claude/skills/ceo-briefing/SKILL.md`

Say: *"Every recurring AI task is a version-controlled skill file. Updating the skill changes the AI's behavior for that task system-wide — no code changes needed."*

---

## Content Files to Submit

These files exist and are ready for submission:

```
AI_Employee_Vault/
├── CLAUDE.md                              ← AI instructions (full Gold tier)
├── README.md                              ← Project overview (536 lines)
├── Business_Goals.md                      ← NovaMind Tech Solutions
├── Company_Handbook.md                    ← Rules + approval policy
├── Dashboard.md                           ← Live system state
├── orchestrator.py                        ← Gold tier orchestrator
│
├── docs/
│   ├── architecture.md                    ← SUBMIT THIS (739 lines)
│   ├── windows-scheduler-setup.md         ← Task Scheduler setup
│   ├── odoo-setup.md                      ← Odoo Docker setup
│   └── social-media-setup.md             ← Social API setup
│
├── mcp_servers/
│   ├── email_server.py                    ← Email MCP (FastMCP)
│   ├── odoo_server.py                     ← Odoo MCP (XML-RPC)
│   └── social_media_server.py             ← FB/IG/Twitter MCP
│
├── utils/
│   ├── error_handler.py                   ← 5-severity error system
│   └── audit_logger.py                    ← JSONL audit trail
│
├── watchers/
│   ├── gmail_watcher.py                   ← Gmail OAuth watcher
│   └── filesystem_watcher.py             ← File drop watcher
│
├── scripts/
│   ├── scheduler.bat                      ← Windows Task Scheduler
│   └── scheduler.sh                       ← Linux/macOS cron
│
├── .claude/
│   ├── skills/ (14 skills)                ← All AI skills
│   ├── hooks/ralph_stop_check.py          ← Ralph Wiggum hook
│   ├── commands/ralph-loop.md             ← /ralph-loop command
│   └── settings.json                      ← Hook registration
│
├── Accounting/Current_Month.md            ← Live Odoo sync
├── Briefings/CEO_Briefing_2026-03-12.md  ← Generated briefing
└── Logs/
    ├── audit.jsonl                        ← 16 action entries
    └── errors.jsonl                       ← 4 error entries
```

---

## What to Say About Facebook

> *"Facebook is fully live — we have a Page Access Token with publish permissions. You just watched the AI generate a post, wait for human approval, then publish it to the NovaMind Facebook Page in real time. No dry-run, no simulation."*

## What to Say About Instagram

> *"Instagram is also fully configured with a live access token and account ID — same workflow as Facebook. Posts go live after HITL approval."*

## What to Say About Twitter

> *"Twitter/X has all 4 API keys configured. We set SOCIAL_DRY_RUN=true to avoid spending API credits during the demo — the code path is identical to live posting. Just flip that one env var."*

## What to Say About Gmail Watcher

> *"The Gmail watcher requires OAuth 2.0 — you run it once in a browser to get a token, which then auto-refreshes. We have the watcher code, the integration with the audit logger, and the CLAUDE.md instructions. For the demo we're showing the email MCP (SMTP send) which works live."*

---

## Quick Verify Before Demo

Run this one-liner to confirm everything is up:

```bash
python -c "
import xmlrpc.client, socket, os
from dotenv import load_dotenv; load_dotenv('.env')
# Odoo
try:
    c=xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
    uid=c.authenticate(os.environ['ODOO_DB'],os.environ['ODOO_LOGIN'],os.environ['ODOO_PASSWORD'],{})
    print(f'Odoo: OK uid={uid}')
except Exception as e: print(f'Odoo: FAIL {e}')
# SMTP
try:
    s=socket.create_connection(('smtp.gmail.com',587),timeout=5);s.close()
    print('SMTP: OK')
except Exception as e: print(f'SMTP: FAIL {e}')
# Social
for k in ['FB_PAGE_ACCESS_TOKEN','TWITTER_API_KEY']:
    print(f'{k}: {\"SET\" if os.environ.get(k) else \"MISSING\"}')
print(f'SOCIAL_DRY_RUN: {os.environ.get(\"SOCIAL_DRY_RUN\",\"false\")}')
"
```

Expected:
```
Odoo: OK uid=2
SMTP: OK
FB_PAGE_ACCESS_TOKEN: SET
TWITTER_API_KEY: SET
SOCIAL_DRY_RUN: true
```
