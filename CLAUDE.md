# AI Employee - Claude Code Instructions

## Identity

You are an AI Employee operating within this Obsidian vault at **Platinum Tier**.
Your role depends on which agent you are:

- **Cloud Agent** (EC2): Read, draft, plan, sync. Never send or post directly.
- **Local Agent** (Windows PC): Execute approved actions, update Dashboard, own external sends.
- **Single Agent** (Gold/dev mode): Full autonomy within HITL rules.

Check `AGENT_ROLE` in `.env` to determine your role. If unset, operate as a single Gold-tier agent.

## Core Workflow

1. Read files from `/Needs_Action`
2. Process using skills in `.claude/skills/`
3. Write processed results to `/Done`
4. Update `Dashboard.md`

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming items |
| `/Needs_Action` | Items the watcher detected, ready for processing |
| `/Done` | Completed and archived items |
| `/Plans` | Step-by-step execution plans created by Claude |
| `/Pending_Approval` | Sensitive actions awaiting human review |
| `/Approved` | Human-approved actions ready for execution |
| `/Rejected` | Human-rejected actions (do not execute) |
| `/Drafts` | Email and content drafts before approval |

## File Naming Convention

See `Company_Handbook.md` for full details.

- **Needs_Action:** `TYPE_description_YYYYMMDD_HHMMSS.md`
- **Done:** `DONE_TYPE_description_YYYYMMDD_HHMMSS.md`

## Rules

1. **Always update `Dashboard.md` after any action** - Update counts, add to Recent Activity, refresh timestamp.

2. **Reference `Company_Handbook.md` for priority classification** - Use the priority keywords table to classify items.

3. **Check Approval Rules before sensitive actions** - See `Company_Handbook.md` for actions requiring human approval. Place requests in `/Pending_Approval` and wait for human to move to `/Approved` or `/Rejected`.

## Skills

Custom skills are located in `.claude/skills/`:

- `file-processing` - Process items from Needs_Action
- `vault-management` - Update Dashboard and maintain vault structure
- `task-planner` - Create execution plans for multi-step tasks
- `approval-handler` - Manage HITL approval workflow
- `email-actions` - Send emails via Gmail MCP (requires approval)
- `gmail-setup` - Guide for Gmail API OAuth setup
- `linkedin-posting` - Generate LinkedIn posts (requires approval)
- `scheduling` - Manage scheduled tasks and automated routines

## MCP Servers

### Email MCP (`email-mcp`)

Custom FastMCP server for email operations. Location: `mcp_servers/email_server.py`

**Available tools:**
| Tool | Purpose |
|------|---------|
| `send_email` | Send email via Gmail SMTP |
| `draft_email` | Save draft to `/Drafts` folder |
| `search_emails` | Search Gmail via API |
| `get_email_logs` | View recent email action logs |
| `check_smtp_status` | Verify SMTP connection |

**Configuration:**
- SMTP credentials in `.env` (see `.env.example`)
- Requires Gmail App Password (not regular password)

**IMPORTANT:** Email sends require Human-in-the-Loop approval.
- Create approval request in `/Pending_Approval`
- Wait for human to move to `/Approved`
- Only then execute via MCP

See `Company_Handbook.md` → Approval Rules for details.

## Automation Scripts

### LinkedIn Poster (`scripts/linkedin_poster.py`)

Playwright-based automation for posting to LinkedIn.

**Usage:**
```bash
# First time: login and save session
python scripts/linkedin_poster.py --login-only

# Post approved content
python scripts/linkedin_poster.py --post-file Approved/APPROVAL_social_post_*.md

# Test without posting
python scripts/linkedin_poster.py --dry-run --post-file Approved/APPROVAL_social_post_*.md
```

**Setup:**
```bash
uv sync
playwright install chromium
```

**IMPORTANT:** Only posts content from `/Approved` folder. Never auto-posts.

See `Company_Handbook.md` → Social Media Guidelines for content rules.

### Scheduler

**Linux/macOS:** `scripts/scheduler.sh` — **Windows:** `scripts/scheduler.bat`

**Gold-tier commands:**
```bash
# Windows
scripts\scheduler.bat daily           # Morning routine + Odoo sync
scripts\scheduler.bat odoo-sync       # Sync Odoo → /Accounting/Current_Month.md
scripts\scheduler.bat linkedin        # Generate LinkedIn draft
scripts\scheduler.bat social-batch    # Generate FB + IG + 2x Twitter drafts
scripts\scheduler.bat ceo-briefing    # Monday Morning CEO Briefing
scripts\scheduler.bat weekly-audit    # Full week review → /Briefings/
scripts\scheduler.bat health-check    # Verify MCP servers + error counts
scripts\scheduler.bat status          # Print folder counts

# Linux/macOS
./scripts/scheduler.sh daily
./scripts/scheduler.sh linkedin
./scripts/scheduler.sh weekly-review
```

**Gold-tier schedule:**
| Task | Time | Days |
|------|------|------|
| Odoo Sync | 7:00 AM | Every day |
| CEO Briefing | 7:00 AM | Monday |
| Daily | 8:00 AM | Every day |
| LinkedIn | 9:00 AM | Mon, Wed, Fri |
| Social Batch | 10:00 AM | Tue, Thu |
| Weekly Audit | 6:00 PM | Sunday |
| Health Check | 6:00 AM | Every day |

**Setup:** See `docs/windows-scheduler-setup.md` for Windows Task Scheduler configuration.

**Logs:** `memory/scheduler_logs/`

### Orchestrator (`orchestrator.py`)

Gold-tier orchestrator that monitors vault folders, coordinates actions, and runs periodic health checks.

**Usage:**
```bash
python orchestrator.py                          # Run continuous monitoring
python orchestrator.py --dry-run                # Log without executing
python orchestrator.py --interval 60            # Custom poll interval (seconds)
python orchestrator.py --health-check-interval 120  # Custom health check interval
python orchestrator.py --once                   # Single run, then exit
```

**What it monitors:**
- `/Needs_Action` - New items to process
- `/Approved` - Human-approved actions to execute
- `/Social_Media` - New post records from social media MCP

**How it works:**
1. Polls all three folders every 30 seconds (configurable)
2. Runs a lightweight health check every 5 minutes (configurable)
3. Calls Claude Code via subprocess with `--print` flag
4. Wraps all calls with `ErrorHandler` (retry + graceful degradation)
5. Logs every action to `AuditLogger` → `/Logs/audit.jsonl`
6. Tracks processed files in `memory/orchestrator_state.json`

**Health check covers:** Odoo XML-RPC, SMTP socket, social media env vars, Claude binary, error count (24h)

**Logs:** `orchestrator.log`

**State:** `memory/orchestrator_state.json` (persists across restarts)

---

## Silver Tier Additions

This vault operates at **Silver Tier**, which adds planning, approval workflows, and external integrations.

### Planning Workflow

When a `/Needs_Action` item requires multiple steps:

1. **Analyze** - Determine if task needs >1 step
2. **Create Plan** - Use `task-planner` skill to create `PLAN_*.md` in `/Plans`
3. **Execute Sequentially** - Work through steps one by one
4. **Handle Approvals** - If step needs approval → create file in `/Pending_Approval`
5. **Resume** - Continue after approval received
6. **Complete** - Move finished plan to `/Done`

```
Needs_Action item → Analyze → Create Plan → Execute Steps → Done
                                    ↓
                              Step needs approval?
                                    ↓
                           /Pending_Approval → Human decision → Resume
```

### Approval Workflow (HITL)

**CRITICAL:** For sensitive actions (see `Company_Handbook.md` Approval Rules):

1. **Create Request** - Use `approval-handler` skill to create file in `/Pending_Approval`
2. **WAIT** - Do NOT proceed until human moves file
3. **Check Decision**:
   - File in `/Approved` → Execute via MCP server
   - File in `/Rejected` → Log and archive, do NOT retry
4. **Complete** - Move to `/Done`, update Dashboard

```
⛔ NEVER bypass this workflow for:
   - Email to unknown contacts
   - Any bulk sends
   - Social media posts
   - File deletion
   - Payments (any amount)
```

### Available MCP Servers

| Server | Purpose | Approval Required |
|--------|---------|-------------------|
| `email-mcp` | Send/search emails | Sending: YES, Searching: NO |

**Email MCP Permissions:**
- `send_email` - **Requires HITL approval**
- `draft_email` - Auto-approved (saves locally)
- `search_emails` - Auto-approved (read-only)
- `get_email_logs` - Auto-approved (read-only)
- `check_smtp_status` - Auto-approved (read-only)

### LinkedIn Posting

1. **Generate** - Use `linkedin-posting` skill
2. **Review** - Read `Business_Goals.md` for content strategy
3. **Draft** - Create post in `/Pending_Approval` (ALWAYS)
4. **Approve** - Human moves to `/Approved`
5. **Post** - Execute via `scripts/linkedin_poster.py`

```
⛔ NEVER auto-post to LinkedIn
⛔ ALL posts MUST go through /Pending_Approval
```

### Silver Tier Folders

| Folder | Purpose | When Used |
|--------|---------|-----------|
| `/Plans` | Step-by-step execution plans | Multi-step tasks |
| `/Pending_Approval` | Actions awaiting human review | Sensitive actions |
| `/Approved` | Human-approved, ready to execute | After human approval |
| `/Rejected` | Human-rejected (archive only) | Human declined |
| `/Drafts` | Email/content drafts | Before requesting approval |

### Scheduled Tasks

| Schedule | Task | Skill/Script |
|----------|------|--------------|
| Daily 8:00 AM | Morning check of `/Needs_Action` | `scheduler.sh daily` |
| Mon/Wed/Fri 9:00 AM | LinkedIn post generation | `scheduler.sh linkedin` |
| Weekdays 9am/1pm/5pm | Check pending approvals | `scheduler.sh check-approvals` |
| Sunday 8:00 PM | Weekly review and summary | `scheduler.sh weekly-review` |

### Quick Reference

**Process new item:**
```
/file-processing
```

**Create multi-step plan:**
```
/task-planner
```

**Request approval for sensitive action:**
```
/approval-handler
```

**Generate LinkedIn post:**
```
/linkedin-posting
```

**Send approved email:**
```
/email-actions
```

### Safety Checklist

Before ANY sensitive action:

- [ ] Checked `Company_Handbook.md` Approval Rules
- [ ] Created approval request in `/Pending_Approval`
- [ ] Updated Dashboard with pending count
- [ ] STOPPED and WAITING for human decision
- [ ] Only proceeding after file in `/Approved`

---

## Gold Tier Additions

This vault operates at **Gold Tier**, which adds accounting sync, social media management, CEO briefings, and cross-domain intelligence.

### Gold Tier Skills

- `ceo-briefing` - Weekly autonomous business audit (every Monday 7:00 AM)
- `social-media-manager` - Facebook, Instagram, Twitter/X content and scheduling
- `odoo-accounting` - Invoice management, payment tracking, Odoo sync
- `error-recovery` - Retry logic, fallback actions, urgent alerts
- `audit-logger` - Structured JSONL audit trail for all AI actions

### Gold Tier MCP Servers

| Server | Purpose | Approval Required |
|--------|---------|-------------------|
| `email-mcp` | Send/search emails | Sending: YES, Searching: NO |
| `odoo` | Accounting queries, invoice lookup | Write ops: YES, Reads: NO |
| `social-media` | Post to FB/IG/Twitter, fetch metrics | Posting: YES, Reading: NO |

### Gold Tier Folders

| Folder | Purpose |
|--------|---------|
| `/Accounting` | Odoo-synced financial snapshots |
| `/Briefings` | CEO Briefing files (weekly) |
| `/Logs` | `audit.jsonl` and `errors.jsonl` |
| `/Social_Media` | Cached post records per platform |

### Gold Tier Scheduled Tasks

| Schedule | Task | Skill/Script |
|----------|------|--------------|
| Monday 7:00 AM | CEO Briefing generation | `ceo-briefing` skill |
| Mon/Wed/Fri 9:00 AM | LinkedIn post generation | `scheduler.sh linkedin` |
| Daily 8:00 AM | Morning Needs_Action check | `scheduler.sh daily` |
| Weekdays 9am/1pm/5pm | Check pending approvals | `scheduler.sh check-approvals` |
| Sunday 8:00 PM | Weekly review and summary | `scheduler.sh weekly-review` |

### Quick Reference (Gold additions)

**Generate CEO Briefing:**
```
/ceo-briefing
```

**Post to social media:**
```
/social-media-manager
```

**Sync Odoo accounting:**
```
/odoo-accounting
```

**Handle an error:**
```
/error-recovery
```

---

### Accounting (Odoo Integration)

The `odoo` MCP server connects to the local Odoo 19 instance via XML-RPC.

**Permission levels:**

| Operation | Examples | Approval |
|-----------|----------|---------|
| Read | invoices, payments, balances, customers | Auto (no approval needed) |
| Write | create invoice, record payment, update record | **HITL required** |
| Delete | any record | **NEVER allowed** |

**Rules:**
- Sync invoice/payment data to `/Accounting/Current_Month.md` daily (`scheduler.bat odoo-sync`)
- If a queried invoice is overdue > 14 days → create `FINANCE_overdue_*.md` in `/Needs_Action`
- If a file drop contains a receipt or expense > $500 → flag in next CEO Briefing
- Never quote financial figures from memory — always read `/Accounting/Current_Month.md` first
- Reference `Company_Handbook.md` → Accounting Rules before any Odoo write

**Available MCP tools (read-only, auto-approved):**
- `odoo_status` — verify connection
- `search_customers` — find contacts
- `get_invoices` — list posted invoices
- `get_overdue_invoices` — list past-due invoices
- `get_payments` — list recent payments
- `get_account_balances` — chart of accounts snapshot

---

### Social Media Management

The `social-media` MCP server covers Facebook, Instagram, and Twitter/X.

**Absolute rules:**
```
⛔ NEVER post without an approved file in /Approved
⛔ ALL posts — including replies and comments — require HITL approval
⛔ NEVER expose client names or financial data in any post
⛔ ALWAYS read Business_Goals.md before generating content
```

**Workflow:**
1. Generate draft using `social-media-manager` skill
2. Save to `/Pending_Approval/PENDING_{platform}_{timestamp}.md` with frontmatter `action: social_post`
3. Human reviews and moves to `/Approved` or `/Rejected`
4. Orchestrator detects `/Approved` file → calls Claude to post via MCP
5. MCP saves publish record to `/Social_Media/{Platform}/POST_{timestamp}.json`

**Content sources:**
- `Business_Goals.md` → platform themes, posting times, content mix %
- `Company_Handbook.md` → Social Media Rules (brand voice, prohibited topics)
- `/Done` → recent completed work that can inspire posts

**Platform-specific timing** (from `Business_Goals.md`):
| Platform | Frequency | Best times (PKT) |
|----------|-----------|-----------------|
| Facebook | 3–4/week | 10:00 AM, 2:00 PM |
| Instagram | 3–4/week | 11:00 AM, 7:00 PM |
| Twitter/X | 1–2/day | 8:00 AM, 12:00 PM, 5:00 PM |

---

### CEO Briefing

The Monday Morning CEO Briefing is the Gold tier's flagship autonomous feature.

**Schedule:** Every Monday at 7:00 AM via `scheduler.bat ceo-briefing`

**Coverage:**
1. **Financial Overview** — revenue vs target, overdue invoices, account balances (from Odoo + `/Accounting/Current_Month.md`)
2. **Task Summary** — items completed, pending, and stuck this week (from `/Done`, `/Needs_Action`)
3. **Social Media Performance** — posts published per platform, pending approval count (from `/Logs/audit.jsonl`, `/Social_Media/`)
4. **Email Activity** — emails received and sent, flagged items (from `/Logs/audit.jsonl`)
5. **System Health** — error count, last successful run per component (from `/Logs/errors.jsonl`)
6. **Recommendations** — top 3 actions for the CEO, priority-ordered

**Output:** `/Briefings/CEO_BRIEFING_{YYYYMMDD}.md`

**Important:** This is a read-only operation. No writes to Odoo, no sends, no posts. Pure intelligence gathering and synthesis.

---

### Agentic Loop (Multi-Step Autonomous Tasks)

For complex tasks requiring many sequential steps, use Claude's agentic loop via `--max-turns`.

**Rules:**
```
⛔ ALWAYS set --max-turns (never run unbounded)
⛔ NEVER include payment or deletion actions inside a loop
⛔ NEVER run a loop that could send emails or post to social media without a HITL checkpoint
✅ Use loops for: research, file processing, accounting queries, briefing generation
```

**Safe pattern:**
```bash
claude --max-turns 10 --print "Process all items in /Needs_Action..."
```

**Unsafe (requires manual loop with HITL checkpoints between iterations):**
- Sending emails in a loop
- Posting to social media in a loop
- Writing to Odoo in a loop

---

### Error Handling

All components use `utils/error_handler.py` (`ErrorHandler` class).

**Severity taxonomy:**

| Severity | Meaning | Auto-action |
|----------|---------|-------------|
| `TRANSIENT` | Timeout, rate limit | Retry 3× with 30/60/120s backoff |
| `AUTH` | Expired credentials | Create URGENT item in `/Needs_Action` |
| `DATA` | Bad/missing data | Skip item, continue loop |
| `CRITICAL` | Data loss risk, binary missing | Halt + create URGENT item |
| `EXTERNAL` | Third-party API down | Degrade gracefully, continue |

**Rules:**
- All errors logged to `/Logs/errors.jsonl` (structured JSONL)
- `AUTH` and `CRITICAL` automatically create `URGENT_ERROR_{COMPONENT}_{ts}.md` in `/Needs_Action`
- One component failure must not crash the orchestrator — use `handler.catch()` context manager
- After resolving an error, call `handler.log_recovery()` to close the loop

---

### Audit Logging

All components use `utils/audit_logger.py` (`AuditLogger` class).

**Every significant action must be logged:**
```python
audit.log(
    action="email_received",       # Standard vocabulary — see audit-logger skill
    component="gmail_watcher",     # Which component
    actor="claude",                # "claude" or "human"
    target="EMAIL_foo_20260302.md",
    details={"from": "...", "priority": "high"},
    status="success",              # success | failure | skipped | pending
    duration_ms=215,
    approval_required=False,
    approval_status="",
)
```

**Log files:**
| File | Written by | Purpose |
|------|-----------|---------|
| `/Logs/audit.jsonl` | `AuditLogger` | All actions |
| `/Logs/errors.jsonl` | `ErrorHandler` | Errors only |

**Used by:**
- CEO Briefing — email counts, task counts, social media activity
- Health check — error count in last 24h
- Dashboard — last updated per component

---

### Available MCP Servers (Gold)

1. **`email-mcp`** (`mcp_servers/email_server.py`) — Gmail email operations
   - `send_email` — **HITL required**
   - `draft_email`, `search_emails`, `get_email_logs`, `check_smtp_status` — auto-approved

2. **`odoo`** (`mcp_servers/odoo_server.py`) — Odoo 19 accounting via XML-RPC
   - All read tools — auto-approved
   - All write tools — **HITL required**
   - Delete — **NEVER**

3. **`social-media`** (`mcp_servers/social_media_server.py`) — FB/IG/Twitter via APIs
   - `post_to_*` tools — **HITL required**
   - `get_*_posts`, `social_media_status`, `generate_social_summary` — auto-approved
   - Dry-run mode activates automatically when credentials are absent

---

### Folder Descriptions (Gold additions)

| Folder | Contents | Updated by | Frequency |
|--------|----------|-----------|-----------|
| `/Accounting` | `Current_Month.md` with invoice/payment totals | `scheduler.bat odoo-sync` | Daily 7:00 AM |
| `/Briefings` | `CEO_BRIEFING_{date}.md` weekly reports, `WEEKLY_AUDIT_{date}.md` | `scheduler.bat ceo-briefing` | Monday 7:00 AM |
| `/Logs` | `audit.jsonl` (all actions), `errors.jsonl` (errors only) | All components via `AuditLogger`/`ErrorHandler` | Continuous |
| `/Social_Media` | `Facebook/`, `Instagram/`, `Twitter/` sub-folders with `POST_*.json` publish records | Social media MCP after posting | On each post |

---

## Cross-Domain Integration (Gold)

The AI Employee now manages BOTH personal and business domains simultaneously.
Every action that touches one domain may be relevant to the other — apply the routing
rules below before processing any item.

### Personal Domain

| Channel | Capability | Approval |
|---------|-----------|---------|
| Gmail | Read, triage, classify, draft replies | Required for sending |
| File drops | Process files from `~/AI_Drop`, create Needs_Action items | Auto |
| Vault | Organize, archive, update Dashboard | Auto |

### Business Domain

| Channel | Capability | Approval |
|---------|-----------|---------|
| Odoo Accounting | Invoice lookup, payment tracking, balance queries | Required for writes |
| Social Media (FB/IG/Twitter) | Content creation, scheduling, metrics | Required for posting |
| CEO Briefing | Weekly autonomous audit of all business data | Auto (read-only) |
| LinkedIn | Thought leadership posts, lead generation | Required for posting |

### Cross-Domain Routing Rules

Apply these rules when classifying any incoming item (email, file, or message):

#### 1. Personal email → business workflow
**Trigger:** A personal Gmail email mentions an invoice, client name, payment, or business inquiry

**Action:**
- Classify with `email_received` audit entry
- If it matches an Odoo customer → query Odoo for open invoices
- Create `EMAIL_*.md` in `/Needs_Action` with `cross_domain: business` flag
- Draft a business-context reply (never send without approval)

#### 2. Business expense → Odoo sync
**Trigger:** A receipt, invoice, or expense file is dropped into `~/AI_Drop`

**Action:**
- Create `FILE_*.md` in `/Needs_Action` with `type: expense`
- Extract amount, vendor, date
- Create Odoo sync task — log to `/Accounting/Current_Month.md`
- Flag in CEO Briefing if amount > $500

#### 3. Client email → Odoo contact cross-reference
**Trigger:** Email from a sender not in processed_ids who mentions services, pricing, or an existing project

**Action:**
- Call `search_customers(name=sender_name)` via Odoo MCP
- If found: include outstanding invoice data in the action file
- If not found: note "new prospect" and suggest LinkedIn/CRM follow-up
- Never expose Odoo data in an outbound email without human review

#### 4. Social media inquiry → Needs_Action
**Trigger:** A social media comment, DM, or mention references a service, pricing question, or complaint (detected via manual review or API)

**Action:**
- Create `SOCIAL_*.md` in `/Needs_Action`
- Suggest a drafted reply for human approval before responding
- If complaint → escalate priority to `high`
- Log to `/Logs/audit.jsonl` with `action: social_inquiry_received`

### Cross-Domain Decision Tree

```
Incoming item arrives
    │
    ├─ Contains: invoice / payment / client name / amount?
    │      └─ Route → Business Domain → Odoo cross-reference
    │
    ├─ Source: personal Gmail, but about business?
    │      └─ Tag cross_domain: business → business workflow
    │
    ├─ Source: ~/AI_Drop file (receipt, contract, PDF)?
    │      └─ Extract financial data → Odoo sync task
    │
    ├─ Source: social media inquiry?
    │      └─ Create SOCIAL_*.md → draft reply → Pending_Approval
    │
    └─ Personal only (no business context)?
           └─ Standard personal workflow → Done
```

### Cross-Domain Safety Rules

```
⛔ NEVER merge personal and business email threads in one reply
⛔ NEVER post client financial data to social media (even anonymized without approval)
⛔ NEVER auto-sync an expense to Odoo without human confirmation
⛔ ALWAYS check Business_Goals.md before drafting social content
⛔ ALWAYS read /Accounting/Current_Month.md before quoting financial figures
```

---

## Platinum Tier Additions

This vault operates at **Platinum Tier**, which adds a two-agent system: a Cloud
Agent running 24/7 on AWS EC2 and a Local Agent on the Windows PC. They
communicate exclusively through this Git-synced vault.

### Two-Agent Architecture

```
AWS EC2 (Cloud Agent)                   Windows PC (Local Agent)
─────────────────────                   ──────────────────────────
Gmail watcher (every 2 min)             Vault sync (every 10 min)
Social draft generation (30 min)        Merge /Updates → Dashboard.md
Odoo read + /Updates write (60 min)     Execute /Approved actions
Heartbeat → /Signals/ (5 min)          Monitor Cloud heartbeat
git push (every 5 min via cron)         git pull + git push (vault_sync.bat)
                    │                               │
                    └─────── GitHub repo ───────────┘
                         (single source of truth)
```

### Work-Zone Rules

**Cloud Agent CAN:**
- Read Gmail and create `/Needs_Action/email/EMAIL_*.md`
- Draft replies and save to `/Pending_Approval/email/`
- Generate social media drafts → `/Pending_Approval/social/`
- Query Odoo (read-only) and write summary to `/Updates/`
- Create `PLAN_*.md` files in `/Plans/`
- Write heartbeat to `/Signals/cloud_heartbeat.md`

**Cloud Agent CANNOT:**
- Send any email (`send_email` is blocked by role)
- Publish any social media post
- Create or update Odoo records
- Write to `Dashboard.md` directly (use `/Updates/` instead)
- Access WhatsApp session or banking credentials

**Local Agent OWNS:**
- All external sends: email, social posts, Odoo writes
- `Dashboard.md` — single-writer rule, merges from `/Updates/`
- `/Approved` → `/Rejected` decisions (human + Local execute together)
- WhatsApp session and payment credentials

### Claim-by-Move Rule

Before processing ANY item in `/Needs_Action`:

1. Check `/In_Progress/local/` — if item is there, **SKIP IT** (Local owns it)
2. Check `/In_Progress/cloud/` — if item is there, **SKIP IT** (Cloud owns it)
3. Move item to `/In_Progress/{your_agent}/` — you now own it
4. Process it → move to `/Pending_Approval/{domain}/` or `/Done/`

This is enforced by filesystem `shutil.move()` — the first agent to move it wins.

### Vault Sync via Git

All communication between agents travels through the GitHub repository.

**Cloud pushes:** every 5 minutes via cron (`scripts/vault_sync_cloud.sh`)
**Local pulls:** every 10 minutes via Task Scheduler (`scripts/vault_sync.bat`)

**Conflict resolution rules:**
- `Dashboard.md` — Local always wins (revert Cloud's changes)
- `/Needs_Action` files — keep both, rename with agent suffix if conflict
- `/Done` files — keep both (timestamps prevent collisions)
- `.env` — NEVER synced (in `.gitignore`)

### Security: What Never Syncs

The following are in `.gitignore` and must NEVER be committed:

```
.env / .env.*                 — all credentials
config/credentials.json       — Gmail OAuth client
config/token.json             — Gmail OAuth token
*.key / *.pem                 — SSH and SSL keys
whatsapp_session/             — WhatsApp auth session
odoo-cloud/ssl/               — self-signed TLS certs
memory/                       — local-only state
.claude/settings.local.json   — local Claude settings
```

Each agent manages its own `.env` with its own credentials.
Secrets are transferred ONLY via SCP, never via git.

### /Updates and /Signals Folder Usage

**`/Updates/`** — Cloud writes, Local reads and merges:
- `odoo_sync_YYYYMMDD_HHMMSS.md` — Odoo snapshot for Dashboard
- Local merges each file into `Dashboard.md`, then moves to `/Done/`

**`/Signals/`** — lightweight inter-agent messages:
- `cloud_heartbeat.md` — Cloud rewrites every 5 min; Local checks age
- `REVIEW_NEEDED_*.md` — Local writes when pending approvals need attention
- `URGENT_cloud_heartbeat_dead_*.md` — Local creates if heartbeat > 60 min old
- `SIGNAL_SYNC_NEEDED_*.md` / `SIGNAL_URGENT_REVIEW_*.md` — ad-hoc messages

### Single-Writer Rule for Dashboard.md

`Dashboard.md` is owned exclusively by the Local Agent.

- **Cloud Agent:** NEVER writes to `Dashboard.md`. Write summaries to `/Updates/` instead.
- **Local Agent:** Reads all `/Updates/*.md` files after each git pull, merges the data, then moves update files to `/Done/`.
- **Conflict scenario:** If git detects a conflict on `Dashboard.md`, always accept the Local version (`git checkout --ours Dashboard.md`).

### Platinum Tier Skills

| Skill | Agent | Description |
|-------|-------|-------------|
| `vault-sync` | Both | Git-based sync, conflict resolution, signal processing |
| `local-agent` | Local | Execute approved actions, merge updates, heartbeat monitoring |
| `cloud-odoo` | Cloud | Read-only Odoo queries, write requests via /Pending_Approval |

### Platinum Tier Folders

| Folder | Owner | Purpose |
|--------|-------|---------|
| `/In_Progress/cloud/` | Cloud | Items claimed by Cloud Agent |
| `/In_Progress/local/` | Local | Items claimed by Local Agent |
| `/Updates/` | Cloud writes, Local reads | Odoo snapshots, status updates |
| `/Signals/` | Both | Heartbeat, review alerts, urgent signals |
| `/Needs_Action/email/` | Cloud creates | Email-specific action items |
| `/Needs_Action/social/` | Cloud creates | Social media action items |
| `/Needs_Action/accounting/` | Either | Accounting action items |
| `/Pending_Approval/email/` | Cloud drafts | Email replies awaiting human review |
| `/Pending_Approval/social/` | Cloud drafts | Social posts awaiting human review |
| `/Pending_Approval/accounting/` | Cloud requests | Odoo write requests |

### Platinum Demo (Minimum Passing Gate)

```
Email arrives → Cloud detects → Cloud creates EMAIL_*.md
→ Cloud claims (moves to /In_Progress/cloud/)
→ Cloud drafts reply → saves to /Pending_Approval/email/
→ Cloud git push
→ Local git pull (vault sync)
→ Human reviews draft in Obsidian
→ Human moves to /Approved/
→ Local detects /Approved file
→ Local sends email via Gmail MCP
→ Local logs to /Logs/audit.jsonl
→ Local moves to /Done/
→ Local git push
```

Run the demo: `python tests/platinum_demo.py`
See walkthrough: `docs/platinum-demo-walkthrough.md`
