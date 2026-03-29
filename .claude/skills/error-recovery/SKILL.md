---
name: error-recovery
description: Handle errors gracefully across all system components. Implements retry logic, fallback actions, and error notification. Use when any operation fails.
version: 1.0.0
---

# Error Recovery Skill

Provides a taxonomy for classifying failures, defines what to do for each class,
and ensures no single component failure brings down the entire system.

**Python utility:** `utils/error_handler.py` — importable by all watchers and scripts.

---

## Error Categories

### 1. TRANSIENT
**Examples:** API timeout, rate limit (429), temporary network drop, slow response

**Action:**
- Retry up to 3 times with exponential backoff: **30s → 60s → 120s**
- Log each attempt to `/Logs/errors.jsonl` with `"severity": "transient"`
- If all 3 retries fail, escalate to the appropriate next category

```python
from utils.error_handler import ErrorHandler, ErrorSeverity
handler = ErrorHandler()
result = handler.retry_with_backoff(
    lambda: api_call(),
    component="gmail_watcher",
    context={"action": "fetch_emails"}
)
```

---

### 2. AUTH
**Examples:** Expired Facebook token, Odoo password changed, Gmail OAuth revoked, Twitter key invalid

**Action:**
- Log to `/Logs/errors.jsonl` immediately
- Create `URGENT_ERROR_{COMPONENT}_{ts}.md` in `/Needs_Action` — human must fix
- Update Dashboard.md System Health row to `❌ Error`
- **Do NOT retry** — retrying bad credentials triggers account lockouts
- Skip all operations for this component until human resolves it

**Signs:** HTTP 401, HTTP 403, `OdooConnectionError: auth failed`, `tweepy.errors.Unauthorized`

---

### 3. DATA
**Examples:** Malformed JSON in a vault file, missing required field in an email, corrupt Needs_Action file

**Action:**
- Log the bad item to `/Logs/errors.jsonl` with full context (filename, field, value)
- **Skip that item** — do not halt processing
- Continue with remaining items in the queue
- Never write partially-processed data to `/Done`

```python
for item in items:
    with handler.catch("file_processor", ErrorSeverity.DATA, context={"file": item}):
        process(item)
    # loop continues even if process(item) raised
```

---

### 4. CRITICAL
**Examples:** Payment recording failure, data corruption detected, unrecoverable disk error, orchestrator crash

**Action:**
- Log to `/Logs/errors.jsonl` immediately
- **Halt** all related operations (do not proceed with dependent steps)
- Create `URGENT_ERROR_{COMPONENT}_{ts}.md` in `/Needs_Action` with `priority: critical`
- Update Dashboard.md — mark affected component `❌ Error`
- Do NOT attempt automatic recovery — wait for human confirmation
- After human resolves: re-run any skipped operations, sync missed data, log recovery

---

### 5. EXTERNAL
**Examples:** Odoo Docker container stopped, Facebook Graph API outage, Gmail SMTP down

**Action:**
- Log to `/Logs/errors.jsonl` with `"severity": "external"`
- **Skip that integration** for this cycle — do not crash the whole system
- Continue processing all other components normally (graceful degradation)
- Note the outage in the next Dashboard.md update

---

## Graceful Degradation Rules

These rules ensure the system stays partially functional even when integrations fail.
**Never let one component failure cascade into a full system halt.**

| Component down | What continues | What is skipped |
|----------------|----------------|-----------------|
| Gmail API | File watcher, Odoo sync, social media | Email fetch, email send |
| Odoo MCP | Email, social media, vault processing | Accounting sync, live financial data in CEO Briefing |
| Odoo down | Use `/Accounting/Current_Month.md` cached values | Live query data |
| Social Media APIs | All other operations | Post publishing (drafts saved locally) |
| One watcher crashes | Other watchers keep running | Items from the crashed watcher |
| Dashboard write fails | All operations continue | Dashboard update only |

**Fallback data sources:**

```
Odoo unavailable  → /Accounting/Current_Month.md  (last synced values)
Social APIs down  → /Social_Media/*/POST_*.json   (cached post records)
Audit log locked  → buffer in memory, retry write on next cycle
```

---

## Recovery Workflow

After a human resolves an AUTH or CRITICAL error:

1. **Verify** the fix — test the connection manually (e.g. run `odoo_status`)
2. **Re-process skipped items** — check `/Needs_Action` for files older than the error timestamp
3. **Sync missed data** — run an on-demand Odoo sync or social media fetch if data was missed
4. **Update Dashboard.md** — change System Health status back to `✅ OK`
5. **Log recovery** to `/Logs/audit.jsonl`:
   ```json
   {"ts": "...", "action": "error_recovery", "component": "...", "resolved_by": "human", "status": "ok"}
   ```
6. **Move the URGENT file** from `/Needs_Action` to `/Done`

---

## Using the ErrorHandler in Code

### Import

```python
# Works from any file in the vault — auto-detects vault root
from utils.error_handler import ErrorHandler, ErrorSeverity

handler = ErrorHandler()
```

### Log a plain error

```python
try:
    result = some_api_call()
except Exception as e:
    handler.log_error("component_name", e, ErrorSeverity.EXTERNAL,
                      context={"url": url, "action": "fetch"})
```

### Retry with backoff

```python
# Retries up to 3×: 30s, 60s, 120s delays
result = handler.retry_with_backoff(
    lambda: requests.get(url, timeout=10),
    component="facebook_api",
    context={"endpoint": "/me/feed"}
)
```

### Context manager (suppress + log)

```python
# Logs the error but does NOT crash — execution resumes after the block
with handler.catch("odoo_sync", ErrorSeverity.EXTERNAL):
    sync_odoo_data()

# With reraise=True — logs AND propagates the exception
with handler.catch("payment_processor", ErrorSeverity.CRITICAL, reraise=True):
    record_payment(amount, invoice_id)
```

### Log a recovery

```python
handler.log_recovery("odoo_sync", {"resolved_by": "human", "downtime_minutes": 15})
```

---

## Log Entry Formats

### `/Logs/errors.jsonl` — one JSON object per line

```json
{
  "ts": "2026-03-02T07:00:00.123456",
  "component": "gmail_watcher",
  "severity": "transient",
  "error_type": "TimeoutError",
  "message": "Request timed out after 30s",
  "context": {"attempt": 1, "max_retries": 3, "retry_in_secs": 30},
  "resolved": false
}
```

### `/Logs/audit.jsonl` — recovery events

```json
{
  "ts": "2026-03-02T08:15:00",
  "action": "error_recovery",
  "component": "odoo_sync",
  "resolved_by": "human",
  "downtime_minutes": 75
}
```

### `/Needs_Action/URGENT_ERROR_{COMPONENT}_{ts}.md` — human alert

Created automatically for AUTH and CRITICAL errors. Contains:
- Error type and full message
- Context at time of failure
- Checklist of resolution steps
- Instruction to move to `/Done` when resolved

---

## Decision Tree

```
Exception raised
    │
    ├─ Is it a timeout or 429?
    │      └─ TRANSIENT → retry_with_backoff() → if exhausted, re-classify
    │
    ├─ Is it 401 / 403 / auth failure?
    │      └─ AUTH → log + create URGENT → stop component → wait for human
    │
    ├─ Is it bad/missing data in a file?
    │      └─ DATA → log + skip item → continue loop
    │
    ├─ Does it risk losing money or corrupting records?
    │      └─ CRITICAL → log + halt + create URGENT → wait for human
    │
    └─ Is an external service just down?
           └─ EXTERNAL → log + skip integration → continue others
```
