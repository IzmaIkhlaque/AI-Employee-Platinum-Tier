---
name: vault-sync
description: Manage vault synchronization between Cloud and Local agents via Git. Handle merge conflicts, process /Updates files, and maintain sync state.
version: 1.0.0
---

# Vault Sync Skill

## Sync Workflow

1. Run `git pull` to get latest changes from the other agent
2. Check `/Signals` for any urgent messages from the other agent
3. Process `/Updates` files (merge into Dashboard.md if running as Local agent)
4. Do your work (create files, process items)
5. `git add -A`, commit with descriptive message, `git push`

## Conflict Resolution

- **Dashboard.md** — Local always wins (single-writer rule). Cloud writes updates to `/Updates/` instead; Local merges them in.
- **/Needs_Action files** — Keep both versions, rename with agent suffix (e.g., `_cloud`, `_local`) to avoid collision.
- **/Done files** — Keep both (no conflict possible — filenames include timestamps).
- **.env files** — NEVER synced (in .gitignore). Each agent manages its own credentials locally.
- **/In_Progress files** — Never modify the other agent's claimed items.

## Claim-by-Move Rule

Before working on any `/Needs_Action` item:
1. Move the file to `/In_Progress/cloud/` (if Cloud) or `/In_Progress/local/` (if Local)
2. Commit and push immediately — this is the claim
3. If pull reveals the other agent already claimed it, abort and pick a different item

## Sync Frequency

- **Cloud agent:** every 5 minutes via cron on EC2
  ```
  */5 * * * * cd ~/AI_Employee_Vault && bash scripts/vault_sync_cloud.sh >> ~/sync.log 2>&1
  ```
- **Local agent:** every 10 minutes via Windows Task Scheduler OR on-demand
  ```
  scripts\vault_sync.bat
  ```

## Signal Files

To send an urgent message to the other agent, create a file in `/Signals/`:

```
SIGNAL_SYNC_NEEDED_20260326_100000.md
SIGNAL_URGENT_REVIEW_20260326_100000.md
SIGNAL_HEALTH_CHECK_20260326_100000.md
```

Signal files are deleted by the receiving agent after processing.

## Remote

- Repository: `https://github.com/IzmaIkhlaque/AI-Employee-Gold-Tier.git`
- Branch: `main`
- Access: Cloud agent needs a Personal Access Token (PAT) or deploy key configured on the EC2 instance
