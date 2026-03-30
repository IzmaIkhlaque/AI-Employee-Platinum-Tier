# Personal AI Employee — Platinum Tier

A personal AI employee that runs 24/7 across two machines: a Cloud Agent on AWS EC2 and a Local Agent on Windows PC. It monitors Gmail, files, and social media; manages business accounting via Odoo; autonomously generates weekly CEO briefings; drafts all content for human approval; and executes sends only after explicit sign-off. Built on Claude Code with three custom MCP servers and a Git-synced Obsidian vault as the communication backbone.

## Tier

**Platinum** — Two-agent distributed system (AWS EC2 + Windows PC), 3 MCP servers, Odoo 19 on EC2 with HTTPS, Git-based vault sync, claim-by-move concurrency control, structured audit logging, graceful error recovery, and the Platinum demo flow: email → Cloud draft → human approval → Local send → audit log → Done.

---

## Architecture

```
                        PLATINUM TWO-AGENT SYSTEM
                        ═══════════════════════════

  AWS EC2 (Cloud Agent)              GitHub Repo              Windows PC (Local Agent)
  ──────────────────────        ─────────────────────        ──────────────────────────
                                │                   │
  Gmail watcher (2min) ─────── │  git push (5min)  │ ──────  git pull (10min)
  Social drafts (30min) ──────►│                   │◄──────  vault_sync.bat
  Odoo read + /Updates ───────►│  Vault = source   │◄──────  Dashboard.md (owner)
  Heartbeat → /Signals ───────►│    of truth       │◄──────  Execute /Approved
  systemd 24/7 uptime  ─────── │                   │ ──────  Task Scheduler
                                └─────────────────────
                                          │
                         ┌────────────────┴────────────────┐
                         │         Obsidian Vault          │
                         │                                 │
                         │  /Needs_Action → /In_Progress   │
                         │  /Pending_Approval → /Approved  │
                         │  /Updates → Dashboard.md        │
                         │  /Signals  (heartbeat, alerts)  │
                         │  /Logs/audit.jsonl              │
                         └─────────────────────────────────┘

  External Sources                                     MCP Servers (Local only)
  ────────────────                                     ────────────────────────
  Gmail    ──► Cloud reads, drafts replies             email-mcp   (send/draft/search)
  Files    ──► Cloud creates action items              odoo        (read auto / write HITL)
  Facebook ──► Cloud generates drafts                 social-media (post HITL / read auto)
  Instagram──► Cloud generates drafts
  Twitter  ──► Cloud generates drafts
  Odoo ERP ──► Cloud reads → /Updates → Local merges → Dashboard.md
```

---

## Two-Agent Specialization

| Capability | Cloud Agent (EC2) | Local Agent (Windows) |
|-----------|-------------------|-----------------------|
| Run 24/7 | Yes (systemd) | Via Task Scheduler |
| Read Gmail | Yes | No |
| Draft email replies | Yes → /Pending_Approval | No |
| Send email | **NO** | Yes (after approval) |
| Generate social drafts | Yes → /Pending_Approval | No |
| Post to social media | **NO** | Yes (after approval) |
| Read Odoo data | Yes → /Updates | Via Local MCP |
| Write to Odoo | **NO** | Yes (after approval) |
| Update Dashboard.md | **NO** (writes /Updates) | Yes (single-writer) |
| Execute /Approved files | **NO** | Yes |
| Monitor Cloud heartbeat | No | Yes |

---

## Platinum Components

| Component | Location | Description |
|-----------|----------|-------------|
| **Cloud Agent** | `cloud/cloud_agent.py` | asyncio loop — Gmail, Odoo reads, social drafts, vault sync |
| **Local Agent** | `local/local_agent.py` | Sync cycle — merge /Updates, notify pending, execute approved |
| **Health Monitor** | `cloud/cloud_health_monitor.py` | Watchdog: restarts cloud_agent if dead (`--once` for cron) |
| **Vault Sync (Cloud)** | `scripts/vault_sync_cloud.sh` | git pull + push every 5 min via cron on EC2 |
| **Vault Sync (Local)** | `scripts/vault_sync.bat` | git pull + push every 10 min via Task Scheduler |
| **Odoo on EC2** | `odoo-cloud/docker-compose.yml` | Odoo 19 + PostgreSQL 16 + Nginx HTTPS (self-signed) |
| **Odoo Backup** | `odoo-cloud/backup.sh` | Daily pg_dump at 2 AM, keeps last 7 |
| **Orchestrator** | `orchestrator.py` | AGENT_ROLE dispatch — delegates to Cloud or Local agent |
| **Platinum Demo** | `tests/platinum_demo.py` | End-to-end 18-step demo with verify mode |

### Gold Tier Components (still active)

| Component | Description |
|-----------|-------------|
| **Email MCP** | Send/draft/search Gmail via SMTP + API (HITL for sending) |
| **Odoo MCP** | Invoice, payment, balance queries via XML-RPC (HITL for writes) |
| **Social Media MCP** | Post to Facebook, Instagram, Twitter/X via APIs (HITL always) |
| **LinkedIn Poster** | Playwright automation for LinkedIn posts |
| **CEO Briefing** | Autonomous Monday morning business intelligence report |
| **Agentic Loop** | Multi-step autonomous task execution via `--max-turns` |
| **Error Recovery** | Retry with backoff, graceful degradation, URGENT alerts |
| **Audit Logger** | JSON Lines structured log of every action (`/Logs/audit.jsonl`) |
| **Scheduler** | Windows Task Scheduler + EC2 cron for all scheduled routines |

---

## Tech Stack

| Component | Purpose |
|-----------|---------|
| Claude Code | AI processing, planning, task execution, agentic loops |
| AWS EC2 t2.micro | Cloud Agent VM (Free Tier, Ubuntu 22.04) |
| systemd | Cloud Agent 24/7 service management |
| Obsidian | Vault interface, dashboard, approval workflow |
| Git + GitHub | Inter-agent communication and state sync |
| Python 3.13 + asyncio | Cloud Agent concurrent task scheduling |
| FastMCP | Custom MCP servers (email, Odoo, social media) |
| Docker Compose | Odoo 19 + PostgreSQL 16 + Nginx on EC2 |
| Gmail API + SMTP | Email monitoring and sending |
| Odoo 19 Community | ERP: accounting, invoicing, contacts |
| Playwright | LinkedIn browser automation |
| tweepy | Twitter/X API v2 |
| requests | Facebook Graph API, Instagram API |
| xmlrpc.client | Odoo XML-RPC connection |
| psutil | Cloud health monitor process detection |
| Windows Task Scheduler | Local Agent scheduling |
| python-dotenv | Per-agent environment variable management |

---

## Prerequisites

**Local PC (Windows):**
- Claude Code CLI (latest)
- Python 3.13+
- `uv` (Python package manager)
- Obsidian
- Docker Desktop (optional — Odoo can also run on EC2)
- Git with GitHub access

**AWS EC2 (Ubuntu 22.04):**
- Free Tier t2.micro instance
- Python 3.13, Node.js 24, Docker, Git, UV, Claude Code
- GitHub Personal Access Token (for private repo clone)
- See `docs/aws-cloud-setup.md` for full setup guide

---

## Quick Start

### 1. Clone and Install (Local PC)

```bash
git clone https://github.com/IzmaIkhlaque/AI-Employee-Gold-Tier.git AI_Employee_Vault
cd AI_Employee_Vault
uv sync
playwright install chromium
```

### 2. Configure Local .env

```bash
cp .env.example .env
```

```env
# Agent identity
AGENT_ROLE=local

# Email
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your-app-password

# Odoo (on EC2 or localhost)
ODOO_URL=http://YOUR_EC2_IP:8069
ODOO_DB=ai_employee_db
ODOO_API_KEY=your_odoo_api_key

# Social Media (optional — dry-run activates if absent)
FB_PAGE_ACCESS_TOKEN=...
FB_PAGE_ID=...
IG_USER_ID=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...
SOCIAL_DRY_RUN=false
```

### 3. Register MCP Servers (Local)

```bash
claude mcp add email-mcp -- uv run python mcp_servers/email_server.py
claude mcp add odoo -- uv run python mcp_servers/odoo_server.py
claude mcp add social-media -- uv run python mcp_servers/social_media_server.py
claude mcp list
```

### 4. Open in Obsidian

```
File → Open Vault → Select AI_Employee_Vault folder
```

### 5. Deploy Cloud Agent on EC2

Follow `docs/aws-cloud-setup.md` completely. Summary:

```bash
# SSH into EC2
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_EC2_IP

# After setup_ec2_services.sh:
cd ~/AI_Employee_Vault
bash cloud/setup_ec2_services.sh

# Start Odoo
cd ~/odoo-cloud && docker compose up -d

# Verify
sudo systemctl status ai-employee-cloud
```

### 6. Configure EC2 .env

```bash
nano ~/AI_Employee_Vault/.env
```

```env
AGENT_ROLE=cloud
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_API_KEY=your_key
SOCIAL_DRY_RUN=true
```

### 7. Copy Gmail Credentials to EC2 (SCP — never via git)

```powershell
scp -i "D:\aws-keys\ai-employee-key.pem" config\credentials.json ubuntu@YOUR_EC2_IP:~/AI_Employee_Vault/config/
scp -i "D:\aws-keys\ai-employee-key.pem" config\token.json ubuntu@YOUR_EC2_IP:~/AI_Employee_Vault/config/
```

### 8. Set Up Windows Task Scheduler (Local)

```powershell
# Run as Administrator — see docs/windows-scheduler-platinum.md for full block
# Creates: AI-LocalAgent, AI-VaultSync (every 10 min)
#          AI-Daily-Morning, AI-CEO-Briefing
```

### 9. Run the Platinum Demo

```bash
# Simulate Cloud side (or run on actual EC2)
python tests/platinum_demo.py --mode cloud --demo-id demo01

# Simulate Local side (after vault sync)
python tests/platinum_demo.py --mode local --demo-id demo01

# Verify everything passed
python tests/platinum_demo.py --mode verify --demo-id demo01
```

See `docs/platinum-demo-walkthrough.md` for the screen-by-screen recording guide.

---

## Folder Structure

```
AI_Employee_Vault/
│
├── Inbox/                      # Raw incoming items
├── Needs_Action/               # Items ready for processing
│   ├── email/                  # [Platinum] Cloud-created email items
│   ├── social/                 # [Platinum] Social media items
│   └── accounting/             # Accounting action items
├── In_Progress/                # [Platinum] Claimed items
│   ├── cloud/                  #   Items owned by Cloud Agent
│   └── local/                  #   Items owned by Local Agent
├── Plans/                      # Multi-step execution plans
│   ├── email/ │ social/ │ accounting/
├── Pending_Approval/           # Actions awaiting human review
│   ├── email/                  #   [Platinum] Cloud-drafted email replies
│   ├── social/                 #   [Platinum] Cloud-drafted social posts
│   └── accounting/             #   [Platinum] Cloud-requested Odoo writes
├── Approved/                   # Human-approved, ready to execute
├── Rejected/                   # Human-rejected (archive only)
├── Done/                       # Completed and archived items
│
├── Updates/                    # [Platinum] Cloud writes, Local reads + merges
├── Signals/                    # [Platinum] Heartbeat, review alerts, urgent signals
│   └── cloud_heartbeat.md      #   Rewritten every 5 min by Cloud Agent
│
├── Accounting/                 # [Gold] Odoo financial snapshots
│   └── Current_Month.md
├── Briefings/                  # [Gold] Autonomous reports
│   ├── CEO_BRIEFING_*.md
│   └── WEEKLY_AUDIT_*.md
├── Social_Media/               # [Gold] Post records by platform
│   ├── Facebook/ │ Instagram/ │ Twitter/
├── Logs/                       # [Gold] Structured logs
│   ├── audit.jsonl             #   Every AI action (JSON Lines)
│   └── errors.jsonl            #   Error log with severity + recovery
│
├── cloud/                      # [Platinum] Cloud Agent
│   ├── cloud_agent.py          #   asyncio agent — main loop
│   ├── cloud_health_monitor.py #   Watchdog process
│   ├── ai-employee-cloud.service # systemd unit file
│   ├── setup_ec2_services.sh   #   One-command EC2 setup
│   └── CLAUDE.md               #   Cloud Agent identity + rules
├── local/                      # [Platinum] Local Agent
│   └── local_agent.py          #   Sync + execute loop
├── odoo-cloud/                 # [Platinum] Odoo on EC2
│   ├── docker-compose.yml      #   Odoo 19 + PostgreSQL 16 + Nginx
│   ├── nginx.conf              #   HTTPS reverse proxy
│   ├── backup.sh               #   Daily pg_dump
│   └── ssl/                    #   Self-signed certs (not in git)
├── tests/                      # [Platinum] Demo and tests
│   └── platinum_demo.py        #   18-step end-to-end demo
│
├── mcp_servers/                # Custom MCP server implementations
│   ├── email_server.py
│   ├── odoo_server.py
│   └── social_media_server.py
├── utils/                      # Shared Python utilities
│   ├── audit_logger.py
│   └── error_handler.py
├── watchers/                   # Folder monitors (Gold/local mode)
│   ├── filesystem_watcher.py
│   └── gmail_watcher.py
├── scripts/                    # Automation scripts
│   ├── vault_sync.bat          #   [Platinum] Local git pull+push
│   ├── vault_sync_cloud.sh     #   [Platinum] Cloud git pull+push
│   ├── scheduler.bat           #   [Gold] Windows scheduled commands
│   └── linkedin_poster.py      #   Playwright LinkedIn automation
├── docs/
│   ├── how-to-run.md           #   Complete start/stop/verify guide
│   ├── aws-cloud-setup.md      #   EC2 setup (every click)
│   ├── platinum-demo-walkthrough.md  # Screen-by-screen demo guide
│   ├── windows-scheduler-platinum.md # Platinum Task Scheduler setup
│   └── windows-scheduler-setup.md   # Gold Task Scheduler setup
│
├── .claude/skills/             # Agent skills
├── orchestrator.py             # AGENT_ROLE dispatch + Gold-tier loop
├── Dashboard.md                # Real-time system status (Local owns)
├── Company_Handbook.md         # Rules, work-zone rules, approval policies
├── Business_Goals.md           # Content strategy, Q1 goals, brand voice
└── CLAUDE.md                   # Claude Code operating instructions (all tiers)
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

### Platinum (Two-Agent System)
| Skill | Agent | Description |
|-------|-------|-------------|
| `vault-sync` | Both | Git sync, conflict resolution, signal processing |
| `local-agent` | Local | Approvals, executes sends, merges Dashboard, heartbeat |
| `cloud-odoo` | Cloud | Read-only Odoo queries, write requests via /Pending_Approval |

---

## HITL Approval Workflow

```
Claude (Cloud or Local) identifies action needing approval
                    │
                    ▼
   Creates PENDING_*.md in /Pending_Approval/{domain}/
   (frontmatter: action, agent, priority, draft content)
                    │
              Cloud git push
                    │
              Local git pull
                    │
                    ▼
        Human reviews in Obsidian
                    │
           ┌────────┴────────┐
           │                 │
       Moves to          Moves to
       /Approved         /Rejected
           │                 │
           ▼                 ▼
    Local Agent runs    Logged + archived
    execution cycle     not retried
           │
           ▼
    Sends via MCP → /Done → git push → audit logged
```

**Actions that always require approval:**
- Any outbound email
- All social media posts (including replies, comments)
- All Odoo write operations (create/update)
- File deletion
- Any bulk operation

---

## Platinum Demo (Minimum Passing Gate)

```
Step 1:  Local goes "offline" (Task Scheduler paused)
Step 2:  Test email arrives in Gmail inbox
Step 3:  Cloud Agent detects it via Gmail watcher
Step 4:  Cloud creates /Needs_Action/email/EMAIL_test_{id}.md
Step 5:  Cloud moves to /In_Progress/cloud/ (claim-by-move)
Step 6:  Cloud drafts a professional reply via Claude
Step 7:  Cloud saves to /Pending_Approval/email/REPLY_test_{id}.md
Step 8:  Cloud git push → draft is in GitHub
Step 9:  Local comes back online, runs vault_sync.bat (git pull)
Step 10: Local reads /Pending_Approval — draft is here
Step 11: Human opens Obsidian, reviews draft
Step 12: Human drags file to /Approved/
Step 13: Local Agent detects /Approved file
Step 14: Local sends email via Gmail MCP (send_email)
Step 15: Local logs to /Logs/audit.jsonl
Step 16: Local moves to /Done/DONE_REPLY_test_{id}.md
Step 17: Local git push — completion synced to Cloud
Step 18: Verify: audit log ✓ | /Done has file ✓ | email sent ✓
```

```bash
# Run the demo
python tests/platinum_demo.py --mode cloud --demo-id demo01
python tests/platinum_demo.py --mode local --demo-id demo01
python tests/platinum_demo.py --mode verify --demo-id demo01

# Safe dry-run (no email sent)
python tests/platinum_demo.py --dry-run
```

See `docs/platinum-demo-walkthrough.md` for the screen-by-screen video recording guide.

---

## MCP Servers

### Email MCP (`email-mcp`)

| Tool | Purpose | Approval |
|------|---------|----------|
| `send_email` | Send via Gmail SMTP | Required |
| `draft_email` | Save to `/Drafts` | Auto |
| `search_emails` | Search Gmail inbox | Auto |
| `get_email_logs` | View action logs | Auto |
| `check_smtp_status` | Test SMTP connection | Auto |

### Odoo MCP (`odoo`)

| Tool | Purpose | Approval |
|------|---------|----------|
| `odoo_status` | Verify XML-RPC connection | Auto |
| `search_customers` | Find contacts by name | Auto |
| `get_invoices` | List posted invoices | Auto |
| `get_overdue_invoices` | List past-due invoices | Auto |
| `get_payments` | List recent payments | Auto |
| `get_account_balances` | Chart of accounts snapshot | Auto |

Write operations: **HITL required** (Cloud creates request in /Pending_Approval/accounting/).
Delete: **never exposed.**

### Social Media MCP (`social-media`)

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

Dry-run mode activates automatically when credentials are absent.

---

## Scheduled Tasks

### EC2 Cron (Cloud Agent)

| Schedule | Task |
|----------|------|
| Every 5 min | `vault_sync_cloud.sh` — git pull + push |
| Every 10 min | `cloud_health_monitor.py --once` |
| 2:00 AM daily | `backup.sh` — Odoo pg_dump |
| Sunday 6 PM UTC | CEO briefing data prep |

### Windows Task Scheduler (Local Agent)

| Schedule | Task |
|----------|------|
| Every 10 min | `local_agent.py --once` — full sync + execute cycle |
| Every 10 min | `vault_sync.bat` — git pull + push (independent of agent) |
| Daily 8:00 AM | `scheduler.bat daily` |
| Monday 7:00 AM | `scheduler.bat ceo-briefing` |
| Mon/Wed/Fri 9 AM | `scheduler.bat linkedin` |
| Tue/Thu 10 AM | `scheduler.bat social-batch` |
| Daily 6:00 AM | `scheduler.bat health-check` |
| Sunday 6:00 PM | `scheduler.bat weekly-audit` |

---

## Security Notes

- **Credentials:** Each agent has its own `.env` (gitignored) — secrets never cross via git
- **SCP only:** Gmail OAuth files (`credentials.json`, `token.json`) copied to EC2 via SCP
- **Self-signed TLS:** Odoo on EC2 served over HTTPS (self-signed cert, not in git)
- **App Passwords:** Gmail uses App Passwords, not account passwords
- **HITL hardcoded:** Approval workflow cannot be bypassed programmatically
- **Odoo deletes:** Blocked at the MCP layer — no delete tools exposed
- **Audit trail:** Every action timestamped and component-tagged in `/Logs/audit.jsonl`
- **Claim-by-move:** Atomic filesystem move prevents both agents processing same item

---

## Error Handling

| Severity | Trigger | Auto-action |
|----------|---------|-------------|
| `TRANSIENT` | Timeout, rate limit | Retry 3× (30s/60s/120s backoff) |
| `AUTH` | Invalid/expired credentials | Create URGENT item in `/Needs_Action` |
| `DATA` | Missing field, bad format | Skip item, continue processing |
| `CRITICAL` | Binary missing, data loss risk | Halt + create URGENT item |
| `EXTERNAL` | Third-party API down | Degrade gracefully, continue loop |

Cloud Agent: one task failure never kills the asyncio loop — each task runs inside `handler.catch()`.
Local Agent: one step failure never stops the cycle — each step wrapped independently.

---

## Lessons Learned

### What Worked Well

**Git-as-message-bus was the right Platinum architecture.** Using the GitHub repository as the only communication channel between Cloud and Local agents meant no open ports, no shared secrets between machines, no WebSockets, no queues. The vault files are the API. Git push/pull is the transport. Conflict resolution rules are in plain text.

**Claim-by-move solved the double-processing problem cleanly.** `shutil.move()` on the same filesystem is atomic. The first agent to move a file to `/In_Progress/{agent}/` wins. No locks, no databases, no coordination protocol needed.

**systemd + cron is the right 24/7 stack for EC2.** systemd handles restart-on-crash and boot-time startup. Cron handles periodic tasks with the right frequency per task. The health monitor (`--once` from cron every 10 min) provides a second layer of protection without the complexity of a supervisor process.

**Separating draft from execute reduced risk dramatically.** The Cloud Agent can draft a reply to 100 emails while Local is offline. When Local comes back, the human reviews all drafts in one Obsidian session and approves/rejects each. No emails are sent during the Cloud's unattended operation.

**Vault-as-interface was the right choice from Bronze onwards.** The HITL workflow — drag a file from `/Pending_Approval` to `/Approved` in Obsidian — requires zero custom UI. Every tier inherited this naturally.

### Challenges and How They Were Solved

**Odoo authentication took multiple rounds.** The published `mcp-server-odoo` package used a non-standard endpoint requiring a module not in Community Edition. Diagnosed via stack trace, replaced with custom `odoo_server.py` using standard `/xmlrpc/2/` path. Lesson: `curl` the API path before integrating any package.

**Docker volume / password desync.** After resetting the Odoo DB password in the UI, connections kept failing — the volume retained the original init password. Fixed with `ALTER USER odoo WITH PASSWORD '...'` inside the Postgres container. Lesson: Docker volumes carry state that survives restarts.

**Windows cp1252 encoding.** Unicode characters (`→`, `✓`, emoji) in print statements caused `UnicodeEncodeError` on Windows. Fixed by replacing all unicode symbols with ASCII in console output. Lesson: set `PYTHONIOENCODING=utf-8` in `.env` from day one.

**Health monitor cron pile-up.** The watchdog was written as a continuous loop. Running it from cron every 10 minutes stacked up processes. Fixed by adding `--once` flag — each cron invocation checks, optionally restarts, and exits. Lesson: cron scripts must exit; daemons must be managed by systemd.

**Git conflict on Dashboard.md.** Both agents touching the same file caused merge conflicts. Fixed with the single-writer rule: Cloud writes only to `/Updates/`, Local is the only writer to `Dashboard.md`. Lesson: define ownership boundaries before writing the first line of agent code.

### Architecture Decisions and Trade-offs

**One GitHub repo, not a message queue.** Trade-off: 5–10 minute latency between Cloud push and Local pull vs. zero infrastructure cost, zero auth complexity, full git history of every inter-agent message. For a personal AI Employee, 10 minutes is acceptable.

**asyncio for Cloud Agent, sync loop for Local Agent.** Cloud Agent benefits from concurrent Gmail + Odoo + social tasks running in the same process. Local Agent's tasks are sequential by design (sync → merge → notify → execute) so a simple `time.sleep` loop is cleaner.

**Self-signed TLS for Odoo, not Let's Encrypt.** Trade-off: browser warning on first visit vs. no domain required, no cert renewal cron, no DNS configuration. For internal EC2 use only, self-signed is sufficient.

**Flat markdown files over a database.** State lives in plain files — inspectable in Obsidian, version-controlled in git, zero infrastructure. The JSONL audit log provides enough structure for all metrics.

### What We Would Do Differently

1. **Define agent work-zone rules before writing any agent code.** We added the single-writer rule and claim-by-move after seeing conflicts in testing. These should be the first design decision, not a correction.

2. **Set `PYTHONIOENCODING=utf-8` and `AGENT_ROLE` in `.env.example` from day one** so both issues surface immediately in local testing.

3. **Write `AuditLogger` before any other component.** Retrofitting structured logging into existing watchers and the orchestrator was tedious. Starting with logging infrastructure makes every subsequent component's behaviour visible from the first run.

4. **Add `--once` flag to all long-running scripts at the time of writing**, not when cron integration surfaces the pile-up problem.

5. **SCP the Gmail credentials on day one of the Cloud setup**, not as an afterthought. The Cloud Agent silently does nothing useful until `credentials.json` and `token.json` are present.

---

## License

MIT
