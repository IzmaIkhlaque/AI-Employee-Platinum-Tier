"""
AI Employee — Utility Package

Provides shared infrastructure for watchers, orchestrator, and MCP servers.

    from utils.error_handler import ErrorHandler, ErrorSeverity
    from utils.audit_logger import AuditLogger
"""

from utils.error_handler import ErrorHandler, ErrorSeverity
from utils.audit_logger import AuditLogger

__all__ = ["ErrorHandler", "ErrorSeverity", "AuditLogger"]
