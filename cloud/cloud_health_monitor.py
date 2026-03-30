#!/usr/bin/env python3
"""
AI Employee — Cloud Agent Health Monitor

Watchdog that checks whether cloud_agent.py is running.
If the process is dead, it restarts it and logs the event.

Usage:
    python3.13 cloud/cloud_health_monitor.py
    python3.13 cloud/cloud_health_monitor.py --dry-run

Dependencies:
    pip install psutil          # or: uv add psutil
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import psutil
except ImportError:
    print("[HealthMonitor] ERROR: psutil not installed. Run: pip install psutil")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
VAULT_ROOT    = Path(__file__).parent.parent
AGENT_SCRIPT  = Path(__file__).parent / "cloud_agent.py"
ERROR_LOG     = VAULT_ROOT / "Logs" / "errors.jsonl"
CHECK_INTERVAL = 60  # seconds between checks


# ── Monitor ───────────────────────────────────────────────────────────────────

class HealthMonitor:
    def __init__(self, dry_run: bool = False):
        self.dry_run    = dry_run
        self._agent_pid: int | None = None
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        print(f"[HealthMonitor] Watching {AGENT_SCRIPT.name} "
              f"every {CHECK_INTERVAL}s {'[DRY-RUN]' if dry_run else ''}")

    def run(self) -> None:
        while True:
            try:
                if self._is_agent_running():
                    print(f"[HealthMonitor] cloud_agent.py is running "
                          f"(pid={self._agent_pid})")
                else:
                    print("[HealthMonitor] cloud_agent.py is NOT running — restarting")
                    self._restart_agent()
            except Exception as exc:
                self._log_error(f"Monitor loop error: {exc}")
            time.sleep(CHECK_INTERVAL)

    def _is_agent_running(self) -> bool:
        """
        Return True if a python process running cloud_agent.py is alive.
        Also updates self._agent_pid.
        """
        target = str(AGENT_SCRIPT)
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline") or []
                if any(target in arg or "cloud_agent.py" in arg
                       for arg in cmdline):
                    self._agent_pid = proc.info["pid"]
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self._agent_pid = None
        return False

    def _restart_agent(self) -> None:
        if self.dry_run:
            print("[HealthMonitor] [DRY-RUN] Would restart cloud_agent.py")
            self._log_error("cloud_agent.py was dead — DRY-RUN restart skipped")
            return

        try:
            proc = subprocess.Popen(
                [sys.executable, str(AGENT_SCRIPT)],
                cwd=str(VAULT_ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,   # detach from monitor's session
            )
            self._agent_pid = proc.pid
            print(f"[HealthMonitor] Restarted cloud_agent.py (new pid={proc.pid})")
            self._log_error(
                f"cloud_agent.py was dead — restarted as pid={proc.pid}",
                severity="transient",
                resolved=True,
            )
        except Exception as exc:
            msg = f"Failed to restart cloud_agent.py: {exc}"
            print(f"[HealthMonitor] ERROR: {msg}")
            self._log_error(msg, severity="critical")

    def _log_error(
        self,
        message: str,
        severity: str = "transient",
        resolved: bool = False,
    ) -> None:
        entry = {
            "ts":        datetime.now().isoformat(),
            "component": "cloud_health_monitor",
            "severity":  severity,
            "error_type": "ProcessDead",
            "message":   message,
            "context":   {"agent_script": str(AGENT_SCRIPT)},
            "resolved":  resolved,
        }
        try:
            with open(ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except IOError as exc:
            print(f"[HealthMonitor] WARNING: Could not write error log: {exc}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Watchdog for the AI Employee Cloud Agent"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Check status but do not restart the agent")
    parser.add_argument("--once", action="store_true",
                        help="Check once and exit (use this when called from cron)")
    args = parser.parse_args()

    monitor = HealthMonitor(dry_run=args.dry_run)
    if args.once:
        # Single check — safe to call from cron without piling up processes
        if not monitor._is_agent_running():
            monitor._restart_agent()
        else:
            print(f"[HealthMonitor] cloud_agent.py is running (pid={monitor._agent_pid})")
        return

    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n[HealthMonitor] Stopped by user.")


if __name__ == "__main__":
    main()
