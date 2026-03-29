# Gold Tier AI Employee — Architecture

> **Tier:** Gold | **Built with:** AI-Driven Development (AIDD) via Claude Code CLI
> **Business:** NovaMind Tech Solutions (AI consulting, South Asian SMEs)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Data Flow](#2-data-flow)
3. [Component Descriptions](#3-component-descriptions)
4. [Security Model](#4-security-model)
5. [Lessons Learned](#5-lessons-learned)

---

## 1. System Overview

The Gold Tier AI Employee is a fully autonomous personal business assistant built
around a **file-based communication pattern**: every piece of work — an email, a
financial record, a social media post — becomes a Markdown file that flows through
a set of clearly named folders. Claude Code acts as the reasoning engine, reading
those files and deciding what to do next.

### Component Diagram

```
 External World                 Vault Core                       External APIs
 ──────────────                 ──────────                       ─────────────

  Gmail Inbox  ──[OAuth]──► Gmail Watcher ──► /Inbox
                                                │
  ~/AI_Drop   ──[watchdog]─► File Watcher ──►  │
                                                ▼
                                         /Needs_Action  ◄── Orchestrator (polls 30s)
                                                │                    │
                                                │              [claude --print]
                                                ▼                    │
                                          Claude Code  ◄─────────────┘
                                          (reasoning)
                                                │
                              ┌─────────────────┼─────────────────┐
                              ▼                 ▼                 ▼
                         /Pending_Approval  /Plans            /Done
                              │
                         Human Review
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                /Approved           /Rejected
                    │
              Orchestrator
              detects file
                    │
        ┌───────────┼──────────────┐
        ▼           ▼              ▼
   email-mcp    odoo MCP    social-media MCP
        │           │              │
        ▼           ▼              ▼
    Gmail SMTP  Odoo 19        FB / IG / X
                localhost:     Graph API /
                8069           Tweepy

 ─────────────────────────────────────────────────────────────────

  Scheduler (Windows Task Scheduler / cron)
     │
     └─► scripts/scheduler.bat {daily,odoo-sync,ceo-briefing,...}
              └─► claude --print "task prompt"

  Audit Trail
     └─► /Logs/audit.jsonl   (all actions)
     └─► /Logs/errors.jsonl  (errors only)
```

### Key Design Principle: Files as Messages

Every inter-component communication is a Markdown file. This design choice means:
- **Human-readable** at every step — open any folder in Obsidian and see exactly what is happening
- **HITL by default** — sensitive actions physically move through `/Pending_Approval` before execution
- **Restartable** — the orchestrator tracks processed filenames in `memory/orchestrator_state.json`; nothing is lost on restart
- **No message broker required** — the filesystem is the queue

---

## 2. Data Flow

### 2.1 Inbound Email Path

```
Gmail API (is:unread is:important)
    │
    ▼
GmailWatcher.check_for_updates()         [polls every 120s]
    │  - OAuth 2.0 via config/token.json
    │  - De-duplication via memory/gmail_processed_ids.json
    │  - Priority classification: critical/high/medium/low
    ▼
/Needs_Action/EMAIL_{subject}_{ts}.md    [YAML frontmatter + body]
    │
    ▼
Orchestrator detects new .md file        [polls every 30s]
    │
    ▼
claude --print "Process Needs_Action/EMAIL_...md"
    │  - Reads file, classifies priority using Company_Handbook.md keywords
    │  - Queries Odoo if sender matches a customer contact
    │  - Creates /Plans/PLAN_*.md for multi-step responses
    │  - Drafts reply → /Drafts/DRAFT_*.md
    │  - Creates /Pending_Approval/PENDING_email_*.md  [HITL gate]
    ▼
Human moves to /Approved
    │
    ▼
Orchestrator detects approved file
    │
    ▼
claude --print "Execute approved email send"
    │  - Uses email-mcp → send_email()
    │  - Logs to audit.jsonl
    ▼
/Done/DONE_EMAIL_*.md + /Done/DONE_PENDING_*.md
```

### 2.2 File Drop Path

```
~/AI_Drop/ (any file: PDF, DOCX, XLSX, image...)
    │
    ▼
FileSystemWatcher (watchdog inotify/FSEvents)
    │  - Triggers on FileCreatedEvent
    │  - Ignores hidden files (. and ~ prefix)
    │  - Classifies by extension
    ▼
/Needs_Action/FILE_{name}_{ts}.md        [with suggested actions checklist]
    │
    ▼
Orchestrator → Claude processes (same as email path above)
```

### 2.3 Odoo Accounting Sync Path

```
scripts/scheduler.bat odoo-sync          [daily 7:00 AM]
    │
    ▼
claude --print "Sync Odoo data..."
    │
    ▼
odoo MCP calls (read-only, auto-approved):
    get_invoices()       → account.move (out_invoice, posted)
    get_payments()       → account.payment (inbound, posted)
    get_overdue_invoices() → overdue filter + date check
    get_account_balances() → account.account (all active, Odoo 19)
    │
    ▼
/Accounting/Current_Month.md             [updated in-place]
    │
    ▼
Dashboard.md Gold Tier Accounting Summary updated
    │
    ▼
audit.jsonl: action=odoo_sync
```

If any overdue invoice is > 14 days past due:
```
    ▼
/Needs_Action/FINANCE_overdue_{client}_{ts}.md   [flags for CEO attention]
```

### 2.4 Social Media Post Path

```
scripts/scheduler.bat social-batch       [Tue/Thu 10:00 AM]
    │
    ▼
claude --print "Generate social media batch..."
    │  - Reads Business_Goals.md for content strategy
    │  - Reads Company_Handbook.md for brand voice rules
    ▼
/Pending_Approval/PENDING_{platform}_{ts}.md     [one per platform]
    │
Human reviews, moves to /Approved
    │
    ▼
Orchestrator detects approved file
    │
    ▼
claude --print "Post approved content to {platform}"
    │  - LinkedIn: scripts/linkedin_poster.py (Playwright)
    │  - Facebook/Instagram: social-media MCP → Graph API
    │  - Twitter/X: social-media MCP → Tweepy
    ▼
/Social_Media/{Platform}/POST_{ts}.json          [publish record]
    │
    ▼
Orchestrator scan_folder_recursive() detects new .json → processes
audit.jsonl: action=social_post_record_processed
```

### 2.5 CEO Briefing Path

```
scripts/scheduler.bat ceo-briefing       [Monday 7:00 AM]
    │
    ▼
claude --print "Generate CEO Briefing..." (uses ceo-briefing skill)
    │
    ├─► get_invoices() + get_overdue_invoices() + get_payments()  [Odoo MCP]
    ├─► Read /Accounting/Current_Month.md
    ├─► Count /Done (completed this week), /Needs_Action (pending)
    ├─► Read /Logs/audit.jsonl  (email/social activity)
    ├─► Read /Logs/errors.jsonl (system health)
    └─► generate_social_summary()  [social-media MCP]
    │
    ▼
/Briefings/CEO_Briefing_{YYYY-MM-DD}.md
    │
    ▼
Dashboard.md CEO Briefings section updated
audit.jsonl: action=ceo_briefing_generated
```

---

## 3. Component Descriptions

### 3.1 Gmail Watcher (`watchers/gmail_watcher.py`)

| Property | Value |
|----------|-------|
| Language | Python 3.12 |
| Auth | OAuth 2.0 — `config/credentials.json` + `config/token.json` |
| Poll interval | 120 seconds (configurable via `--interval`) |
| Gmail query | `is:unread is:important` (max 20 per poll) |
| De-duplication | `memory/gmail_processed_ids.json` (persists across restarts) |
| Output | `/Needs_Action/EMAIL_{subject}_{ts}.md` |

The watcher classifies each email into `critical / high / medium / low` by scanning
subject + body snippet against keyword lists defined at the top of the file.
It logs both the individual email detection (`email_received`) and each poll cycle
(`gmail_check`) to `audit.jsonl`, making it easy to see exactly when each message
was first seen.

Token refresh is handled automatically — if the OAuth token expires, `creds.refresh()`
is called silently. If refresh fails, a `FileNotFoundError` is raised and the watcher
falls back to re-running the OAuth consent flow.

### 3.2 Filesystem Watcher (`watchers/filesystem_watcher.py`)

| Property | Value |
|----------|-------|
| Language | Python 3.12 |
| Library | `watchdog` (cross-platform inotify/FSEvents/ReadDirectoryChangesW) |
| Watch path | `~/AI_Drop` (default, configurable via `--watch-path`) |
| Event type | `FileCreatedEvent` only (ignores directories, `.` and `~` prefixed files) |
| Output | `/Needs_Action/FILE_{name}_{ts}.md` |

The watcher uses a `Queue` to buffer events from the watchdog thread and drains
it on a 1-second tick in the main loop. Each created action file includes YAML
frontmatter (type, original path, size, detected timestamp) plus a suggested
actions checklist tailored to the file extension (PDF → extract info; Excel →
review data; Image → determine context; etc.).

Both `file_detected` and `action_file_created` are logged to `audit.jsonl` with
the duration in milliseconds.

### 3.3 Obsidian Vault (folder structure)

The vault is the central nervous system. Every folder has a single, well-defined
purpose:

| Folder | Owner | Contents |
|--------|-------|----------|
| `/Inbox` | Watcher input | Raw drops not yet moved to Needs_Action |
| `/Needs_Action` | Watchers write, Orchestrator reads | Pending items for Claude to process |
| `/Plans` | Claude writes | `PLAN_*.md` for multi-step tasks |
| `/Drafts` | Claude writes | Email/content drafts before approval |
| `/Pending_Approval` | Claude writes, Human moves | HITL gate for sensitive actions |
| `/Approved` | Human moves, Orchestrator reads | Cleared for execution |
| `/Rejected` | Human moves | Logged, never re-executed |
| `/Done` | Claude writes | Completed items with `DONE_` prefix |
| `/Accounting` | Odoo sync writes | `Current_Month.md` — financial snapshot |
| `/Briefings` | CEO Briefing writes | `CEO_Briefing_{date}.md` weekly reports |
| `/Social_Media` | Social MCP writes | `{Platform}/POST_{ts}.json` publish records |
| `/Logs` | All components append | `audit.jsonl`, `errors.jsonl` |
| `/Plans` | Claude writes | Multi-step execution plans |
| `memory/` | Orchestrator, Watchers | State files, processed ID lists, scheduler logs |

File naming follows a strict convention enforced by all components:
- **Needs_Action:** `TYPE_description_YYYYMMDD_HHMMSS.md`
- **Done:** `DONE_TYPE_description_YYYYMMDD_HHMMSS.md`
- **Pending:** `PENDING_type_description_YYYYMMDD_HHMMSS.md`

### 3.4 Claude Code (reasoning engine)

Claude Code is invoked in two modes:

**Interactive session** — the human types commands or skill shortcuts (`/ceo-briefing`,
`/ralph-loop`, etc.). Claude has full access to the vault via MCP tools and direct
file reads.

**Subprocess mode** — the orchestrator and scheduler call:
```bash
claude --print "task prompt"
```
with `cwd` set to the vault root and a 300-second timeout. The orchestrator wraps
this in `ErrorHandler.retry_with_backoff()` with 2 retries and a 10-second base
delay.

Agent skills (`.claude/skills/*/SKILL.md`) provide structured instructions that
Claude reads before acting. Each skill defines: what it does, when to use it,
step-by-step execution, and quality rules. This means the AI's behavior for recurring
tasks is version-controlled and auditable.

### 3.5 MCP Servers

Three custom FastMCP servers expose external integrations as tools:

#### Email MCP (`mcp_servers/email_server.py`)

| Tool | Approval | Transport |
|------|----------|-----------|
| `send_email` | **HITL required** | Gmail SMTP (App Password + TLS) |
| `draft_email` | Auto | Saves to `/Drafts` locally |
| `search_emails` | Auto | Gmail API (read-only) |
| `get_email_logs` | Auto | Reads `/Logs/audit.jsonl` |
| `check_smtp_status` | Auto | TCP socket check to SMTP host:port |

#### Odoo MCP (`mcp_servers/odoo_server.py`)

Connects to Odoo 19 Community via standard XML-RPC (`/xmlrpc/2/common` + `/xmlrpc/2/object`).
All tools are read-only and auto-approved. Write operations require HITL and are
initiated via approval files rather than direct MCP calls.

| Tool | Model queried |
|------|--------------|
| `odoo_status` | `common.version()` + `authenticate()` |
| `search_customers` | `res.partner` |
| `get_invoices` | `account.move` (out_invoice) |
| `get_overdue_invoices` | `account.move` with date + payment_state filter |
| `get_payments` | `account.payment` (inbound, posted) |
| `get_account_balances` | `account.account` — **empty domain** (Odoo 19 removed `deprecated` field) |

> **Bug encountered and fixed:** Odoo 19 removed the `deprecated` field from
> `account.account`. The original query used `[["deprecated","=",False]]`, which
> raised `ValueError: Invalid field account.account.deprecated`. Fixed to `[]`.

#### Social Media MCP (`mcp_servers/social_media_server.py`)

Covers Facebook Graph API, Instagram Basic Display API, and Twitter/X via Tweepy.
**Dry-run mode activates automatically** when credentials are absent (safe for demos
without live tokens). Dry-run responses are marked `_(demo)_` in all outputs.

| Tool | Approval | Notes |
|------|----------|-------|
| `post_to_facebook` | **HITL required** | Graph API page post |
| `post_to_instagram` | **HITL required** | Media container + publish flow |
| `post_to_twitter` | **HITL required** | Tweepy v2 |
| `get_*_posts` | Auto | Read cached records from `/Social_Media/` |
| `generate_social_summary` | Auto | 7-day engagement rollup |
| `social_media_status` | Auto | Env var presence check |

### 3.6 HITL Layer (Human-in-the-Loop)

The approval workflow is the system's primary safety mechanism. It is enforced at
the **filesystem level** — Claude cannot execute a sensitive action until a file
physically exists in `/Approved`.

```
Claude creates:  /Pending_Approval/PENDING_{type}_{ts}.md
                   (YAML frontmatter: action, target, priority, approval_required: true)

Human decides:
  → Move to /Approved   → Orchestrator detects, Claude executes
  → Move to /Rejected   → Orchestrator logs, never retried

Actions requiring HITL (non-exhaustive):
  email_send     — any outbound email
  social_post    — any platform post, including replies
  odoo_write     — create/update any Odoo record
  file_delete    — deletion of any vault file

Actions never allowed (even with approval):
  odoo_delete    — Odoo record deletion is blocked at the MCP layer
  bulk_email     — sending to more than one recipient in a loop
```

The orchestrator reads the `action` field from frontmatter to route approved files
to the correct Claude prompt template (`email_send`, `social_post`, `odoo_write`,
`file_delete`, or a generic handler for unknown types).

### 3.7 Ralph Wiggum (autonomous loop)

Ralph Wiggum is a **stop-hook pattern** that keeps Claude iterating on a long-running
task until a completion promise is output.

```
/ralph-loop "task prompt" --max-iterations N --completion-promise "TOKEN"
```

**Components:**
- `.claude/commands/ralph-loop.md` — slash command definition and usage docs
- `.claude/hooks/ralph_stop_check.py` — the Stop hook registered in `settings.json`
- `.claude/settings.json` — registers the hook: `"Stop": [{"hooks": [{"type": "command", "command": "python .claude/hooks/ralph_stop_check.py"}]}]`
- `.claude/hooks/ralph_state.json` — runtime state (active, task, promise, iteration count)

**Execution flow:**
1. `/ralph-loop` writes `ralph_state.json` (active=true, iteration=1)
2. Claude executes the task in the current conversation
3. When Claude tries to stop, `ralph_stop_check.py` runs (via the Stop hook):
   - Scans the session transcript for `<promise>TOKEN</promise>`
   - **Found:** clears state, exits 0 (stop allowed) — loop complete
   - **Not found + iter < max:** increments iteration, prints re-inject prompt, exits 1 (stop blocked)
   - **Max iterations reached:** clears state, exits 0 (safety valve)
4. The re-inject prompt is written to stdout and Claude Code feeds it back into the conversation

**Safety rules enforced in the skill:**
- Always set `--max-iterations` (no unbounded loops)
- Never include payment, deletion, or bulk-send actions in a loop
- Cancel by deleting `ralph_state.json`

### 3.8 Error Handler (`utils/error_handler.py`)

Five-severity taxonomy with distinct responses per class:

| Severity | Trigger | Auto action |
|----------|---------|-------------|
| `TRANSIENT` | Timeout, rate limit (429) | `retry_with_backoff()` — 3× at 30s/60s/120s |
| `AUTH` | HTTP 401/403, Odoo auth failure | Log + create `URGENT_ERROR_*.md` in `/Needs_Action` |
| `DATA` | Malformed file, missing field | Log + skip item, continue loop |
| `CRITICAL` | Data loss risk, claude binary missing | Log + halt + create `URGENT_ERROR_*.md` |
| `EXTERNAL` | Third-party API down | Log + skip integration, continue others |

The `handler.catch(component, severity)` context manager suppresses exceptions so
a single component failure never crashes the orchestrator loop:

```python
with handler.catch("odoo_sync", ErrorSeverity.EXTERNAL):
    sync_odoo_data()
# execution always continues here
```

`AUTH` and `CRITICAL` errors also auto-create a human-readable `URGENT_ERROR_*.md`
in `/Needs_Action` with a recovery checklist specific to the error type. The
orchestrator picks this up on its next poll, and `log_recovery()` closes the loop
once the human resolves it.

### 3.9 Audit Logger (`utils/audit_logger.py`)

Every significant action in the system appends a JSON line to `/Logs/audit.jsonl`.
The schema is fixed across all components:

```jsonc
{
  "ts":               "2026-03-12T10:05:00.000000",  // ISO 8601, always UTC-like
  "action":           "odoo_sync",                   // verb_noun vocabulary
  "component":        "odoo_accounting_test",         // which file/class
  "actor":            "claude",                       // "claude" or "human"
  "target":           "Accounting/Current_Month.md",  // file or URL
  "details":          { ... },                        // free-form context
  "status":           "success",                      // success|failure|pending|skipped
  "duration_ms":      55,
  "approval_required": false,
  "approval_status":  ""                              // pending|approved|rejected
}
```

`/Logs/errors.jsonl` is a parallel file written only by `ErrorHandler`, with
additional fields `severity`, `error_type`, `message`, and `resolved: false`.

Both files are append-only JSONL — one JSON object per line, no commas between
entries. This makes them trivially parseable with any line-by-line tool (`jq`,
Python `json.loads(line)`, etc.) and safe for concurrent writes from multiple
processes.

The `AuditLogger` class auto-detects the vault root from `Path(__file__).parent.parent`
so any component that imports it gets the correct log path without configuration.

### 3.10 Scheduler (`scripts/scheduler.bat`)

The scheduler is a Windows batch file that dispatches named commands to `claude --print`:

| Command | Schedule | Purpose |
|---------|----------|---------|
| `daily` | 8:00 AM daily | Morning Needs_Action check + Odoo sync |
| `odoo-sync` | 7:00 AM daily | Sync Odoo → `Current_Month.md` |
| `linkedin` | 9:00 AM Mon/Wed/Fri | Generate LinkedIn draft |
| `social-batch` | 10:00 AM Tue/Thu | Generate FB + IG + 2× Twitter drafts |
| `ceo-briefing` | 7:00 AM Monday | Full weekly business audit |
| `weekly-audit` | 6:00 PM Sunday | `/Briefings/WEEKLY_AUDIT_*.md` |
| `health-check` | 6:00 AM daily | MCP + error count check |
| `check-approvals` | 9/1/5 PM weekdays | Review pending approvals |
| `email-check` | On demand | One-shot Gmail poll |
| `status` | On demand | Print folder counts |

The script auto-detects the vault path via `for %%I in ("%SCRIPT_DIR%..") do` —
no hardcoded paths. All runs are logged to `memory/scheduler_logs/scheduler_{ts}.log`.

Linux/macOS equivalent: `scripts/scheduler.sh` with identical command interface,
deployable via standard `cron` or `launchd`.

Task Scheduler setup is documented in `docs/windows-scheduler-setup.md` with a
PowerShell one-shot block that creates all 7 recurring tasks.

### 3.11 Orchestrator (`orchestrator.py`)

The orchestrator is the Gold tier's central coordinator — a continuous Python
process that polls three folders and dispatches Claude subprocess calls.

| Parameter | Default | CLI flag |
|-----------|---------|----------|
| Poll interval | 30s | `--interval` |
| Health check | 300s | `--health-check-interval` |
| Dry run | false | `--dry-run` |
| One-shot mode | false | `--once` |

**State persistence** (`memory/orchestrator_state.json`):
- Tracks processed filenames per folder (last 500 retained per list)
- Records `last_run`, `last_health_check`, cumulative stats
- Survives restarts without reprocessing already-handled files

**Health check** (pure Python, no Claude subprocess):
1. Odoo: `xmlrpc.client.ServerProxy.version()` call
2. SMTP: `socket.create_connection(smtp_host, smtp_port, timeout=5)`
3. Social media: checks env var presence (`FB_PAGE_ACCESS_TOKEN`, `IG_USER_ID`, `TWITTER_API_KEY`)
4. Claude binary: `subprocess.run(["claude", "--version"])`
5. Error count: reads `errors.jsonl`, counts entries with `ts >= now - 86400`

The result updates the `## System Health` section in `Dashboard.md` via `re.sub()`
and is logged to `audit.jsonl`.

---

## 4. Security Model

### 4.1 Credential isolation

All secrets live in `.env` at the vault root. This file is in `.gitignore` and
never referenced in vault Markdown files.

```
.env (never committed)
├── ODOO_URL, ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD
├── SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_APP_PASSWORD
├── FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID
├── IG_USER_ID, IG_ACCESS_TOKEN
├── TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
└── SOCIAL_DRY_RUN=true   (safe default — must explicitly set to false for live posts)
```

MCP servers load `.env` at startup via `python-dotenv`. The orchestrator has a
fallback `_load_dotenv()` parser that works without the package installed.

### 4.2 HITL enforcement

The table below summarises which operations are auto-approved vs. human-gated:

| Operation | Approval | Enforcement |
|-----------|----------|-------------|
| Read any Odoo record | Auto | MCP tool design (read-only tools only) |
| Read/search Gmail | Auto | Gmail API `readonly` scope |
| Read social media posts | Auto | GET only in social MCP |
| Sync accounting to vault | Auto | File write to `/Accounting/` only |
| Send email | **HITL** | `/Pending_Approval` gate + orchestrator check |
| Post to any social platform | **HITL** | `/Pending_Approval` gate + orchestrator check |
| Create/update Odoo record | **HITL** | `/Pending_Approval` gate; no write MCP tools exposed |
| Delete Odoo record | **Blocked** | No delete tool exists in `odoo_server.py` |
| Delete vault files | **HITL** | `file_delete` action type requires approval |
| Bulk email (loop) | **Blocked** | Explicitly prohibited in CLAUDE.md and skill rules |

### 4.3 Odoo write protection

`mcp_servers/odoo_server.py` exposes **only read tools**. There is no `create_invoice`,
`update_record`, or `delete_*` tool. Write operations are handled by Claude generating
an approval file, which after human review causes the orchestrator to call Claude
again with the approved data. This two-pass approach means Claude never writes to
Odoo in a single unreviewed step.

Delete operations are not implemented anywhere in the codebase. The MCP layer
cannot be asked to delete Odoo records — it simply has no such tool.

### 4.4 Audit trail

Every action — including human approvals, errors, recoveries, and health checks —
produces a structured entry in `/Logs/audit.jsonl`. The `actor` field distinguishes
`"claude"` from `"human"` actions. `approval_required` and `approval_status` fields
track the HITL state of every sensitive operation.

This gives a complete, tamper-evident record of:
- What the AI decided to do and when
- What the human approved or rejected
- Which external systems were contacted
- What errors occurred and when they were resolved

---

## 5. Lessons Learned

### 5.1 The file-based communication pattern is more powerful than it looks

The decision to route everything through Markdown files in named folders initially
felt like a workaround — a poor man's message queue. In practice it turned out to
be the system's strongest feature. Because every work item is a file, the human can
see the entire state of the system by opening the vault in Obsidian. Folders act as
visual queues. The HITL workflow is just "drag a file from one folder to another" —
no special UI, no dashboard login, no API call. This simplicity made the approval
workflow the easiest part of the system to explain and demo.

The tradeoff is that the system has no atomic transactions. If Claude crashes mid-file-write,
the partial file lands in `/Needs_Action` and the orchestrator may try to process it.
Mitigated by the orchestrator's state file (so reprocessing is idempotent) and by
always writing files completely before the orchestrator can see them.

### 5.2 AIDD (AI-Driven Development) dramatically changes the shape of iteration

Building with Claude Code means your bottleneck is no longer typing — it's thinking
clearly enough to describe what you want. Prompts that were ambiguous produced
surprising results; prompts with concrete acceptance criteria produced correct code
on the first or second try. The most productive pattern was: read the spec, write
the test description first, then ask Claude to write the implementation that would
pass it.

The unexpected consequence: you write far more documentation than you would in
traditional development, because documentation is how you communicate with the AI.
`CLAUDE.md`, `Company_Handbook.md`, and the skills in `.claude/skills/` are
simultaneously developer docs, AI instructions, and runtime prompts. They collapse
three normally separate artifacts into one.

### 5.3 MCP servers require careful boundary design

The first instinct when building the Odoo MCP was to expose every XML-RPC method —
create, read, update, delete, search. Resisting that instinct and exposing only read
tools was one of the best architectural decisions in the project. It made the HITL
workflow mandatory rather than optional, it made the error surface smaller, and it
made it impossible for a misguided Claude prompt to accidentally corrupt financial
records.

The practical challenge with MCP servers is the lack of real-time feedback during
development. Unlike a REST API where you can `curl` an endpoint, MCP tools are
invoked through Claude's tool-use interface. The fastest debugging workflow was to
extract the XML-RPC logic into a standalone Python script, verify it there, then
wrap it in the MCP tool decorator.

### 5.4 Odoo version drift is a real maintenance burden

Odoo makes breaking changes to its model fields between minor versions. The `deprecated`
field on `account.account` was removed in Odoo 19 — a change with no obvious migration
guide. The error message (`ValueError: Invalid field account.account.deprecated`) was
clear enough, but tracking down which version introduced the removal required reading
Odoo commit history. Any system that integrates with self-hosted Odoo needs a test
against the live instance as part of every deployment.

The fix was trivial (change the domain to `[]`) but finding it required understanding
the Odoo ORM domain syntax, the XML-RPC `search_read` call, and the Odoo 19 changelog.
The lesson: pin your Odoo Docker image version and treat any `docker pull` as a
potentially breaking change.

### 5.5 Exponential backoff timing matters in demos vs. production

`utils/error_handler.py` implements `30s → 60s → 120s` retry delays — correct for
production where you don't want to hammer a rate-limited API. But those delays make
integration tests painfully slow. The solution used throughout this project was to
pass `base_delay=1` in test contexts, making the 3-retry sequence complete in under
4 seconds. This should be a named constant (`TEST_BASE_DELAY`) rather than an
argument, to prevent accidentally shipping 1-second delays in production code.

### 5.6 The orchestrator's state file is not a database

`memory/orchestrator_state.json` tracks processed filenames with a 500-entry rolling
window per folder. This works fine for a single-user personal assistant. In a team
context, two orchestrator instances would both process the same file and produce
duplicate actions. The file-based queue model would need to be replaced with an
actual database or a locking mechanism (e.g., rename the file while processing,
rename back on failure) to scale beyond one process.

### 5.7 Ralph Wiggum's stop-hook pattern is elegant but fragile at the edges

The stop-hook approach — intercept Claude's exit, check for a promise string,
re-inject if not found — is architecturally clean and requires no external
dependencies. However, it depends on Claude consistently outputting the exact promise
string `<promise>TOKEN</promise>` when it considers the task complete. If Claude
paraphrases it, wraps it in code fences, or outputs it mid-sentence rather than on
its own line, the hook's string search misses it.

The robustness fix is to use a regex pattern (`<promise>\s*TOKEN\s*</promise>`) rather
than an exact substring search, and to document in the skill that the promise must
appear on its own line. The current implementation uses a simple `in` check for
clarity, which works well in practice because Claude reliably follows the instruction.

### 5.8 Gmail OAuth in a server context has a hidden bootstrap problem

The Gmail watcher uses OAuth 2.0 with `InstalledAppFlow`, which requires a browser
to complete the consent flow on first run. On a headless server (or a VM without a
browser), this silently fails. The solution used here is to complete the OAuth flow
once on a machine with a browser, save the resulting `config/token.json`, and copy
it to the server. The token refreshes automatically thereafter and typically lasts
months between manual interventions.

The lesson is that any OAuth integration needs a documented one-time bootstrap
procedure. In this project, that lives in `docs/` as a step-by-step guide with
screenshots.

### 5.9 Dashboard.md as the single pane of glass is genuinely useful

Having all system state reflected in one Markdown file that updates automatically
proved more valuable than expected. During development, `Dashboard.md` was the
first thing checked after running any operation — not log files, not Odoo. The
`## System Health` section in particular (auto-updated by the health check) made
diagnosing problems fast: a `FAIL — AUTH` row immediately pointed to the specific
component without needing to grep logs.

The limitation is that `Dashboard.md` is updated by regex replacement (`re.sub`)
which can corrupt the file if the section header format is inconsistent. A more
robust approach would be to regenerate the entire file from a template rather than
doing in-place section replacement.

### 5.10 Agent skills as version-controlled prompt engineering

The decision to put every recurring task's instructions into `.claude/skills/*/SKILL.md`
rather than inline in Python strings turned out to be the right call. When the CEO
briefing output was too terse, updating the skill file to add "Be specific — use
actual numbers from the data" immediately changed the output quality in every future
run without touching any Python code. The skills are effectively a configuration
layer sitting above the code — modifiable by the business owner without needing
to understand the implementation.

The risk is skill drift — if the codebase evolves but the skills aren't updated,
Claude follows outdated instructions. This is mitigated by referencing specific
file paths and folder names in skills (so a renamed folder breaks the skill visibly
rather than silently producing wrong output).

---

*Document generated: 2026-03-12 | Vault version: Gold Tier | Claude Code CLI*
