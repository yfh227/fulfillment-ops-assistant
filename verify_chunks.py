"""Verify the chunker against the Meridian corpus.

Three checks, all reported per-document rather than in aggregate:

1. No markdown table is split across two chunks.
2. No numbered step is separated from its own sub-detail.
3. Every chunk carries a source filename, and it matches the document.

Plus size distribution and outlier flagging. Reads docs/ from disk; no
Bedrock or S3 calls.
"""

import re
import statistics as st
import sys
from pathlib import Path

from chunking import MAX_CHARS, TABLE_RE, chunk_document, parse_blocks

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOCS = Path(__file__).parent / "docs"
STEP_RE = re.compile(r"^#{2,4}\s+(?:Step\s+\d+|\d+\.)\s", re.I)


def tables_in(text: str) -> list[str]:
    """Every table in a document, as its full text."""
    return [b.text for b in parse_blocks(text) if b.kind == "table"]


def numbered_steps_in(text: str) -> list[str]:
    return [b.text for b in parse_blocks(text)
            if b.kind == "heading" and STEP_RE.match(b.text)]


def main() -> int:
    docs = sorted((p.name, p.read_text(encoding="utf-8"))
                  for p in DOCS.glob("*.md"))
    print(f"documents: {len(docs)}")
    print()

    all_chunks = []
    per_doc = {}
    for name, text in docs:
        cs = chunk_document(name, text)
        per_doc[name] = (text, cs)
        all_chunks.extend(cs)

    failures = 0

    # ---- Check 0: source filename on every chunk -------------------------
    print("=" * 100)
    print("CHECK 0 — every chunk carries its source filename")
    print("=" * 100)
    missing = [c for c in all_chunks if not c.metadata.get("source")]
    wrong = [(n, c) for n, (_, cs) in per_doc.items()
             for c in cs if c.metadata.get("source") != n]
    print(f"  chunks total            : {len(all_chunks)}")
    print(f"  missing source          : {len(missing)}")
    print(f"  source != document name : {len(wrong)}")
    if missing or wrong:
        failures += 1
        print("  FAIL")
    else:
        print("  PASS — all chunks attributable, citation guardrail intact")
    print()

    # ---- Check 1: tables not split, per document -------------------------
    print("=" * 100)
    print("CHECK 1 — no table split across chunks (per document)")
    print("=" * 100)
    print(f"{'DOCUMENT':<52}{'TABLES':>7}{'INTACT':>8}{'SPLIT':>7}  STATUS")
    print("-" * 100)
    total_tables = split_tables = 0
    for name, (text, cs) in per_doc.items():
        tabs = tables_in(text)
        if not tabs:
            continue
        intact = 0
        broken = []
        for t in tabs:
            # normalise whitespace so the chunk header/rejoin cannot mask a hit
            needle = "\n".join(ln.rstrip() for ln in t.splitlines())
            if any(needle in c.text for c in cs):
                intact += 1
            else:
                broken.append(t.splitlines()[0][:60])
        total_tables += len(tabs)
        split_tables += len(broken)
        status = "ok" if not broken else f"SPLIT x{len(broken)}"
        print(f"{name:<52}{len(tabs):>7}{intact:>8}{len(broken):>7}  {status}")
        for b in broken:
            print(f"      broken: {b}")
    print("-" * 100)
    print(f"{'TOTAL':<52}{total_tables:>7}{total_tables - split_tables:>8}"
          f"{split_tables:>7}")
    if split_tables:
        failures += 1
        print("  FAIL")
    else:
        print("  PASS — every table intact within a single chunk")
    print()

    # ---- Check 2: numbered steps keep their sub-detail -------------------
    print("=" * 100)
    print("CHECK 2 — numbered steps not separated from their sub-detail")
    print("=" * 100)
    print(f"{'DOCUMENT':<52}{'STEPS':>7}{'ORPHAN':>8}  STATUS")
    print("-" * 100)
    total_steps = orphans = 0
    for name, (text, cs) in per_doc.items():
        steps = numbered_steps_in(text)
        if not steps:
            continue
        bad = []
        for s in steps:
            for c in cs:
                if s in c.text:
                    after = c.text.split(s, 1)[1].strip()
                    # a step heading that ends its chunk has lost its detail
                    if len(after) < 40:
                        bad.append(s[:60])
                    break
        total_steps += len(steps)
        orphans += len(bad)
        status = "ok" if not bad else f"ORPHANED x{len(bad)}"
        print(f"{name:<52}{len(steps):>7}{len(bad):>8}  {status}")
        for b in bad:
            print(f"      orphaned: {b}")
    print("-" * 100)
    print(f"{'TOTAL':<52}{total_steps:>7}{orphans:>8}")
    if orphans:
        failures += 1
        print("  FAIL")
    else:
        print("  PASS — no step heading left without its content")
    print()

    # extra: no chunk ends on a heading of any kind
    trailing = [c for c in all_chunks
                if c.text.strip().splitlines()[-1].lstrip().startswith("#")]
    print(f"  chunks ending on a bare heading: {len(trailing)}")
    if trailing:
        failures += 1
        for c in trailing[:5]:
            print(f"      {c.source} :: {c.text.strip().splitlines()[-1][:60]}")
    print()

    # ---- Check 3: size distribution and outliers -------------------------
    print("=" * 100)
    print("CHECK 3 — chunk count and size distribution")
    print("=" * 100)
    sizes = [len(c) for c in all_chunks]
    mean = st.mean(sizes)
    sd = st.pstdev(sizes)
    print(f"  chunks          : {len(all_chunks)}")
    print(f"  min / mean / max: {min(sizes):,} / {mean:,.0f} / {max(sizes):,} chars")
    print(f"  median          : {st.median(sizes):,.0f}")
    print(f"  std dev         : {sd:,.0f}")
    print(f"  total chars     : {sum(sizes):,}")
    print(f"  est. tokens     : ~{sum(sizes) / 3.5:,.0f}")
    print(f"  cap             : {MAX_CHARS:,} (fallback only)")
    print(f"  over cap        : {sum(1 for s in sizes if s > MAX_CHARS)}")
    print()

    print("  chunks per document:")
    print(f"  {'DOCUMENT':<52}{'CHUNKS':>7}{'MIN':>8}{'MEAN':>8}{'MAX':>8}")
    for name, (_, cs) in per_doc.items():
        s = [len(c) for c in cs]
        print(f"  {name:<52}{len(cs):>7}{min(s):>8,}{st.mean(s):>8,.0f}{max(s):>8,}")
    print()

    hi = mean + 2 * sd
    lo = max(200, mean - 2 * sd)
    outliers = [c for c in all_chunks if len(c) > hi or len(c) < lo]
    print(f"  outliers (>2 sd from mean, i.e. <{lo:,.0f} or >{hi:,.0f} chars): "
          f"{len(outliers)}")
    for c in sorted(outliers, key=len, reverse=True)[:12]:
        kind = "LARGE" if len(c) > hi else "small"
        sec = c.metadata["section"] or "(document head)"
        print(f"      {kind:<5} {len(c):>6,}  {c.source:<44} {sec[:40]}")
    print()

    print("=" * 100)
    print(f"RESULT: {'ALL CHECKS PASSED' if not failures else f'{failures} CHECK(S) FAILED'}")
    print("=" * 100)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
