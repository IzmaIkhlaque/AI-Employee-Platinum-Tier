#!/bin/bash
BACKUP_DIR=~/odoo-backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
cd ~/odoo-cloud
docker compose exec -T db pg_dump -U odoo postgres > $BACKUP_DIR/odoo_db_$DATE.sql
ls -t $BACKUP_DIR/odoo_db_*.sql | tail -n +8 | xargs rm -f 2>/dev/null
echo "Backup complete: odoo_db_$DATE.sql"
