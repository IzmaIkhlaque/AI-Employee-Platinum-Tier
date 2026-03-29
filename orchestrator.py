#!/usr/bin/env python3
"""
AI Employee Orchestrator (Gold Tier)

Monitors vault folders and coordinates all AI Employee actions.
Polls /Needs_Action, /Approved, and /Social_Media every 30 seconds.
Runs a lightweight MCP/service health check every 5 minutes.

Usage:
    python orchestrator.py
    python orchestrator.py --dry-run
    python orchestrator.py --vault-path /custom/path
    python orchestrator.py --interval 60
    python orchestrator.py --health-check-interval 120
    python orchestrator.py --once
"""

import argparse
import json
import logging
import os
import re
import socket
import subprocess
import sys
import time
import xmlrpc.client
from datetime import datetime
from pathlib import Path
from typing import Optional

# Allow importing shared utils from vault root (this file lives at vault root)
sys.path.insert(0, str(Path(__file__).parent))

from utils.audit_logger import AuditLogger
from utils.error_handler import ErrorHandler, ErrorSeverity

# ── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_INTERVAL = 30             # seconds between folder polls
DEFAULT_HEALTH_CHECK_INTERVAL = 300  # seconds between health checks (5 min)
STATE_FILE = "memory/orchestrator_state.json"
LOG_FILE = "orchestrator.log"


# ── Logging ───────────────────────────────────────────────────────────────────

def setup_logging(vault_path: Path) -> logging.Logger:
    """Set up logging to both file and console."""
    logger = logging.getLogger("orchestrator")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(vault_path / LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(message)s",
        datefmt="%H:%M:%S"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


# ── State ─────────────────────────────────────────────────────────────────────

class OrchestratorState:
    """Manages persistent state across restarts."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load()

    def _load(self) -> dict:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "processed_needs_action": [],
            "processed_approved": [],
            "processed_social_media": [],
            "last_run": None,
            "last_health_check": None,
            "odoo_last_sync": None,
            "stats": {
                "needs_action_processed": 0,
                "approved_executed": 0,
                "social_media_processed": 0,
                "health_checks": 0,
                "errors": 0,
            },
        }

    def save(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state["last_run"] = datetime.now().isoformat()
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def is_processed(self, folder: str, filename: str) -> bool:
        key = f"processed_{folder}"
        return filename in self.state.get(key, [])

    def mark_processed(self, folder: str, filename: str) -> None:
        key = f"processed_{folder}"
        if key not in self.state:
            self.state[key] = []
        if filename not in self.state[key]:
            self.state[key].append(filename)
        self.state[key] = self.state[key][-500:]

    def increment_stat(self, stat: str) -> None:
        if stat in self.state["stats"]:
            self.state["stats"][stat] += 1


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
    return frontmatter


def scan_folder(folder: Path) -> list[Path]:
    """Get all .md files in a folder (excluding hidden files)."""
    if not folder.exists():
        return []
    return [f for f in folder.glob("*.md") if not f.name.startswith(".")]


def scan_folder_recursive(folder: Path) -> list[Path]:
    """Get all .md files recursively (for /Social_Media sub-folders)."""
    if not folder.exists():
        return []
    return [f for f in folder.rglob("*.md") if not f.name.startswith(".")]


# ── Call Claude ───────────────────────────────────────────────────────────────

def call_claude(
    vault_path: Path,
    prompt: str,
    logger: logging.Logger,
    dry_run: bool = False,
    handler: Optional[ErrorHandler] = None,
) -> tuple[bool, str]:
    """
    Call Claude Code with a prompt.  Returns (success, output).
    Uses ErrorHandler.retry_with_backoff for transient subprocess failures.
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would call Claude:\n{prompt[:200]}...")
        return True, "Dry run - no action taken"

    def _run():
        result = subprocess.run(
            ["claude", "--print"],
            input=prompt,
            capture_output=True,
            text=True,
            cwd=str(vault_path),
            timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr[:500])
        return result.stdout

    try:
        if handler:
            output = handler.retry_with_backoff(
                _run,
                max_retries=2,
                base_delay=10,
                component="orchestrator.call_claude",
                context={"prompt_preview": prompt[:100]},
            )
        else:
            output = _run()
        return True, output

    except subprocess.TimeoutExpired:
        logger.error("Claude timed out after 5 minutes")
        if handler:
            handler.log_error(
                "orchestrator",
                TimeoutError("Claude subprocess timed out"),
                ErrorSeverity.TRANSIENT,
            )
        return False, "Timeout"

    except FileNotFoundError:
        logger.error("Claude Code not found — is it installed and in PATH?")
        if handler:
            handler.log_error(
                "orchestrator",
                FileNotFoundError("claude binary not found"),
                ErrorSeverity.CRITICAL,
            )
        return False, "Claude not found"

    except Exception as e:
        logger.error(f"Error calling Claude: {e}")
        if handler:
            handler.log_error("orchestrator", e, ErrorSeverity.EXTERNAL)
        return False, str(e)


# ── Folder processors ─────────────────────────────────────────────────────────

def process_needs_action(
    file_path: Path,
    vault_path: Path,
    logger: logging.Logger,
    dry_run: bool = False,
    audit: Optional[AuditLogger] = None,
    handler: Optional[ErrorHandler] = None,
) -> bool:
    """Process a file from /Needs_Action."""
    logger.info(f"  [Needs_Action] Processing: {file_path.name}")
    t0 = time.monotonic()

    prompt = f"""
Process the file at Needs_Action/{file_path.name}

1. Read the file content
2. Use the file-processing skill to:
   - Classify priority using Company_Handbook.md keywords
   - Create a summary
   - Determine if any follow-up actions are needed
3. Cross-domain check (Gold tier):
   - If the file mentions invoice, payment, or client name → query Odoo MCP for related records
   - If it's a social media inquiry → note cross_domain: social in your summary
4. If multi-step task, use task-planner skill to create a plan in /Plans
5. Move processed file to /Done with DONE_ prefix
6. Update Dashboard.md with the action
7. Log to /Logs/audit.jsonl

Be concise. Report what was done.
"""

    success, output = call_claude(vault_path, prompt, logger, dry_run, handler)
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    if success:
        logger.info(f"  [Needs_Action] Done: {file_path.name} ({elapsed_ms}ms)")
    else:
        logger.error(f"  [Needs_Action] FAILED: {file_path.name}")
        if handler:
            handler.log_error(
                "orchestrator",
                RuntimeError(f"process_needs_action failed: {file_path.name}"),
                ErrorSeverity.DATA,
                context={"file": file_path.name},
            )

    if audit:
        audit.log(
            action="file_processed",
            component="orchestrator",
            target=file_path.name,
            details={"dry_run": dry_run},
            status="success" if success else "failure",
            duration_ms=elapsed_ms,
        )
    return success


def execute_approved_action(
    file_path: Path,
    vault_path: Path,
    logger: logging.Logger,
    dry_run: bool = False,
    audit: Optional[AuditLogger] = None,
    handler: Optional[ErrorHandler] = None,
) -> bool:
    """Execute an approved action from /Approved."""
    logger.info(f"  [Approved] Executing: {file_path.name}")
    t0 = time.monotonic()

    try:
        content = file_path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)
    except Exception as e:
        logger.error(f"  [Approved] Could not read {file_path.name}: {e}")
        if handler:
            handler.log_error(
                "orchestrator",
                e,
                ErrorSeverity.DATA,
                context={"file": file_path.name},
            )
        if audit:
            audit.log(
                action="approved_action_executed",
                component="orchestrator",
                target=file_path.name,
                details={"error": str(e)},
                status="failure",
                approval_required=True,
                approval_status="approved",
            )
        return False

    action_type = frontmatter.get("action", "unknown")
    target = frontmatter.get("target", "unknown")
    logger.info(f"  [Approved] Action type: {action_type}, Target: {target}")

    if action_type == "email_send":
        prompt = f"""
An email send action has been approved.

1. Read the approved file at Approved/{file_path.name}
2. Use the email-actions skill to send the email
3. Extract recipient, subject, and body from the approval file
4. Send the email using the email MCP server
5. Log the result in the approval file
6. Move to /Done with DONE_ prefix
7. Update Dashboard.md

Report the result.
"""
    elif action_type == "social_post":
        platform = frontmatter.get("platform", "linkedin")
        prompt = f"""
A social media post has been approved for {platform}.

1. Read the approved file at Approved/{file_path.name}
2. Extract the post content from the ## Preview section
3. Post via the appropriate MCP server or script:
   - LinkedIn: scripts/linkedin_poster.py
   - Facebook/Instagram/Twitter: social-media MCP server
4. Save a post record to /Social_Media/{platform.title()}/POST_<timestamp>.json
5. Log the result in the approval file
6. Move to /Done with DONE_ prefix
7. Update Dashboard.md

Report the result.
"""
    elif action_type == "odoo_write":
        prompt = f"""
An Odoo write operation has been approved.

1. Read the approved file at Approved/{file_path.name}
2. Identify the Odoo model and data from the frontmatter
3. Execute via Odoo MCP server
4. Log the result
5. Update /Accounting/Current_Month.md if financial data changed
6. Move to /Done with DONE_ prefix
7. Update Dashboard.md

Report the result.
"""
    elif action_type == "file_delete":
        prompt = f"""
A file deletion has been approved.

1. Read the approved file at Approved/{file_path.name}
2. Identify the file(s) to delete from the target field
3. Perform the deletion carefully
4. Log what was deleted
5. Move approval file to /Done with DONE_ prefix
6. Update Dashboard.md

Report the result.
"""
    else:
        prompt = f"""
An action has been approved.

1. Read the approved file at Approved/{file_path.name}
2. Understand what action was approved:
   - Action: {action_type}
   - Target: {target}
3. Execute the action appropriately
4. Log the result
5. Move to /Done with DONE_ prefix
6. Update Dashboard.md

Report the result.
"""

    success, output = call_claude(vault_path, prompt, logger, dry_run, handler)
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    if success:
        logger.info(f"  [Approved] Executed: {file_path.name} ({action_type}) {elapsed_ms}ms")
    else:
        logger.error(f"  [Approved] FAILED: {file_path.name}")
        if handler:
            handler.log_error(
                "orchestrator",
                RuntimeError(f"execute_approved_action failed: {file_path.name}"),
                ErrorSeverity.EXTERNAL,
                context={"file": file_path.name, "action_type": action_type},
            )

    if audit:
        audit.log(
            action="approved_action_executed",
            component="orchestrator",
            target=file_path.name,
            details={"action_type": action_type, "target": target, "dry_run": dry_run},
            status="success" if success else "failure",
            duration_ms=elapsed_ms,
            approval_required=True,
            approval_status="approved",
        )
    return success


def process_social_media_item(
    file_path: Path,
    vault_path: Path,
    logger: logging.Logger,
    dry_run: bool = False,
    audit: Optional[AuditLogger] = None,
    handler: Optional[ErrorHandler] = None,
) -> bool:
    """
    Handle new items appearing in /Social_Media sub-folders.

    These are typically post-publish records saved by the social media MCP
    server, or incoming inquiry files dropped there manually.
    """
    logger.info(f"  [Social_Media] Processing: {file_path.name}")
    t0 = time.monotonic()

    # Determine platform from the parent folder name
    platform = file_path.parent.name  # Facebook, Instagram, Twitter, etc.

    prompt = f"""
A new item has appeared in /Social_Media/{platform}/{file_path.name}

1. Read the file content
2. Determine its type:
   - Published post record → log engagement metrics if present, no further action needed
   - Incoming inquiry or comment → create SOCIAL_inquiry_*.md in /Needs_Action for review
   - Error or failure record → create URGENT_social_*.md in /Needs_Action
3. If it's a published post record, update /Social_Media/{platform}/ summary if one exists
4. Log to /Logs/audit.jsonl with action: social_post_record_processed
5. Do NOT move the file — leave it in place as a record

Report what type it was and any follow-up actions created.
"""

    success, output = call_claude(vault_path, prompt, logger, dry_run, handler)
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    if success:
        logger.info(f"  [Social_Media] Done: {file_path.name} ({elapsed_ms}ms)")
    else:
        logger.error(f"  [Social_Media] FAILED: {file_path.name}")
        if handler:
            handler.log_error(
                "orchestrator",
                RuntimeError(f"process_social_media_item failed: {file_path.name}"),
                ErrorSeverity.EXTERNAL,
                context={"file": file_path.name, "platform": platform},
            )

    if audit:
        audit.log(
            action="social_post_record_processed",
            component="orchestrator",
            target=file_path.name,
            details={"platform": platform, "dry_run": dry_run},
            status="success" if success else "failure",
            duration_ms=elapsed_ms,
        )
    return success


# ── Health check ──────────────────────────────────────────────────────────────

def _load_dotenv(vault_path: Path) -> None:
    """Load .env without requiring python-dotenv (simple fallback parser)."""
    env_file = vault_path / ".env"
    if not env_file.exists():
        return
    try:
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass


def run_health_check(
    vault_path: Path,
    state: OrchestratorState,
    logger: logging.Logger,
    audit: Optional[AuditLogger] = None,
    handler: Optional[ErrorHandler] = None,
) -> dict:
    """
    Lightweight Python health check — no Claude subprocess required.

    Checks:
      - Odoo: XML-RPC connection to localhost:8069
      - Email SMTP: TCP socket to configured SMTP host:port
      - Social Media: env var presence (dry-run detection)
      - Claude binary: which/where check
      - Error count: last 24h from /Logs/errors.jsonl

    Returns a status dict and updates Dashboard.md health section.
    """
    logger.info("[Health] Running system health check...")
    _load_dotenv(vault_path)

    results: dict[str, dict] = {}

    # ── 1. Odoo ────────────────────────────────────────────────────────────────
    odoo_url  = os.environ.get("ODOO_URL", "http://localhost:8069")
    odoo_db   = os.environ.get("ODOO_DB", "")
    odoo_user = os.environ.get("ODOO_LOGIN", os.environ.get("ODOO_USER", ""))
    odoo_pw   = os.environ.get("ODOO_PASSWORD", "")

    try:
        proxy = xmlrpc.client.ServerProxy(
            f"{odoo_url}/xmlrpc/2/common",
            allow_none=True,
        )
        version = proxy.version()
        results["odoo"] = {"status": "ok", "detail": f"Odoo {version.get('server_version', '?')}"}
        state.state["odoo_last_sync"] = datetime.now().isoformat()
    except Exception as e:
        results["odoo"] = {"status": "error", "detail": str(e)[:120]}
        if handler:
            handler.log_error(
                "orchestrator.health_check",
                e,
                ErrorSeverity.EXTERNAL,
                context={"service": "odoo", "url": odoo_url},
            )

    # ── 2. Email SMTP ──────────────────────────────────────────────────────────
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", os.environ.get("GMAIL_ADDRESS", ""))

    try:
        with socket.create_connection((smtp_host, smtp_port), timeout=5):
            pass
        label = f"SMTP {smtp_host}:{smtp_port}"
        if not smtp_user:
            label += " (credentials not configured)"
        results["email"] = {"status": "ok", "detail": label}
    except Exception as e:
        results["email"] = {"status": "error", "detail": str(e)[:120]}
        if handler:
            handler.log_error(
                "orchestrator.health_check",
                e,
                ErrorSeverity.EXTERNAL,
                context={"service": "smtp", "host": smtp_host, "port": smtp_port},
            )

    # ── 3. Social Media (env var presence) ────────────────────────────────────
    sm_tokens = {
        "facebook":  bool(os.environ.get("FB_PAGE_ACCESS_TOKEN")),
        "instagram": bool(os.environ.get("IG_USER_ID")),
        "twitter":   bool(os.environ.get("TWITTER_API_KEY")),
    }
    configured = [k for k, v in sm_tokens.items() if v]
    dry_run_flag = os.environ.get("SOCIAL_DRY_RUN", "true").lower() in ("true", "1")
    if configured:
        results["social_media"] = {
            "status": "ok",
            "detail": f"Configured: {', '.join(configured)}"
                      + (" [dry-run]" if dry_run_flag else ""),
        }
    else:
        results["social_media"] = {
            "status": "warning",
            "detail": "No social media credentials — dry-run mode active",
        }

    # ── 4. Claude binary ──────────────────────────────────────────────────────
    try:
        r = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        ver = (r.stdout or r.stderr).strip().splitlines()[0][:60]
        results["claude"] = {"status": "ok", "detail": ver}
    except FileNotFoundError:
        results["claude"] = {"status": "error", "detail": "claude binary not found in PATH"}
        if handler:
            handler.log_error(
                "orchestrator.health_check",
                FileNotFoundError("claude not in PATH"),
                ErrorSeverity.CRITICAL,
            )
    except Exception as e:
        results["claude"] = {"status": "warning", "detail": str(e)[:120]}

    # ── 5. Error count (last 24h) ──────────────────────────────────────────────
    error_count_24h = 0
    errors_file = vault_path / "Logs" / "errors.jsonl"
    if errors_file.exists():
        cutoff = time.time() - 86400
        try:
            with open(errors_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        ts = datetime.fromisoformat(entry.get("ts", "2000-01-01"))
                        if ts.timestamp() >= cutoff:
                            error_count_24h += 1
                    except Exception:
                        continue
        except Exception:
            pass
    results["errors_24h"] = {
        "status": "ok" if error_count_24h < 5 else "warning",
        "detail": f"{error_count_24h} errors in last 24h",
    }

    # ── Overall status ─────────────────────────────────────────────────────────
    has_error = any(v["status"] == "error" for v in results.values())
    has_warn  = any(v["status"] == "warning" for v in results.values())
    overall = "ERROR" if has_error else ("WARNING" if has_warn else "HEALTHY")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[Health] Overall: {overall}")
    for svc, info in results.items():
        icon = {"ok": "OK", "warning": "WARN", "error": "FAIL"}.get(info["status"], "?")
        logger.info(f"[Health]   [{icon}] {svc}: {info['detail']}")

    # ── Update Dashboard.md health section ────────────────────────────────────
    _update_dashboard_health(vault_path, overall, results, now_str)

    # ── Audit log ─────────────────────────────────────────────────────────────
    if audit:
        audit.log(
            action="health_check",
            component="orchestrator",
            details={"overall": overall, "results": results, "errors_24h": error_count_24h},
            status="success" if not has_error else "failure",
        )

    # ── Urgent alert if critical ───────────────────────────────────────────────
    if has_error and handler:
        failed = [k for k, v in results.items() if v["status"] == "error"]
        handler.log_error(
            "orchestrator.health_check",
            RuntimeError(f"Health check FAILED for: {', '.join(failed)}"),
            ErrorSeverity.CRITICAL,
            context={"failed_services": failed, "overall": overall},
        )

    return results


def _update_dashboard_health(
    vault_path: Path,
    overall: str,
    results: dict,
    timestamp: str,
) -> None:
    """Rewrite the ## System Health section in Dashboard.md."""
    dashboard = vault_path / "Dashboard.md"
    if not dashboard.exists():
        return

    status_icons = {"ok": "OK", "warning": "WARN", "error": "FAIL"}
    lines = [
        f"## System Health",
        f"",
        f"**Status:** {overall}  |  **Last checked:** {timestamp}",
        f"",
        f"| Service | Status | Detail |",
        f"|---------|--------|--------|",
    ]
    for svc, info in results.items():
        icon = status_icons.get(info["status"], "?")
        lines.append(f"| {svc} | {icon} | {info['detail']} |")
    lines.append("")

    health_block = "\n".join(lines)

    try:
        content = dashboard.read_text(encoding="utf-8")
        # Replace existing block or append
        if "## System Health" in content:
            # Replace from "## System Health" to next "## " heading (or end of file)
            pattern = r"## System Health\n.*?(?=\n## |\Z)"
            new_content = re.sub(pattern, health_block, content, flags=re.DOTALL)
        else:
            new_content = content.rstrip() + "\n\n" + health_block
        dashboard.write_text(new_content, encoding="utf-8")
    except Exception as e:
        print(f"[Orchestrator] Warning: could not update Dashboard health: {e}")


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_orchestrator(
    vault_path: Path,
    interval: int,
    dry_run: bool,
    logger: logging.Logger,
    health_check_interval: int = DEFAULT_HEALTH_CHECK_INTERVAL,
) -> None:
    """Main Gold-tier orchestrator loop."""

    state_file = vault_path / STATE_FILE
    state  = OrchestratorState(state_file)
    audit  = AuditLogger(str(vault_path))
    handler = ErrorHandler(str(vault_path))

    # Monitored folders
    needs_action_path  = vault_path / "Needs_Action"
    approved_path      = vault_path / "Approved"
    social_media_path  = vault_path / "Social_Media"

    logger.info("=" * 55)
    logger.info("  AI Employee Orchestrator (Gold Tier)")
    logger.info("=" * 55)
    logger.info(f"  Vault       : {vault_path}")
    logger.info(f"  Poll every  : {interval}s")
    logger.info(f"  Health check: every {health_check_interval}s")
    logger.info(f"  Dry run     : {dry_run}")
    logger.info(f"  Monitoring  : Needs_Action | Approved | Social_Media")
    logger.info("=" * 55)
    logger.info("  Ctrl+C to stop")
    logger.info("")

    audit.log(
        action="orchestrator_started",
        component="orchestrator",
        details={
            "interval_secs": interval,
            "health_check_interval_secs": health_check_interval,
            "dry_run": dry_run,
            "tier": "gold",
        },
        status="success",
    )

    last_health_check = 0.0  # force a health check on first iteration

    try:
        while True:
            # ── Periodic health check ──────────────────────────────────────────
            if time.monotonic() - last_health_check >= health_check_interval:
                with handler.catch("orchestrator.health_check", ErrorSeverity.EXTERNAL):
                    run_health_check(vault_path, state, logger, audit, handler)
                state.increment_stat("health_checks")
                state.state["last_health_check"] = datetime.now().isoformat()
                last_health_check = time.monotonic()
                state.save()

            # ── /Needs_Action ─────────────────────────────────────────────────
            for file_path in scan_folder(needs_action_path):
                if not state.is_processed("needs_action", file_path.name):
                    logger.info(f"New item in Needs_Action: {file_path.name}")

                    success = process_needs_action(
                        file_path, vault_path, logger, dry_run, audit, handler
                    )

                    if success or dry_run:
                        state.mark_processed("needs_action", file_path.name)
                        state.increment_stat("needs_action_processed")
                    else:
                        state.increment_stat("errors")
                    state.save()

            # ── /Approved ─────────────────────────────────────────────────────
            for file_path in scan_folder(approved_path):
                if not state.is_processed("approved", file_path.name):
                    logger.info(f"New approved action: {file_path.name}")

                    success = execute_approved_action(
                        file_path, vault_path, logger, dry_run, audit, handler
                    )

                    if success or dry_run:
                        state.mark_processed("approved", file_path.name)
                        state.increment_stat("approved_executed")
                    else:
                        state.increment_stat("errors")
                    state.save()

            # ── /Social_Media (recursive — sub-folders per platform) ──────────
            for file_path in scan_folder_recursive(social_media_path):
                if not state.is_processed("social_media", str(file_path.relative_to(vault_path))):
                    logger.info(f"New Social_Media item: {file_path.name}")

                    success = process_social_media_item(
                        file_path, vault_path, logger, dry_run, audit, handler
                    )

                    rel = str(file_path.relative_to(vault_path))
                    if success or dry_run:
                        state.mark_processed("social_media", rel)
                        state.increment_stat("social_media_processed")
                    else:
                        state.increment_stat("errors")
                    state.save()

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("Shutting down orchestrator...")
        state.save()
        audit.log(
            action="orchestrator_stopped",
            component="orchestrator",
            details={"stats": state.state["stats"]},
            status="success",
        )
        logger.info(f"Stats: {json.dumps(state.state['stats'])}")
        logger.info("Goodbye!")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Employee Orchestrator (Gold Tier)"
    )
    parser.add_argument(
        "--vault-path",
        type=Path,
        default=Path(__file__).parent,
        help="Path to the vault directory",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Folder poll interval in seconds (default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--health-check-interval",
        type=int,
        default=DEFAULT_HEALTH_CHECK_INTERVAL,
        help=f"Health check interval in seconds (default: {DEFAULT_HEALTH_CHECK_INTERVAL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without executing",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (no loop)",
    )

    args = parser.parse_args()
    vault_path = args.vault_path.resolve()

    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    # Ensure all Gold-tier folders exist
    for folder in [
        "Needs_Action", "Approved", "Done", "memory",
        "Social_Media", "Briefings", "Accounting", "Logs",
    ]:
        (vault_path / folder).mkdir(exist_ok=True)

    logger = setup_logging(vault_path)

    if args.once:
        logger.info("Running single check (--once)...")
        state = OrchestratorState(vault_path / STATE_FILE)
        audit = AuditLogger(str(vault_path))
        handler = ErrorHandler(str(vault_path))

        for file_path in scan_folder(vault_path / "Needs_Action"):
            if not state.is_processed("needs_action", file_path.name):
                process_needs_action(file_path, vault_path, logger, args.dry_run, audit, handler)
                state.mark_processed("needs_action", file_path.name)

        for file_path in scan_folder(vault_path / "Approved"):
            if not state.is_processed("approved", file_path.name):
                execute_approved_action(file_path, vault_path, logger, args.dry_run, audit, handler)
                state.mark_processed("approved", file_path.name)

        for file_path in scan_folder_recursive(vault_path / "Social_Media"):
            rel = str(file_path.relative_to(vault_path))
            if not state.is_processed("social_media", rel):
                process_social_media_item(file_path, vault_path, logger, args.dry_run, audit, handler)
                state.mark_processed("social_media", rel)

        # One health check in --once mode
        run_health_check(vault_path, state, logger, audit, handler)

        state.save()
        logger.info("Single run complete.")
    else:
        run_orchestrator(
            vault_path,
            args.interval,
            args.dry_run,
            logger,
            health_check_interval=args.health_check_interval,
        )


if __name__ == "__main__":
    main()
