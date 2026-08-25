"""Spend controls for the public, unauthenticated tier.

The login used to be the only thing between a public URL and the deployer's
AWS bill. Opening the assistant to anonymous visitors removes that, so these
caps ship with the public tier rather than after it.

WHY THE PUBLIC TIER IS ALREADY CHEAP
------------------------------------
An earlier version of this module forced the public tier onto the retrieval
path, reasoning from the committed figures of $4.86 per 100 questions for
cached direct context against $1.87 for retrieval. Measurement retired that
reasoning: those numbers describe the full 23-document corpus, and the public
tier sees exactly one document.

    public context      2,862 chars   ~715 tokens    1.0% of the corpus
    full corpus       273,554 chars ~68,388 tokens

At 1% of the context the direct path is already far below either published
figure, so the public tier uses the same code path as every other role rather
than a special-cased one. That also avoids making the main answer path depend
on vector_index.npz; the access pre-check still uses the index, and already
degrades to the ordinary refusal without it.

Output is the component no context strategy reduces, so it is capped directly
by PUBLIC_MAX_OUTPUT_TOKENS.

A LIMIT WORTH UNDERSTANDING BEFORE RELYING ON IT
------------------------------------------------
The daily counter reads usage.db, which is gitignored and therefore absent from
a fresh checkout. Streamlit Community Cloud rebuilds from a clean checkout, so
on a hosted deployment this counter resets on every restart and redeploy. It is
a container-lifetime cap there, not a true daily one.

That still stops the case that actually costs money - one sustained loop against
a running container - but it is not a guarantee, and it should not be described
as one. The real backstop is an AWS Budgets alarm on the account, which lives
outside this application and cannot be bypassed by restarting it.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import usage_log

# Questions an anonymous visitor may ask, across all sessions, per UTC day.
# At retrieval pricing this bounds the public tier near $2/day.
PUBLIC_DAILY_LIMIT = 100

# Per-session courtesy limit. Trivially bypassed by opening a new tab, which is
# why it is a speed bump and the daily cap is the control.
PUBLIC_SESSION_LIMIT = 10

# Cap on generated tokens for public answers. Output is the part no retrieval
# strategy reduces, so it is capped directly.
PUBLIC_MAX_OUTPUT_TOKENS = 600

# Both tables represent Bedrock spend, so both count against the cap.
_COUNT = """
SELECT (SELECT COUNT(*) FROM {table} WHERE substr(timestamp, 1, 10) = ?) AS n
"""


def _count_table(conn: sqlite3.Connection, table: str, day: str) -> int:
    try:
        return conn.execute(_COUNT.format(table=table), (day,)).fetchone()[0]
    except sqlite3.OperationalError:
        # Table not created yet - that is zero calls, not an error.
        return 0


def calls_today(db_path: Path = None) -> int:
    """Bedrock-billed calls recorded for the current UTC day.

    Counts asks and agent runs together. Returns 0 when the database does not
    exist yet, which is the correct reading of "no calls recorded", not a
    failure to be worked around.
    """
    db_path = db_path or usage_log.DB_PATH
    if not Path(db_path).exists():
        return 0
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        with sqlite3.connect(db_path) as conn:
            return _count_table(conn, "usage", day) + _count_table(conn, "agent_run", day)
    except sqlite3.Error:
        # An unreadable database is treated as the cap being reached rather than
        # as zero. This fails closed on purpose: the failure mode of guessing
        # low is an uncapped bill, and the failure mode of guessing high is a
        # demo that says come back later.
        return PUBLIC_DAILY_LIMIT


def daily_remaining(db_path: Path = None) -> int:
    return max(0, PUBLIC_DAILY_LIMIT - calls_today(db_path))


def check_public(session_calls: int, db_path: Path = None) -> tuple[bool, str]:
    """May an anonymous visitor ask another question?

    Returns (allowed, reason). `reason` is empty when allowed and is written for
    a visitor to read, not for a log.
    """
    if session_calls >= PUBLIC_SESSION_LIMIT:
        return False, (
            f"This demo allows {PUBLIC_SESSION_LIMIT} questions per session. "
            "Sign in for full access, or come back later."
        )
    if daily_remaining(db_path) <= 0:
        return False, (
            f"The public demo has used its {PUBLIC_DAILY_LIMIT} questions for "
            "today. It resets at midnight UTC. Sign in for full access."
        )
    return True, ""
