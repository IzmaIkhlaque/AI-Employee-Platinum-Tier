---
name: ceo-briefing
description: Generate the weekly "Monday Morning CEO Briefing" — an autonomous audit of business operations, accounting, and social media performance. This is the hackathon's standout feature.
version: 1.0.0
---

# CEO Briefing Skill

> **What this delivers:** The AI autonomously audits accounting, tasks, social media,
> and email — then produces a single executive document that transforms the AI from a
> chatbot into a proactive business partner.

---

## When to Generate

| Trigger | Schedule / Command |
|---------|--------------------|
| Automatic | Every Monday at 7:00 AM (via `scripts/scheduler.sh`) |
| On-demand | User says "generate CEO briefing" or "Monday briefing" |
| Post-sync | After a full Odoo sync if data is significantly changed |

---

## Data Sources

Before writing a single line of the briefing, gather from all of these:

| Source | What to read | How |
|--------|-------------|-----|
| `/Accounting/Current_Month.md` | Revenue, expenses, profit, pending invoices | Read file |
| `/Done` | Count of files completed this week | Count files with this-week timestamps |
| `/Needs_Action` | Count of pending items + oldest file age | Count + check creation timestamps |
| `/Pending_Approval` | Count of items awaiting human decision | Count files |
| `/Plans` | Active plans and completion status | Read each PLAN_*.md |
| `/Logs/errors.jsonl` | Error count last 7 days | Read + filter by timestamp |
| `/Logs/audit.jsonl` | Last successful sync per component | Read + filter by action |
| Odoo MCP → `get_invoices` | Fresh invoice data for the week | MCP call |
| Odoo MCP → `get_overdue_invoices` | Overdue payments | MCP call |
| Odoo MCP → `get_payments` | Cash received this week | MCP call |
| Social Media MCP → `generate_social_summary` | Engagement metrics, 7 days | MCP call |

Call `odoo_status` and `social_media_status` first — if either is unavailable, note it
in the System Health section and proceed with vault data only. Never abort the briefing
because one source is down.

---

## Generation Steps

### Step 1 — Compute the Reporting Period

```
period_end   = today (Monday)
period_start = today − 7 days
```

Use ISO dates throughout: `2026-03-02`.

### Step 2 — Pull Financial Data

1. Call `get_invoices(state="posted")` — filter to `invoice_date >= period_start`
2. Call `get_overdue_invoices()` — all overdue, regardless of period
3. Call `get_payments()` — filter to `date >= period_start`
4. Read `/Accounting/Current_Month.md` for month-to-date totals
5. Calculate:
   - **This week revenue** = sum of `amount_total` from step 1
   - **This week cash** = sum of `amount` from step 3
   - **Overdue count + total** = count and sum `amount_residual` from step 2
   - **Flag** any single transaction > $500

> If Odoo is unavailable, fall back to values in `/Accounting/Current_Month.md`
> and note "⚠️ Live Odoo data unavailable — showing last synced values."

### Step 3 — Pull Task Metrics

Count files by folder and age:

```
completed_this_week  = files in /Done with modification date >= period_start
pending_count        = files in /Needs_Action
pending_oldest       = oldest file in /Needs_Action (days since creation)
approval_count       = files in /Pending_Approval
approval_oldest      = oldest file in /Pending_Approval (days since creation)
active_plans         = files in /Plans (non-Done)
```

**Bottleneck threshold:** Any item in `/Needs_Action` or `/Pending_Approval`
older than 48 hours is a bottleneck — list it by filename and age in days.

### Step 4 — Pull Social Media Data

Call `generate_social_summary(platform="all", days=7)` from the social-media MCP.

Extract per platform:
- Post count
- Total and average likes
- Total comments / retweets
- Best performing post (highest engagement)

If social-media MCP is in dry-run, include the data but mark each table cell with
`_(demo)_` so the CEO knows it's not live.

### Step 5 — Pull Email Activity

Read from `/Logs/audit.jsonl` — filter entries from the past 7 days:
- `action: email_received` → emails received
- `action: send_success` → emails sent
- Cross-reference `/Needs_Action` for any unresponded emails still pending

### Step 6 — Check System Health

For each component, find the most recent audit log entry matching its action:

| Component | Audit log action to look for |
|-----------|------------------------------|
| Gmail Watcher | `email_received` or `gmail_check` |
| Odoo Sync | `odoo_sync` |
| Social Media MCP | `get_facebook_posts` or `get_instagram_posts` or `get_twitter_posts` |
| File Watcher | `file_detected` |

Check `/Logs/errors.jsonl` for any errors in the last 24 hours per component.

Status logic:
- `✅ OK` — last activity within 25 hours, no recent errors
- `⚠️ Stale` — last activity > 25 hours ago
- `❌ Error` — error entry in last 24 hours

### Step 7 — Write the Briefing File

**Filename:** `/Briefings/CEO_Briefing_{YYYY-MM-DD}.md`

Use the template below exactly. Replace all `{placeholders}`. Do not leave any
placeholder unfilled — use `—` if data is genuinely unavailable.

---

## Briefing Template

```markdown
---
type: ceo_briefing
generated: {ISO-8601 timestamp}
period_start: {YYYY-MM-DD}
period_end: {YYYY-MM-DD}
status: generated
---

# CEO Briefing — Week of {YYYY-MM-DD}

> Generated by AI Employee at {HH:MM} on {day, date}.

---

## Executive Summary

{2–3 sentences covering: (1) revenue trend vs prior week, (2) most significant
accomplishment or event this week, (3) primary blocker or action item requiring CEO attention.
Be specific — use actual numbers from the data.}

---

## Financial Overview

| Metric | This Week | MTD Total | Status |
|--------|----------|-----------|--------|
| Revenue (invoiced) | ${this_week_revenue} | ${mtd_revenue} | {trend} |
| Cash Received | ${this_week_cash} | ${mtd_cash} | {trend} |
| Expenses | ${this_week_expenses} | ${mtd_expenses} | {trend} |
| Net Profit | ${this_week_net} | ${mtd_net} | {trend} |
| Outstanding Invoices | {count} invoices / ${total} | — | {ok/flag} |
| Overdue Payments | {count} invoices / ${total} | — | {⚠️ if >0} |

### Flagged Transactions

{List each transaction > $500 or any anomaly (expense without invoice, duplicate, etc.)
Format: `- {date} · {description} · ${amount} · {reason for flag}`
If none: "No transactions flagged this week."}

---

## Task Summary

| Category | Count | Oldest Item |
|----------|-------|-------------|
| Completed This Week | {completed_this_week} | — |
| Pending in Needs_Action | {pending_count} | {pending_oldest} days |
| Awaiting Approval | {approval_count} | {approval_oldest} days |
| Active Plans | {active_plans} | — |

### Bottlenecks

{List items stuck > 48 hours. Format: `- {filename} — {age} days old — {folder}`
If none: "No bottlenecks. All items processed within 48 hours. ✅"}

---

## Social Media Performance

| Platform | Posts | Avg Likes | Total Comments | Best Post |
|----------|-------|-----------|----------------|-----------|
| Facebook | {fb_posts} | {fb_avg_likes} | {fb_comments} | "{fb_best_post[:60]}..." |
| Instagram | {ig_posts} | {ig_avg_likes} | {ig_comments} | "{ig_best_post[:60]}..." |
| Twitter/X | {tw_posts} | {tw_avg_likes} | {tw_rts} RTs | "{tw_best_post[:60]}..." |

{If any platform is in dry-run mode, add: "_Note: [Platform] data is demo only — live token not configured._"}

---

## Email Activity

| Metric | Count |
|--------|-------|
| Emails Received | {emails_received} |
| Emails Processed | {emails_processed} |
| Emails Sent (approved) | {emails_sent} |
| Pending Responses | {emails_pending} |

---

## Recommendations

{Generate 3 specific, data-driven action items. Base them on:
- Overdue invoices (who owes what — follow up)
- Bottlenecks (what has been waiting longest)
- Social media gaps (any platform with 0 posts)
- System health issues (any ❌ components)

Format:
1. **[Category]** {specific action} — {reason from data}
2. **[Category]** {specific action} — {reason from data}
3. **[Category]** {specific action} — {reason from data}}

---

## System Health

| Component | Status | Last Active | Last Error |
|-----------|--------|-------------|-----------|
| Gmail Watcher | {status} | {last_active} | {last_error or "None"} |
| Odoo Sync | {status} | {last_active} | {last_error or "None"} |
| Social Media MCP | {status} | {last_active} | {last_error or "None"} |
| File Watcher | {status} | {last_active} | {last_error or "None"} |

---

_Next briefing: {next_monday} at 7:00 AM_
_Questions? Ask the AI Employee: "Explain the [metric] in this week's briefing"_
```

---

### Step 8 — Update Dashboard.md

In the **CEO Briefings** section, update:

```markdown
| Next CEO Briefing | Monday, {next_monday} at 7:00 AM |
| Last Briefing | {today} — [View](/Briefings/CEO_Briefing_{today}.md) |
```

Also update **Last Updated** timestamp at the top of Dashboard.md.

### Step 9 — Sync Accounting File

After writing the briefing, update `/Accounting/Current_Month.md`:
- Set `last_synced` frontmatter to current ISO timestamp
- Update the Summary table with the fresh Odoo values used in the briefing

### Step 10 — Log to Audit

Append to `/Logs/audit.jsonl`:

```json
{"ts": "2026-03-02T07:00:00", "action": "ceo_briefing_generated", "file": "CEO_Briefing_2026-03-02.md", "data_sources": ["odoo", "vault", "social_media"], "status": "ok"}
```

---

## Quality Rules

Before saving the briefing file, verify:

- [ ] No `{placeholder}` strings remain in the output
- [ ] All dollar amounts use `$X,XXX.XX` format
- [ ] All dates use `YYYY-MM-DD` format
- [ ] Executive Summary references at least one real number from the data
- [ ] Recommendations are specific (not generic advice like "improve sales")
- [ ] System Health table has a row for every component
- [ ] If Odoo was unavailable, the file contains the stale-data warning

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Odoo MCP unreachable | Use `/Accounting/Current_Month.md` values, note in System Health |
| Social Media MCP unavailable | Use `/Social_Media/*/POST_*.json` records if present, else note as unavailable |
| `/Briefings` folder missing | Create it, then write the file |
| Previous briefing exists for same date | Overwrite — append `_v2` suffix if the user requests a re-run |
| All data sources unavailable | Write a minimal briefing with vault-only data, flag all metrics as stale |

---

## File Naming

| File | Location |
|------|----------|
| Briefing | `/Briefings/CEO_Briefing_{YYYY-MM-DD}.md` |
| Accounting snapshot | `/Accounting/Current_Month.md` (updated in place) |
| Audit entry | `/Logs/audit.jsonl` (appended) |
