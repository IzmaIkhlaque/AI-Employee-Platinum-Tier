---
month: April 2026
last_synced: 2026-04-06T15:35:00
source: odoo
odoo_version: 19.0-20260217
database: ai_employee_db
---
# Accounting — April 2026

> **Last synced:** 2026-04-06 15:35 PKT via Odoo MCP (live sync)
> **Source:** Odoo 19 — `ai_employee_db` — `http://localhost:8069`

---

## Summary

| Metric | Amount (PKR) |
|--------|-------------|
| Total Revenue (invoiced, April) | 0.00 |
| Total Payments Received (April) | 0.00 |
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

## Chart of Accounts (Snapshot — first 30 accounts returned)

All accounts returned a balance of **0.00 PKR**. Key accounts:

| Code | Account Name | Type | Balance (PKR) |
|------|-------------|------|--------------|
| 1111001 | Building | asset_fixed | 0.00 |
| 1111002 | Furniture and Fixture | asset_fixed | 0.00 |
| 1111003 | Tools and Equipment | asset_fixed | 0.00 |
| 1111004 | Plant and Machinery | asset_fixed | 0.00 |
| 1111005 | Technology | asset_fixed | 0.00 |
| 1111006 | Land | asset_fixed | 0.00 |
| 1111007 | Construction | asset_fixed | 0.00 |
| 1111008 | Installations | asset_fixed | 0.00 |
| 1111009 | Vehicle | asset_fixed | 0.00 |
| 1111010 | Vehicle Accessories | asset_fixed | 0.00 |
| 1112001 | ERP System | asset_non_current | 0.00 |
| 1113000 | Investment Property | asset_non_current | 0.00 |
| 1114000 | Long Term Investments | asset_non_current | 0.00 |
| 1115000 | Long Term Deposits | asset_non_current | 0.00 |
| 1116000 | Biological Assets | asset_non_current | 0.00 |
| 1117000 | Investments in Associates | asset_non_current | 0.00 |
| 1118000 | Investments in Jointly Controlled Entities | asset_non_current | 0.00 |
| 1119000 | Other Financial Assets | asset_non_current | 0.00 |
| 1121001 | Receivable from Customers | asset_receivable | 0.00 |
| 1122001 | Advances to Suppliers | asset_current | 0.00 |
| 1122002 | Withholding Tax- Advance | asset_current | 0.00 |
| 1122003 | Loan to Employees | asset_current | 0.00 |
| 1123001 | Security Deposits | asset_current | 0.00 |
| 1123002 | Prepaid Rent | asset_current | 0.00 |
| 1123003 | Income Tax Refundable | asset_current | 0.00 |
| 1123004 | Sales Tax Refundable | asset_receivable | 0.00 |
| 1123005 | Sales Tax Paid | asset_current | 0.00 |
| 1124000 | Other Current Assets | asset_current | 0.00 |
| 1125001 | Stock in Hand | asset_current | 0.00 |
| 1125002 | Work in Process | asset_current | 0.00 |

> Full chart returned 30 accounts — all at zero. Record transactions in Odoo to populate balances.

---

## Notes

- This file is auto-synced daily at 7:00 AM by `scripts/scheduler.bat odoo-sync`
- Do NOT edit manually — changes will be overwritten on next sync
- COA uses Pakistani standard chart of accounts template
- Write operations to Odoo (create invoice, record payment) require HITL approval via `/Pending_Approval`
