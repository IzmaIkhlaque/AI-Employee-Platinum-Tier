# Odoo 19 Community Edition — Local Setup Guide

> Used by the AI Employee to sync accounting data into `/Accounting/Current_Month.md`
> and generate CEO Briefings.

---

## Option A: Docker (Recommended for Hackathon)

Docker gives you a clean, reproducible Odoo instance with no system-level dependencies.

### Step 1 — Prerequisites

1. Install **Docker Desktop for Windows**: https://www.docker.com/products/docker-desktop/
2. Run the installer and restart your machine if prompted.
3. Open Docker Desktop and confirm the status shows **"Engine running"** in the bottom-left corner.

Verify in a terminal:

```bash
docker --version
docker compose version
```

Both commands must return a version number before proceeding.

---

### Step 2 — Create the Project Folder

Create a dedicated folder **outside the vault** — Docker volumes and config files do not belong inside Obsidian.

```bash
mkdir D:\odoo-local
mkdir D:\odoo-local\config
mkdir D:\odoo-local\addons
```

---

### Step 3 — Create docker-compose.yml

Create `D:\odoo-local\docker-compose.yml` with the following content:

```yaml
version: '3.1'
services:
  odoo:
    image: odoo:19
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo_password

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo_password
      - POSTGRES_USER=odoo
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  db-data:
```

---

### Step 4 — Start Odoo

```bash
cd D:\odoo-local
docker compose up -d
```

Docker will pull the `odoo:19` and `postgres:16` images on the first run — this may take a few minutes depending on your connection.

Check that both containers are running:

```bash
docker compose ps
```

You should see both `odoo` and `db` with status `Up`.

---

### Step 5 — Access Odoo and Create the Database

1. Open your browser and go to: **http://localhost:8069**
2. You will see the **Database Manager** screen on the first launch.
3. Fill in the form:
   - **Master Password:** choose a strong password and save it somewhere safe
   - **Database Name:** `ai_employee_db`
   - **Email:** your admin email
   - **Password:** your admin password
   - **Language:** English
   - **Country:** (optional)
4. Click **Create Database** and wait ~60 seconds for initialization.

---

### Step 6 — Install Required Modules

Once logged in as admin:

1. Go to **Apps** (top menu)
2. Search for and install each of the following:
   - **Accounting** — core ledger, journals, financial reports
   - **Invoicing** — customer invoices and vendor bills
   - **Contacts** — customer and vendor records

> **Note:** Installing Accounting will automatically install Invoicing as a dependency.

---

### Step 7 — Add Sample Data for the Hackathon Demo

The AI Employee's CEO Briefing needs real data to demonstrate. Add the following:

**Contacts (customers):**
1. Go to **Contacts → New**
2. Create 3–4 sample customers, e.g.:
   - TechStartup.io — Sara Khan
   - Next Solutions Pvt Ltd — Ahmed Raza
   - DemoClient Corp — any name

**Invoices:**
1. Go to **Accounting → Customers → Invoices → New**
2. Create 2–3 sample invoices against your contacts
3. Set amounts between $200–$2,000 to trigger the $500 review flag
4. **Confirm** (post) at least one invoice so it appears in reports

**Payments:**
1. On a confirmed invoice, click **Register Payment**
2. Record at least one payment to show cash flow in the CEO Briefing

This gives the AI Employee real revenue, expense, and payment data to sync.

---

### Step 8 — Generate an API Key

The AI Employee connects to Odoo via the XML-RPC API authenticated with an API key.

1. In Odoo, go to **Settings → Users & Companies → Users**
2. Open your admin user
3. Click **Preferences** (top-right of the user form)
4. Scroll to the **API Keys** section
5. Click **New API Key**
6. Name it: `AI Employee MCP`
7. Click **Generate Key** — copy the key immediately (it is only shown once)

---

### Step 9 — Add Credentials to .env

Open `AI_Employee_Vault/.env` and add:

```env
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with the key you copied in Step 8.

> The `.env` file is listed in `.gitignore` — never commit credentials to git.

---

### Step 10 — Verify the Connection

> **Important:** Odoo XML-RPC requires your **login email** (the email you used when
> creating the database), not the word `admin`. The API key acts as the password.

Save this as a temporary file `test_odoo.py` in `D:\odoo-local\` and run it:

```python
import xmlrpc.client

# ── Edit these values ────────────────────────────────────────────────────────
ODOO_URL      = "http://localhost:8069"
ODOO_DB       = "ai_employee_db"
ODOO_LOGIN    = "your_admin_email@example.com"  # email used when creating the DB
ODOO_PASSWORD = "your_odoo_password"            # your Odoo login password
# ─────────────────────────────────────────────────────────────────────────────
# Note: XML-RPC accepts your login password directly.
# API keys (Security tab) require developer mode and behave differently.
# ─────────────────────────────────────────────────────────────────────────────

print(f"[1] Connecting to {ODOO_URL} ...")
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")

print(f"[2] Server version: {common.version()['server_version']}")

print(f"[3] Authenticating as '{ODOO_LOGIN}' ...")
uid = common.authenticate(ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD, {})

if uid:
    print(f"[4] ✅ Connected! UID = {uid}")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    invoices = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "account.move", "search_count",
        [[["move_type", "=", "out_invoice"]]]
    )
    print(f"[5] Customer invoices found: {invoices}")
else:
    print("[4] ❌ Authentication failed — uid is False")
    print("    Check: correct email? correct DB name? correct password?")
```

Run it:

```bash
cd D:\odoo-local
python test_odoo.py
```

A successful run prints all five steps ending with `✅ Connected!`.

---

## Option B: Direct Install on Windows (Alternative)

If you prefer not to use Docker:

1. Download the Odoo 19 Windows installer from: https://www.odoo.com/page/download
2. Run the `.exe` installer — it bundles PostgreSQL automatically.
3. Follow the on-screen setup wizard.
4. Odoo will start as a Windows Service on port 8069.
5. Continue from **Step 5** above (database creation, modules, API key).

> Direct install is harder to reset cleanly. Docker is recommended for hackathon demos
> because you can `docker compose down -v` to wipe and start fresh.

---

## Stopping and Restarting Odoo

```bash
# Stop containers (data is preserved in volumes)
cd D:\odoo-local
docker compose down

# Start again
docker compose up -d

# Full reset — DELETES all data
docker compose down -v
```

---

## Troubleshooting

### "Port 8069 already in use"

Another process is occupying port 8069. Either stop that process or change the port in `docker-compose.yml`:

```yaml
ports:
  - "8070:8069"   # Change 8070 to any free port
```

Then access Odoo at `http://localhost:8070` and update `ODOO_URL` in `.env` accordingly.

---

### "Database creation failed"

The PostgreSQL container may not be fully ready when Odoo starts.

```bash
# Check DB container health
docker compose logs db

# Restart only Odoo (DB stays up)
docker compose restart odoo
```

If the problem persists, do a full restart:

```bash
docker compose down
docker compose up -d
```

---

### "Cannot connect to http://localhost:8069"

1. Confirm Docker Desktop is running (check the system tray icon).
2. Run `docker compose ps` — both containers must show `Up`.
3. If the `odoo` container shows `Exited`, check its logs:

```bash
docker compose logs odoo
```

Common cause: the `config` folder is missing or has wrong permissions. Ensure `D:\odoo-local\config\` exists (even if empty).

---

### "API authentication returns uid: False"

This is the most common error. Work through these checks in order:

**0. Confirm what login Odoo actually has (run this first)**

Query the database directly to see the real login — no guessing:

```bash
cd D:\odoo-local
docker exec odoo-local-db-1 psql -U odoo -d ai_employee_db -c "SELECT id, login FROM res_users WHERE active=true;"
```

Use whatever appears in the `login` column as your username in `authenticate()`.

**1. Check if any API key is actually saved**

The most common failure: the Odoo API key dialog was dismissed before completion
and the key was never written to the database.

```bash
docker exec odoo-local-db-1 psql -U odoo -d ai_employee_db -c "SELECT name, index FROM res_users_apikeys;"
```

If this returns **0 rows**, no API key exists. Go regenerate one (see Step 8).

**2. Wrong username — second most likely cause**

Odoo XML-RPC does NOT accept `'admin'` as the username. It requires the **login email**
you typed when you first created the database. To confirm your login:

- Log into Odoo → click your avatar (top-right) → **My Profile**
- The **Login** field shows the exact string to use (usually an email address)

**2. API key not copied fully**

API keys are long (~40 characters). A missing character at the end causes silent failure.
Go to **Settings → Users → your user → Preferences → API Keys** and generate a fresh key.
Copy it again — select all, no trailing spaces.

**3. Database name mismatch**

The DB name is case-sensitive. If you named it `AI_Employee_DB` it will not match
`ai_employee_db`. Confirm the exact name at http://localhost:8069/web/database/manager

**4. Technical Manager permission required**

API key authentication requires the user to have **Technical** access level.
Go to **Settings → Users → your user** → set "Technical" to ✅ Allowed.

**5. Quick sanity test (no API key needed)**

```bash
python -c "
import xmlrpc.client
c = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
print(c.version())
"
```

If this prints a version dict, Odoo is reachable and the problem is credentials only.
If it throws `ConnectionRefusedError`, the container isn't running — see above.

---

## Reference

| Item | Value |
|------|-------|
| Odoo URL | http://localhost:8069 |
| Database | ai_employee_db |
| API key env var | `ODOO_API_KEY` |
| Accounting data file | `/Accounting/Current_Month.md` |
| Sync schedule | Daily at 7:00 AM (see `Company_Handbook.md`) |
| Audit log | `/Logs/audit.jsonl` |
| Error log | `/Logs/errors.jsonl` |
