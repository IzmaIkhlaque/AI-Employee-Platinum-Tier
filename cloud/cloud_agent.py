#!/usr/bin/env python3
"""
AI Employee — Cloud Agent
Runs 24/7 on AWS EC2. Reads, drafts, and syncs. Never sends or posts.

Usage:
    python3.13 cloud/cloud_agent.py
    python3.13 cloud/cloud_agent.py --dry-run
"""

import argparse
import asyncio
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
# cloud/cloud_agent.py -> parent.parent = vault root
VAULT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(VAULT_ROOT))

from utils.audit_logger import AuditLogger
from utils.error_handler import ErrorHandler, ErrorSeverity

# ── Folder constants ───────────────────────────────────────────────────────────
NEEDS_ACTION     = VAULT_ROOT / "Needs_Action"
IN_PROGRESS_CLOUD = VAULT_ROOT / "In_Progress" / "cloud"
IN_PROGRESS_LOCAL = VAULT_ROOT / "In_Progress" / "local"
PENDING_APPROVAL = VAULT_ROOT / "Pending_Approval"
DONE             = VAULT_ROOT / "Done"
UPDATES          = VAULT_ROOT / "Updates"
SIGNALS          = VAULT_ROOT / "Signals"
LOGS             = VAULT_ROOT / "Logs"
PLANS            = VAULT_ROOT / "Plans"

# ── Intervals (seconds) ───────────────────────────────────────────────────────
INTERVAL_GMAIL       = 120   # 2 min
INTERVAL_VAULT_SYNC  = 300   # 5 min
INTERVAL_SOCIAL      = 1800  # 30 min
INTERVAL_ODOO        = 3600  # 60 min
INTERVAL_HEALTH      = 300   # 5 min


# ── Cloud Agent ───────────────────────────────────────────────────────────────

class CloudAgent:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.audit   = AuditLogger(str(VAULT_ROOT))
        self.handler = ErrorHandler(str(VAULT_ROOT))

        # Track last-run times
        self._last: dict[str, float] = {
            "gmail":      0,
            "vault_sync": 0,
            "social":     0,
            "odoo":       0,
            "health":     0,
        }

        self._ensure_dirs()
        mode = "[DRY-RUN] " if dry_run else ""
        print(f"[CloudAgent] {mode}Starting — vault: {VAULT_ROOT}")

    def _ensure_dirs(self) -> None:
        for d in [IN_PROGRESS_CLOUD, IN_PROGRESS_LOCAL, UPDATES, SIGNALS, LOGS,
                  PENDING_APPROVAL / "email", PENDING_APPROVAL / "social",
                  PENDING_APPROVAL / "accounting",
                  NEEDS_ACTION / "email", NEEDS_ACTION / "social",
                  NEEDS_ACTION / "accounting", PLANS / "email",
                  PLANS / "social", PLANS / "accounting"]:
            d.mkdir(parents=True, exist_ok=True)

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def run(self) -> None:
        self.audit.log("agent_start", "cloud_agent",
                       details={"dry_run": self.dry_run})
        while True:
            now = asyncio.get_event_loop().time()
            tasks = []

            if now - self._last["health"] >= INTERVAL_HEALTH:
                tasks.append(self._run_task("health", self._health_check))

            if now - self._last["vault_sync"] >= INTERVAL_VAULT_SYNC:
                tasks.append(self._run_task("vault_sync", self._vault_sync))

            if now - self._last["gmail"] >= INTERVAL_GMAIL:
                tasks.append(self._run_task("gmail", self._check_gmail))

            if now - self._last["odoo"] >= INTERVAL_ODOO:
                tasks.append(self._run_task("odoo", self._sync_odoo))

            if now - self._last["social"] >= INTERVAL_SOCIAL:
                tasks.append(self._run_task("social", self._generate_social_drafts))

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

            await asyncio.sleep(30)

    async def _run_task(self, name: str, coro) -> None:
        try:
            await coro()
            self._last[name] = asyncio.get_event_loop().time()
        except Exception as exc:
            self.handler.log_error(f"cloud_agent.{name}", exc,
                                   ErrorSeverity.EXTERNAL)

    # ── Task: Health check ────────────────────────────────────────────────────

    async def _health_check(self) -> None:
        ts = _ts()
        error_count = self.audit.get_error_count(hours=24)
        heartbeat_file = SIGNALS / "cloud_heartbeat.md"

        content = f"""# Cloud Agent Heartbeat

**Timestamp:** {ts}
**Status:** {"[DRY-RUN] " if self.dry_run else ""}RUNNING
**Errors (24h):** {error_count}
**Vault:** {VAULT_ROOT}
**PID:** {os.getpid()}
"""
        if not self.dry_run:
            heartbeat_file.write_text(content, encoding="utf-8")

        self.audit.log("health_check", "cloud_agent",
                       details={"errors_24h": error_count,
                                "dry_run": self.dry_run})
        print(f"[CloudAgent] Health check — errors_24h={error_count}")

    # ── Task: Vault sync ──────────────────────────────────────────────────────

    async def _vault_sync(self) -> None:
        if self.dry_run:
            print("[CloudAgent] [DRY-RUN] vault_sync skipped")
            return

        t0 = _now_ms()

        # Pull
        pull = await asyncio.create_subprocess_exec(
            "git", "pull", "origin", "main", "--no-edit",
            cwd=str(VAULT_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await pull.communicate()
        if pull.returncode != 0:
            raise RuntimeError(f"git pull failed: {stderr.decode().strip()}")

        # Stage + commit + push (empty commit is fine — git returns 1, we ignore)
        await asyncio.create_subprocess_exec(
            "git", "add", "-A", cwd=str(VAULT_ROOT),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        commit_msg = f"Cloud sync: {_ts()}"
        await asyncio.create_subprocess_exec(
            "git", "commit", "-m", commit_msg,
            cwd=str(VAULT_ROOT),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        push = await asyncio.create_subprocess_exec(
            "git", "push", "origin", "main",
            cwd=str(VAULT_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, push_err = await push.communicate()
        if push.returncode != 0:
            raise RuntimeError(f"git push failed: {push_err.decode().strip()}")

        self.audit.log("vault_sync", "cloud_agent",
                       details={"pull": stdout.decode().strip()},
                       duration_ms=_now_ms() - t0)
        print(f"[CloudAgent] Vault sync complete")

    # ── Task: Gmail check ─────────────────────────────────────────────────────

    async def _check_gmail(self) -> None:
        """
        Invoke Claude Code with the email-actions skill to read Gmail and
        create action files. Claude does the heavy lifting; we just call it.
        """
        if self.dry_run:
            print("[CloudAgent] [DRY-RUN] gmail check skipped")
            return

        t0 = _now_ms()
        prompt = (
            "You are the Cloud Agent. Check Gmail for new unread emails. "
            "For each new email: "
            "1. Create an EMAIL_*.md file in /Needs_Action/email/ with subject, sender, summary. "
            "2. Draft a reply and save to /Pending_Approval/email/. "
            "3. Log each action to /Logs/audit.jsonl. "
            "IMPORTANT: Do NOT send any email. Draft only. "
            f"Vault root: {VAULT_ROOT}"
        )

        with self.handler.catch("cloud_agent.gmail", ErrorSeverity.EXTERNAL):
            proc = await asyncio.create_subprocess_exec(
                "claude", "--print", "--max-turns", "10", prompt,
                cwd=str(VAULT_ROOT),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=300)

        self.audit.log("gmail_check", "cloud_agent",
                       details={"output_len": len(stdout)},
                       duration_ms=_now_ms() - t0)
        print(f"[CloudAgent] Gmail check complete")

    # ── Task: Social media drafts ─────────────────────────────────────────────

    async def _generate_social_drafts(self) -> None:
        if self.dry_run:
            print("[CloudAgent] [DRY-RUN] social drafts skipped")
            return

        t0 = _now_ms()
        prompt = (
            "You are the Cloud Agent. Read Business_Goals.md and generate ONE "
            "social media post draft. Choose the platform with the oldest last post. "
            "Save the draft to /Pending_Approval/social/PENDING_social_{platform}_{ts}.md "
            "with frontmatter: action: social_post. "
            "Do NOT post directly. Draft only. "
            "Log to /Logs/audit.jsonl. "
            f"Vault root: {VAULT_ROOT}"
        )

        with self.handler.catch("cloud_agent.social", ErrorSeverity.EXTERNAL):
            proc = await asyncio.create_subprocess_exec(
                "claude", "--print", "--max-turns", "8", prompt,
                cwd=str(VAULT_ROOT),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=240)

        self.audit.log("social_draft_generated", "cloud_agent",
                       duration_ms=_now_ms() - t0,
                       approval_required=True, approval_status="pending")
        print(f"[CloudAgent] Social draft generated")

    # ── Task: Odoo sync ───────────────────────────────────────────────────────

    async def _sync_odoo(self) -> None:
        if self.dry_run:
            print("[CloudAgent] [DRY-RUN] Odoo sync skipped")
            return

        t0 = _now_ms()
        ts = _ts_file()

        prompt = (
            "You are the Cloud Agent. Query Odoo via MCP (read-only): "
            "1. Call get_invoices — list open invoices. "
            "2. Call get_overdue_invoices — list overdue. "
            "3. Call get_payments — list recent payments. "
            "4. Call get_account_balances — balance snapshot. "
            f"Write a Markdown summary to /Updates/odoo_sync_{ts}.md "
            "with frontmatter: action: odoo_sync. "
            "The Local agent will merge this into Dashboard.md. "
            "Do NOT write to Odoo. Read only. "
            f"Vault root: {VAULT_ROOT}"
        )

        with self.handler.catch("cloud_agent.odoo", ErrorSeverity.EXTERNAL):
            proc = await asyncio.create_subprocess_exec(
                "claude", "--print", "--max-turns", "8", prompt,
                cwd=str(VAULT_ROOT),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=180)

        self.audit.log("odoo_sync", "cloud_agent",
                       target=f"Updates/odoo_sync_{ts}.md",
                       duration_ms=_now_ms() - t0)
        print(f"[CloudAgent] Odoo sync written to Updates/odoo_sync_{ts}.md")

    # ── Claim-by-move ─────────────────────────────────────────────────────────

    def claim_item(self, item_path: Path) -> bool:
        """
        Attempt to claim a /Needs_Action item for the Cloud agent.

        Returns True if claimed, False if already owned by Local or missing.
        This is best-effort: on Windows/Linux the rename is atomic for same-FS moves.
        """
        if not item_path.exists():
            return False  # already claimed by Local via git sync

        # Check if Local already has this item
        local_copy = IN_PROGRESS_LOCAL / item_path.name
        if local_copy.exists():
            print(f"[CloudAgent] Skipping {item_path.name} — owned by Local")
            return False

        dest = IN_PROGRESS_CLOUD / item_path.name
        try:
            shutil.move(str(item_path), str(dest))
            self.audit.log("item_claimed", "cloud_agent",
                           target=str(dest),
                           details={"source": str(item_path)})
            return True
        except (OSError, shutil.Error) as exc:
            # Race condition — Local claimed it first
            self.handler.log_error("cloud_agent.claim", exc,
                                   ErrorSeverity.DATA,
                                   {"item": str(item_path)})
            return False

    def release_item(self, item_path: Path, dest_folder: Path) -> None:
        """
        Move a claimed item out of /In_Progress/cloud/ to its final destination.
        dest_folder is typically /Pending_Approval/... or /Done.
        """
        dest = dest_folder / item_path.name
        try:
            if not self.dry_run:
                shutil.move(str(item_path), str(dest))
            self.audit.log("item_released", "cloud_agent",
                           target=str(dest),
                           details={"dry_run": self.dry_run})
        except (OSError, shutil.Error) as exc:
            self.handler.log_error("cloud_agent.release", exc,
                                   ErrorSeverity.DATA,
                                   {"item": str(item_path)})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _ts_file() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _now_ms() -> int:
    return int(datetime.now().timestamp() * 1000)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="AI Employee Cloud Agent")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log actions without making changes or calling Claude")
    args = parser.parse_args()

    agent = CloudAgent(dry_run=args.dry_run)
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n[CloudAgent] Stopped by user.")
        agent.audit.log("agent_stop", "cloud_agent",
                        details={"reason": "KeyboardInterrupt"})


if __name__ == "__main__":
    main()
