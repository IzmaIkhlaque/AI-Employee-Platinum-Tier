#!/usr/bin/env python3
"""
AI Employee — Audit Logger Utility

Centralised structured audit trail for all AI Employee actions.
Every watcher, orchestrator, and MCP server writes here.

Usage:
    from utils.audit_logger import AuditLogger

    audit = AuditLogger()   # auto-detects vault root from file location

    # Log a successful action
    audit.log("email_received", "gmail_watcher", target="msg_abc123",
              details={"from": "client@example.com"}, duration_ms=215)

    # Log a failure
    audit.log("odoo_sync", "odoo_mcp", status="failure",
              details={"error": "Connection refused"})

    # Query recent entries
    recent = audit.get_recent_logs(count=50)
    errors  = audit.get_error_count(hours=24)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


class AuditLogger:
    """
    Writes structured JSONL audit entries to /Logs/audit.jsonl.

    All file paths are resolved relative to the vault root, which is
    auto-detected from this file's location (utils/ → parent = vault root).
    """

    def __init__(self, vault_path: Optional[str] = None):
        if vault_path:
            self.vault_root = Path(vault_path)
        else:
            # utils/audit_logger.py → parent.parent = vault root
            self.vault_root = Path(__file__).parent.parent

        self.log_file = self.vault_root / "Logs" / "audit.jsonl"

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def log(
        self,
        action: str,
        component: str,
        actor: str = "claude",
        target: str = "",
        details: Optional[dict] = None,
        status: str = "success",
        duration_ms: int = 0,
        approval_required: bool = False,
        approval_status: str = "",
    ) -> None:
        """
        Append a structured audit entry to /Logs/audit.jsonl.

        Args:
            action:           What happened — use standard vocabulary from SKILL.md
                              (e.g. "email_received", "file_processed", "send_success")
            component:        Which component performed the action
                              (e.g. "gmail_watcher", "orchestrator", "email-actions")
            actor:            "claude" for AI actions, "human" for manual steps
            target:           File path, email ID, post ID, or record affected
            details:          Action-specific context dict (varies per action)
            status:           "success" | "failure" | "skipped" | "pending"
            duration_ms:      Time taken in milliseconds (0 if not measured)
            approval_required: Whether HITL approval was needed for this action
            approval_status:  "approved" | "rejected" | "" (empty if not applicable)
        """
        entry = {
            "ts":               datetime.now().isoformat(),
            "action":           action,
            "component":        component,
            "actor":            actor,
            "target":           target,
            "details":          details or {},
            "status":           status,
            "duration_ms":      duration_ms,
            "approval_required": approval_required,
            "approval_status":  approval_status,
        }
        self._append_jsonl(entry)
        suffix = f" -> {target}" if target else ""
        print(f"[AuditLogger] {status.upper()} | {component} | {action}{suffix}")

    def get_recent_logs(
        self,
        count: int = 50,
        action_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Return the most recent audit log entries.

        Args:
            count:         Maximum number of entries to return
            action_filter: If provided, only return entries with this action value

        Returns:
            List of log entry dicts, most recent last.
        """
        if not self.log_file.exists():
            return []

        entries = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if action_filter is None or entry.get("action") == action_filter:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except IOError:
            return []

        # Return last `count` entries
        return entries[-count:]

    def get_error_count(self, hours: int = 24) -> int:
        """
        Count audit entries with status="failure" in the last N hours.

        Args:
            hours: Look-back window in hours (default: 24)

        Returns:
            Integer count of failure entries in the window.
        """
        if not self.log_file.exists():
            return 0

        cutoff = datetime.now() - timedelta(hours=hours)
        count = 0

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("status") == "failure":
                            ts_str = entry.get("ts", "")
                            ts = datetime.fromisoformat(ts_str)
                            if ts >= cutoff:
                                count += 1
                    except (json.JSONDecodeError, ValueError):
                        continue
        except IOError:
            return 0

        return count

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _append_jsonl(self, entry: dict) -> None:
        """Write one JSON line to the audit log file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except IOError as e:
            # Never crash the calling component over a logging failure
            print(f"[AuditLogger] WARNING: Could not write to audit log: {e}")
