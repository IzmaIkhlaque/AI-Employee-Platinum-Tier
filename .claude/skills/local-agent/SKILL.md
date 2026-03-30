---
name: local-agent
description: Local agent operations for Platinum tier. Handles approvals, executes sends, merges Dashboard updates, manages vault sync. Local agent is the ONLY agent that can execute external actions.
version: 1.0.0
---

# Local Agent Skill

The Local Agent runs on the user's Windows PC and is the **sole executor** of
external actions. Cloud drafts everything; Local executes.

---

## What Only the Local Agent Can Do

| Action | Tool / Method |
|--------|---------------|
| Send email | `email-mcp` → `send_email` |
| Post to social media | `social-media` MCP or `scripts/linkedin_poster.py` |
| Write to Odoo | `odoo` MCP write tools |
| Update Dashboard.md | Direct file write (single-writer rule) |
| Move files to /Approved or /Rejected | Human decision, then Local executes |
| Access WhatsApp session | Local session only |

---

## Sync-Then-Act Cycle

Every cycle (default 10 minutes):

```
1. git pull  — get Cloud drafts
2. Merge /Updates → Dashboard.md
3. Check /Signals/cloud_heartbeat.md
4. Write /Signals/REVIEW_NEEDED_*.md  if pending approvals exist
5. Execute files in /Approved
6. Claim unclaimed /Needs_Action items → /In_Progress/local/
7. git push  — share completed work
```

---

## Merging /Updates into Dashboard.md

Cloud writes status files to `/Updates/`. Local is the only writer to `Dashboard.md`.

**odoo_sync update** → replace `## Cloud Agent Status` section
**Generic update** → append one row to `## Recent Activity`

After merging: move update file to `/Done/DONE_{filename}`.

---

## Claim-by-Move Rule

Before processing any `/Needs_Action` item:

1. Check `/In_Progress/cloud/` — if item is there, **SKIP** (Cloud owns it)
2. Move item to `/In_Progress/local/` — Local now owns it
3. Process item (draft plan, route to `/Pending_Approval`, or resolve to `/Done`)

Race condition handling: `shutil.move` is atomic on same filesystem.
If Cloud claimed it first, the move will fail — catch the error and skip.

---

## Executing Approved Actions

For each file in `/Approved`:

1. Read frontmatter to determine `action` type
2. Route to the correct executor:

| `action` value | Executor |
|----------------|----------|
| `email_reply` | `email-mcp` → `send_email` |
| `social_post` | `social-media` MCP or `linkedin_poster.py` |
| `odoo_write` | `odoo` MCP write tool |
| `file_delete` | Python `Path.unlink()` |
| anything else | Ask Claude to interpret and execute |

3. On success: move to `/Done/DONE_{filename}`
4. On failure: log to `/Logs/errors.jsonl`, keep file in `/Approved` for retry

---

## Heartbeat Monitoring

| Heartbeat age | Action |
|---------------|--------|
| < 15 min | OK — log and continue |
| 15–60 min | Log WARNING to audit.jsonl |
| > 60 min | Create `URGENT_cloud_heartbeat_dead_*.md` in `/Needs_Action` and `/Signals` |

Heartbeat file: `/Signals/cloud_heartbeat.md` (written by Cloud every 5 min)

---

## Running the Local Agent

```bash
# Continuous mode (recommended — add to Windows Task Scheduler)
python local/local_agent.py

# Single cycle (for testing)
python local/local_agent.py --once

# Custom interval
python local/local_agent.py --interval 300

# Dry run (no writes, no sends)
python local/local_agent.py --dry-run --once
```

---

## Windows Task Scheduler Setup

1. Open Task Scheduler → Create Task
2. **General:** Name: `AI Employee Local Agent`, Run whether user is logged on or not
3. **Trigger:** At startup, repeat every 10 minutes indefinitely
4. **Action:** Program: `python`, Arguments: `local/local_agent.py`
   Start in: `D:\Izma folder\...\AI_Employee_Vault`
5. **Settings:** If already running, do not start a new instance

---

## Safety Rules

```
NEVER send email without an /Approved file
NEVER post to social media without an /Approved file
NEVER write to Odoo without an /Approved file
ALWAYS update Dashboard.md after any executed action
ALWAYS move completed /Approved files to /Done
NEVER process items in /In_Progress/cloud/
```
