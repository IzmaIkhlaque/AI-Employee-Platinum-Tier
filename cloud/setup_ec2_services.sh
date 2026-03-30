#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# AI Employee — EC2 Service Setup
# Run this ONCE on the EC2 VM after cloning the vault.
#
# Usage:
#   bash cloud/setup_ec2_services.sh
#   bash cloud/setup_ec2_services.sh --dry-run   (print commands, don't run)
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

VAULT_DIR="$HOME/AI_Employee_Vault"
LOG_DIR="$HOME/logs"
SERVICE_SRC="$VAULT_DIR/cloud/ai-employee-cloud.service"
SERVICE_DST="/etc/systemd/system/ai-employee-cloud.service"
CRONTAB_TMP="/tmp/ai_employee_crontab_$$.txt"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "[setup] DRY-RUN mode — commands will be printed but not executed"
fi

run() {
    if $DRY_RUN; then
        echo "  [DRY-RUN] $*"
    else
        "$@"
    fi
}

echo ""
echo "=========================================="
echo "  AI Employee EC2 Service Setup"
echo "=========================================="
echo "  Vault : $VAULT_DIR"
echo "  Logs  : $LOG_DIR"
echo ""

# ── 1. Create log directory ───────────────────────────────────────────────────
echo "[1/4] Creating log directory..."
run mkdir -p "$LOG_DIR"
echo "      -> $LOG_DIR"

# ── 2. Install systemd service ────────────────────────────────────────────────
echo "[2/4] Installing systemd service..."

if [[ ! -f "$SERVICE_SRC" ]]; then
    echo "ERROR: Service file not found at $SERVICE_SRC"
    echo "       Run 'git pull' in the vault first."
    exit 1
fi

run sudo cp "$SERVICE_SRC" "$SERVICE_DST"
echo "      -> Copied to $SERVICE_DST"

run sudo systemctl daemon-reload
run sudo systemctl enable ai-employee-cloud
run sudo systemctl start ai-employee-cloud

echo "      -> Service enabled and started"
echo ""

if ! $DRY_RUN; then
    sleep 2
    echo "      Service status:"
    sudo systemctl status ai-employee-cloud --no-pager --lines=5 || true
fi

# ── 3. Install cron jobs ──────────────────────────────────────────────────────
echo "[3/4] Installing cron jobs..."

# Preserve any existing crontab lines that are NOT ours
if crontab -l 2>/dev/null | grep -v "AI EMPLOYEE" | grep -v "AI_Employee_Vault" > "$CRONTAB_TMP" 2>/dev/null; then
    true
else
    # No existing crontab — start fresh
    true > "$CRONTAB_TMP"
fi

# Append our cron block
cat >> "$CRONTAB_TMP" << 'CRON'

# ─── AI EMPLOYEE CLOUD CRON JOBS ───────────────────────────────────────────

# Git vault sync every 5 minutes
*/5 * * * * cd ~/AI_Employee_Vault && bash scripts/vault_sync_cloud.sh >> ~/logs/sync.log 2>&1

# Odoo daily backup at 2:00 AM
0 2 * * * bash ~/odoo-cloud/backup.sh >> ~/logs/backup.log 2>&1

# Health monitor every 10 minutes (--once flag prevents process pile-up)
*/10 * * * * cd ~/AI_Employee_Vault && python3.13 cloud/cloud_health_monitor.py --once >> ~/logs/health.log 2>&1

# Weekly CEO briefing data prep (Sunday 6 PM UTC)
0 18 * * 0 cd ~/AI_Employee_Vault && claude --print "Prepare CEO briefing data: gather Odoo metrics, count processed items, save to /Updates/weekly_data.md" >> ~/logs/briefing.log 2>&1

# ───────────────────────────────────────────────────────────────────────────
CRON

if $DRY_RUN; then
    echo "  [DRY-RUN] Would install crontab:"
    cat "$CRONTAB_TMP"
else
    crontab "$CRONTAB_TMP"
    echo "      -> Cron jobs installed"
    echo ""
    echo "      Installed cron entries:"
    crontab -l | grep -A 20 "AI EMPLOYEE" || true
fi

rm -f "$CRONTAB_TMP"

# ── 4. Verify everything ──────────────────────────────────────────────────────
echo ""
echo "[4/4] Verification..."

if $DRY_RUN; then
    echo "  [DRY-RUN] Skipping live checks"
else
    echo ""
    echo "  systemd service:"
    if sudo systemctl is-active --quiet ai-employee-cloud; then
        echo "  -> ai-employee-cloud  ACTIVE (running)"
    else
        echo "  -> ai-employee-cloud  NOT RUNNING — check logs:"
        echo "     journalctl -u ai-employee-cloud -n 20 --no-pager"
    fi

    echo ""
    echo "  Odoo containers:"
    docker compose -f "$HOME/odoo-cloud/docker-compose.yml" ps 2>/dev/null || \
        echo "  -> Odoo not started yet (run: cd ~/odoo-cloud && docker compose up -d)"

    echo ""
    echo "  Cron jobs:"
    crontab -l | grep "AI_Employee_Vault" | wc -l | xargs -I{} echo "  -> {} AI Employee cron entries installed"
fi

echo ""
echo "=========================================="
echo "  Setup complete."
echo "=========================================="
echo ""
echo "  Useful commands:"
echo "  sudo systemctl status ai-employee-cloud   # Service status"
echo "  sudo systemctl restart ai-employee-cloud  # Restart agent"
echo "  journalctl -u ai-employee-cloud -f        # Live systemd logs"
echo "  tail -f ~/logs/cloud_agent.log            # Live agent log"
echo "  tail -f ~/logs/sync.log                   # Live sync log"
echo "  crontab -l                                # Show cron jobs"
echo ""
