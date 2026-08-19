"""Reporting queries over usage.db.

Run directly to print every section to the terminal:

    python stats.py [path/to/usage.db]

write_summary() renders the same underlying numbers as adoption_summary.md,
the artifact intended for a non-technical reader.

Rows recording a failed call (error IS NOT NULL) carry NULL result columns, so
guardrail and latency figures exclude them - averaging over them would silently
treat an outage as a fast, unflagged answer.
"""

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from usage_log import DB_PATH

SUMMARY_PATH = Path(__file__).parent / "adoption_summary.md"

VOLUME_BY_DAY = """
SELECT substr(timestamp, 1, 10)                     AS day,
       COUNT(*)                                     AS calls,
       COALESCE(SUM(input_tokens), 0)               AS input_tokens,
       COALESCE(SUM(output_tokens), 0)              AS output_tokens,
       COALESCE(SUM(input_tokens + output_tokens), 0) AS total_tokens
FROM usage
GROUP BY day
ORDER BY day
"""

GUARDRAIL_RATES = """
SELECT COUNT(*)                                          AS answered,
       COALESCE(SUM(review_flagged), 0)                  AS flagged,
       COALESCE(SUM(refused), 0)                         AS refused,
       ROUND(100.0 * SUM(review_flagged) / COUNT(*), 1)  AS pct_flagged,
       ROUND(100.0 * SUM(refused) / COUNT(*), 1)         AS pct_refused
FROM usage
WHERE error IS NULL
"""

# cited_docs holds a comma-separated list, so it is split into one row per
# filename before counting.
TOP_DOCUMENTS = """
WITH RECURSIVE split(doc, rest) AS (
    SELECT '', cited_docs || ','
    FROM usage
    WHERE cited_docs IS NOT NULL AND cited_docs <> ''
    UNION ALL
    SELECT substr(rest, 1, instr(rest, ',') - 1),
           substr(rest, instr(rest, ',') + 1)
    FROM split
    WHERE rest <> ''
)
SELECT doc AS document, COUNT(*) AS citations
FROM split
WHERE doc <> ''
GROUP BY doc
ORDER BY citations DESC, document ASC
"""

PERFORMANCE = """
SELECT COUNT(*)                     AS measured,
       ROUND(AVG(latency_ms), 0)    AS avg_ms,
       MIN(latency_ms)              AS min_ms,
       MAX(latency_ms)              AS max_ms
FROM usage
WHERE error IS NULL AND latency_ms IS NOT NULL
"""

ERROR_COUNT = """
SELECT COUNT(*) AS errors
FROM usage
WHERE error IS NOT NULL
"""

FEEDBACK_SPLIT = """
SELECT COUNT(*)                                            AS with_feedback,
       COALESCE(SUM(CASE WHEN feedback = 'up' THEN 1 END), 0)   AS thumbs_up,
       COALESCE(SUM(CASE WHEN feedback = 'down' THEN 1 END), 0) AS thumbs_down
FROM usage
WHERE feedback IS NOT NULL
"""


# --------------------------------------------------------------------------
# Agent runs (V5)
#
# Separate from the `usage` queries above because an agent run is a bounded
# loop of turns and tool calls, not one question and one answer. Reported in
# its own sections rather than averaged in with asks, which would make both
# sets of figures harder to read and neither more accurate.
# --------------------------------------------------------------------------

AGENT_VOLUME_BY_DAY = """
SELECT substr(timestamp, 1, 10)                        AS day,
       COUNT(*)                                        AS runs,
       COALESCE(SUM(input_tokens), 0)                  AS input_tokens,
       COALESCE(SUM(output_tokens), 0)                 AS output_tokens
FROM agent_run
GROUP BY day
ORDER BY day
"""

AGENT_GUARDRAIL = """
SELECT COUNT(*)                                              AS runs,
       COALESCE(SUM(requires_approval), 0)                   AS approvals,
       COALESCE(SUM(hit_turn_cap), 0)                        AS turn_caps,
       COALESCE(SUM(CASE WHEN denied_tools IS NOT NULL THEN 1 END), 0) AS with_denials,
       ROUND(AVG(turns), 2)                                  AS avg_turns,
       ROUND(AVG(latency_ms), 0)                             AS avg_ms
FROM agent_run
WHERE error IS NULL
"""

AGENT_BY_ROLE = """
SELECT role,
       COUNT(*)                            AS runs,
       COALESCE(SUM(requires_approval), 0) AS approvals
FROM agent_run
WHERE error IS NULL
GROUP BY role
ORDER BY runs DESC, role ASC
"""

TOOL_USAGE = """
SELECT tool,
       COUNT(*)                                        AS calls,
       COALESCE(SUM(denied), 0)                        AS denied
FROM agent_step
WHERE kind = 'tool_call' AND tool IS NOT NULL
GROUP BY tool
ORDER BY calls DESC, tool ASC
"""

AGENT_ERROR_COUNT = """
SELECT COUNT(*) AS errors FROM agent_run WHERE error IS NOT NULL
"""


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    """Databases written before V5 have no agent tables; report around them."""
    return bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,),
    ).fetchone())


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _rows(conn: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    return conn.execute(query).fetchall()


def _pct(part: int, whole: int) -> float:
    return round(100.0 * part / whole, 1) if whole else 0.0


def _heading(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def summary_stats(db_path: Path = DB_PATH) -> dict:
    """Headline figures for the app sidebar.

    Uses the same queries - and therefore the same error-row exclusions - as
    report(), so the sidebar cannot disagree with the CLI. Returns zeros rather
    than raising when the database is missing or empty, and never creates the
    file as a side effect of being asked.
    """
    empty = {
        "answered": 0,
        "pct_flagged": 0.0,
        "pct_refused": 0.0,
        "avg_ms": None,
        "measured": 0,
    }
    if not Path(db_path).exists():
        return empty

    try:
        with connect(db_path) as conn:
            g = _rows(conn, GUARDRAIL_RATES)[0]
            p = _rows(conn, PERFORMANCE)[0]
    except sqlite3.OperationalError:
        # Database file exists but the table has not been created yet.
        return empty

    return {
        "answered": g["answered"],
        "pct_flagged": _pct(g["flagged"], g["answered"]),
        "pct_refused": _pct(g["refused"], g["answered"]),
        "avg_ms": p["avg_ms"] if p["measured"] else None,
        "measured": p["measured"],
    }


def report(db_path: Path = DB_PATH) -> None:
    """Print every section to stdout."""
    with connect(db_path) as conn:
        _heading("VOLUME AND TOKENS BY DAY")
        rows = _rows(conn, VOLUME_BY_DAY)
        if not rows:
            print("(no rows logged yet)")
        else:
            print(f"{'DAY':<12}{'CALLS':>7}{'INPUT':>10}{'OUTPUT':>9}{'TOTAL':>10}")
            for r in rows:
                print(
                    f"{r['day']:<12}{r['calls']:>7}{r['input_tokens']:>10,}"
                    f"{r['output_tokens']:>9,}{r['total_tokens']:>10,}"
                )

        _heading("GUARDRAIL RATES (excluding error rows)")
        g = _rows(conn, GUARDRAIL_RATES)[0]
        print(f"answered      : {g['answered']}")
        print(f"flagged       : {g['flagged']}  ({g['pct_flagged'] or 0.0}%)")
        print(f"refused       : {g['refused']}  ({g['pct_refused'] or 0.0}%)")

        _heading("MOST-CITED DOCUMENTS")
        rows = _rows(conn, TOP_DOCUMENTS)
        if not rows:
            print("(no citations recorded yet)")
        else:
            for r in rows:
                print(f"{r['citations']:>4}  {r['document']}")

        _heading("PERFORMANCE (excluding error rows)")
        p = _rows(conn, PERFORMANCE)[0]
        if not p["measured"]:
            print("(no successful calls yet)")
        else:
            print(f"calls measured: {p['measured']}")
            print(f"avg latency   : {p['avg_ms']:,.0f} ms")
            print(f"min latency   : {p['min_ms']:,} ms")
            print(f"max latency   : {p['max_ms']:,} ms")

        _heading("ERRORS")
        print(f"error rows    : {_rows(conn, ERROR_COUNT)[0]['errors']}")

        _heading("FEEDBACK")
        f = _rows(conn, FEEDBACK_SPLIT)[0]
        print(f"with feedback : {f['with_feedback']}")
        print(f"thumbs up     : {f['thumbs_up']}")
        print(f"thumbs down   : {f['thumbs_down']}")

        if not _table_exists(conn, "agent_run"):
            print()
            return

        _heading("AGENT RUNS")
        rows = _rows(conn, AGENT_VOLUME_BY_DAY)
        if not rows:
            print("(no agent runs logged yet)")
        else:
            print(f"{'DAY':<12}{'RUNS':>7}{'INPUT':>10}{'OUTPUT':>9}")
            for r in rows:
                print(f"{r['day']:<12}{r['runs']:>7}{r['input_tokens']:>10,}"
                      f"{r['output_tokens']:>9,}")

            a = _rows(conn, AGENT_GUARDRAIL)[0]
            print()
            print(f"runs measured : {a['runs']}")
            print(f"needing approval: {a['approvals']}  "
                  f"({_pct(a['approvals'], a['runs'])}%)")
            print(f"with a denied tool: {a['with_denials']}  "
                  f"({_pct(a['with_denials'], a['runs'])}%)")
            print(f"hit turn cap  : {a['turn_caps']}")
            print(f"avg turns     : {a['avg_turns']}")
            print(f"avg latency   : {a['avg_ms']:,.0f} ms" if a["avg_ms"]
                  else "avg latency   : -")
            print(f"error rows    : {_rows(conn, AGENT_ERROR_COUNT)[0]['errors']}")

            _heading("AGENT RUNS BY ROLE")
            for r in _rows(conn, AGENT_BY_ROLE):
                print(f"{r['role']:<18}{r['runs']:>5} runs   "
                      f"{r['approvals']:>3} needing approval")

        _heading("TOOL CALLS")
        rows = _rows(conn, TOOL_USAGE)
        if not rows:
            print("(no tool calls recorded yet)")
        else:
            print(f"{'TOOL':<22}{'CALLS':>7}{'DENIED':>8}")
            for r in rows:
                print(f"{r['tool']:<22}{r['calls']:>7}{r['denied']:>8}")
        print()


def write_summary(db_path: Path = DB_PATH, out_path: Path = SUMMARY_PATH) -> Path:
    """Render the same figures as a short markdown brief for leadership."""
    with connect(db_path) as conn:
        g = _rows(conn, GUARDRAIL_RATES)[0]
        f = _rows(conn, FEEDBACK_SPLIT)[0]
        errors = _rows(conn, ERROR_COUNT)[0]["errors"]
        top = _rows(conn, TOP_DOCUMENTS)[:3]

    answered = g["answered"]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "# Fulfillment Ops Assistant — Adoption Summary",
        "",
        f"_Generated {generated} from {answered} answered "
        f"{'question' if answered == 1 else 'questions'}._",
        "",
        "## Usage",
        "",
        f"- **Questions answered:** {answered}",
        f"- **Failed requests:** {errors}",
        "",
        "## Guardrails",
        "",
        f"- **Flagged for human review:** {_pct(g['flagged'], answered)}% "
        f"({g['flagged']} of {answered})",
        f"- **Declined — not covered by the documents:** "
        f"{_pct(g['refused'], answered)}% ({g['refused']} of {answered})",
        "",
        "## Feedback",
        "",
        f"- **Answers rated:** {f['with_feedback']} of {answered} "
        f"({_pct(f['with_feedback'], answered)}%)",
        f"- **Helpful:** {f['thumbs_up']} · **Not helpful:** {f['thumbs_down']}",
        "",
        "## Most-referenced documents",
        "",
    ]

    if top:
        for i, r in enumerate(top, start=1):
            label = "citation" if r["citations"] == 1 else "citations"
            lines.append(f"{i}. `{r['document']}` — {r['citations']} {label}")
    else:
        lines.append("_No citations recorded yet._")

    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    db = Path(sys.argv[1]) if len(sys.argv) > 1 else DB_PATH
    if not db.exists():
        print(f"No database at {db}. Ask a question in the app first.")
        raise SystemExit(1)
    report(db)
    # Keep the project summary tied to the project database: reporting on some
    # other database writes its summary alongside that file instead of
    # overwriting the real one.
    out = SUMMARY_PATH if db == DB_PATH else db.with_name("adoption_summary.md")
    written = write_summary(db, out)
    print(f"Wrote {written}")
