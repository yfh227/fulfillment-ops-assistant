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
