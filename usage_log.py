"""SQLite usage logging for the fulfillment ops assistant.

One row per ask, successful or not. Answer analysis (refusal detection,
review-flag detection, citation extraction) is imported from core so it stays
identical to what eval.py scores against.

Every statement is parameterized; no value is ever interpolated into SQL.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core import cited_docs, refused, review_flagged

DB_PATH = Path(__file__).parent / "usage.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS usage (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp      TEXT    NOT NULL,
    question       TEXT    NOT NULL,
    answer         TEXT,
    latency_ms     INTEGER,
    input_tokens   INTEGER,
    output_tokens  INTEGER,
    cited_docs     TEXT,
    review_flagged INTEGER,
    refused        INTEGER,
    error          TEXT,
    feedback       TEXT,
    feedback_note  TEXT
)
"""


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open a fresh connection.

    Deliberately per-call: Streamlit serves reruns from a pool of threads, and
    a SQLite connection may only be used on the thread that created it.
    """
    return sqlite3.connect(db_path)


def init(db_path: Path = DB_PATH) -> None:
    """Create the table if absent. Safe to call repeatedly."""
    with _connect(db_path) as conn:
        conn.execute(SCHEMA)


def log_call(
    question: str,
    result: dict = None,
    error: BaseException = None,
    documents=(),
    db_path: Path = DB_PATH,
) -> int:
    """Write one row and return its id, so feedback can attach to it later.

    Pass `result` from core.ask on success, or `error` on failure - a failed
    call is still logged, with the exception in `error` and every result
    column left NULL.

    `documents` is the known document list, either (filename, text) pairs or
    bare filenames; only those filenames can be recorded as citations.
    """
    init(db_path)

    known = [d[0] if isinstance(d, (tuple, list)) else d for d in documents]

    if error is not None:
        row = {
            "answer": None,
            "latency_ms": None,
            "input_tokens": None,
            "output_tokens": None,
            "cited_docs": None,
            "review_flagged": None,
            "refused": None,
            "error": f"{type(error).__name__}: {error}",
        }
    else:
        answer = result["answer"]
        row = {
            "answer": answer,
            "latency_ms": result.get("latency_ms"),
            "input_tokens": result.get("input_tokens"),
            "output_tokens": result.get("output_tokens"),
            "cited_docs": ",".join(cited_docs(answer, known)),
            "review_flagged": int(review_flagged(answer)),
            "refused": int(refused(answer)),
            "error": None,
        }

    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO usage (
                timestamp, question, answer, latency_ms, input_tokens,
                output_tokens, cited_docs, review_flagged, refused, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                question,
                row["answer"],
                row["latency_ms"],
                row["input_tokens"],
                row["output_tokens"],
                row["cited_docs"],
                row["review_flagged"],
                row["refused"],
                row["error"],
            ),
        )
        return cursor.lastrowid


def record_feedback(
    row_id: int, feedback: str, note: str = None, db_path: Path = DB_PATH
) -> None:
    """Attach feedback to a previously logged row."""
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE usage SET feedback = ?, feedback_note = ? WHERE id = ?",
            (feedback, note, row_id),
        )
