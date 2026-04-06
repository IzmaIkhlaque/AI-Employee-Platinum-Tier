---
month: April 2026
last_synced: 2026-04-06T10:00:00
source: odoo
odoo_version: 19.0-20260217
database: ai_employee_db
---
# Accounting — April 2026

> **Last synced:** 2026-04-06 10:00 PKT via Odoo MCP (live sync)
> **Source:** Odoo 19 — `ai_employee_db` — `http://localhost:8069`

---

## Summary

| Metric | Amount (PKR) |
|--------|-------------|
| Total Revenue (invoiced, March) | 0.00 |
| Total Payments Received (March) | 0.00 |
| Outstanding Receivables | 0.00 |
| Overdue Receivables | 0.00 |
| Open Invoices (count) | 0 |
| Overdue Invoices (count) | 0 |

> Fresh Odoo 19 instance. No transactions recorded yet. Add customers and create invoices to populate this report.

---

## Customers (Contacts)

| ID | Name | Email | Phone | City | Customer | Vendor |
|----|------|-------|-------|------|----------|--------|
| 1 | My Company | izmarao99@gmail.com | +92 3105482613 | — | No | No |

> Only the default company record exists. Add client contacts in Odoo to track customers here.

---

## Customer Invoices

| Invoice # | Customer | Issue Date | Due Date | Amount (PKR) | Status |
|-----------|----------|------------|----------|--------------|--------|
| — | — | — | — | — | No posted invoices |

---

## Recent Payments

| Payment # | Customer | Date | Amount (PKR) | Method |
|-----------|----------|------|--------------|--------|
| — | — | — | — | No payments recorded |

---

## Overdue Invoices

No overdue invoices.

---

## Chart of Accounts (Snapshot — accounts with non-zero balance)

All 30 accounts returned a balance of **0.00 PKR**. Sample accounts:

| Code | Account Name | Type | Balance (PKR) |
|------|-------------|------|--------------|
| 1111001 | Building | asset_fixed | 0.00 |
| 1111002 | Furniture and Fixture | asset_fixed | 0.00 |
| 1111005 | Technology | asset_fixed | 0.00 |
| 1112001 | ERP System | asset_non_current | 0.00 |
| 1121001 | Receivable from Customers | asset_receivable | 0.00 |
| 1123002 | Prepaid Rent | asset_current | 0.00 |
| 1125001 | Stock in Hand | asset_current | 0.00 |
| 1125002 | Work in Process | asset_current | 0.00 |

> Full chart contains 30 accounts — all at zero. Record transactions in Odoo to populate balances.

---

## Notes

- This file is auto-synced daily at 7:00 AM by `scripts/scheduler.bat odoo-sync`
- Do NOT edit manually — changes will be overwritten on next sync
- COA uses Pakistani standard chart of accounts template
- Write operations to Odoo (create invoice, record payment) require HITL approval via `/Pending_Approval`
