#!/usr/bin/env python3
"""
Odoo MCP Server for AI Employee

Connects to local Odoo 19 via standard XML-RPC (no Odoo module required).
Reads credentials from .env file.

Tools exposed to Claude:
  - search_customers     : List companies from res.partner
  - get_invoices         : Customer invoices from account.move
  - get_payments         : Payments from account.payment
  - get_account_balances : Chart of accounts balances
  - get_overdue_invoices : Unpaid invoices past due date
  - odoo_status          : Connection health check
"""

import json
import os
import xmlrpc.client
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

# ── Load credentials ──────────────────────────────────────────────────────────
_vault_root = Path(__file__).parent.parent
load_dotenv(_vault_root / ".env")

ODOO_URL      = os.environ.get("ODOO_URL",      "http://localhost:8069")
ODOO_DB       = os.environ.get("ODOO_DB",       "ai_employee_db")
ODOO_USER     = os.environ.get("ODOO_LOGIN",    os.environ.get("ODOO_USER", ""))
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "")

# ── XML-RPC helpers ───────────────────────────────────────────────────────────

def _authenticate() -> int:
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise RuntimeError(
            f"Odoo auth failed for user '{ODOO_USER}'. "
            "Check ODOO_LOGIN and ODOO_PASSWORD in .env"
        )
    return uid


def _models():
    return xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def _query(model: str, domain: list, fields: list, limit: int = 50) -> list:
    uid = _authenticate()
    return _models().execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        model, "search_read",
        [domain],
        {"fields": fields, "limit": limit},
    )


# ── MCP Server ────────────────────────────────────────────────────────────────

mcp = FastMCP(
    "odoo",
    instructions=(
        "Odoo ERP connector for AI Employee. "
        "Provides read access to customers, invoices, payments, and account balances. "
        "Write operations (create/update) require HITL approval — do not call them directly."
    ),
)


@mcp.tool()
def odoo_status() -> str:
    """Check Odoo connection health. Returns server version and auth status."""
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        version = common.version()
        uid = _authenticate()
        return json.dumps({
            "status": "connected",
            "server": ODOO_URL,
            "database": ODOO_DB,
            "user": ODOO_USER,
            "uid": uid,
            "odoo_version": version.get("server_version", "unknown"),
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
def search_customers(limit: int = 20) -> str:
    """
    Search for all companies (customers/vendors) in Odoo.
    Returns name, email, phone, city, and whether they are a customer or vendor.
    """
    records = _query(
        "res.partner",
        [["is_company", "=", True]],
        ["name", "email", "phone", "city", "customer_rank", "supplier_rank"],
        limit=limit,
    )
    return json.dumps(records, default=str)


@mcp.tool()
def get_invoices(state: str = "posted", limit: int = 50) -> str:
    """
    Get customer invoices from Odoo.

    Args:
        state: Invoice state — 'draft', 'posted', or 'cancel'. Default: 'posted'
        limit: Max records to return. Default: 50
    """
    records = _query(
        "account.move",
        [["move_type", "=", "out_invoice"], ["state", "=", state]],
        ["name", "partner_id", "invoice_date", "invoice_date_due",
         "amount_untaxed", "amount_tax", "amount_total", "payment_state", "state"],
        limit=limit,
    )
    return json.dumps(records, default=str)


@mcp.tool()
def get_overdue_invoices() -> str:
    """
    Get all posted customer invoices that are overdue (past due date, unpaid).
    Useful for flagging in CEO Briefings.
    """
    today = date.today().isoformat()
    records = _query(
        "account.move",
        [
            ["move_type", "=", "out_invoice"],
            ["state", "=", "posted"],
            ["payment_state", "in", ["not_paid", "partial"]],
            ["invoice_date_due", "<", today],
        ],
        ["name", "partner_id", "invoice_date_due", "amount_residual", "payment_state"],
        limit=50,
    )
    return json.dumps(records, default=str)


@mcp.tool()
def get_payments(limit: int = 50) -> str:
    """
    Get recent customer payments recorded in Odoo.

    Args:
        limit: Max records to return. Default: 50
    """
    records = _query(
        "account.payment",
        [["payment_type", "=", "inbound"], ["state", "=", "posted"]],
        ["name", "partner_id", "date", "amount", "currency_id", "state"],
        limit=limit,
    )
    return json.dumps(records, default=str)


@mcp.tool()
def get_account_balances(limit: int = 30) -> str:
    """
    Get chart of accounts with current balances.
    Useful for generating accounting summaries and CEO Briefings.

    Args:
        limit: Max accounts to return. Default: 30
    """
    records = _query(
        "account.account",
        [],  # Odoo 19 removed the 'deprecated' field; fetch all active accounts
        ["code", "name", "account_type", "current_balance"],
        limit=limit,
    )
    return json.dumps(records, default=str)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
