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


@lru_cache(maxsize=1)
def _orders() -> dict:
    with open(ORDERS_PATH, encoding="utf-8") as f:
        return {row["order_id"]: row for row in json.load(f)}


@lru_cache(maxsize=1)
def _inventory() -> dict:
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        return {row["sku"]: row for row in json.load(f)}


def get_order(order_id: str) -> dict | None:
    """One order record, or None. Returns a copy - the cache is shared."""
    row = _orders().get((order_id or "").strip().upper())
    return dict(row) if row else None


def get_sku(sku: str) -> dict | None:
    """One inventory record, or None. Returns a copy - the cache is shared."""
    row = _inventory().get((sku or "").strip().upper())
    return dict(row) if row else None


def all_order_ids() -> list[str]:
    return sorted(_orders())


def all_skus() -> list[str]:
    return sorted(_inventory())
