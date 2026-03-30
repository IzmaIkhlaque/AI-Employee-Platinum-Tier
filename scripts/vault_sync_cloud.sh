#!/bin/bash
echo "[$(date)] Starting cloud vault sync..."
cd ~/AI_Employee_Vault

# Pull Local changes
git pull origin main --no-edit
if [ $? -ne 0 ]; then
    echo "[$(date)] ERROR: git pull failed. Check for conflicts."
    exit 1
fi

# Push Cloud changes
git add -A
git commit -m "Cloud sync: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
git push origin main
if [ $? -ne 0 ]; then
    echo "[$(date)] ERROR: git push failed."
    exit 1
fi

echo "[$(date)] Cloud sync complete."
