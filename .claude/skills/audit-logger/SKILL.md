---
name: audit-logger
description: Comprehensive audit trail for all AI Employee actions. Records every significant event — file detections, email processing, approvals, social posts, Odoo syncs — to /Logs/audit.jsonl. Use when implementing new watchers, scripts, or MCP tools.
version: 1.0.0
---

# Audit Logger Skill

Provides a structured, queryable audit trail of every action the AI Employee takes.
Every component writes to `/Logs/audit.jsonl` using the shared `AuditLogger` utility.

**Python utility:** `utils/audit_logger.py` — importable by all watchers, scripts, and MCP servers.

---

## Log File Location

| File | Purpose |
|------|---------|
| `/Logs/audit.jsonl` | All successful and failed actions |
| `/Logs/errors.jsonl` | Error-specific entries (written by `ErrorHandler`) |

Both are JSONL — one JSON object per line, append-only, never overwritten.

---

## Standard Log Entry Fields

Every entry written by `AuditLogger.log()` contains:

```json
{
  "ts":               "2026-03-02T08:00:00.123456",
  "action":           "email_received",
  "component":        "gmail_watcher",
  "actor":            "claude",
  "target":           "EMAIL_invoice_request_20260302_080000.md",
  "details":          {"from": "client@example.com", "priority": "high"},
  "status":           "success",
  "duration_ms":      142,
  "approval_required": false,
  "approval_status":  ""
}
```

| Field | Type | Description |
|-------|------|-------------|
| `ts` | ISO-8601 | UTC timestamp of the event |
| `action` | string | What happened (see Action Vocabulary below) |
| `component` | string | Which system component performed the action |
| `actor` | string | `"claude"` for AI actions, `"human"` for manual steps |
| `target` | string | File, email ID, post ID, or record affected |
| `details` | object | Action-specific context (varies per action) |
| `status` | string | `"success"`, `"failure"`, `"skipped"`, `"pending"` |
| `duration_ms` | int | Time taken in milliseconds (0 if not measured) |
| `approval_required` | bool | Whether HITL approval was needed |
| `approval_status` | string | `"approved"`, `"rejected"`, `""` (if not applicable) |

---

## Action Vocabulary

Use these exact action strings for consistency across all components.

### File Operations
| Action | Component | Meaning |
|--------|-----------|---------|
| `file_detected` | filesystem_watcher | New file dropped into watch folder |
| `action_file_created` | filesystem_watcher / gmail_watcher | Created FILE_*.md or EMAIL_*.md in /Needs_Action |
| `file_processed` | orchestrator | Claude processed a /Needs_Action item |
| `file_moved_to_done` | orchestrator / file-processing | Item moved to /Done |
| `file_skipped` | any | Item skipped due to DATA error or already processed |

### Email Operations
| Action | Component | Meaning |
|--------|-----------|---------|
| `gmail_check` | gmail_watcher | Completed a Gmail API poll (even if 0 results) |
| `email_received` | gmail_watcher | New qualifying email detected |
| `email_draft_created` | email-actions | Draft saved to /Drafts |
| `email_send_requested` | email-actions | Approval request created in /Pending_Approval |
| `send_success` | email-actions | Email sent via MCP |
| `send_failure` | email-actions | Email send failed |

### Approval Operations
| Action | Component | Meaning |
|--------|-----------|---------|
| `approval_requested` | approval-handler | File created in /Pending_Approval |
| `approval_granted` | orchestrator | Human moved file to /Approved |
| `approval_rejected` | orchestrator | Human moved file to /Rejected |
| `approved_action_executed` | orchestrator | Approved action ran successfully |

### Social Media
| Action | Component | Meaning |
|--------|-----------|---------|
| `social_post_drafted` | social-media-manager | Post draft created for approval |
| `social_post_approved` | orchestrator | Post approved by human |
| `get_facebook_posts` | social_media MCP | Facebook feed fetched |
| `get_instagram_posts` | social_media MCP | Instagram feed fetched |
| `get_twitter_posts` | social_media MCP | Twitter timeline fetched |
| `post_published` | social-media-manager | Post published to platform |

### Odoo / Accounting
| Action | Component | Meaning |
|--------|-----------|---------|
| `odoo_sync` | odoo MCP / orchestrator | Odoo data fetched and synced |
| `invoice_queried` | odoo MCP | Invoices retrieved |
| `payment_recorded` | odoo MCP | Payment written to Odoo |
| `accounting_file_updated` | ceo-briefing | /Accounting/Current_Month.md updated |

### System
| Action | Component | Meaning |
|--------|-----------|---------|
| `orchestrator_started` | orchestrator | Orchestrator process launched |
| `orchestrator_stopped` | orchestrator | Orchestrator shut down cleanly |
| `ceo_briefing_generated` | ceo-briefing | CEO Briefing file written |
| `error_recovery` | error_handler | Error condition resolved |
| `dashboard_updated` | any | Dashboard.md refreshed |

---

## Using AuditLogger in Code

### Import

```python
# Works from any file in the vault — auto-detects vault root
from utils.audit_logger import AuditLogger

audit = AuditLogger()
```

### Log a successful action

```python
audit.log(
    action="email_received",
    component="gmail_watcher",
    target="msg_id_abc123",
    details={"from": "client@example.com", "subject": "Invoice Q1", "priority": "high"},
    status="success",
    duration_ms=215,
)
```

### Log with approval tracking

```python
audit.log(
    action="email_send_requested",
    component="email-actions",
    target="PENDING_email_reply_20260302_090000.md",
    details={"to": "client@example.com", "subject": "Re: Invoice Q1"},
    status="pending",
    approval_required=True,
    approval_status="",
)

# After human approves:
audit.log(
    action="send_success",
    component="email-actions",
    actor="human",       # human approved it
    target="client@example.com",
    details={"subject": "Re: Invoice Q1"},
    status="success",
    approval_required=True,
    approval_status="approved",
)
```

### Log a failure

```python
audit.log(
    action="odoo_sync",
    component="odoo_mcp",
    status="failure",
    details={"error": "Connection refused", "url": "http://localhost:8069"},
)
```

### Query recent logs

```python
# Get last 50 audit entries
recent = audit.get_recent_logs(count=50)

# Filter to a specific action
email_logs = audit.get_recent_logs(count=100, action_filter="email_received")

# Count errors in the last 24 hours
error_count = audit.get_error_count(hours=24)
```

---

## Integration Pattern

Every component should follow this pattern:

```python
from utils.audit_logger import AuditLogger
from utils.error_handler import ErrorHandler, ErrorSeverity

audit   = AuditLogger()
handler = ErrorHandler()

# 1. Log the start of a significant action
t0 = time.monotonic()
try:
    result = do_the_thing()
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    # 2. Log success
    audit.log(
        action="action_name",
        component="my_component",
        target=str(result),
        status="success",
        duration_ms=elapsed_ms,
    )

except Exception as exc:
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    # 3. Log failure to BOTH audit and error logs
    audit.log(
        action="action_name",
        component="my_component",
        status="failure",
        duration_ms=elapsed_ms,
        details={"error": str(exc)},
    )
    handler.log_error("my_component", exc, ErrorSeverity.EXTERNAL)
```

---

## CEO Briefing Integration

The CEO Briefing skill reads `/Logs/audit.jsonl` to populate:
- **Email Activity** — counts of `email_received` and `send_success` in last 7 days
- **System Health** — last timestamp per component action
- **Task Summary** — counts of `file_processed` and `file_moved_to_done`

Keep action names consistent with the vocabulary above so the briefing queries work correctly.

---

## Retention Policy

The audit log is append-only. No automatic rotation is implemented.

Recommended manual rotation: when `audit.jsonl` exceeds 10 MB, rename to
`audit_YYYY-MM.jsonl` and start a fresh `audit.jsonl`.

---

## Decision Tree

```
Significant action about to happen?
    │
    ├─ Yes → call audit.log() BEFORE starting (status="pending") if long-running
    │         call audit.log() AFTER completing (status="success" or "failure")
    │
    ├─ Approval required?
    │      └─ Set approval_required=True
    │         Set approval_status="" until human decides
    │         Update with approval_status="approved"/"rejected" after decision
    │
    └─ Error occurred?
           └─ Log to BOTH audit (status="failure") AND ErrorHandler.log_error()
```
