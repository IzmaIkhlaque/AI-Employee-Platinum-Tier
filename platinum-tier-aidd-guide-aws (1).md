# Platinum Tier AIDD Guide — Personal AI Employee Hackathon 0

> **Methodology:** AI-Driven Development (AIDD) — everything built through Claude Code CLI
> **Tier:** Platinum (60+ hours)
> **Prerequisite:** Gold tier completed (Bronze + Silver + Gold all done)
> **Cloud Platform:** AWS EC2 Free Tier (t2.micro — free for 12 months)

---

## What Is Platinum?

Platinum turns your local AI Employee into a **production-grade, always-on system** with two agents:

- **Cloud Agent** (runs 24/7 on AWS EC2) — watches emails, drafts replies, creates social media drafts
- **Local Agent** (runs on your Windows PC) — approves actions, handles sensitive operations, executes sends

They communicate through a **synced Obsidian vault** using Git. When you're offline, the Cloud Agent keeps working. When you come back online, you approve what it did.

---

## Platinum Requirements (From Hackathon Document)

| # | Requirement | What It Means Simply |
|---|------------|---------------------|
| 1 | Run AI Employee on Cloud 24/7 | Deploy to AWS EC2 Free Tier VM |
| 2 | Work-Zone Specialization | Cloud = drafts only, Local = approvals + sends |
| 3 | Delegation via Synced Vault | Git sync between Cloud and Local vault copies |
| 4 | Claim-by-move rule | Prevent both agents working on same item |
| 5 | Security: secrets never sync | .env, tokens stay local — never pushed to Git |
| 6 | Deploy Odoo on Cloud VM | Odoo 24/7 with HTTPS and backups on EC2 |
| 7 | Optional: A2A upgrade | Replace some file handoffs with direct messages (bonus) |
| 8 | **Platinum demo (MUST PASS)** | Email arrives → Cloud drafts reply → you approve when back → Local sends → Done |

---

## New Folders Needed for Platinum

```
AI_Employee_Vault/
├── (All Bronze + Silver + Gold folders)
│
├── (NEW Platinum folders)
│   ├── /In_Progress              ← Items currently being worked on
│   │   ├── /cloud/               ← Cloud agent claimed these
│   │   └── /local/               ← Local agent claimed these
│   ├── /Updates                  ← Cloud writes status updates here
│   ├── /Signals                  ← Cloud → Local communication files
│   ├── /Needs_Action
│   │   ├── /email/               ← Domain-specific subfolders
│   │   ├── /social/
│   │   └── /accounting/
│   ├── /Plans
│   │   ├── /email/
│   │   ├── /social/
│   │   └── /accounting/
│   └── /Pending_Approval
│       ├── /email/
│       ├── /social/
│       └── /accounting/
```

---

## How the Two-Agent System Works (Simple Explanation)

```
┌─────────────────────────────┐     Git Sync     ┌──────────────────────────────┐
│      CLOUD AGENT (24/7)      │ ◄══════════════► │      LOCAL AGENT (your PC)    │
│   AWS EC2 (t2.micro)         │                  │   Windows D:\AI_Employee_Vault│
│                              │                  │                              │
│ OWNS (draft-only):           │                  │ OWNS (execute):              │
│  • Email triage + draft      │                  │  • Approve/reject actions    │
│  • Social media drafts       │                  │  • Send emails (Gmail MCP)   │
│  • Schedule post drafts      │                  │  • Post to social media      │
│  • Odoo read-only queries    │                  │  • WhatsApp session          │
│                              │                  │  • Payments/banking          │
│ CANNOT DO:                   │                  │  • Update Dashboard.md       │
│  ✗ Send emails               │                  │  • Execute Odoo writes       │
│  ✗ Publish social posts      │                  │                              │
│  ✗ Make payments             │                  │ HOW IT WORKS:                │
│  ✗ Update Dashboard.md       │                  │  1. git pull (get Cloud work)│
│                              │                  │  2. Review /Pending_Approval │
│ HOW IT WORKS:                │                  │  3. Move to /Approved        │
│  1. Watchers detect events   │                  │  4. Claude executes actions  │
│  2. Create files in vault    │                  │  5. Move to /Done            │
│  3. git push (share work)    │                  │  6. git push (share results) │
└─────────────────────────────┘                  └──────────────────────────────┘
```

**The Golden Rule:** Cloud DRAFTS, Local EXECUTES. Secrets NEVER leave your PC.

---

## Step-by-Step AIDD Prompts

### Step 1: Create Platinum Folder Structure

```bash
cd D:\AI_Employee_Vault
claude
```

#### Prompt 1 — Extend Vault for Platinum

```
We're upgrading from Gold to Platinum tier. This adds a two-agent system
(Cloud + Local) that communicates through a synced vault.

DO NOT touch existing folders. Create these NEW additions:

1. Create new folders:
   - /In_Progress/cloud/     ← Cloud agent claims items here
   - /In_Progress/local/     ← Local agent claims items here
   - /Updates/               ← Cloud writes status updates here
   - /Signals/               ← Cloud-to-Local signal files

2. Add domain subfolders to existing folders:
   - /Needs_Action/email/
   - /Needs_Action/social/
   - /Needs_Action/accounting/
   - /Plans/email/
   - /Plans/social/
   - /Plans/accounting/
   - /Pending_Approval/email/
   - /Pending_Approval/social/
   - /Pending_Approval/accounting/

3. Create /Updates/README.md:
   # Updates Folder
   Cloud agent writes status files here.
   Local agent reads them and merges into Dashboard.md.
   Files are moved to /Done after merging.

4. Create /Signals/README.md:
   # Signals Folder
   Used for Cloud → Local communication.
   Example signals: SYNC_NEEDED, URGENT_REVIEW, HEALTH_CHECK
   Local agent checks this folder on every sync.

5. Update Dashboard.md to add:
   ## Cloud Agent Status
   | Metric | Value |
   |--------|-------|
   | Cloud Status | ⏳ Not deployed yet |
   | Last Sync | Never |
   | Cloud Uptime | — |
   | Items Drafted (Cloud) | 0 |
   | Items Pending Approval | 0 |

6. Update Company_Handbook.md to add:
   ## Work-Zone Rules (Platinum)
   ### Cloud Agent CAN:
   - Read emails and draft replies
   - Generate social media post drafts
   - Read Odoo data (invoices, balances)
   - Create Plan.md files
   - Move items to /Pending_Approval

   ### Cloud Agent CANNOT:
   - Send any email
   - Publish any social media post
   - Create/update Odoo records
   - Make any payment
   - Update Dashboard.md directly (writes to /Updates instead)
   - Access WhatsApp session
   - Access banking credentials

   ### Local Agent OWNS:
   - All approvals (move files to /Approved or /Rejected)
   - All external sends (email, social, payments)
   - Dashboard.md updates (single-writer rule)
   - WhatsApp session
   - Banking/payment credentials

   ### Claim-by-Move Rule:
   - First agent to move an item from /Needs_Action to /In_Progress/{agent}/ owns it
   - Other agent MUST ignore items in /In_Progress
   - This prevents double-work
```

---

### Step 2: Set Up Git Vault Sync

#### Prompt 2 — Git Sync Configuration

```
Set up Git-based vault sync between Cloud and Local agents.

1. Initialize Git in the vault (if not already):
   cd D:\AI_Employee_Vault
   git init

2. Create a comprehensive .gitignore:
   # Secrets — NEVER sync these
   .env
   .env.*
   config/credentials.json
   config/token.json
   *.key
   *.pem

   # WhatsApp session data
   whatsapp_session/
   session_data/

   # MCP server credentials
   **/gcp-oauth.keys.json
   **/.gmail-mcp/

   # OS files
   .DS_Store
   Thumbs.db
   desktop.ini

   # Python
   __pycache__/
   *.pyc
   .venv/
   venv/

   # Node
   node_modules/

   # Obsidian internal
   .obsidian/workspace.json
   .obsidian/workspace-mobile.json

   # Docker volumes (Odoo data)
   odoo-data/
   db-data/

   # Large files
   *.zip
   *.tar.gz

3. Create a private GitHub repository:
   - Go to github.com → New Repository
   - Name: ai-employee-vault
   - Set to PRIVATE (important — your vault contains business data)
   - Do NOT initialize with README (we already have one)

4. Connect local vault to GitHub:
   git remote add origin https://github.com/YOUR_USERNAME/ai-employee-vault.git
   git add -A
   git commit -m "Platinum: initial vault sync setup"
   git push -u origin main

5. Create a sync script at scripts/vault_sync.bat (Windows Local):
   @echo off
   echo [%date% %time%] Starting vault sync...
   cd /d D:\AI_Employee_Vault

   REM Pull Cloud changes first
   git pull origin main --no-edit

   REM Push Local changes
   git add -A
   git commit -m "Local sync: %date% %time%" 2>nul
   git push origin main

   echo [%date% %time%] Sync complete.

6. Create a sync script for Cloud at scripts/vault_sync_cloud.sh (Linux — runs on EC2):
   #!/bin/bash
   echo "[$(date)] Starting cloud vault sync..."
   cd ~/AI_Employee_Vault

   # Pull Local changes
   git pull origin main --no-edit

   # Push Cloud changes
   git add -A
   git commit -m "Cloud sync: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
   git push origin main

   echo "[$(date)] Cloud sync complete."

7. Create Agent Skill at .claude/skills/vault-sync/SKILL.md:
   ---
   name: vault-sync
   description: Manage vault synchronization between Cloud and Local agents via Git. Handle merge conflicts, process /Updates files, and maintain sync state.
   version: 1.0.0
   ---

   Include:
   ## Sync Workflow
   1. Run git pull to get latest changes
   2. Check /Signals for any urgent messages from other agent
   3. Process /Updates files (merge into Dashboard.md if Local)
   4. Do your work (create files, process items)
   5. git add, commit, push

   ## Conflict Resolution
   - Dashboard.md: Local always wins (single-writer rule)
   - /Needs_Action files: keep both versions, rename with agent suffix
   - /Done files: keep both (no conflict possible)
   - .env files: NEVER synced (in .gitignore)

   ## Sync Frequency
   - Cloud: every 5 minutes (via cron on EC2)
   - Local: every 10 minutes (via Task Scheduler) OR on-demand
```

---

### Step 3: Set Up AWS EC2 VM (Cloud Server)

#### Prompt 3 — AWS Cloud VM Setup Guide

```
Create docs/aws-cloud-setup.md — a complete step-by-step guide to deploy the AI Employee
on AWS EC2 Free Tier.

This must be simple enough for a beginner. Include EVERY click.

## Part 1: Launch the EC2 Instance

1. Log into AWS Console: https://console.aws.amazon.com
2. Search "EC2" in the top search bar → click EC2 (the simple one, NOT Image Builder)
3. Click "Launch Instance" (orange button)

4. Configure:
   - Name: ai-employee-cloud
   - Application and OS Image: Click "Ubuntu" → select "Ubuntu Server 22.04 LTS (Free tier eligible)"
   - Instance type: t2.micro (says "Free tier eligible")
   - Key pair: Click "Create new key pair"
     - Name: ai-employee-key
     - Type: RSA
     - Format: .pem
     - Click Create → downloads .pem file
     - Save to D:\aws-keys\ai-employee-key.pem
   - Network settings:
     - ✅ Allow SSH traffic (from Anywhere)
     - ✅ Allow HTTPS traffic from the internet
     - ✅ Allow HTTP traffic from the internet
   - Storage: Change to 30 GB gp3 (free tier allows up to 30GB)

5. Click "Launch Instance"
6. Wait for status to show "Running"
7. Click on the instance → note the Public IPv4 address (example: 54.123.xx.xx)

## Part 2: Open Port 8069 for Odoo

1. In EC2 Dashboard → click your instance
2. Click the "Security" tab → click the Security Group link (sg-xxxxx)
3. Click "Edit inbound rules"
4. Click "Add rule":
   - Type: Custom TCP
   - Port range: 8069
   - Source: Anywhere-IPv4 (0.0.0.0/0)
5. Click "Save rules"

Now port 8069 (Odoo) is open alongside SSH (22), HTTP (80), and HTTPS (443).

## Part 3: Connect via SSH

Open PowerShell or Command Prompt on Windows:

# Fix permissions first (one-time)
icacls "D:\aws-keys\ai-employee-key.pem" /inheritance:r /grant:r "%USERNAME%:R"

# Connect
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_PUBLIC_IP

You should see: ubuntu@ip-xx-xx-xx-xx:~$
You are now inside your Cloud VM.

## Part 4: Install Software on Cloud VM

Run these commands one by one on the VM:

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev

# Install Node.js 24
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker ubuntu

# IMPORTANT: Log out and back in for docker group to take effect
exit

# SSH back in
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_PUBLIC_IP

# Install Git
sudo apt install -y git

# Install UV (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify everything
python3.13 --version
node --version
docker --version
git --version
uv --version
claude --version

## Part 5: Clone the Vault on Cloud VM

# Set up Git credentials (use your GitHub username and Personal Access Token)
git config --global user.name "YOUR_GITHUB_USERNAME"
git config --global user.email "YOUR_EMAIL"

# Clone vault
git clone https://github.com/YOUR_USERNAME/ai-employee-vault.git ~/AI_Employee_Vault
cd ~/AI_Employee_Vault

Note: If repo is private, you'll need a GitHub Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → select "repo" scope → Copy token
3. Use token as password when git asks for credentials
4. Or use: git clone https://YOUR_TOKEN@github.com/YOUR_USERNAME/ai-employee-vault.git

## Part 6: Create Cloud .env (secrets stay separate)

Create .env on the Cloud VM (CLOUD-SPECIFIC credentials):

nano ~/AI_Employee_Vault/.env

Add:
# Cloud Agent Identity
AGENT_ROLE=cloud

# Odoo (read-only for cloud)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_API_KEY=your_key

# Social Media (draft-only — no posting from cloud)
DRY_RUN=true

Save: Ctrl+O, Enter, Ctrl+X

## Part 7: Copy Gmail Credentials to Cloud (securely via SCP)

From your LOCAL Windows PC, copy credentials file:

scp -i "D:\aws-keys\ai-employee-key.pem" D:\AI_Employee_Vault\config\credentials.json ubuntu@YOUR_PUBLIC_IP:~/AI_Employee_Vault/config/

scp -i "D:\aws-keys\ai-employee-key.pem" D:\AI_Employee_Vault\config\token.json ubuntu@YOUR_PUBLIC_IP:~/AI_Employee_Vault/config/

IMPORTANT: These files are in .gitignore so they won't sync via Git.
You must copy them manually via SCP.

## Part 8: Keep Your VM IP From Changing (Elastic IP)

AWS changes your public IP when you stop/start the instance.
To get a permanent IP:

1. Go to EC2 Dashboard → Elastic IPs (left sidebar)
2. Click "Allocate Elastic IP address" → Allocate
3. Select the new IP → Actions → "Associate Elastic IP address"
4. Select your ai-employee-cloud instance → Associate

Now your IP stays the same even if you stop/start the VM.
FREE as long as it's associated with a running instance.

## Troubleshooting

### SSH: "Permission denied (publickey)"
→ Check key path is correct. Run: icacls on the .pem file.

### SSH: "Connection timed out"
→ Check Security Group has port 22 open. Check instance is "Running".

### "No space left on device"
→ You used less than 30GB storage. Increase EBS volume in AWS console.

### Docker: "permission denied"
→ Run: sudo usermod -aG docker ubuntu, then logout and login again.

### "t2.micro not available"
→ Try a different Availability Zone in the launch wizard dropdown.
```

---

### Step 4: Deploy Odoo on AWS EC2 (24/7)

#### Prompt 4 — Cloud Odoo Deployment

```
Create the Odoo deployment for the AWS EC2 VM with HTTPS and backups.

SSH into your EC2: ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_PUBLIC_IP

1. Create Odoo directory:
   mkdir -p ~/odoo-cloud/config ~/odoo-cloud/addons ~/odoo-cloud/ssl

2. Create ~/odoo-cloud/docker-compose.yml:

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
      - PASSWORD=odoo_secure_password_change_this
    restart: always

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo_secure_password_change_this
      - POSTGRES_USER=odoo
    volumes:
      - db-data:/var/lib/postgresql/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - odoo
    restart: always

volumes:
  odoo-data:
  db-data:

3. Create ~/odoo-cloud/nginx.conf:

server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://odoo:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

4. Generate self-signed SSL certificate:
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ~/odoo-cloud/ssl/key.pem \
     -out ~/odoo-cloud/ssl/cert.pem \
     -subj "/CN=ai-employee-odoo"

5. Create backup script at ~/odoo-cloud/backup.sh:
   #!/bin/bash
   BACKUP_DIR=~/odoo-backups
   mkdir -p $BACKUP_DIR
   DATE=$(date +%Y%m%d_%H%M%S)
   cd ~/odoo-cloud
   docker compose exec -T db pg_dump -U odoo postgres > $BACKUP_DIR/odoo_db_$DATE.sql
   ls -t $BACKUP_DIR/odoo_db_*.sql | tail -n +8 | xargs rm -f 2>/dev/null
   echo "Backup complete: odoo_db_$DATE.sql"

   chmod +x ~/odoo-cloud/backup.sh

6. Start Odoo:
   cd ~/odoo-cloud
   docker compose up -d

7. Wait 30 seconds, then access Odoo:
   - In browser: http://YOUR_EC2_PUBLIC_IP:8069
   - OR via HTTPS: https://YOUR_EC2_PUBLIC_IP (accept self-signed cert warning)
   - Create database: "ai_employee_db"
   - Set master password (write it down!)
   - Create admin user
   - Install modules: Accounting, Invoicing, Contacts
   - Create sample data (customers, invoices, payments)

8. Generate Odoo API Key:
   - Settings → Users → Your User → Preferences
   - Under "API Keys" → New API Key → name: "AI Employee Cloud"
   - Copy the key → update ~/AI_Employee_Vault/.env:
     ODOO_API_KEY=your_new_key

9. Set up daily backup cron:
   crontab -e
   # Add this line:
   0 2 * * * ~/odoo-cloud/backup.sh >> ~/logs/backup.log 2>&1

10. Create Agent Skill at .claude/skills/cloud-odoo/SKILL.md:
    ---
    name: cloud-odoo
    description: Cloud-specific Odoo integration. Cloud agent can READ Odoo data but CANNOT write. All write operations must go through /Pending_Approval for Local agent.
    version: 1.0.0
    ---
```

---

### Step 5: Cloud Agent Setup

#### Prompt 5 — Cloud Agent Configuration

```
Create the Cloud Agent — this runs 24/7 on the AWS EC2 VM.

1. Create cloud/cloud_agent.py — the main Cloud Agent:

This script runs continuously on the EC2 VM and does:

a) Every 2 minutes: Check Gmail for new emails
   - Use Gmail API (read-only)
   - Create action files in /Needs_Action/email/
   - Draft replies and save to /Pending_Approval/email/

b) Every 5 minutes: Sync vault via Git
   - git pull (get Local changes — approvals, rejections)
   - git add, commit, push (share new drafts with Local)

c) Every 30 minutes: Generate social media drafts
   - Read Business_Goals.md
   - Create post drafts in /Pending_Approval/social/

d) Every 60 minutes: Sync Odoo data (read-only)
   - Query Odoo for latest invoices and payments
   - Write summary to /Updates/odoo_sync_{timestamp}.md
   - Local will merge this into Dashboard.md

e) Every 5 minutes: Health check
   - Write heartbeat to /Signals/cloud_heartbeat.md with timestamp
   - Check error count, log system health

f) Claim-by-move logic:
   - Before processing any /Needs_Action item:
     1. Check if item is already in /In_Progress/local/ → skip
     2. Move item to /In_Progress/cloud/ → Cloud owns it
     3. Process the item
     4. Move to /Pending_Approval or /Done

Requirements:
- Use asyncio for concurrent operations
- Use ErrorHandler and AuditLogger from Gold tier
- Support --dry-run flag
- Log everything to /Logs/audit.jsonl
- On any error: log and continue (graceful degradation)

CLI:
  python3.13 cloud/cloud_agent.py
  python3.13 cloud/cloud_agent.py --dry-run

2. Create cloud/CLAUDE.md — Cloud-specific Claude Code configuration:
   # Cloud Agent Configuration

   You are the CLOUD AGENT for the AI Employee system.

   ## Your Identity
   - Role: CLOUD (draft-only)
   - Location: AWS EC2 VM
   - Running: 24/7

   ## What You CAN Do
   - Read emails from Gmail
   - Draft email replies (save to /Pending_Approval/email/)
   - Generate social media drafts (save to /Pending_Approval/social/)
   - Read Odoo accounting data
   - Create Plan.md files in /Plans/
   - Write status updates to /Updates/

   ## What You CANNOT Do (STRICTLY ENFORCED)
   - ✗ Send any email
   - ✗ Publish any social media post
   - ✗ Write to Odoo (create/update/delete)
   - ✗ Update Dashboard.md (write to /Updates instead)
   - ✗ Access WhatsApp
   - ✗ Make any payment

   ## Claim-by-Move Rule
   Before processing any item in /Needs_Action:
   1. Check /In_Progress/local/ — if item exists there, SKIP
   2. Move item to /In_Progress/cloud/
   3. Process it
   4. Move to /Pending_Approval or /Done

3. Create cloud/cloud_health_monitor.py:
   Simple script that checks if cloud_agent.py is running.
   If not running, restart it.
   Uses: subprocess, psutil (install with: pip install psutil)
   Checks: Is cloud_agent.py process alive?
   Action: If dead → restart → log to /Logs/errors.jsonl
   Frequency: Every 60 seconds
```

---

### Step 6: Local Agent Enhancement

#### Prompt 6 — Local Agent Updates

```
Update the Local Agent (your Windows PC) for Platinum two-agent communication.

1. Create local/local_agent.py — enhanced Local Agent:

a) Every 10 minutes (or on-demand): Sync vault
   - Run scripts/vault_sync.bat (git pull, git push)

b) After sync: Process /Updates from Cloud
   - Read all .md files in /Updates/
   - Merge data into Dashboard.md (Local owns Dashboard — single-writer rule)
   - Move processed update files to /Done

c) After sync: Check /Pending_Approval for Cloud-created items
   - List items that Cloud drafted
   - Notify user (write to a REVIEW_NEEDED signal)
   - Wait for human to move files to /Approved or /Rejected

d) After approval: Execute approved actions
   - Email sends: use Gmail MCP
   - Social posts: use Social Media MCP or Playwright
   - Odoo writes: use Odoo MCP
   - Move completed items to /Done

e) Claim-by-move logic (same as Cloud):
   - Check /In_Progress/cloud/ before claiming any item
   - Move to /In_Progress/local/ before processing

f) Check /Signals for Cloud heartbeat:
   - If cloud_heartbeat.md is older than 15 minutes → log warning
   - If older than 1 hour → create URGENT item

2. Create Agent Skill at .claude/skills/local-agent/SKILL.md:
   ---
   name: local-agent
   description: Local agent operations for Platinum tier. Handles approvals, executes sends, merges Dashboard updates, manages vault sync. Local agent is the ONLY agent that can execute external actions.
   version: 1.0.0
   ---

3. Update existing orchestrator.py to check AGENT_ROLE from .env:
   - If AGENT_ROLE=cloud → run cloud_agent.py behavior
   - If AGENT_ROLE=local → run local_agent.py behavior
   - If not set → run Gold-tier behavior (single agent)
```

---

### Step 7: Cloud Cron Jobs + Systemd (Always-On)

#### Prompt 7 — Cloud Scheduling and Auto-Restart

```
Set up cron jobs AND systemd on the AWS EC2 VM for 24/7 operation.

SSH into the EC2 VM first.

PART 1: Create systemd service (auto-starts on boot, restarts on crash)

sudo nano /etc/systemd/system/ai-employee-cloud.service

Content:
[Unit]
Description=AI Employee Cloud Agent
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AI_Employee_Vault
ExecStart=/usr/bin/python3.13 cloud/cloud_agent.py
Restart=always
RestartSec=30
Environment=PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=/home/ubuntu/AI_Employee_Vault/.env

StandardOutput=append:/home/ubuntu/logs/cloud_agent.log
StandardError=append:/home/ubuntu/logs/cloud_agent_error.log

[Install]
WantedBy=multi-user.target

Enable and start:
mkdir -p ~/logs
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-cloud
sudo systemctl start ai-employee-cloud

USEFUL COMMANDS:
sudo systemctl status ai-employee-cloud   # Check if running
sudo systemctl restart ai-employee-cloud  # Restart
sudo systemctl stop ai-employee-cloud     # Stop
journalctl -u ai-employee-cloud -f        # Watch live logs
tail -f ~/logs/cloud_agent.log            # Watch log file

PART 2: Set up cron jobs

crontab -e

Add:
# ─── AI EMPLOYEE CLOUD CRON JOBS ───

# Git vault sync every 5 minutes
*/5 * * * * cd ~/AI_Employee_Vault && bash scripts/vault_sync_cloud.sh >> ~/logs/sync.log 2>&1

# Odoo daily backup at 2:00 AM
0 2 * * * bash ~/odoo-cloud/backup.sh >> ~/logs/backup.log 2>&1

# Health monitor every 10 minutes
*/10 * * * * cd ~/AI_Employee_Vault && python3.13 cloud/cloud_health_monitor.py >> ~/logs/health.log 2>&1

# Weekly CEO briefing data prep (Sunday 6 PM UTC)
0 18 * * 0 cd ~/AI_Employee_Vault && claude --print "Prepare CEO briefing data: gather Odoo metrics, count processed items, save to /Updates/weekly_data.md" >> ~/logs/briefing.log 2>&1

PART 3: Verify everything is running

sudo systemctl status ai-employee-cloud   # Should show "active (running)"
crontab -l                                 # Should show all cron entries
docker compose -f ~/odoo-cloud/docker-compose.yml ps  # Should show odoo + db + nginx running
```

---

### Step 8: Local Agent Scheduling (Windows Task Scheduler)

#### Prompt 8 — Windows Scheduling

```
Set up Windows Task Scheduler for the Local Agent.

Create docs/windows-scheduler-platinum.md:

## Task 1: Local Agent Run (every 10 minutes)
- Program: python
- Arguments: local/local_agent.py --once
- Working directory: D:\AI_Employee_Vault
- Trigger: Every 10 minutes

## Task 2: Vault Sync (every 10 minutes)
- Program: cmd
- Arguments: /c "D:\AI_Employee_Vault\scripts\vault_sync.bat"
- Trigger: Every 10 minutes

## Task 3: Daily Morning Routine (8:00 AM)
- Program: cmd
- Arguments: /c "D:\AI_Employee_Vault\scripts\scheduler.bat daily"
- Trigger: Daily at 8:00 AM

## Task 4: CEO Briefing (Monday 7:00 AM)
- Program: cmd
- Arguments: /c "D:\AI_Employee_Vault\scripts\scheduler.bat ceo-briefing"
- Trigger: Weekly, Monday at 7:00 AM

How to create a task:
1. Open Start Menu → search "Task Scheduler" → open it
2. Click "Create Basic Task..."
3. Name: AI-Employee-LocalAgent
4. Trigger: Daily → Repeat every 10 minutes for 1 day
5. Action: Start a program
6. Program: python
7. Arguments: local/local_agent.py --once
8. Start in: D:\AI_Employee_Vault
9. Finish → check "Open Properties" → under Settings, check "Run whether user is logged on or not"
```

---

### Step 9: The Platinum Demo Flow (MUST PASS)

#### Prompt 9 — Implement the Required Demo

```
The hackathon document requires this EXACT demo to pass Platinum:

"Email arrives while Local is offline → Cloud drafts reply + writes approval file →
 when Local returns, user approves → Local executes send via MCP → logs → moves task to /Done"

Implement this end-to-end:

1. Create tests/platinum_demo.py that simulates the full flow:

   Step 1: "Local goes offline" (stop local_agent, stop syncing)
   Step 2: Send a test email to your Gmail
   Step 3: Cloud Agent on EC2 detects the email (Gmail watcher)
   Step 4: Cloud creates /Needs_Action/email/EMAIL_test_{id}.md
   Step 5: Cloud moves to /In_Progress/cloud/ (claim-by-move)
   Step 6: Cloud drafts a reply
   Step 7: Cloud saves draft to /Pending_Approval/email/REPLY_test_{id}.md
   Step 8: Cloud runs git push (cron syncs vault)
   Step 9: "Local comes back online" — run scripts\vault_sync.bat
   Step 10: Local runs git pull (gets Cloud's work)
   Step 11: Open Obsidian → see /Pending_Approval/email/REPLY_test_{id}.md
   Step 12: Review draft → move file to /Approved/email/
   Step 13: Local Agent reads /Approved file
   Step 14: Local sends email via Gmail MCP
   Step 15: Local logs to /Logs/audit.jsonl
   Step 16: Local moves to /Done/REPLY_test_{id}.md
   Step 17: Local runs git push (syncs completion)
   Step 18: Verify: audit log, /Done has file, email sent

2. Create docs/platinum-demo-walkthrough.md:
   Step-by-step screen-by-screen for recording the demo video.
   Include: what to show, what to say, expected time per step.

This is the MINIMUM PASSING GATE for Platinum. If this works, you pass.
```

---

### Step 10: Update CLAUDE.md and README.md

#### Prompt 10 — Final Documentation

```
Update all documentation for Platinum tier:

1. Update CLAUDE.md:
   - Two-agent system (AWS EC2 Cloud + Local Windows)
   - Work-zone specialization rules
   - Claim-by-move rule
   - Vault sync via Git
   - Security: secrets never sync
   - /Updates and /Signals folder usage
   - Single-writer rule for Dashboard.md

2. Update README.md:
   - Tier: Platinum
   - Architecture diagram (AWS EC2 + Local + Git sync)
   - All MCP servers, Agent Skills listed
   - Setup instructions
   - Demo video script
   - Lessons learned

3. Create docs/how-to-run.md — COMPLETE run instructions:

   ## Running Locally Only (Development / Bronze-Gold)
   cd D:\AI_Employee_Vault
   
   # Start watchers (each in separate terminal)
   python watchers/filesystem_watcher.py
   python watchers/gmail_watcher.py
   
   # Start orchestrator
   python orchestrator.py
   
   # Open Claude Code
   claude

   ## Running Cloud Agent Only (Test EC2)
   ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_EC2_IP
   cd ~/AI_Employee_Vault
   sudo systemctl start ai-employee-cloud
   sudo systemctl status ai-employee-cloud
   
   # Watch logs
   tail -f ~/logs/cloud_agent.log

   ## Running BOTH (Platinum Mode — Production)
   
   ### On AWS EC2 (Cloud):
   ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_EC2_IP
   
   # Start Odoo (if not running)
   cd ~/odoo-cloud && docker compose up -d
   
   # Start Cloud Agent (or verify it's running)
   sudo systemctl start ai-employee-cloud
   sudo systemctl status ai-employee-cloud
   
   # Verify cron is set up
   crontab -l
   
   # Check Odoo is accessible
   curl -s http://localhost:8069 | head -5

   ### On Local PC (Windows):
   cd D:\AI_Employee_Vault
   
   # Pull latest from Cloud
   git pull origin main
   
   # Start Local Agent
   python local/local_agent.py
   
   # Or sync manually
   scripts\vault_sync.bat
   
   # Open Obsidian to review pending approvals
   # Check /Pending_Approval folder

   ## Stopping Everything
   
   ### Cloud (SSH into EC2):
   sudo systemctl stop ai-employee-cloud
   cd ~/odoo-cloud && docker compose down
   
   ### Local:
   Ctrl+C on local_agent.py
   Close Claude Code

   ## Verifying Everything Works
   1. Obsidian Dashboard.md — all sections populated
   2. /Logs/audit.jsonl — entries from both "cloud" and "local" agents
   3. /Signals/cloud_heartbeat.md — timestamp within 15 minutes
   4. sudo systemctl status ai-employee-cloud — shows "active (running)"
   5. Odoo accessible at http://YOUR_EC2_IP:8069
   6. git log — commits from both "Cloud sync" and "Local sync"
```

---

### Step 11: Test Everything

#### Prompt 11A — Test Cloud Agent on EC2

```
Test the Cloud Agent on the EC2 VM:

1. SSH into EC2
2. Check Cloud Agent status: sudo systemctl status ai-employee-cloud
3. Send a test email to your Gmail
4. Watch logs: tail -f ~/logs/cloud_agent.log
5. Wait 2-3 minutes for detection
6. Check /Needs_Action/email/ for new file
7. Check /Pending_Approval/email/ for draft reply
8. Run: git log --oneline -5  (should show "Cloud sync" commits)
9. Check /Logs/audit.jsonl for entries
10. Check /Signals/cloud_heartbeat.md has recent timestamp
```

#### Prompt 11B — Test Full Platinum Demo

```
Run the full Platinum demo end-to-end:

1. Verify Cloud Agent running on EC2: sudo systemctl status ai-employee-cloud
2. On Local PC: stop local_agent.py (simulate "offline")
3. Send test email to your Gmail from another account
4. Wait 2-3 minutes
5. SSH into EC2: check /Pending_Approval/email/ has the draft
6. On Local PC: run git pull origin main
7. Open Obsidian → see the draft in /Pending_Approval/email/
8. Review the draft → move file to /Approved/email/ in Obsidian
9. Start Local Agent: python local/local_agent.py --once
10. Verify: email sent (or logged in dry-run)
11. Check /Done/ for completed item
12. Check /Logs/audit.jsonl for full trace
13. Run: git push origin main
14. SSH into EC2: git pull → verify /Done has the file
```

---

### Step 12: Final Git Commit

#### Prompt 12 — Commit Platinum

```
Final commit for Platinum tier:

1. git add -A
2. Verify NOT staged:
   - .env (all locations)
   - credentials.json, token.json
   - SSH keys (.pem files)
   - WhatsApp session data
   - Docker volume data
3. git commit -m "Platinum tier: AWS EC2 cloud, two-agent system, vault sync, Odoo 24/7 with HTTPS, work-zone specialization, claim-by-move, systemd service, health monitoring"
4. git push origin main
5. Show complete file tree
6. Count: total files, total skills, total MCP servers
```

---

## Platinum Tier Final Checklist

| # | Requirement | How to Verify |
|---|------------|---------------|
| 1 | Cloud VM running 24/7 | SSH → `systemctl status ai-employee-cloud` = active |
| 2 | Work-zone specialization | Cloud only drafts, Local only executes — audit log confirms |
| 3 | Vault sync via Git | `git log` shows "Cloud sync" and "Local sync" commits |
| 4 | Claim-by-move | Items in /In_Progress/cloud/ are not processed by Local |
| 5 | Secrets never sync | `git show HEAD:.env` returns error (not tracked) |
| 6 | Odoo on Cloud with HTTPS | Browser: https://YOUR_EC2_IP loads Odoo |
| 7 | **Platinum demo passes** | Email → Cloud drafts → approve → Local sends → Done ✅ |
| 8 | Health monitoring | /Signals/cloud_heartbeat.md has recent timestamp |

---

## Demo Video Script (5-10 minutes)

1. **Architecture Overview** (1 min): Show Cloud (AWS EC2) + Local (Windows) + Git sync diagram
2. **AWS EC2** (1 min): SSH in, show `systemctl status`, show Odoo running
3. **Go "Offline"** (30 sec): Close Local Agent on your PC
4. **Send Test Email** (30 sec): Send email from another account
5. **Cloud Processes** (1 min): Show Cloud logs detecting email, creating draft
6. **Vault Sync** (30 sec): Show git log with Cloud commit
7. **Come "Online"** (30 sec): Run git pull on Local, open Obsidian
8. **Review Draft** (1 min): Show /Pending_Approval in Obsidian, review the draft
9. **Approve** (30 sec): Move file to /Approved in Obsidian
10. **Execute** (1 min): Local Agent sends email via MCP, moves to /Done
11. **Verify** (1 min): Show audit log, Dashboard.md, /Done folder
12. **Summary** (30 sec): AWS Free Tier, production-ready, 24/7 operation

---

## AWS Free Tier Important Notes

| Limit | Value | What It Means |
|-------|-------|---------------|
| t2.micro hours | 750/month | Enough for 1 instance running 24/7 (744 hrs/month) ✅ |
| EBS storage | 30 GB | Enough for vault + Odoo + Docker ✅ |
| Data transfer | 100 GB/month outbound | More than enough for Git sync + Odoo ✅ |
| Duration | 12 months free | Covers hackathon period ✅ |
| Elastic IP | Free (if associated) | Permanent IP, no extra cost ✅ |

**After 12 months:** t2.micro costs ~$8.50/month. You can stop the instance or migrate to Oracle Free Tier (which is forever free) later.

---

## Complete System Architecture (Platinum)

```
                    ┌─────────────────────────────────┐
                    │        GITHUB (Private)          │
                    │     ai-employee-vault repo       │
                    │    (markdown + code only)         │
                    │    (NO secrets, NO tokens)        │
                    └──────────┬──────┬────────────────┘
                         git push  git pull
                    ┌──────────┴──┐  ┌┴──────────────┐
                    │             │  │                │
   ┌────────────────▼──┐    ┌────▼──▼────────────────┐
   │  AWS EC2 (24/7)    │    │  LOCAL PC (Windows)     │
   │  t2.micro Ubuntu   │    │  D:\AI_Employee_Vault   │
   │                    │    │                         │
   │ ┌────────────────┐ │    │ ┌─────────────────────┐ │
   │ │ Cloud Agent    │ │    │ │ Local Agent         │ │
   │ │ (systemd)      │ │    │ │ (Task Scheduler)    │ │
   │ │ (draft-only)   │ │    │ │ (approve + execute) │ │
   │ └───┬────────────┘ │    │ └───┬─────────────────┘ │
   │     │              │    │     │                   │
   │ ┌───▼────────────┐ │    │ ┌───▼─────────────────┐ │
   │ │ Gmail Watcher  │ │    │ │ Gmail MCP (send)    │ │
   │ │ (read-only)    │ │    │ │ Odoo MCP (write)    │ │
   │ └────────────────┘ │    │ │ Social MCP (post)   │ │
   │                    │    │ └─────────────────────┘ │
   │ ┌────────────────┐ │    │                         │
   │ │ Odoo (Docker)  │ │    │ ┌─────────────────────┐ │
   │ │ HTTPS + Backup │ │    │ │ Obsidian GUI        │ │
   │ └────────────────┘ │    │ │ (Dashboard, Review)  │ │
   │                    │    │ └─────────────────────┘ │
   │ ┌────────────────┐ │    │                         │
   │ │ Cron + systemd │ │    │ ┌─────────────────────┐ │
   │ │ (auto-restart) │ │    │ │ Human (YOU)         │ │
   │ └────────────────┘ │    │ │ Approve/Reject      │ │
   └────────────────────┘    │ └─────────────────────┘ │
                             └─────────────────────────┘
```

---

## Troubleshooting

### Can't SSH into AWS EC2
→ Check key path: `icacls "D:\aws-keys\ai-employee-key.pem" /inheritance:r /grant:r "%USERNAME%:R"`
→ Check Security Group has port 22 open
→ Check instance is in "Running" state

### Odoo won't start on EC2
→ Run: `cd ~/odoo-cloud && docker compose logs` to see errors
→ Common: port 8069 already in use, or not enough RAM (t2.micro has 1GB — Odoo needs ~512MB)
→ If RAM issue: add 1GB swap file:
   sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile

### Odoo MCP returns "connection refused"
→ Odoo must be running: `docker compose ps` should show odoo + db "Up"
→ Check: `curl http://localhost:8069` should return HTML

### Git sync conflicts
→ Dashboard.md: Local always wins → `git checkout --ours Dashboard.md && git add Dashboard.md && git commit`
→ Other conflicts: keep both versions, rename manually

### Cloud Agent keeps crashing
→ Check: `journalctl -u ai-employee-cloud -n 50`
→ Common: missing Python dependency, .env not found, Gmail token expired
→ Fix dependency: `cd ~/AI_Employee_Vault && uv sync`

### EC2 instance stops unexpectedly
→ Free tier instances sometimes get stopped if AWS detects abuse
→ Check: EC2 Dashboard → instance state
→ Just start it again → systemd auto-restarts the Cloud Agent

### Public IP changed
→ You forgot to assign Elastic IP
→ Go to EC2 → Elastic IPs → Allocate → Associate with your instance

---

*Built with AIDD methodology using Claude Code CLI for Panaversity Hackathon 0*
*Platinum Tier — AWS EC2 Free Tier (meets all hackathon requirements)*
*Estimated 60+ hours*
