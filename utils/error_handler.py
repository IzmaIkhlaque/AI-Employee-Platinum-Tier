#!/usr/bin/env python3
"""
AI Employee — Error Handler Utility

Centralised error logging, retry logic, and urgent-action creation.
Used by watchers, orchestrator, and MCP servers.

Usage:
    from utils.error_handler import ErrorHandler, ErrorSeverity

    handler = ErrorHandler()   # auto-detects vault root from file location

    # Log a plain error
    handler.log_error("gmail_watcher", exc, ErrorSeverity.TRANSIENT)

    # Retry with exponential backoff
    result = handler.retry_with_backoff(lambda: risky_api_call())

    # Use as context manager (logs + re-raises on failure)
    with handler.catch("odoo_sync", ErrorSeverity.EXTERNAL):
        sync_odoo_data()
"""

import json
import time
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


# ── Error taxonomy ────────────────────────────────────────────────────────────

class ErrorSeverity(Enum):
    TRANSIENT = "transient"   # Timeouts, rate limits — retry automatically
    AUTH      = "auth"        # Expired/invalid credentials — human must fix
    DATA      = "data"        # Bad data, missing fields — skip item, continue
    CRITICAL  = "critical"    # Payment failure, data loss risk — halt + alert
    EXTERNAL  = "external"    # Third-party API down — degrade gracefully


# Severities that require an URGENT /Needs_Action file
_URGENT_SEVERITIES = {ErrorSeverity.AUTH, ErrorSeverity.CRITICAL}

# Retry delays (seconds) for each attempt: 30s → 60s → 120s
_BACKOFF_BASE = 30


# ── Handler ───────────────────────────────────────────────────────────────────

class ErrorHandler:
    """
    Centralised error handler for the AI Employee system.

    All file paths are resolved relative to the vault root, which is
    auto-detected from this file's location (utils/ → parent = vault root).
    """

    def __init__(self, vault_path: Optional[str] = None):
        if vault_path:
            self.vault_root = Path(vault_path)
        else:
            # utils/error_handler.py → parent.parent = vault root
            self.vault_root = Path(__file__).parent.parent

        self.error_log   = self.vault_root / "Logs" / "errors.jsonl"
        self.audit_log   = self.vault_root / "Logs" / "audit.jsonl"
        self.needs_action = self.vault_root / "Needs_Action"

        # Ensure log directory exists
        self.error_log.parent.mkdir(parents=True, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def log_error(
        self,
        component: str,
        error: Exception,
        severity: ErrorSeverity,
        context: Optional[dict] = None,
    ) -> None:
        """
        Write a structured entry to /Logs/errors.jsonl.

        For AUTH and CRITICAL severities, also creates an URGENT file
        in /Needs_Action so the human is alerted immediately.

        Args:
            component: Name of the failing component (e.g. "gmail_watcher")
            error:     The exception that was caught
            severity:  ErrorSeverity enum value
            context:   Optional dict of additional context (e.g. file being processed)
        """
        entry = {
            "ts":         datetime.now().isoformat(),
            "component":  component,
            "severity":   severity.value,
            "error_type": type(error).__name__,
            "message":    str(error),
            "context":    context or {},
            "resolved":   False,
        }
        self._append_jsonl(self.error_log, entry)
        print(f"[ErrorHandler] {severity.value.upper()} in {component}: {error}")

        if severity in _URGENT_SEVERITIES:
            self._create_urgent_action(component, error, severity, context or {})

    def log_recovery(self, component: str, details: dict) -> None:
        """
        Write a recovery event to /Logs/audit.jsonl.
        Call this after an error condition is resolved.
        """
        entry = {
            "ts":        datetime.now().isoformat(),
            "action":    "error_recovery",
            "component": component,
            **details,
        }
        self._append_jsonl(self.audit_log, entry)
        print(f"[ErrorHandler] Recovery logged for {component}")

    def retry_with_backoff(
        self,
        func: Callable,
        max_retries: int = 3,
        base_delay: int = _BACKOFF_BASE,
        component: str = "unknown",
        context: Optional[dict] = None,
    ) -> Any:
        """
        Call func() up to max_retries times with exponential backoff.

        Delays: base_delay × 2^attempt  →  30s, 60s, 120s (defaults)

        Logs each failed attempt as TRANSIENT. Re-raises the final exception
        if all retries are exhausted so the caller can decide what to do.

        Args:
            func:        Zero-argument callable to retry
            max_retries: Maximum number of attempts (default: 3)
            base_delay:  Seconds for first retry wait (default: 30)
            component:   Label used in error log entries
            context:     Extra context dict for log entries

        Returns:
            Return value of func() on success

        Raises:
            The last exception raised by func() if all retries fail
        """
        last_exc: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as exc:
                last_exc = exc
                delay = base_delay * (2 ** attempt)
                self.log_error(
                    component,
                    exc,
                    ErrorSeverity.TRANSIENT,
                    {
                        **(context or {}),
                        "attempt":       attempt + 1,
                        "max_retries":   max_retries,
                        "retry_in_secs": delay if attempt < max_retries - 1 else None,
                    },
                )
                if attempt < max_retries - 1:
                    print(
                        f"[ErrorHandler] Retry {attempt + 1}/{max_retries} "
                        f"for {component} in {delay}s…"
                    )
                    time.sleep(delay)
                else:
                    print(
                        f"[ErrorHandler] All {max_retries} retries exhausted for {component}."
                    )

        raise last_exc  # type: ignore[misc]

    @contextmanager
    def catch(
        self,
        component: str,
        severity: ErrorSeverity = ErrorSeverity.EXTERNAL,
        context: Optional[dict] = None,
        reraise: bool = False,
    ):
        """
        Context manager that logs any exception and optionally suppresses it.

        Use this to wrap integration calls so a failure in one component
        does not crash the surrounding loop.

        Args:
            component: Label for the log entry
            severity:  How to classify the error (default: EXTERNAL)
            context:   Extra context for the log entry
            reraise:   If True, re-raises after logging (default: False = suppress)

        Example:
            with handler.catch("odoo_sync", ErrorSeverity.EXTERNAL):
                result = odoo_client.get_invoices()
            # execution continues here even if get_invoices() raised
        """
        try:
            yield
        except Exception as exc:
            self.log_error(component, exc, severity, context)
            if reraise:
                raise

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _append_jsonl(self, path: Path, entry: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def _create_urgent_action(
        self,
        component: str,
        error: Exception,
        severity: ErrorSeverity,
        context: dict,
    ) -> None:
        """
        Write an URGENT_ERROR_*.md file to /Needs_Action.

        The file follows the standard Needs_Action naming convention so the
        orchestrator and watcher pick it up for human review.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"URGENT_ERROR_{component.upper()}_{ts}.md"
        filepath = self.needs_action / filename

        context_lines = "\n".join(
            f"- **{k}:** {v}" for k, v in context.items()
        ) or "_No additional context_"

        suggested = _RECOVERY_STEPS.get(severity, _RECOVERY_STEPS["default"])

        content = f"""---
type: system_error
component: {component}
severity: {severity.value}
created: {datetime.now().isoformat()}
priority: critical
status: pending
---

# URGENT: {component} Error

**Severity:** 🔴 {severity.value.upper()}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Error Details

- **Component:** `{component}`
- **Error Type:** `{type(error).__name__}`
- **Message:** {str(error)}

## Context

{context_lines}

## Required Action

{_REQUIRED_ACTION.get(severity, _REQUIRED_ACTION["default"])}

## Suggested Steps

{suggested}

---

_Move this file to `/Done` once the issue is resolved._
_The AI Employee will resume normal operations automatically._
"""
        self.needs_action.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        print(f"[ErrorHandler] Created urgent action: {filename}")


# ── Per-severity response text ─────────────────────────────────────────────

_REQUIRED_ACTION = {
    ErrorSeverity.AUTH: (
        "Authentication has expired or credentials are invalid. "
        "Manual credential refresh required before the system can continue."
    ),
    ErrorSeverity.CRITICAL: (
        "A critical error has occurred that may risk data integrity. "
        "Review immediately and confirm no data was lost before resuming."
    ),
    "default": (
        "This error requires manual review. "
        "Check the component configuration and resolve the underlying issue."
    ),
}

_RECOVERY_STEPS = {
    ErrorSeverity.AUTH: (
        "- [ ] Check `.env` for the correct credentials\n"
        "- [ ] Verify the token/password has not expired\n"
        "- [ ] Regenerate credentials if expired (see `docs/` for platform guides)\n"
        "- [ ] Restart the affected service\n"
        "- [ ] Move this file to `/Done` when resolved"
    ),
    ErrorSeverity.CRITICAL: (
        "- [ ] **Stop** any related automated operations\n"
        "- [ ] Check `/Logs/errors.jsonl` for the full error trace\n"
        "- [ ] Verify no data was corrupted or lost\n"
        "- [ ] Fix the root cause\n"
        "- [ ] Re-run any operations that were skipped\n"
        "- [ ] Move this file to `/Done` when resolved"
    ),
    "default": (
        "- [ ] Check `/Logs/errors.jsonl` for details\n"
        "- [ ] Resolve the underlying issue\n"
        "- [ ] Restart the affected component if needed\n"
        "- [ ] Move this file to `/Done` when resolved"
    ),
}
