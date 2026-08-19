"""Read-only accessor for the operational fixtures.

Tools go through here rather than reading `fixtures/*.json` directly, so
swapping the backing store for SQLite in Phase 2 changes this module and
nothing else.

JSON rather than a database on purpose: `eval_roles.py` asserts exact outcomes
across a role x tool matrix, and any source that varies between runs would
reintroduce the flakiness Part 5 spent real effort separating from genuine
defects. A fixture diff is also legible in review; a binary database is not.
"""

import json
from functools import lru_cache
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
ORDERS_PATH = FIXTURES / "orders.json"
INVENTORY_PATH = FIXTURES / "inventory.json"
INVOICES_PATH = FIXTURES / "invoices.json"
RATE_SCHEDULES_PATH = FIXTURES / "rate_schedules.json"
CAPACITY_PATH = FIXTURES / "capacity.json"


def _load(path: Path, key: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return {row[key]: row for row in json.load(f)}


@lru_cache(maxsize=1)
def _orders() -> dict:
    return _load(ORDERS_PATH, "order_id")


@lru_cache(maxsize=1)
def _inventory() -> dict:
    return _load(INVENTORY_PATH, "sku")


@lru_cache(maxsize=1)
def _invoices() -> dict:
    return _load(INVOICES_PATH, "invoice_id")


@lru_cache(maxsize=1)
def _rate_schedules() -> dict:
    # Keyed on client name rather than an id: a rate schedule is looked up by
    # who it belongs to, which is also how the agent will have it from an
    # invoice.
    return {k.upper(): v for k, v in _load(RATE_SCHEDULES_PATH, "client").items()}


@lru_cache(maxsize=1)
def _capacity() -> dict:
    return {k.upper(): v for k, v in _load(CAPACITY_PATH, "facility").items()}


def get_order(order_id: str) -> dict | None:
    """One order record, or None. Returns a copy - the cache is shared."""
    row = _orders().get((order_id or "").strip().upper())
    return dict(row) if row else None


def get_sku(sku: str) -> dict | None:
    """One inventory record, or None. Returns a copy - the cache is shared."""
    row = _inventory().get((sku or "").strip().upper())
    return dict(row) if row else None


def get_invoice(invoice_id: str) -> dict | None:
    """One invoice record, or None. Returns a copy - the cache is shared."""
    row = _invoices().get((invoice_id or "").strip().upper())
    return dict(row) if row else None


def get_rate_schedule(client: str) -> dict | None:
    """One client's contracted rates, or None. Returns a copy."""
    row = _rate_schedules().get((client or "").strip().upper())
    return dict(row) if row else None


def get_capacity(facility: str) -> dict | None:
    """One facility's capacity position, or None. Returns a copy."""
    row = _capacity().get((facility or "").strip().upper())
    return dict(row) if row else None


def all_order_ids() -> list[str]:
    return sorted(_orders())


def all_skus() -> list[str]:
    return sorted(_inventory())


def all_invoice_ids() -> list[str]:
    return sorted(_invoices())


def all_rate_clients() -> list[str]:
    return sorted(row["client"] for row in _rate_schedules().values())


def all_facilities() -> list[str]:
    return sorted(row["facility"] for row in _capacity().values())
