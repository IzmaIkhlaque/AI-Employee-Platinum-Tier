# AWS EC2 Cloud Agent Setup Guide

Deploy the AI Employee Cloud Agent on AWS EC2 Free Tier.
This guide covers every click — no prior AWS experience needed.

---

## Part 1: Launch the EC2 Instance

1. Log into AWS Console: https://console.aws.amazon.com
2. Search **"EC2"** in the top search bar → click **EC2** (the simple one, NOT Image Builder)
3. Click **"Launch Instance"** (orange button)

4. Configure:
   - **Name:** `ai-employee-cloud`
   - **Application and OS Image:** Click **"Ubuntu"** → select **"Ubuntu Server 22.04 LTS (Free tier eligible)"**
   - **Instance type:** `t2.micro` (says "Free tier eligible")
   - **Key pair:** Click **"Create new key pair"**
     - Name: `ai-employee-key`
     - Type: RSA
     - Format: `.pem`
     - Click **Create** → file downloads automatically
     - Save to `D:\aws-keys\ai-employee-key.pem`
   - **Network settings:**
     - ✅ Allow SSH traffic (from Anywhere)
     - ✅ Allow HTTPS traffic from the internet
     - ✅ Allow HTTP traffic from the internet
   - **Storage:** Change to **30 GB gp3** (free tier allows up to 30 GB)

5. Click **"Launch Instance"**
6. Wait for status to show **"Running"**
7. Click on the instance → note the **Public IPv4 address** (example: `54.123.xx.xx`)

---

## Part 2: Open Port 8069 for Odoo

1. In EC2 Dashboard → click your instance
2. Click the **"Security"** tab → click the Security Group link (`sg-xxxxx`)
3. Click **"Edit inbound rules"**
4. Click **"Add rule"**:
   - Type: Custom TCP
   - Port range: `8069`
   - Source: Anywhere-IPv4 (`0.0.0.0/0`)
5. Click **"Save rules"**

Now port 8069 (Odoo) is open alongside SSH (22), HTTP (80), and HTTPS (443).

---

## Part 3: Connect via SSH

Open **PowerShell** or **Command Prompt** on Windows:

```powershell
# Fix permissions first (one-time — required or SSH will reject the key)
icacls "D:\aws-keys\ai-employee-key.pem" /inheritance:r /grant:r "%USERNAME%:R"

# Connect
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_PUBLIC_IP
```

You should see: `ubuntu@ip-xx-xx-xx-xx:~$`
You are now inside your Cloud VM.

---

## Part 4: Install Software on Cloud VM

Run these commands one by one on the VM:

```bash
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
```

SSH back in:

```powershell
ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_PUBLIC_IP
```

```bash
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
```

---

## Part 5: Clone the Vault on Cloud VM

```bash
# Set up Git identity
git config --global user.name "YOUR_GITHUB_USERNAME"
git config --global user.email "YOUR_EMAIL"

# Clone vault
git clone https://github.com/IzmaIkhlaque/AI-Employee-Gold-Tier.git ~/AI_Employee_Vault
cd ~/AI_Employee_Vault
```

> **Note:** Since the repo is private, Git will ask for credentials.
> Use a **GitHub Personal Access Token** instead of your password:
>
> 1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
> 2. **Generate new token** → select **"repo"** scope → Copy token
> 3. Paste the token when Git asks for a password
>
> Or embed the token directly in the URL to avoid repeated prompts:
> ```bash
> git clone https://YOUR_TOKEN@github.com/IzmaIkhlaque/AI-Employee-Gold-Tier.git ~/AI_Employee_Vault
> ```

---

## Part 6: Create Cloud .env (secrets stay local, never in Git)

```bash
nano ~/AI_Employee_Vault/.env
```

Paste the following (replace placeholder values):

```env
# Cloud Agent Identity
AGENT_ROLE=cloud

# Odoo (read-only for cloud)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_API_KEY=your_key

# Social Media (draft-only — no posting from cloud)
SOCIAL_DRY_RUN=true
```

Save: **Ctrl+O** → **Enter** → **Ctrl+X**

---

## Part 7: Copy Gmail Credentials to Cloud (securely via SCP)

Run these commands from your **LOCAL Windows PC** (not the VM):

```powershell
# Copy OAuth credentials
scp -i "D:\aws-keys\ai-employee-key.pem" "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault\config\credentials.json" ubuntu@YOUR_PUBLIC_IP:~/AI_Employee_Vault/config/

# Copy OAuth token
scp -i "D:\aws-keys\ai-employee-key.pem" "D:\Izma folder\Governer sindh course\Q4\GEMINI_CLI\HACKATHONS\Ai-Employee-FTE\AI_Employee_Vault\config\token.json" ubuntu@YOUR_PUBLIC_IP:~/AI_Employee_Vault/config/
```

> **IMPORTANT:** Both files are listed in `.gitignore` and will never sync via Git.
> You must copy them manually via SCP every time they change.

---

## Part 8: Keep Your VM IP From Changing (Elastic IP)

AWS assigns a new public IP each time you stop and start your instance.
To get a permanent IP (free while associated with a running instance):

1. Go to **EC2 Dashboard** → **Elastic IPs** (left sidebar, under Network & Security)
2. Click **"Allocate Elastic IP address"** → **Allocate**
3. Select the new IP → **Actions** → **"Associate Elastic IP address"**
4. Select your `ai-employee-cloud` instance → **Associate**

Your IP now stays the same across stop/start cycles.

---

## Part 9: Set Up Vault Sync Cron (Cloud Agent Auto-Sync)

On the VM, open the cron editor:

```bash
crontab -e
```

Add these lines at the bottom:

```cron
# Sync vault with GitHub every 5 minutes
*/5 * * * * cd ~/AI_Employee_Vault && bash scripts/vault_sync_cloud.sh >> ~/sync.log 2>&1

# Run Claude health check every hour
0 * * * * cd ~/AI_Employee_Vault && claude --print "Run a health check on all MCP servers and write the result to /Signals/SIGNAL_HEALTH_CHECK_$(date +\%Y\%m\%d_\%H\%M\%S).md" >> ~/claude.log 2>&1
```

Save and exit (in nano: **Ctrl+O** → **Enter** → **Ctrl+X**).

Verify cron is running:

```bash
crontab -l
tail -f ~/sync.log
```

---

## Troubleshooting

### SSH: "Permission denied (publickey)"
Check that you ran `icacls` to fix the key permissions. The `.pem` file must not be
readable by other users — Windows rejects keys with open permissions.

```powershell
icacls "D:\aws-keys\ai-employee-key.pem" /inheritance:r /grant:r "%USERNAME%:R"
```

### SSH: "Connection timed out"
- Check the Security Group has port 22 open (Anywhere-IPv4)
- Check the instance status is **"Running"** in EC2 console
- If you assigned an Elastic IP, use that IP — not the old one

### "No space left on device"
You may have exceeded the 30 GB storage allocation. Check usage:
```bash
df -h
```
Increase the EBS volume size in AWS console: **EC2 → Volumes → Modify Volume**.

### Docker: "permission denied while trying to connect to Docker daemon"
You need to log out and back in after the `usermod` command:
```bash
sudo usermod -aG docker ubuntu
exit
# SSH back in, then test:
docker run hello-world
```

### "t2.micro not available in this Availability Zone"
In the launch wizard, scroll down to **"Advanced details"** → change the
**Availability Zone** to a different one (e.g., us-east-1b instead of us-east-1a).

### Git push fails on Cloud VM: "Authentication failed"
Your Personal Access Token may have expired. Generate a new one on GitHub and
update the remote URL:
```bash
git remote set-url origin https://NEW_TOKEN@github.com/IzmaIkhlaque/AI-Employee-Gold-Tier.git
```
