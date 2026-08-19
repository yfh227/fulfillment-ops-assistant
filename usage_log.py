"""SQLite usage logging for the fulfillment ops assistant.

One row per ask, successful or not. Answer analysis (refusal detection,
review-flag detection, citation extraction) is imported from core so it stays
identical to what eval.py scores against.

Agent runs are logged separately, in agent_run and agent_step, rather than
being forced into the `usage` table. An ask is one question and one answer; an
agent run is a bounded loop of reasoning turns and tool calls, and flattening
it into a single row would either lose the tool calls or make every existing
column meaningless for half the rows. Same database, same conventions, own
shape.

Every statement is parameterized; no value is ever interpolated into SQL.
"""

import json
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

SCHEMA_AGENT_RUN = """
CREATE TABLE IF NOT EXISTS agent_run (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         TEXT    NOT NULL,
    question          TEXT    NOT NULL,
    role              TEXT    NOT NULL,
    answer            TEXT,
    turns             INTEGER,
    stop_reason       TEXT,
    requires_approval INTEGER,
    hit_turn_cap      INTEGER,
    denied_tools      TEXT,
    latency_ms        INTEGER,
    input_tokens      INTEGER,
    output_tokens     INTEGER,
    error             TEXT
)
"""

SCHEMA_AGENT_STEP = """
CREATE TABLE IF NOT EXISTS agent_step (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id     INTEGER NOT NULL REFERENCES agent_run(id),
    seq        INTEGER NOT NULL,
    turn       INTEGER NOT NULL,
    kind       TEXT    NOT NULL,
    tool       TEXT,
    tool_input TEXT,
    denied     INTEGER,
    status     TEXT,
    text       TEXT
)
"""


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open a fresh connection.

    Deliberately per-call: Streamlit serves reruns from a pool of threads, and
    a SQLite connection may only be used on the thread that created it.
    """
    return sqlite3.connect(db_path)


def init(db_path: Path = DB_PATH) -> None:
    """Create every table if absent. Safe to call repeatedly."""
    with _connect(db_path) as conn:
        conn.execute(SCHEMA)
        conn.execute(SCHEMA_AGENT_RUN)
        conn.execute(SCHEMA_AGENT_STEP)


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


def log_agent_run(
    result: dict = None,
    question: str = None,
    role: str = None,
    error: BaseException = None,
    db_path: Path = DB_PATH,
) -> int:
    """Write one agent_run row plus its agent_step rows. Returns the run id.

    Pass `result` from agent.run_agent on success, or `error` with `question`
    and `role` on failure - mirroring log_call, a failed run is still recorded
    with the exception in `error` and the result columns left NULL.

    Run and steps are written in one transaction, so a run never lands without
    the steps that explain it.
    """
    init(db_path)

    if error is not None:
        row = (datetime.now(timezone.utc).isoformat(), question or "", role or "",
               None, None, None, None, None, None, None, None, None,
               f"{type(error).__name__}: {error}")
        steps = []
    else:
        row = (
            datetime.now(timezone.utc).isoformat(),
            result.get("question") or question or "",
            result.get("role") or role or "",
            result.get("answer"),
            result.get("turns"),
            result.get("stop_reason"),
            int(bool(result.get("requires_approval"))),
            int(bool(result.get("hit_turn_cap"))),
            ",".join(result.get("denied_tools") or []) or None,
            result.get("latency_ms"),
            result.get("input_tokens"),
            result.get("output_tokens"),
            None,
        )
        steps = result.get("steps") or []

    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO agent_run (
                timestamp, question, role, answer, turns, stop_reason,
                requires_approval, hit_turn_cap, denied_tools, latency_ms,
                input_tokens, output_tokens, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            row,
        )
        run_id = cursor.lastrowid

        conn.executemany(
            """
            INSERT INTO agent_step (
                run_id, seq, turn, kind, tool, tool_input, denied, status, text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    run_id,
                    seq,
                    step.get("turn"),
                    step.get("kind"),
                    step.get("tool"),
                    json.dumps(step["input"]) if step.get("input") is not None else None,
                    None if step.get("denied") is None else int(step["denied"]),
                    step.get("status"),
                    step.get("text"),
                )
                for seq, step in enumerate(steps, start=1)
            ],
        )
        return run_id


def record_feedback(
    row_id: int, feedback: str, note: str = None, db_path: Path = DB_PATH
) -> None:
    """Attach feedback to a previously logged row."""
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE usage SET feedback = ?, feedback_note = ? WHERE id = ?",
            (feedback, note, row_id),
        )
