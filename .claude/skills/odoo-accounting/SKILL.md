---
name: odoo-accounting
description: Manage business accounting through Odoo ERP. Search invoices, record payments, check balances, sync transaction data to vault. Use when processing financial items or generating CEO briefings.
version: 1.0.0
---

# Odoo Accounting Skill

Connect to the local Odoo instance via the `odoo` MCP server to read and write accounting data.

---

## MCP Server

**Server file:** `mcp_servers/odoo_server.py` (custom — uses standard `/xmlrpc/2/` path)
**Registered as:** `odoo` in Claude Code local config

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `odoo_status` | Connection health check — call this first |
| `search_customers` | Companies from `res.partner` |
| `get_invoices` | Customer invoices (filter by state) |
| `get_overdue_invoices` | Unpaid invoices past due date |
| `get_payments` | Inbound payments from `account.payment` |
| `get_account_balances` | Chart of accounts with balances |

## Available Odoo Operations (via MCP)

### Read Operations (auto-approved)

| Operation | Tool / Model | Domain / Notes |
|-----------|-------------|----------------|
| Search customers | `search_customers` | companies only |
| Search invoices | `get_invoices` | filter by `state` param |
| Overdue invoices | `get_overdue_invoices` | past due + unpaid |
| Search bills | `account.move` | `[["move_type","=","in_invoice"]]` |
| Search payments | `get_payments` | inbound, posted |
| Get account balances | `get_account_balances` | active accounts only |

### Write Operations (require HITL approval)

| Operation | Model | Notes |
|-----------|-------|-------|
| Create invoice | `account.move` | needs `partner_id`, `invoice_line_ids` |
| Record payment | `account.payment` | needs `partner_id`, `amount`, `payment_type` |
| Update record | any model | create approval request first |

### Never Allowed

- `unlink` (delete) on any model — never automate deletions
- `action_cancel` on posted invoices without approval

---

## Sync Workflow

When asked to sync accounting data:

1. **Query Odoo** — fetch invoices, payments, and expenses since `last_synced` in frontmatter
2. **Calculate totals:**
   - Revenue = sum of posted `out_invoice` amounts
   - Expenses = sum of posted `in_invoice` amounts
   - Net Profit = Revenue − Expenses
3. **Update `/Accounting/Current_Month.md`:**
   - Replace Summary table values
   - Add rows to Recent Transactions table
   - Update `last_synced` frontmatter timestamp (ISO 8601: `YYYY-MM-DDTHH:MM:SS`)
4. **Flag anomalies:**
   - Any invoice overdue by >30 days → add to Notes section
   - Any single transaction >$500 → flag for review
   - Any expense with no matching invoice → flag
5. **Log to `/Logs/audit.jsonl`** — append one JSON line per sync:
   ```json
   {"ts": "2026-03-02T07:00:00", "action": "odoo_sync", "records": 12, "status": "ok"}
   ```
6. **Update Dashboard.md** — refresh Accounting Summary section

---

## CEO Briefing Workflow

When asked to generate a CEO briefing:

1. Run the sync workflow above first
2. Create `/Briefings/BRIEFING_YYYYMMDD.md` with:
   - Executive summary (3–5 bullet points)
   - Revenue vs previous period
   - Top 3 customers by invoice value
   - Outstanding payments (overdue > 7 days)
   - Flagged anomalies
   - Recommended actions
3. Update Dashboard.md → CEO Briefings section with new file path and date

---

## Error Handling

- On MCP tool failure: log to `/Logs/errors.jsonl`, retry once after 30s
- On auth failure: create `URGENT_odoo_auth_failure_YYYYMMDD_HHMMSS.md` in `/Needs_Action`
- On partial sync: write what succeeded, note failures in `/Accounting/Current_Month.md` Notes

---

## Rules

- Read operations: **auto-approved** — query freely
- Create/update operations: **require HITL approval** — move request to `/Pending_Approval`
- Delete operations: **NEVER allowed** through automation
- Always update `last_synced` timestamp in `Current_Month.md` frontmatter after any sync
- Never expose raw passwords or API keys in vault files
