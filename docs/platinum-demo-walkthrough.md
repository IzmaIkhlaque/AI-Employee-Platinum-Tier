# Platinum Demo Walkthrough
### AI Employee — Minimum Passing Gate

**Total demo time:** ~4 minutes
**What you're proving:** End-to-end two-agent communication with human-in-the-loop approval

---

## The Story (say this out loud at the start)

> "This is the AI Employee running at Platinum tier. I have two agents:
> a Cloud Agent running 24/7 on AWS EC2, and a Local Agent on my Windows PC.
> I'm going to simulate receiving a business email while my PC is offline,
> have the Cloud Agent draft a reply autonomously, then come back online,
> review the draft in Obsidian, approve it, and watch the Local Agent
> send it via Gmail — all logged and tracked."

---

## Before You Record

**Checklist — do these before starting the camera:**

- [ ] EC2 is running: `sudo systemctl status ai-employee-cloud` shows "active"
- [ ] Odoo containers are up: `docker compose -f ~/odoo-cloud/docker-compose.yml ps`
- [ ] Obsidian is open on the vault folder
- [ ] Terminal 1 (Windows): open in vault root
- [ ] Terminal 2 (EC2 SSH): `ssh -i "D:\aws-keys\ai-employee-key.pem" ubuntu@YOUR_IP`
- [ ] Demo script installed: `python tests/platinum_demo.py --dry-run` runs without errors
- [ ] Split your screen: Obsidian on left, terminal on right
- [ ] Clear `/Pending_Approval/email/`, `/Approved/`, `/In_Progress/` of any old demo files

---

## Scene 1 — Setup (30 seconds)

**Show on screen:** Obsidian vault with Dashboard.md open

**Say:**
> "Here's the AI Employee vault in Obsidian. You can see the Dashboard at Platinum tier.
> The Cloud Agent Status shows it's running on EC2. All folders are clean."

**Click through:**
1. `Dashboard.md` — show the Platinum tier badge and Cloud Agent Status section
2. `Needs_Action/email/` — show it's empty
3. `Pending_Approval/email/` — show it's empty

---

## Scene 2 — Local goes offline (15 seconds)

**Show on screen:** Windows terminal

**Say:**
> "I'm going to simulate the Local Agent being offline — my PC is shut down,
> Task Scheduler isn't running. The Cloud Agent is still running on EC2."

**Type:**
```cmd
REM Just a comment — we're not running local_agent.py
REM Local is "offline"
```

**Then switch to EC2 terminal**

---

## Scene 3 — Email arrives + Cloud detects it (45 seconds)

**Show on screen:** EC2 terminal

**Say:**
> "An email just arrived from a prospective client. The Cloud Agent's Gmail
> watcher detects it within 2 minutes. Let me run the demo script to simulate
> exactly what the Cloud Agent does."

**Type on EC2:**
```bash
cd ~/AI_Employee_Vault
python3.13 tests/platinum_demo.py --mode cloud --demo-id demo_$(date +%H%M%S)
```

**Watch the output — narrate each step as it prints:**
- Step 1: "Local is offline"
- Step 2: "Email arrives"
- Step 3: "Cloud Gmail watcher detects it"
- Step 4: "Cloud creates the action file in /Needs_Action/email/"
- Step 5: "Cloud claims the item — moves it to /In_Progress/cloud/"
- Step 6: "Cloud drafts a professional reply using Claude"
- Step 7: "Draft saved to /Pending_Approval/email/ — waiting for human review"
- Step 8: "Cloud pushes to GitHub — the draft is now synced"

**Expected output (green OK on every step):**
```
Step 04  Cloud creates /Needs_Action/email/EMAIL_test_demo_123456.md
  [OK]  Created EMAIL_test_demo_123456.md

Step 07  Cloud saves draft to /Pending_Approval/email/REPLY_test_demo_123456.md
  [OK]  Draft saved to /Pending_Approval/email/

Step 08  Cloud runs git push (vault sync cron)
  [OK]  git push complete — Cloud's work is in GitHub
```

---

## Scene 4 — Local comes back online + syncs (30 seconds)

**Show on screen:** Switch to Windows terminal

**Say:**
> "My PC is back online. The Local Agent runs its sync cycle and pulls
> Cloud's work from GitHub."

**Type:**
```cmd
scripts\vault_sync.bat
```

**Show the git pull output:** "Updating ... Fast-forward"

**Say:**
> "The vault is now in sync. Cloud's draft is on my PC."

---

## Scene 5 — Review in Obsidian (45 seconds)

**Show on screen:** Obsidian

**Say:**
> "I can see the draft in Obsidian. Let me open it."

**Click:**
1. Navigate to `Pending_Approval/email/`
2. Open `REPLY_test_demo_XXXXXX.md`
3. Read through it — pause for 3 seconds on the email body

**Say:**
> "The Cloud Agent drafted a professional response to the service inquiry.
> It's addressed their specific needs, mentioned our free audit offer,
> and kept the tone professional. This looks good."

**Show the frontmatter:**
> "You can see it has `action: email_reply`, `agent: cloud` — this tells
> the Local Agent exactly what to do when I approve it."

---

## Scene 6 — Human approval (20 seconds)

**Show on screen:** Obsidian file manager

**Say:**
> "I'm going to approve this. I drag the file from /Pending_Approval/email/
> into /Approved/"

**Do it:**
- Right-click `REPLY_test_demo_XXXXXX.md` in Obsidian
- Move file to → `/Approved/`

**Say:**
> "That's the human-in-the-loop checkpoint. The Local Agent can't send
> anything without this move."

---

## Scene 7 — Local Agent executes (45 seconds)

**Show on screen:** Windows terminal

**Say:**
> "Now I'll run the Local Agent. In production this runs automatically
> every 10 minutes via Task Scheduler. I'll run it manually here."

**Type:**
```cmd
python local/local_agent.py --once
```

**Watch and narrate:**
- "Vault sync — pulling latest"
- "Checking /Updates for Cloud status files"
- "Checking Cloud heartbeat — OK"
- "Found 1 approved action"
- "Routing: email_reply → Gmail MCP send_email"

**Say:**
> "The Local Agent found the approved file, read the action type,
> and is now calling the Gmail MCP server to send the email."

**Expected output:**
```
[LocalAgent] === Cycle start 2026-03-26 10:00:00 ===
[LocalAgent] 1 approved action(s) to execute
[LocalAgent] Executing: REPLY_test_demo_XXXXXX.md (action=email_reply)
[AuditLogger] SUCCESS | local_agent | email_sent -> REPLY_test_demo_XXXXXX.md
[LocalAgent] Vault sync complete
```

---

## Scene 8 — Verification (30 seconds)

**Show on screen:** Split — Obsidian on left, terminal on right

**Say:**
> "Let me verify everything completed correctly."

**In Obsidian:**
1. Show `/Done/` — `DONE_REPLY_test_demo_XXXXXX.md` is there
2. Show `/Pending_Approval/email/` — empty
3. Show `/In_Progress/cloud/` — empty

**In terminal:**
```cmd
python tests/platinum_demo.py --mode verify --demo-id demo_XXXXXX
```

**Expected output:**
```
  [OK]  /Done file: DONE_REPLY_test_demo_XXXXXX.md
  [OK]  Audit log: email_sent found (ts=2026-03-26 10:00:00)
  [OK]  Pending_Approval/email/ — file cleared
  [OK]  In_Progress/cloud/ — file cleared

PLATINUM DEMO PASSED
  All 18 steps completed successfully.
```

**Say:**
> "The verification confirms it. Email sent, logged to the audit trail,
> task moved to Done, and the vault synced back to Cloud. That's the
> complete Platinum loop."

---

## Scene 9 — Audit log (30 seconds)

**Show on screen:** Terminal

**Say:**
> "Every action has a structured audit trail. Let me show the log."

**Type:**
```cmd
python -c "
import json
from pathlib import Path
log = Path('Logs/audit.jsonl')
entries = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
for e in entries[-10:]:
    print(e['ts'][:19], e.get('component','').ljust(18), e['action'].ljust(25), e['status'])
"
```

**Show the output — it should show the full chain:**
```
2026-03-26 09:58:01  cloud_agent         demo_step                 success
2026-03-26 09:58:02  cloud_agent         email_action_created      success
2026-03-26 09:58:03  cloud_agent         item_claimed              success
2026-03-26 09:58:04  cloud_agent         email_draft_saved         success
2026-03-26 10:00:01  local_agent         vault_sync                success
2026-03-26 10:00:04  local_agent         approved_action_read      success
2026-03-26 10:00:08  local_agent         email_sent                success
2026-03-26 10:00:09  local_agent         item_done                 success
```

**Say:**
> "Every step — Cloud detection, draft creation, human approval, send,
> and archive — is in the audit log with timestamps and components.
> That's the complete Platinum AI Employee."

---

## Closing (15 seconds)

**Say:**
> "To recap: email arrived while Local was offline. Cloud autonomously
> drafted a reply and synced it via Git. I came back online, reviewed
> and approved in Obsidian — one drag-and-drop. The Local Agent sent
> the email via Gmail MCP, logged it, and archived the task.
> No manual copying, no polling, no missed messages."

---

## Timing Summary

| Scene | Time | Key moment |
|-------|------|------------|
| 1. Setup | 0:00–0:30 | Dashboard.md showing Platinum tier |
| 2. Local offline | 0:30–0:45 | EC2 still running |
| 3. Cloud detects email | 0:45–1:30 | Demo script Steps 1–8 |
| 4. Local syncs | 1:30–2:00 | git pull output |
| 5. Review in Obsidian | 2:00–2:45 | Draft reply content |
| 6. Human approval | 2:45–3:05 | File drag to /Approved/ |
| 7. Local executes | 3:05–3:50 | `local_agent.py --once` output |
| 8. Verification | 3:50–4:20 | `--mode verify` all green |
| 9. Audit log | 4:20–4:50 | Full chain in JSONL |
| Closing | 4:50–5:05 | Summary |

**Target total: under 5 minutes**

---

## If Something Goes Wrong

| Problem | Fix |
|---------|-----|
| `git push` fails | Check GitHub PAT: `git remote -v` — add token to URL |
| Claude not found | `claude --version` — reinstall if missing |
| Email MCP fails | Run `--dry-run` flag — demo still shows the full flow |
| File not found after pull | Wait 30s, re-run `vault_sync.bat`, check `git log` |
| Verify shows FAILED | Check `Logs/errors.jsonl` for the root cause |

**Dry-run fallback** — if Gmail MCP has credential issues on demo day:
```cmd
python tests/platinum_demo.py --dry-run
```
All 18 steps complete, files are created, audit log is written.
Only the actual email send is skipped. The flow and logs are identical.
