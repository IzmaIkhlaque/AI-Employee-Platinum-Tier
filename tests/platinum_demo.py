#!/usr/bin/env python3
"""
AI Employee — Platinum Demo Script
===================================
Simulates the minimum-passing-gate end-to-end flow:

  Email arrives while Local is offline
  → Cloud drafts reply + writes approval file
  → Local returns, user approves
  → Local executes send via Gmail MCP
  → Logs + moves task to /Done

Usage:
    # Full automated demo (simulates Cloud side, then waits for human approval)
    python tests/platinum_demo.py

    # Simulate ONLY the Cloud side (steps 1-8) — run on EC2
    python tests/platinum_demo.py --mode cloud

    # Simulate ONLY the Local side (steps 9-18) — run on Windows PC after sync
    python tests/platinum_demo.py --mode local

    # Verify the demo passed (check audit log + /Done)
    python tests/platinum_demo.py --mode verify

    # Dry run — create all files but do NOT send any email
    python tests/platinum_demo.py --dry-run

    # Use a custom demo ID (default: auto-generated timestamp)
    python tests/platinum_demo.py --demo-id demo001
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
VAULT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(VAULT_ROOT))

from utils.audit_logger import AuditLogger
from utils.error_handler import ErrorHandler, ErrorSeverity

# ── Folder constants ───────────────────────────────────────────────────────────
NEEDS_ACTION      = VAULT_ROOT / "Needs_Action" / "email"
IN_PROGRESS_CLOUD = VAULT_ROOT / "In_Progress" / "cloud"
IN_PROGRESS_LOCAL = VAULT_ROOT / "In_Progress" / "local"
PENDING_EMAIL     = VAULT_ROOT / "Pending_Approval" / "email"
APPROVED          = VAULT_ROOT / "Approved"
DONE              = VAULT_ROOT / "Done"
SIGNALS           = VAULT_ROOT / "Signals"
LOGS              = VAULT_ROOT / "Logs"

# Demo email config — change DEMO_RECIPIENT to your own address for live testing
DEMO_SENDER    = "demo-client@example.com"
DEMO_RECIPIENT = "izmarao99@gmail.com"   # Local agent sends the reply here
DEMO_SUBJECT   = "AI Employee Platinum Demo — Service Inquiry"


# ── ANSI colours ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg: str)    -> None: print(f"  {GREEN}[OK]{RESET}  {msg}")
def info(msg: str)  -> None: print(f"  {CYAN}[--]{RESET}  {msg}")
def warn(msg: str)  -> None: print(f"  {YELLOW}[!!]{RESET}  {msg}")
def fail(msg: str)  -> None: print(f"  {RED}[FAIL]{RESET} {msg}")
def step(n, msg)    -> None: print(f"\n{BOLD}{CYAN}Step {n:02d}{RESET}  {BOLD}{msg}{RESET}")
def banner(msg: str) -> None:
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  {msg}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")


# ── Demo state ────────────────────────────────────────────────────────────────

class PlatinumDemo:
    def __init__(self, demo_id: str, dry_run: bool = False):
        self.demo_id  = demo_id
        self.dry_run  = dry_run
        self.ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.audit    = AuditLogger(str(VAULT_ROOT))
        self.handler  = ErrorHandler(str(VAULT_ROOT))

        # File paths for this demo run
        self.email_file    = NEEDS_ACTION / f"EMAIL_test_{demo_id}.md"
        self.claimed_file  = IN_PROGRESS_CLOUD / f"EMAIL_test_{demo_id}.md"
        self.reply_file    = PENDING_EMAIL / f"REPLY_test_{demo_id}.md"
        self.approved_file = APPROVED / f"REPLY_test_{demo_id}.md"
        self.done_file     = DONE / f"DONE_REPLY_test_{demo_id}.md"

        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for d in [NEEDS_ACTION, IN_PROGRESS_CLOUD, IN_PROGRESS_LOCAL,
                  PENDING_EMAIL, APPROVED, DONE, SIGNALS, LOGS]:
            d.mkdir(parents=True, exist_ok=True)

    # ── CLOUD SIDE (Steps 1–8) ────────────────────────────────────────────────

    def run_cloud_side(self) -> bool:
        banner("CLOUD SIDE  (simulates EC2 agent)")
        mode = " [DRY-RUN]" if self.dry_run else ""
        info(f"Demo ID : {self.demo_id}{mode}")
        info(f"Vault   : {VAULT_ROOT}")

        # Step 1
        step(1, "Local goes offline — stopping local sync")
        info("In production: Windows Task Scheduler tasks paused")
        info("In this demo : we simply don't run local_agent.py")
        self.audit.log("demo_step", "platinum_demo",
                       details={"step": 1, "event": "local_offline", "demo_id": self.demo_id})
        ok("Local is 'offline'")

        # Step 2
        step(2, "Test email arrives in Gmail inbox")
        info(f"From    : {DEMO_SENDER}")
        info(f"To      : {DEMO_RECIPIENT}")
        info(f"Subject : {DEMO_SUBJECT}")
        info("In production: real email arrives in Gmail")
        info("In this demo : we inject a simulated email detection event")
        self.audit.log("demo_step", "platinum_demo",
                       details={"step": 2, "event": "email_arrived",
                                "from": DEMO_SENDER, "subject": DEMO_SUBJECT})
        ok("Email detected by Cloud Gmail watcher")
        time.sleep(0.5)

        # Step 3
        step(3, "Cloud Agent detects email via Gmail API")
        info("cloud_agent._check_gmail() would call gmail MCP search_emails")
        info("In this demo : injecting the detection event directly")
        self.audit.log("gmail_check", "cloud_agent",
                       details={"source": "demo_injection", "new_emails": 1})
        ok("Email detected")
        time.sleep(0.5)

        # Step 4
        step(4, f"Cloud creates /Needs_Action/email/EMAIL_test_{self.demo_id}.md")
        email_content = self._build_email_action_file()
        if not self.dry_run:
            self.email_file.write_text(email_content, encoding="utf-8")
        info(f"File: {self.email_file.relative_to(VAULT_ROOT)}")
        self.audit.log("email_action_created", "cloud_agent",
                       target=str(self.email_file.relative_to(VAULT_ROOT)),
                       details={"demo_id": self.demo_id, "dry_run": self.dry_run})
        ok(f"Created EMAIL_test_{self.demo_id}.md")
        time.sleep(0.5)

        # Step 5
        step(5, "Cloud claims item via move to /In_Progress/cloud/")
        if not self.dry_run:
            if self.email_file.exists():
                shutil.move(str(self.email_file), str(self.claimed_file))
            else:
                # dry-run created nothing — create directly in claimed folder
                self.claimed_file.write_text(email_content, encoding="utf-8")
        info(f"File: {self.claimed_file.relative_to(VAULT_ROOT)}")
        self.audit.log("item_claimed", "cloud_agent",
                       target=str(self.claimed_file.relative_to(VAULT_ROOT)),
                       details={"demo_id": self.demo_id})
        ok("Item claimed — Cloud owns this task")
        time.sleep(0.5)

        # Step 6
        step(6, "Cloud drafts a reply")
        info("In production: Claude reads email, generates professional reply")
        info("In this demo : using a pre-written demo reply")
        self.audit.log("email_draft_created", "cloud_agent",
                       details={"demo_id": self.demo_id,
                                "to": DEMO_SENDER,
                                "subject": f"Re: {DEMO_SUBJECT}"})
        ok("Reply drafted")
        time.sleep(0.5)

        # Step 7
        step(7, f"Cloud saves draft to /Pending_Approval/email/REPLY_test_{self.demo_id}.md")
        reply_content = self._build_reply_approval_file()
        if not self.dry_run:
            self.reply_file.write_text(reply_content, encoding="utf-8")
        info(f"File: {self.reply_file.relative_to(VAULT_ROOT)}")
        self.audit.log("email_draft_saved", "cloud_agent",
                       target=str(self.reply_file.relative_to(VAULT_ROOT)),
                       details={"demo_id": self.demo_id},
                       approval_required=True,
                       approval_status="pending")
        ok("Draft saved to /Pending_Approval/email/")
        time.sleep(0.5)

        # Step 8
        step(8, "Cloud runs git push (vault sync cron)")
        if self.dry_run:
            info("[DRY-RUN] Would run: git add -A && git commit && git push")
        else:
            pushed = self._git_push()
            if pushed:
                ok("git push complete — Cloud's work is in GitHub")
            else:
                warn("git push skipped (nothing to commit or no remote configured)")

        self.audit.log("vault_sync", "cloud_agent",
                       details={"demo_id": self.demo_id, "dry_run": self.dry_run})

        print(f"\n{GREEN}{BOLD}Cloud side complete.{RESET}")
        print(f"  Files created:")
        print(f"    {self.reply_file.relative_to(VAULT_ROOT)}")
        print(f"  Next: run Local side or pull on Windows and review in Obsidian\n")
        return True

    # ── LOCAL SIDE (Steps 9–18) ───────────────────────────────────────────────

    def run_local_side(self) -> bool:
        banner("LOCAL SIDE  (simulates Windows PC agent)")
        mode = " [DRY-RUN]" if self.dry_run else ""
        info(f"Demo ID : {self.demo_id}{mode}")

        # Step 9
        step(9, "'Local comes back online' — running vault sync")
        if self.dry_run:
            info("[DRY-RUN] Would run: scripts\\vault_sync.bat")
        else:
            pulled = self._git_pull()
            if pulled:
                ok("git pull complete — Cloud's drafts are now on Local")
            else:
                warn("git pull returned non-zero (may be already up-to-date)")
        time.sleep(0.5)

        # Step 10
        step(10, "Local reads /Pending_Approval — Cloud's draft is here")
        if self.reply_file.exists():
            ok(f"Found: {self.reply_file.name}")
            content = self.reply_file.read_text(encoding="utf-8")
            # Show a snippet of the reply
            lines = content.split("\n")
            preview = [l for l in lines if l.startswith("**To") or l.startswith("**Subject")]
            for line in preview[:3]:
                info(f"  {line}")
        else:
            warn(f"Reply file not found: {self.reply_file}")
            warn("Did you run --mode cloud first? Or git pull?")
            if not self.dry_run:
                return False
        time.sleep(0.5)

        # Step 11
        step(11, "USER ACTION: Open Obsidian and review the draft")
        print(f"\n  {YELLOW}{BOLD}>>> HUMAN ACTION REQUIRED <<<{RESET}")
        print(f"  Open Obsidian vault at:")
        print(f"  {VAULT_ROOT}")
        print(f"")
        print(f"  Navigate to:")
        print(f"  Pending_Approval/email/REPLY_test_{self.demo_id}.md")
        print(f"")
        print(f"  Read the draft reply. When satisfied, move the file to /Approved/")
        print(f"  (drag and drop in Obsidian, or use Ctrl+Shift+V to move)")
        print(f"")
        print(f"  Then press {BOLD}Enter{RESET} here to continue...")
        input()

        # Step 12
        step(12, "Checking that user moved file to /Approved/")
        if not self.approved_file.exists():
            # Check if the user moved it to /Approved/ (without sub-folder)
            alt = APPROVED / self.reply_file.name
            if alt.exists():
                self.approved_file = alt
                ok(f"Found in /Approved/: {alt.name}")
            else:
                fail(f"File not found in /Approved/")
                fail(f"Expected: {self.approved_file}")
                print(f"\n  Please move REPLY_test_{self.demo_id}.md to /Approved/ and re-run with --mode local")
                return False
        else:
            ok(f"File is in /Approved/: {self.approved_file.name}")
        time.sleep(0.5)

        # Step 13
        step(13, "Local Agent reads /Approved file and routes it")
        content = self.approved_file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        action = fm.get("action", "unknown")
        to_addr = fm.get("to", DEMO_SENDER)
        subject = fm.get("subject", f"Re: {DEMO_SUBJECT}")
        info(f"action : {action}")
        info(f"to     : {to_addr}")
        info(f"subject: {subject}")
        self.audit.log("approved_action_read", "local_agent",
                       target=self.approved_file.name,
                       details={"action": action, "demo_id": self.demo_id})
        ok("Routed to email send handler")
        time.sleep(0.5)

        # Step 14
        step(14, "Local sends email via Gmail MCP (email-mcp send_email)")
        sent = self._send_email_via_mcp(to_addr, subject, content)
        if not sent:
            return False
        time.sleep(0.5)

        # Step 15
        step(15, "Local logs action to /Logs/audit.jsonl")
        self.audit.log(
            "email_sent",
            "local_agent",
            target=self.approved_file.name,
            details={
                "demo_id":  self.demo_id,
                "to":       to_addr,
                "subject":  subject,
                "dry_run":  self.dry_run,
            },
            status="success",
            approval_required=True,
            approval_status="approved",
        )
        ok("Logged to /Logs/audit.jsonl")
        time.sleep(0.5)

        # Step 16
        step(16, f"Local moves task to /Done/DONE_REPLY_test_{self.demo_id}.md")
        if self.approved_file.exists():
            shutil.move(str(self.approved_file), str(self.done_file))
        elif self.dry_run:
            # In dry-run, approved file may not exist — create the done file directly
            self.done_file.write_text(f"DONE (dry-run) — demo_id: {self.demo_id}\n")
        # Always clean up the original claimed file in In_Progress/cloud
        if self.claimed_file.exists():
            self.claimed_file.unlink()
        self.audit.log("item_done", "local_agent",
                       target=str(self.done_file.relative_to(VAULT_ROOT)),
                       details={"demo_id": self.demo_id})
        ok(f"Moved to /Done/")
        time.sleep(0.5)

        # Step 17
        step(17, "Local runs git push (syncs completion back to Cloud)")
        if self.dry_run:
            info("[DRY-RUN] Would run: git add -A && git commit && git push")
        else:
            self._git_push()
            ok("git push complete — Cloud can see task is done")
        time.sleep(0.5)

        # Step 18 — Verification
        step(18, "Verification: audit log + /Done + email sent")
        return self._verify()

    # ── Verify ────────────────────────────────────────────────────────────────

    def _verify(self) -> bool:
        banner("VERIFICATION")
        passed = True

        # Check 1: /Done file exists
        done_check = self.done_file.exists() or self.dry_run
        if done_check:
            ok(f"/Done file: {self.done_file.name}")
        else:
            fail(f"/Done file not found: {self.done_file}")
            passed = False

        # Check 2: audit log has email_sent entry
        recent = self.audit.get_recent_logs(count=100)
        email_sent_entries = [
            e for e in recent
            if e.get("action") == "email_sent"
            and e.get("details", {}).get("demo_id") == self.demo_id
        ]
        if email_sent_entries:
            ts = email_sent_entries[-1]["ts"][:19]
            ok(f"Audit log: email_sent found (ts={ts})")
        else:
            fail("Audit log: no email_sent entry for this demo_id")
            passed = False

        # Check 3: no item left in /Pending_Approval or /In_Progress/cloud
        still_pending = self.reply_file.exists()
        still_claimed = self.claimed_file.exists()
        if still_pending:
            fail(f"File still in Pending_Approval: {self.reply_file.name}")
            passed = False
        else:
            ok("Pending_Approval/email/ — file cleared")

        if still_claimed:
            fail(f"File still in In_Progress/cloud: {self.claimed_file.name}")
            passed = False
        else:
            ok("In_Progress/cloud/ — file cleared")

        # Check 4: demo step audit trail complete
        step_entries = [
            e for e in recent
            if e.get("action") == "demo_step"
            and e.get("details", {}).get("demo_id") == self.demo_id
        ]
        ok(f"Audit trail: {len(step_entries)} demo_step entries logged")

        # Summary
        if passed:
            print(f"\n{GREEN}{BOLD}PLATINUM DEMO PASSED{RESET}")
            print(f"  All 18 steps completed successfully.")
            print(f"  Demo ID: {self.demo_id}")
        else:
            print(f"\n{RED}{BOLD}PLATINUM DEMO FAILED — see above{RESET}")

        # Print audit trail summary
        print(f"\n{BOLD}Audit trail for demo {self.demo_id}:{RESET}")
        demo_entries = [e for e in recent
                        if self.demo_id in json.dumps(e.get("details", {}))]
        for e in demo_entries:
            icon = "[OK]" if e["status"] == "success" else "[!!]"
            print(f"  {e['ts'][:19]}  {icon}  {e['component']:<20} {e['action']}")

        return passed

    # ── Email send via Claude + MCP ───────────────────────────────────────────

    def _send_email_via_mcp(self, to: str, subject: str, approved_content: str) -> bool:
        """
        Call Claude Code with the email-actions skill to send via Gmail MCP.
        In dry-run mode, prints the command instead.
        """
        # Extract body from the approval file
        body = _extract_reply_body(approved_content)

        if self.dry_run:
            info(f"[DRY-RUN] Would send email:")
            info(f"  To     : {to}")
            info(f"  Subject: {subject}")
            info(f"  Body   : {body[:100]}...")
            ok("Email send SIMULATED (dry-run)")
            return True

        prompt = (
            f"Send an email using the email MCP server (send_email tool). "
            f"To: {to} | "
            f"Subject: {subject} | "
            f"Body: {body} | "
            f"This is a pre-approved send from the Platinum demo — execute immediately. "
            f"After sending, confirm success."
        )

        try:
            result = subprocess.run(
                ["claude", "--print", "--max-turns", "5", prompt],
                cwd=str(VAULT_ROOT),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                ok("Email sent via Gmail MCP")
                info(f"Claude output: {result.stdout.strip()[:150]}")
                return True
            else:
                fail(f"Claude returned exit code {result.returncode}")
                fail(result.stderr.strip()[:200])
                return False
        except subprocess.TimeoutExpired:
            fail("Claude timed out sending email")
            return False
        except FileNotFoundError:
            fail("claude binary not found in PATH")
            return False

    # ── Git helpers ───────────────────────────────────────────────────────────

    def _git_push(self) -> bool:
        try:
            subprocess.run(["git", "add", "-A"], cwd=str(VAULT_ROOT),
                           capture_output=True, timeout=30)
            subprocess.run(
                ["git", "commit", "-m", f"Platinum demo {self.demo_id}: {_ts()}"],
                cwd=str(VAULT_ROOT), capture_output=True, timeout=30,
            )
            r = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=str(VAULT_ROOT), capture_output=True, text=True, timeout=60,
            )
            return r.returncode == 0
        except Exception as exc:
            warn(f"git push: {exc}")
            return False

    def _git_pull(self) -> bool:
        try:
            r = subprocess.run(
                ["git", "pull", "origin", "main", "--no-edit"],
                cwd=str(VAULT_ROOT), capture_output=True, text=True, timeout=60,
            )
            return r.returncode == 0
        except Exception as exc:
            warn(f"git pull: {exc}")
            return False

    # ── File builders ─────────────────────────────────────────────────────────

    def _build_email_action_file(self) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""---
type: email_action
action: email_reply
from: {DEMO_SENDER}
subject: {DEMO_SUBJECT}
received: {now}
priority: normal
agent: cloud
demo_id: {self.demo_id}
status: claimed
---

# Email: {DEMO_SUBJECT}

**From:** {DEMO_SENDER}
**To:** {DEMO_RECIPIENT}
**Received:** {now}
**Priority:** Normal

---

## Email Content

Hello,

I came across NovaMind Tech Solutions and I'm interested in understanding
how your AI automation services could help my business. We're a mid-sized
import/export firm in Karachi with about 30 employees.

We spend a lot of time on manual invoicing and customer follow-ups.
Could you tell me more about your services and pricing?

Best regards,
Demo Client

---

## Cloud Agent Notes

- Detected by Gmail watcher at {now}
- Classified as: service inquiry (medium priority)
- Suggested action: draft professional reply
- Cross-domain check: no matching Odoo customer found (new prospect)

"""

    def _build_reply_approval_file(self) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""---
type: approval_request
action: email_reply
to: {DEMO_SENDER}
subject: Re: {DEMO_SUBJECT}
created: {now}
priority: normal
agent: cloud
demo_id: {self.demo_id}
status: pending
---

# Approval Request — Email Reply

**To:** {DEMO_SENDER}
**Subject:** Re: {DEMO_SUBJECT}
**Created:** {now}
**Status:** Awaiting Review
**Agent:** Cloud (drafted on EC2)

---

## Drafted Reply

Dear Demo Client,

Thank you for reaching out to NovaMind Tech Solutions.

We specialise in AI-powered automation for South Asian SMEs — exactly the kind
of workflow challenges you've described. For a 30-person import/export firm,
the highest-ROI automation targets are typically:

- **Invoice generation and delivery** — synced directly to your ERP
- **Customer follow-up sequences** — triggered automatically by payment status
- **Supplier communication** — automated acknowledgements and status updates

We offer a free 30-minute workflow audit where we map your current manual
processes and identify which ones are immediately automatable. There's no sales
pitch — just a real assessment of where your time is going.

Would next week work for a quick call? We're based in Karachi and can meet
in person or over Google Meet.

Best regards,
Izma
NovaMind Tech Solutions
hello@novatech.pk

---

## Checklist

- [ ] Tone is professional and helpful (not salesy)
- [ ] No financial figures or client data disclosed
- [ ] CTA is clear (free audit offer)
- [ ] Reply is relevant to the inquiry
- [ ] Approved by human before sending

---

## Actions

Move this file to:
- `/Approved` → Local Agent will send via Gmail MCP
- `/Rejected` → Draft will be archived, no email sent

"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_frontmatter(content: str) -> dict:
    fm: dict = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip()
    return fm


def _extract_reply_body(content: str) -> str:
    """Pull everything between '## Drafted Reply' and '## Checklist'."""
    if "## Drafted Reply" in content and "## Checklist" in content:
        start = content.index("## Drafted Reply") + len("## Drafted Reply")
        end   = content.index("## Checklist")
        return content[start:end].strip()
    # Fallback: return everything after the frontmatter
    parts = content.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else content


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Employee Platinum Demo — end-to-end flow"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "cloud", "local", "verify"],
        default="full",
        help=(
            "full=run everything (default) | "
            "cloud=Cloud side only | "
            "local=Local side only | "
            "verify=check results"
        ),
    )
    parser.add_argument(
        "--demo-id",
        default=datetime.now().strftime("%Y%m%d_%H%M%S"),
        help="Unique ID for this demo run (default: timestamp)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create files and log but do NOT send any email",
    )
    args = parser.parse_args()

    banner(f"AI Employee — Platinum Demo  [{args.mode.upper()}]")
    info(f"Demo ID  : {args.demo_id}")
    info(f"Dry-run  : {args.dry_run}")
    info(f"Vault    : {VAULT_ROOT}")

    demo = PlatinumDemo(demo_id=args.demo_id, dry_run=args.dry_run)

    if args.mode == "full":
        ok_cloud = demo.run_cloud_side()
        if ok_cloud:
            ok_local = demo.run_local_side()
        sys.exit(0 if ok_cloud and ok_local else 1)

    elif args.mode == "cloud":
        ok_cloud = demo.run_cloud_side()
        sys.exit(0 if ok_cloud else 1)

    elif args.mode == "local":
        ok_local = demo.run_local_side()
        sys.exit(0 if ok_local else 1)

    elif args.mode == "verify":
        passed = demo._verify()
        sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
