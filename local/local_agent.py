#!/usr/bin/env python3
"""
AI Employee — Local Agent (Windows PC)
Platinum Tier — two-agent system, Local side.

Responsibilities:
  - Sync vault via Git (pull Cloud changes, push Local changes)
  - Merge /Updates files from Cloud into Dashboard.md
  - Notify user of pending approvals via /Signals
  - Execute approved actions (email, social, Odoo writes)
  - Claim /Needs_Action items that Cloud hasn't claimed
  - Monitor Cloud heartbeat

Usage:
    python local/local_agent.py
    python local/local_agent.py --dry-run
    python local/local_agent.py --once
    python local/local_agent.py --interval 600
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ── Path setup ────────────────────────────────────────────────────────────────
VAULT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(VAULT_ROOT))

from utils.audit_logger import AuditLogger
from utils.error_handler import ErrorHandler, ErrorSeverity

# ── Folders ───────────────────────────────────────────────────────────────────
NEEDS_ACTION      = VAULT_ROOT / "Needs_Action"
IN_PROGRESS_LOCAL = VAULT_ROOT / "In_Progress" / "local"
IN_PROGRESS_CLOUD = VAULT_ROOT / "In_Progress" / "cloud"
PENDING_APPROVAL  = VAULT_ROOT / "Pending_Approval"
APPROVED          = VAULT_ROOT / "Approved"
REJECTED          = VAULT_ROOT / "Rejected"
DONE              = VAULT_ROOT / "Done"
UPDATES           = VAULT_ROOT / "Updates"
SIGNALS           = VAULT_ROOT / "Signals"
LOGS              = VAULT_ROOT / "Logs"
DASHBOARD         = VAULT_ROOT / "Dashboard.md"

# ── Intervals ─────────────────────────────────────────────────────────────────
DEFAULT_INTERVAL          = 600   # 10 min between sync cycles
HEARTBEAT_WARN_SECS       = 900   # 15 min — warn if cloud heartbeat older
HEARTBEAT_URGENT_SECS     = 3600  # 60 min — urgent if cloud heartbeat older


# ── Local Agent ───────────────────────────────────────────────────────────────

class LocalAgent:
    def __init__(
        self,
        dry_run: bool = False,
        interval: int = DEFAULT_INTERVAL,
        run_once: bool = False,
    ):
        self.dry_run   = dry_run
        self.interval  = interval
        self.run_once  = run_once
        self.audit     = AuditLogger(str(VAULT_ROOT))
        self.handler   = ErrorHandler(str(VAULT_ROOT))

        self._ensure_dirs()
        mode = "[DRY-RUN] " if dry_run else ""
        print(f"[LocalAgent] {mode}Starting — vault: {VAULT_ROOT}")
        print(f"[LocalAgent] Sync interval: {interval}s | once={run_once}")

    def _ensure_dirs(self) -> None:
        for d in [IN_PROGRESS_LOCAL, IN_PROGRESS_CLOUD, UPDATES, SIGNALS,
                  LOGS, APPROVED, REJECTED, DONE,
                  PENDING_APPROVAL / "email",
                  PENDING_APPROVAL / "social",
                  PENDING_APPROVAL / "accounting"]:
            d.mkdir(parents=True, exist_ok=True)

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        self.audit.log("agent_start", "local_agent",
                       details={"dry_run": self.dry_run, "interval": self.interval})
        try:
            while True:
                self._cycle()
                if self.run_once:
                    print("[LocalAgent] --once flag set, exiting.")
                    break
                print(f"[LocalAgent] Sleeping {self.interval}s until next cycle...")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n[LocalAgent] Stopped by user.")
            self.audit.log("agent_stop", "local_agent",
                           details={"reason": "KeyboardInterrupt"})

    def _cycle(self) -> None:
        """One full sync-process-execute cycle."""
        print(f"\n[LocalAgent] === Cycle start {_ts()} ===")

        # 1. Sync vault (git pull + push)
        with self.handler.catch("local_agent.vault_sync", ErrorSeverity.EXTERNAL):
            self._vault_sync()

        # 2. Merge /Updates from Cloud into Dashboard.md
        with self.handler.catch("local_agent.merge_updates", ErrorSeverity.DATA):
            self._merge_updates()

        # 3. Check Cloud heartbeat
        with self.handler.catch("local_agent.heartbeat", ErrorSeverity.EXTERNAL):
            self._check_heartbeat()

        # 4. Notify user of pending approvals
        with self.handler.catch("local_agent.pending_notify", ErrorSeverity.DATA):
            self._notify_pending_approvals()

        # 5. Execute approved actions
        with self.handler.catch("local_agent.execute_approved", ErrorSeverity.EXTERNAL):
            self._execute_approved()

        # 6. Claim and process unclaimed /Needs_Action items
        with self.handler.catch("local_agent.needs_action", ErrorSeverity.DATA):
            self._process_needs_action()

        print(f"[LocalAgent] === Cycle end {_ts()} ===")

    # ── Step 1: Vault sync ────────────────────────────────────────────────────

    def _vault_sync(self) -> None:
        if self.dry_run:
            print("[LocalAgent] [DRY-RUN] vault_sync skipped")
            return

        t0 = _now_ms()
        sync_script = VAULT_ROOT / "scripts" / "vault_sync.bat"

        if platform.system() == "Windows" and sync_script.exists():
            result = subprocess.run(
                ["cmd", "/c", str(sync_script)],
                cwd=str(VAULT_ROOT),
                capture_output=True,
                text=True,
                timeout=120,
            )
        else:
            # Linux/macOS fallback (Cloud VM or WSL)
            result = subprocess.run(
                ["bash", str(VAULT_ROOT / "scripts" / "vault_sync_cloud.sh")],
                cwd=str(VAULT_ROOT),
                capture_output=True,
                text=True,
                timeout=120,
            )

        success = result.returncode == 0
        if not success:
            raise RuntimeError(
                f"vault_sync failed (rc={result.returncode}): "
                f"{result.stderr.strip()[:300]}"
            )

        self.audit.log("vault_sync", "local_agent",
                       details={"output": result.stdout.strip()[:200]},
                       duration_ms=_now_ms() - t0)
        print(f"[LocalAgent] Vault sync complete")

    # ── Step 2: Merge /Updates into Dashboard.md ──────────────────────────────

    def _merge_updates(self) -> None:
        updates = [f for f in UPDATES.glob("*.md") if not f.name.startswith("README")]
        if not updates:
            return

        print(f"[LocalAgent] Merging {len(updates)} update(s) into Dashboard.md")
        for update_file in sorted(updates):
            try:
                self._apply_update(update_file)
                if not self.dry_run:
                    dest = DONE / f"DONE_{update_file.name}"
                    shutil.move(str(update_file), str(dest))
                self.audit.log("update_merged", "local_agent",
                               target=update_file.name,
                               details={"dry_run": self.dry_run})
            except Exception as exc:
                self.handler.log_error("local_agent.merge_updates", exc,
                                       ErrorSeverity.DATA,
                                       {"file": update_file.name})

    def _apply_update(self, update_file: Path) -> None:
        """
        Parse the update file's frontmatter to determine merge strategy,
        then patch Dashboard.md accordingly.
        """
        content = update_file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        action = fm.get("action", "")

        if not DASHBOARD.exists():
            print(f"[LocalAgent] Dashboard.md missing — skipping update merge")
            return

        dashboard_text = DASHBOARD.read_text(encoding="utf-8")

        if action == "odoo_sync":
            # Extract Cloud Agent Status block from update and refresh Dashboard
            dashboard_text = _replace_section(
                dashboard_text,
                "## Cloud Agent Status",
                _extract_cloud_status_block(content, update_file),
            )
        else:
            # Generic: append a one-line entry to Recent Activity
            activity_line = (
                f"| {_ts()} | Cloud update: {update_file.stem} | ✅ Merged |"
            )
            dashboard_text = _append_to_recent_activity(dashboard_text, activity_line)

        if not self.dry_run:
            DASHBOARD.write_text(dashboard_text, encoding="utf-8")
        print(f"[LocalAgent] Merged: {update_file.name}")

    # ── Step 3: Cloud heartbeat check ────────────────────────────────────────

    def _check_heartbeat(self) -> None:
        heartbeat = SIGNALS / "cloud_heartbeat.md"
        if not heartbeat.exists():
            print("[LocalAgent] No cloud heartbeat file found — Cloud may not be deployed")
            return

        age_secs = time.time() - heartbeat.stat().st_mtime
        age_min  = int(age_secs / 60)

        if age_secs > HEARTBEAT_URGENT_SECS:
            msg = f"Cloud heartbeat is {age_min}m old — URGENT, Cloud agent may be down"
            print(f"[LocalAgent] URGENT: {msg}")
            self._create_urgent_signal("URGENT_cloud_heartbeat_dead", msg)
            self.audit.log("heartbeat_check", "local_agent",
                           status="failure",
                           details={"age_minutes": age_min, "threshold": "60m"})
        elif age_secs > HEARTBEAT_WARN_SECS:
            msg = f"Cloud heartbeat is {age_min}m old — warning threshold exceeded"
            print(f"[LocalAgent] WARNING: {msg}")
            self.audit.log("heartbeat_check", "local_agent",
                           status="failure",
                           details={"age_minutes": age_min, "threshold": "15m"})
        else:
            print(f"[LocalAgent] Cloud heartbeat OK ({age_min}m old)")
            self.audit.log("heartbeat_check", "local_agent",
                           details={"age_minutes": age_min})

    def _create_urgent_signal(self, name: str, message: str) -> None:
        ts = _ts_file()
        signal_file = SIGNALS / f"{name}_{ts}.md"
        content = f"""# {name.replace('_', ' ').title()}

**Time:** {_ts()}
**Message:** {message}

Move this file to `/Done` once the issue is resolved.
"""
        if not self.dry_run:
            signal_file.write_text(content, encoding="utf-8")
            # Also create an urgent needs-action item
            urgent = NEEDS_ACTION / f"URGENT_{name}_{ts}.md"
            urgent.write_text(content, encoding="utf-8")

    # ── Step 4: Notify of pending approvals ───────────────────────────────────

    def _notify_pending_approvals(self) -> None:
        pending = list(PENDING_APPROVAL.rglob("*.md"))
        pending = [f for f in pending if not f.name.startswith(".")]

        if not pending:
            return

        count   = len(pending)
        domains: dict[str, list[str]] = {}
        for f in pending:
            domain = f.parent.name  # email / social / accounting / (root)
            domains.setdefault(domain, []).append(f.name)

        summary_lines = [f"- **{d}:** {len(files)} item(s)" for d, files in domains.items()]
        summary       = "\n".join(summary_lines)

        ts = _ts_file()
        review_file = SIGNALS / f"REVIEW_NEEDED_{ts}.md"
        content = f"""# Review Needed — {count} Pending Approval(s)

**Generated:** {_ts()}
**Total items:** {count}

{summary}

## Items Awaiting Your Decision

| File | Domain | Action |
|------|--------|--------|
"""
        for f in sorted(pending):
            fm = _parse_frontmatter(f.read_text(encoding="utf-8"))
            action = fm.get("action", "unknown")
            domain = f.parent.name
            content += f"| {f.name} | {domain} | {action} |\n"

        content += "\nMove files to `/Approved` or `/Rejected` to proceed.\n"

        if not self.dry_run:
            review_file.write_text(content, encoding="utf-8")

        print(f"[LocalAgent] {count} item(s) pending approval — wrote {review_file.name}")
        self.audit.log("pending_approval_notify", "local_agent",
                       details={"count": count, "domains": list(domains.keys()),
                                "dry_run": self.dry_run})

    # ── Step 5: Execute approved actions ──────────────────────────────────────

    def _execute_approved(self) -> None:
        approved_files = [f for f in APPROVED.glob("*.md")
                          if not f.name.startswith(".")]
        if not approved_files:
            return

        print(f"[LocalAgent] {len(approved_files)} approved action(s) to execute")
        for f in sorted(approved_files):
            self._execute_one_approved(f)

    def _execute_one_approved(self, file_path: Path) -> None:
        try:
            content  = file_path.read_text(encoding="utf-8")
            fm       = _parse_frontmatter(content)
            action   = fm.get("action", "unknown")
            agent    = fm.get("agent", "unknown")
        except Exception as exc:
            self.handler.log_error("local_agent.execute_approved", exc,
                                   ErrorSeverity.DATA,
                                   {"file": file_path.name})
            return

        print(f"[LocalAgent] Executing: {file_path.name} (action={action}, agent={agent})")
        t0 = _now_ms()

        if action == "email_reply":
            prompt = _email_send_prompt(file_path)
        elif action == "social_post":
            platform = fm.get("platform", "unknown")
            prompt = _social_post_prompt(file_path, platform)
        elif action == "odoo_write":
            prompt = _odoo_write_prompt(file_path)
        else:
            prompt = _generic_execute_prompt(file_path, action)

        success = self._call_claude(prompt, component=f"local_agent.execute.{action}")

        self.audit.log(
            "approved_action_executed",
            "local_agent",
            target=file_path.name,
            details={"action": action, "agent_origin": agent, "dry_run": self.dry_run},
            status="success" if success else "failure",
            duration_ms=_now_ms() - t0,
            approval_required=True,
            approval_status="approved",
        )

        if success and not self.dry_run:
            dest = DONE / f"DONE_{file_path.name}"
            shutil.move(str(file_path), str(dest))

    # ── Step 6: Process unclaimed /Needs_Action items ─────────────────────────

    def _process_needs_action(self) -> None:
        # Scan root + domain sub-folders
        items = list(NEEDS_ACTION.glob("*.md")) + list(NEEDS_ACTION.rglob("**/*.md"))
        items = [f for f in items if not f.name.startswith(".")]

        unclaimed = [f for f in items
                     if not (IN_PROGRESS_CLOUD / f.name).exists()
                     and not (IN_PROGRESS_LOCAL / f.name).exists()]

        if not unclaimed:
            return

        print(f"[LocalAgent] {len(unclaimed)} unclaimed item(s) in Needs_Action")
        for item in sorted(unclaimed):
            claimed = self._claim_item(item)
            if claimed:
                self._process_claimed_item(item)

    def _claim_item(self, item_path: Path) -> bool:
        """Atomic claim via filesystem move."""
        if not item_path.exists():
            return False
        if (IN_PROGRESS_CLOUD / item_path.name).exists():
            print(f"[LocalAgent] Skipping {item_path.name} — owned by Cloud")
            return False
        dest = IN_PROGRESS_LOCAL / item_path.name
        try:
            if not self.dry_run:
                shutil.move(str(item_path), str(dest))
            self.audit.log("item_claimed", "local_agent",
                           target=str(dest),
                           details={"source": str(item_path)})
            return True
        except (OSError, shutil.Error) as exc:
            self.handler.log_error("local_agent.claim", exc,
                                   ErrorSeverity.DATA,
                                   {"item": str(item_path)})
            return False

    def _process_claimed_item(self, original_path: Path) -> None:
        claimed = IN_PROGRESS_LOCAL / original_path.name
        actual  = claimed if claimed.exists() else original_path

        prompt = f"""
You are the Local Agent (Platinum tier). Process this item from In_Progress/local/{actual.name}

1. Read the file content
2. Use file-processing skill to classify priority and summarise
3. If the item needs a multi-step plan, create PLAN_*.md in /Plans
4. If the item needs human action, move to /Pending_Approval/{{domain}}/
5. If fully resolved, move to /Done with DONE_ prefix
6. Update Dashboard.md
7. Log to /Logs/audit.jsonl

Vault root: {VAULT_ROOT}
Report what was done.
"""
        success = self._call_claude(prompt, component="local_agent.process_item")
        self.audit.log("item_processed", "local_agent",
                       target=actual.name,
                       status="success" if success else "failure")

    # ── Claude subprocess ─────────────────────────────────────────────────────

    def _call_claude(self, prompt: str, component: str = "local_agent") -> bool:
        if self.dry_run:
            print(f"[LocalAgent] [DRY-RUN] Would call Claude: {prompt[:80]}...")
            return True
        try:
            result = subprocess.run(
                ["claude", "--print", "--max-turns", "10", prompt],
                cwd=str(VAULT_ROOT),
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr[:400])
            return True
        except Exception as exc:
            self.handler.log_error(component, exc, ErrorSeverity.EXTERNAL)
            return False


# ── Prompt builders ───────────────────────────────────────────────────────────

def _email_send_prompt(f: Path) -> str:
    return f"""
An email reply has been approved by the human.

1. Read Approved/{f.name}
2. Use email-actions skill — call the email MCP send_email tool
3. Extract recipient, subject, and body from the file
4. Send the email
5. Append send confirmation to the file
6. Move to /Done with DONE_ prefix
7. Update Dashboard.md Recent Activity
8. Log to /Logs/audit.jsonl with action: email_sent

Vault root: {VAULT_ROOT}
Report the send result.
"""

def _social_post_prompt(f: Path, platform: str) -> str:
    return f"""
A social media post for {platform} has been approved by the human.

1. Read Approved/{f.name}
2. Extract the post content from the ## Preview section
3. Post using the appropriate tool:
   - LinkedIn: use scripts/linkedin_poster.py
   - Facebook/Instagram/Twitter: use social-media MCP server
4. Save post record to /Social_Media/{platform.title()}/POST_{{timestamp}}.json
5. Move approval file to /Done with DONE_ prefix
6. Update Dashboard.md Social Media Status section
7. Log to /Logs/audit.jsonl with action: social_post_published

Vault root: {VAULT_ROOT}
Report the post result.
"""

def _odoo_write_prompt(f: Path) -> str:
    return f"""
An Odoo write operation has been approved by the human.

1. Read Approved/{f.name}
2. Identify the Odoo model, operation, and data from the frontmatter
3. Execute via Odoo MCP server (the appropriate write tool)
4. Update /Accounting/Current_Month.md with the change
5. Move approval file to /Done with DONE_ prefix
6. Update Dashboard.md Accounting Summary section
7. Log to /Logs/audit.jsonl with action: odoo_write_executed

Vault root: {VAULT_ROOT}
Report the result.
"""

def _generic_execute_prompt(f: Path, action: str) -> str:
    return f"""
An action ({action}) has been approved by the human.

1. Read Approved/{f.name}
2. Execute the approved action
3. Move to /Done with DONE_ prefix
4. Update Dashboard.md
5. Log to /Logs/audit.jsonl

Vault root: {VAULT_ROOT}
Report the result.
"""


# ── Dashboard helpers ─────────────────────────────────────────────────────────

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


def _replace_section(text: str, heading: str, new_block: str) -> str:
    pattern = rf"{re.escape(heading)}\n.*?(?=\n## |\Z)"
    if re.search(pattern, text, flags=re.DOTALL):
        return re.sub(pattern, new_block, text, flags=re.DOTALL)
    return text.rstrip() + "\n\n" + new_block + "\n"


def _append_to_recent_activity(text: str, new_row: str) -> str:
    marker = "## Recent Activity"
    if marker not in text:
        return text
    # Insert after the header row separator
    idx = text.index(marker)
    section = text[idx:]
    # Find the first data row (after the |---| line)
    lines = section.split("\n")
    insert_at = None
    for i, line in enumerate(lines):
        if line.startswith("|---") or line.startswith("| ---"):
            insert_at = i + 1
            break
    if insert_at is not None:
        lines.insert(insert_at, new_row)
        return text[:idx] + "\n".join(lines)
    return text


def _extract_cloud_status_block(update_content: str, update_file: Path) -> str:
    """Build a refreshed Cloud Agent Status section from an odoo_sync update."""
    ts = _ts()
    return f"""## Cloud Agent Status

| Metric | Value |
|--------|-------|
| Cloud Status | Running |
| Last Sync | {ts} |
| Cloud Uptime | — |
| Items Drafted (Cloud) | — |
| Items Pending Approval | — |

> Last update: {update_file.name}
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _ts_file() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _now_ms() -> int:
    return int(datetime.now().timestamp() * 1000)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="AI Employee Local Agent (Platinum)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log actions without executing")
    parser.add_argument("--once", action="store_true",
                        help="Run one cycle then exit")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Seconds between sync cycles (default: {DEFAULT_INTERVAL})")
    args = parser.parse_args()

    agent = LocalAgent(
        dry_run=args.dry_run,
        interval=args.interval,
        run_once=args.once,
    )
    agent.run()


if __name__ == "__main__":
    main()
