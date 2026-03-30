---
name: cloud-odoo
description: Cloud-specific Odoo integration. Cloud agent can READ Odoo data but CANNOT write. All write operations must go through /Pending_Approval for Local agent.
version: 1.0.0
---

# Cloud Odoo Skill

## Permission Model

| Operation | Cloud Agent | Local Agent |
|-----------|-------------|-------------|
| Read invoices, payments, balances | YES (auto-approved) | YES |
| Search customers | YES (auto-approved) | YES |
| Create invoice | NO — create file in /Pending_Approval | YES (after approval) |
| Update Odoo record | NO — create file in /Pending_Approval | YES (after approval) |
| Delete any record | NEVER | NEVER |

## How to Read Odoo Data (Cloud)

Use the MCP tools directly — no approval needed:

```
odoo_status           — verify connection
search_customers      — find contacts by name
get_invoices          — list posted invoices
get_overdue_invoices  — list past-due invoices
get_payments          — list recent payments
get_account_balances  — chart of accounts snapshot
```

## How to Request a Write (Cloud)

Cloud CANNOT write to Odoo. Instead:

1. Create a file in `/Pending_Approval/accounting/PENDING_odoo_write_YYYYMMDD_HHMMSS.md`
2. Include frontmatter:
   ```yaml
   ---
   action: odoo_write
   operation: create_invoice  # or update_record, record_payment
   priority: normal
   agent: cloud
   ---
   ```
3. Describe the exact write operation needed
4. Sync via git — Local agent picks it up and executes after human approval

## Infrastructure (on EC2)

Odoo runs via Docker Compose at `~/odoo-cloud/`:

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Odoo 19 + PostgreSQL 16 + Nginx |
| `nginx.conf` | HTTPS reverse proxy (self-signed cert) |
| `backup.sh` | Daily pg_dump, keeps last 7 backups |
| `ssl/` | Self-signed cert files (not in git) |

**Access:**
- HTTP (redirects to HTTPS): `http://YOUR_EC2_IP:80`
- HTTPS (self-signed): `https://YOUR_EC2_IP`
- Direct Odoo port: `http://YOUR_EC2_IP:8069`

**Manage containers:**
```bash
cd ~/odoo-cloud
docker compose up -d       # start
docker compose down        # stop
docker compose logs -f     # tail logs
docker compose ps          # status
```

**Manual backup:**
```bash
~/odoo-cloud/backup.sh
```

## ODOO_URL for Cloud Agent

In `~/AI_Employee_Vault/.env`:
```
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_API_KEY=your_key_here
```

Odoo runs locally on the same EC2 instance, so `localhost` is correct.

## Safety Rules

```
NEVER quote financial figures from memory — always call get_invoices or get_account_balances
NEVER bypass /Pending_Approval for any write operation
NEVER delete any Odoo record under any circumstances
ALWAYS read /Accounting/Current_Month.md before generating financial summaries
```
