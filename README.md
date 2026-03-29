# Personal AI Employee — Gold Tier

A personal AI employee that monitors Gmail, files, and social media; manages business accounting via Odoo; autonomously generates weekly CEO briefings; and executes all sensitive actions through a Human-in-the-Loop approval layer. Built on Claude Code with three custom MCP servers.

## Tier

**Gold** — Full cross-domain integration (personal + business), 3 MCP servers, Odoo accounting, social media automation, autonomous CEO Briefing, structured audit logging, and graceful error recovery.

---

## Architecture

```
External Sources
┌────────────────────────────────────────────────┐
│  Gmail │ Files │ Facebook │ Instagram │ Twitter │
└────┬───────┬──────────┬─────────┬────────┬─────┘
     │       │          │         │        │
┌────▼───────▼──────────▼─────────▼────────▼─────┐
│              Watchers + Schedulers               │
│     Gmail │ Filesystem │ Cron (social/odoo)      │
└──────────────────┬──────────────────────────────┘
                   │ Creates .md files
┌──────────────────▼──────────────────────────────┐
│              Obsidian Vault                      │
│  /Needs_Action → /Plans → /Pending_Approval     │
│  Dashboard.md │ Handbook │ Business_Goals        │
│  /Accounting │ /Briefings │ /Social_Media │ /Logs│
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              Claude Code + Agentic Loop          │
│        Read → Think → Plan → Act → Iterate       │
└──────┬──────────┬────────────┬──────────────────┘
       │          │            │
┌──────▼───┐ ┌───▼────┐ ┌────▼───────────┐
│ Gmail MCP│ │Odoo MCP│ │Social Media MCP│
│(email)   │ │(acctg) │ │(FB/IG/Twitter) │
└──────────┘ └────────┘ └────────────────┘
       │
┌──────▼──────────────────────────────────────────┐
│              HITL Layer                          │
│  /Pending_Approval → Human Review → /Approved   │
└─────────────────────────────────────────────────┘
```

---

## Gold Tier Components

| Component | Description |
|-----------|-------------|
| **File Watcher** | Monitors `~/AI_Drop`, creates action items in `/Needs_Action` |
| **Gmail Watcher** | Monitors inbox, classifies priority, creates `EMAIL_*.md` |
| **Orchestrator** | Polls `/Needs_Action`, `/Approved`, `/Social_Media` every 30s; health checks every 5min |
| **Email MCP** | Send/draft/search Gmail via SMTP + API (HITL for sending) |
| **Odoo MCP** | Invoice, payment, balance queries via XML-RPC (HITL for writes) |
| **Social Media MCP** | Post to Facebook, Instagram, Twitter/X via APIs (HITL always) |
| **LinkedIn Poster** | Playwright automation for LinkedIn posts |
| **CEO Briefing** | Autonomous Monday morning business intelligence report |
| **Agentic Loop** | Multi-step autonomous task execution via `--max-turns` |
| **Error Recovery** | Retry with backoff, graceful degradation, URGENT alerts |
| **Audit Logger** | JSON Lines structured log of every action (`/Logs/audit.jsonl`) |
| **Scheduler** | Windows Task Scheduler / cron for all Gold-tier routines |

---

## Tech Stack

| Component | Purpose |
|-----------|---------|
| Claude Code | AI processing, planning, task execution, agentic loops |
| Obsidian | Vault interface, dashboard viewing |
| Python + watchdog | Filesystem monitoring |
| Gmail API + SMTP | Email monitoring and sending |
| Odoo 19 Community | ERP: accounting, invoicing, contacts |
| FastMCP | Custom MCP servers (email, Odoo, social media) |
| Playwright | LinkedIn browser automation |
| tweepy | Twitter/X API v2 |
| requests | Facebook Graph API, Instagram API |
| xmlrpc.client | Odoo XML-RPC connection |
| Docker Compose | Odoo + PostgreSQL local deployment |
| Windows Task Scheduler / cron | Scheduled Gold-tier routines |
| python-dotenv | Environment variable management |

---

## Prerequisites

- Claude Code CLI (latest)
- Python 3.13+
- `uv` (Python package manager)
- Obsidian
- Docker Desktop (for Odoo)
- Gmail account with API access
- LinkedIn account (for posting)
- Facebook Page + Instagram Business account (optional)
- Twitter/X Developer account (optional)

---

## Quick Start

### 1. Clone and Install

```bash
git clone <repo-url>
cd AI_Employee_Vault

# Install all Python dependencies
uv sync

# Install Playwright browser for LinkedIn
playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Email
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your-app-password

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_LOGIN=you@gmail.com
ODOO_PASSWORD=your-odoo-password

# Social Media (optional — dry-run mode activates if absent)
FB_PAGE_ACCESS_TOKEN=...
FB_PAGE_ID=...
IG_USER_ID=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...
SOCIAL_DRY_RUN=false
```

### 3. Start Odoo (Docker)

```bash
# From the Odoo install directory
docker compose up -d

# First-time setup: create database
# Visit http://localhost:8069 → create DB → set master password
# See docs/odoo-setup.md for full walkthrough
```

Verify connection:

```bash
python -c "
import xmlrpc.client
c = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
print(c.version())
"
```

### 4. Gmail API Setup

```bash
./scripts/setup_gmail_mcp.sh
# Or follow .claude/skills/gmail-setup/SKILL.md
```

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop App)
4. Download as `config/credentials.json`
5. Run Gmail watcher once to complete OAuth flow

### 5. Register MCP Servers

```bash
# Email
claude mcp add email-mcp -- uv run python mcp_servers/email_server.py

# Odoo (uses .env credentials automatically)
claude mcp add odoo -- uv run python mcp_servers/odoo_server.py

# Social Media
claude mcp add social-media -- uv run python mcp_servers/social_media_server.py

# Verify all three
claude mcp list
```

### 6. Social Media API Setup

See `docs/social-media-setup.md` for step-by-step guides. Summary:

- **Facebook:** Create App → add Page token → set `FB_PAGE_ACCESS_TOKEN` + `FB_PAGE_ID`
- **Instagram:** Connect Business account → set `IG_USER_ID`
- **Twitter/X:** Apply for Elevated access → create Project + App with Read+Write → set all 4 keys
- **Dry-run:** Leave credentials blank — all posts log to console without calling the API

### 7. Open in Obsidian

```
File → Open Vault → Select AI_Employee_Vault folder
```

### 8. Start the Orchestrator

```bash
# Continuous monitoring (all 3 folders + health checks every 5 min)
python orchestrator.py

# Dry run — logs actions but doesn't call Claude
python orchestrator.py --dry-run

# Custom intervals
python orchestrator.py --interval 60 --health-check-interval 120
```

### 9. Set Up Scheduled Tasks (Windows)

```powershell
# Run as Administrator — creates all 7 Task Scheduler tasks
# See docs/windows-scheduler-setup.md for the full PowerShell block
```

| Task | Time | Days |
|------|------|------|
| Odoo Sync | 7:00 AM | Daily |
| CEO Briefing | 7:00 AM | Monday |
| Daily Routine | 8:00 AM | Daily |
| LinkedIn Draft | 9:00 AM | Mon/Wed/Fri |
| Social Batch | 10:00 AM | Tue/Thu |
| Health Check | 6:00 AM | Daily |
| Weekly Audit | 6:00 PM | Sunday |

### 10. Run Your First CEO Briefing

```bash
scripts\scheduler.bat ceo-briefing
# Output: /Briefings/CEO_BRIEFING_YYYYMMDD.md
```

---

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items ready for processing
├── Plans/                    # Multi-step execution plans
├── Pending_Approval/         # Actions awaiting human approval
├── Approved/                 # Human-approved, ready to execute
├── Rejected/                 # Human-rejected (archive only)
├── Drafts/                   # Email/content drafts
├── Done/                     # Completed and archived items
│
├── Accounting/               # [Gold] Odoo financial snapshots
│   └── Current_Month.md      #   Invoice/payment totals, synced daily
├── Briefings/                # [Gold] Autonomous reports
│   ├── CEO_BRIEFING_*.md     #   Monday morning business intelligence
│   └── WEEKLY_AUDIT_*.md     #   Sunday week-in-review
├── Social_Media/             # [Gold] Post records by platform
│   ├── Facebook/
│   ├── Instagram/
│   └── Twitter/
├── Logs/                     # [Gold] Structured logs
│   ├── audit.jsonl           #   Every AI action (JSON Lines)
│   └── errors.jsonl          #   Error log with severity + recovery steps
│
├── memory/                   # Persistent state files
│   ├── orchestrator_state.json
│   ├── gmail_processed_ids.json
│   └── scheduler_logs/
├── config/                   # Credentials and tokens
│   ├── credentials.json      #   Gmail OAuth client
│   └── token.json            #   Gmail OAuth token (auto-generated)
│
├── watchers/                 # Folder monitors
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   └── gmail_watcher.py
├── mcp_servers/              # Custom MCP server implementations
│   ├── email_server.py       #   Gmail SMTP + API
│   ├── odoo_server.py        #   Odoo 19 XML-RPC [Gold]
│   └── social_media_server.py#   FB/IG/Twitter [Gold]
├── utils/                    # Shared Python utilities [Gold]
│   ├── audit_logger.py       #   AuditLogger class
│   └── error_handler.py      #   ErrorHandler + ErrorSeverity
├── scripts/                  # Automation scripts
│   ├── scheduler.bat         #   Windows Task Scheduler commands [Gold]
│   ├── scheduler.sh          #   Linux/macOS cron commands
│   └── linkedin_poster.py    #   Playwright LinkedIn automation
├── docs/                     # Documentation
│   ├── odoo-setup.md         #   Odoo Docker setup guide
│   ├── social-media-setup.md #   FB/IG/Twitter API setup
│   └── windows-scheduler-setup.md  # Task Scheduler configuration
│
├── .claude/skills/           # Agent skills (invoked by Claude)
├── orchestrator.py           # Gold-tier folder monitor + health check
├── Dashboard.md              # Real-time system status
├── Company_Handbook.md       # Rules, approval policies, priorities
├── Business_Goals.md         # Content strategy, Q1 goals, brand voice
└── CLAUDE.md                 # Claude Code operating instructions
```

---

## Agent Skills

### Bronze (Core)
| Skill | Description |
|-------|-------------|
| `file-processing` | Process items from `/Needs_Action`, classify priority |
| `vault-management` | Update `Dashboard.md`, track file counts |
| `task-planner` | Create step-by-step plans for complex tasks |
| `approval-handler` | Manage HITL approval workflow |
| `gmail-setup` | Guide for Gmail API OAuth setup |

### Silver (Integrations)
| Skill | Description |
|-------|-------------|
| `email-actions` | Send emails via Gmail MCP (requires approval) |
| `linkedin-posting` | Generate LinkedIn post drafts for approval |
| `scheduling` | Manage scheduled tasks and routines |

### Gold (Autonomous Operations)
| Skill | Description |
|-------|-------------|
| `ceo-briefing` | Generate Monday Morning CEO Briefing — full business audit |
| `social-media-manager` | Draft FB/IG/Twitter content, generate weekly summaries |
| `odoo-accounting` | Sync invoices/payments, flag overdue, update `/Accounting/` |
| `error-recovery` | Retry logic, fallback actions, URGENT alert creation |
| `audit-logger` | Standard vocabulary + usage guide for `/Logs/audit.jsonl` |

---

## HITL Approval Workflow

Every sensitive action passes through human review:

```
Claude identifies action that needs approval
           │
           ▼
Creates PENDING_*.md in /Pending_Approval
  (with frontmatter: action, target, draft content)
           │
           ▼
     Human reviews in Obsidian
           │
     ┌─────┴─────┐
     │           │
  Moves to    Moves to
  /Approved   /Rejected
     │           │
     ▼           ▼
 Orchestrator  Logged +
 executes via  archived,
 MCP server    not retried
     │
     ▼
Moved to /Done + audit logged
```

**Actions that always require approval:**
- Any outbound email
- All social media posts (including replies)
- All Odoo write operations (create/update)
- File deletion
- Any bulk operation

---

## Scheduled Tasks

| Task | Command | Time | Days |
|------|---------|------|------|
| Odoo Sync | `scheduler.bat odoo-sync` | 7:00 AM | Daily |
| CEO Briefing | `scheduler.bat ceo-briefing` | 7:00 AM | Monday |
| Daily Routine | `scheduler.bat daily` | 8:00 AM | Daily |
| LinkedIn Draft | `scheduler.bat linkedin` | 9:00 AM | Mon/Wed/Fri |
| Social Batch | `scheduler.bat social-batch` | 10:00 AM | Tue/Thu |
| Health Check | `scheduler.bat health-check` | 6:00 AM | Daily |
| Weekly Audit | `scheduler.bat weekly-audit` | 6:00 PM | Sunday |

See `docs/windows-scheduler-setup.md` for setup instructions.

---

## MCP Servers

### Email MCP (`email-mcp`) — Silver

| Tool | Purpose | Approval |
|------|---------|----------|
| `send_email` | Send via Gmail SMTP | Required |
| `draft_email` | Save to `/Drafts` | Auto |
| `search_emails` | Search Gmail inbox | Auto |
| `get_email_logs` | View action logs | Auto |
| `check_smtp_status` | Test SMTP connection | Auto |

### Odoo MCP (`odoo`) — Gold

| Tool | Purpose | Approval |
|------|---------|----------|
| `odoo_status` | Verify XML-RPC connection | Auto |
| `search_customers` | Find contacts by name | Auto |
| `get_invoices` | List posted invoices | Auto |
| `get_overdue_invoices` | List past-due invoices | Auto |
| `get_payments` | List recent payments | Auto |
| `get_account_balances` | Chart of accounts snapshot | Auto |

Write operations (create/update): **HITL required.** Delete: **never.**

### Social Media MCP (`social-media`) — Gold

| Tool | Purpose | Approval |
|------|---------|----------|
| `post_to_facebook` | Publish to Facebook Page | Required |
| `post_to_instagram` | Two-step IG publish | Required |
| `post_to_twitter` | Tweet via OAuth 1.0a | Required |
| `get_facebook_posts` | Fetch recent Page posts | Auto |
| `get_instagram_posts` | Fetch recent IG posts | Auto |
| `get_twitter_posts` | Fetch recent tweets | Auto |
| `social_media_status` | Check credentials + dry-run | Auto |
| `generate_social_summary` | Weekly engagement summary | Auto |

Dry-run mode activates automatically when API credentials are absent.

---

## Error Handling

All components share `utils/error_handler.py`:

| Severity | Trigger | Auto-action |
|----------|---------|-------------|
| `TRANSIENT` | Timeout, rate limit | Retry 3× (30s/60s/120s backoff) |
| `AUTH` | Invalid/expired credentials | Create URGENT item in `/Needs_Action` |
| `DATA` | Missing field, bad format | Skip item, continue processing |
| `CRITICAL` | Binary missing, data loss risk | Halt + create URGENT item |
| `EXTERNAL` | Third-party API down | Degrade gracefully, continue loop |

One component failure never crashes the orchestrator — each call is wrapped in `handler.catch()`.

---

## Audit Logging

Every AI action is logged to `/Logs/audit.jsonl` (JSON Lines format):

```json
{
  "ts": "2026-03-03T07:00:00.123456",
  "action": "email_received",
  "component": "gmail_watcher",
  "actor": "claude",
  "target": "EMAIL_invoice_request_20260303.md",
  "details": {"from": "client@example.com", "priority": "high"},
  "status": "success",
  "duration_ms": 142,
  "approval_required": false,
  "approval_status": ""
}
```

The CEO Briefing reads this log to produce email counts, task summaries, and system health metrics.

---

## Security Notes

- **Credentials:** Stored in `.env` (gitignored) — never committed
- **App Passwords:** Use Gmail App Passwords, not account passwords
- **OAuth tokens:** Stored in `config/token.json` — gitignored
- **Approval Workflow:** Hard-coded; cannot be bypassed programmatically
- **Odoo deletes:** Blocked at the MCP layer — no delete tools exposed
- **Social posts:** Dry-run activates automatically if credentials missing
- **Audit trail:** Every action timestamped in `/Logs/audit.jsonl`

---

## Lessons Learned

### What Worked Well

**Vault-as-interface was the right choice.** Using Obsidian markdown files as the communication layer between Claude and the human operator meant zero custom UI code. The HITL workflow — moving a file from `/Pending_Approval` to `/Approved` — is as simple as dragging in a file explorer. No buttons, no forms, no web server.

**FastMCP made server creation fast.** Each MCP server (`email_server.py`, `odoo_server.py`, `social_media_server.py`) was a single Python file with decorated functions. Adding a new tool took under 10 minutes.

**CLAUDE.md as operating system.** Writing detailed instructions into `CLAUDE.md` and `Company_Handbook.md` meant Claude consistently followed the same workflow across every session. The AI Employee's "personality" and decision-making framework lived in plain text files — version-controlled and human-readable.

**Dry-run by default.** Building dry-run mode into every component (watchers, MCP servers, orchestrator) from day one meant the system could be tested safely before any real credentials were added. This eliminated a whole class of accidental-send bugs.

### Challenges and How They Were Solved

**Odoo authentication took multiple rounds.** The `mcp-server-odoo` package (all versions) used a non-standard `/mcp/xmlrpc/common` endpoint that requires an Odoo module not present in Community Edition. Diagnosed by reading the full stack trace, then replaced with a custom `odoo_server.py` using the standard `/xmlrpc/2/` path. Lesson: always verify which API path a package hits before assuming it works.

**Docker volume / password desync.** After resetting the Odoo DB password in the UI, connections kept failing because the volume had been initialized with a different password. Fixed by running `ALTER USER odoo WITH PASSWORD '...'` directly inside the Postgres container. Lesson: docker volumes carry state that survives container restarts — always check the volume's original init values.

**Windows cp1252 encoding.** Several unicode characters (`→`, `✓`, emoji) in print statements caused `UnicodeEncodeError` on Windows. Fixed by replacing all unicode symbols with ASCII equivalents in console output. Lesson: develop on the same OS you'll deploy to, or set `PYTHONIOENCODING=utf-8` in the environment.

**HITL workflow friction.** Early versions required the human to create a new file in `/Approved` from scratch. Simplified by having Claude pre-fill the approval file with all necessary fields — the human only needs to move it, not edit it.

### Architecture Decisions and Trade-offs

**One orchestrator process, not many.** Chose a single polling orchestrator over per-folder watchdog observers. Trade-off: 30-second polling latency vs. the simplicity of a single process with a single restart command. For a personal AI Employee, 30 seconds is acceptable.

**Flat markdown files over a database.** All state (processed IDs, approval status, audit log) lives in plain files. Trade-off: no query language, no transactions — but zero infrastructure, works offline, and is fully inspectable in Obsidian. The JSONL audit log provides enough structure for the metrics the CEO Briefing needs.

**Custom Odoo MCP over the published package.** The custom `odoo_server.py` is ~200 lines and only exposes the 6 read tools we actually use. Trade-off: no automatic updates from upstream — but full control over error messages, connection handling, and the `.env` loading path.

**Health checks in Python, not via Claude.** The orchestrator health check runs pure Python (XML-RPC ping, socket connect, env var check) rather than calling `claude --print "check if Odoo is up"`. Trade-off: less natural language, but no API cost every 5 minutes and sub-second execution.

### What We Would Do Differently

1. **Start with the Odoo MCP path problem.** We spent significant time on `mcp-server-odoo` before discovering the non-standard endpoint. A 5-minute `curl http://localhost:8069/mcp/xmlrpc/common` before integrating would have surfaced this immediately.

2. **Set `PYTHONIOENCODING=utf-8` in the `.env` from day one** to avoid the Windows encoding issue showing up repeatedly in tests.

3. **Write the `AuditLogger` before writing any other component.** We added audit logging as a Gold-tier addition, which meant retrofitting it into watchers and the orchestrator. Starting with logging infrastructure first would have made the CEO Briefing metrics more complete.

4. **Generate the approval file template earlier.** The HITL workflow became much smoother once Claude pre-populated approval files. We would define the template in `Company_Handbook.md` at the Bronze tier and enforce it from the start.

---

## License

MIT
