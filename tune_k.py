"""Sweep retrieval K against the eval and report the whole trade-off curve.

Runs the eight eval cases at each K, three times, and reports pass rate, which
cases fail, tokens, latency and cost. Query embeddings are computed once per
question and reused across every K and run — the vector does not change, only
the cut-off does.

Reports the full curve rather than stopping at the first K that passes: the
useful result is the shape, including where retrieval's cost advantage over
prompt-cached direct context disappears.
"""

import json
import statistics as st
import sys
import time
from pathlib import Path

from core import RELEVANCE_FLOOR, ask, retrieve_context
from eval import CASES, _credentials, grade
from vector_store import embed_query, get_client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

K_VALUES = [6, 10, 14, 18, 24]
RUNS = 3

IN_RATE = 3.30 / 1e6
OUT_RATE = 16.50 / 1e6

# Incumbents to beat, from baseline_direct_context.md / baseline_prompt_caching.md
DIRECT_UNCACHED_PER_100 = 27.20
DIRECT_CACHED_PER_100 = 4.86
DIRECT_INPUT_TOKENS = 79_667
DIRECT_LATENCY_MS = 15_352

OUT = Path(__file__).parent / "tuning_k_results.json"


def main() -> int:
    kid, sec = _credentials()
    client = get_client(kid, sec)

    print("pre-embedding the eight questions once (reused across all K)")
    qvecs = {c["name"]: embed_query(c["question"], client) for c in CASES}
    print(f"  {len(qvecs)} vectors cached\n")

    results = []
    t_start = time.perf_counter()

    for k in K_VALUES:
        print("=" * 96)
        print(f"K = {k}   (floor={RELEVANCE_FLOOR})")
        print("=" * 96)
        for run in range(1, RUNS + 1):
            row = {"k": k, "run": run, "cases": []}
            for c in CASES:
                ctx, hits = retrieve_context(
                    c["question"], client, k=k, query_vec=qvecs[c["name"]])
                r = ask(c["question"], ctx, client, use_cache=False,
                        use_retrieval=False)
                checks = grade(c, r["answer"])
                passed = all(v for v in checks.values() if v is not None)
                row["cases"].append({
                    "name": c["name"], "passed": passed,
                    "failed_checks": [n for n, v in checks.items() if v is False],
                    "in": r["input_tokens"], "out": r["output_tokens"],
                    "latency": r["latency_ms"], "chunks": len(hits),
                    "docs": len({h.source for h in hits}),
                    "ctx_chars": len(ctx),
                })
            npass = sum(1 for x in row["cases"] if x["passed"])
            row["passed"] = npass
            results.append(row)
            fails = [x["name"] for x in row["cases"] if not x["passed"]]
            mi = st.mean(x["in"] for x in row["cases"])
            ml = st.mean(x["latency"] for x in row["cases"])
            print(f"  run {run}: {npass}/8  "
                  f"in={mi:>7,.0f}  lat={ml:>7,.0f}ms  "
                  f"fails={fails if fails else '—'}")
        print()

    elapsed = time.perf_counter() - t_start
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    # ---------------- summary ----------------
    print("=" * 96)
    print("CURVE")
    print("=" * 96)
    print(f"{'K':>4}{'PASS':>18}{'IN tok':>10}{'OUT tok':>9}{'LATENCY':>10}"
          f"{'$/100':>9}{'vs cached':>11}{'chunks':>8}{'docs':>6}")
    print("-" * 96)
    summary = []
    for k in K_VALUES:
        rows = [r for r in results if r["k"] == k]
        cases = [c for r in rows for c in r["cases"]]
        mi = st.mean(c["in"] for c in cases)
        mo = st.mean(c["out"] for c in cases)
        ml = st.mean(c["latency"] for c in cases)
        cost100 = (mi * IN_RATE + mo * OUT_RATE) * 100
        passes = "/".join(str(r["passed"]) for r in rows)
        vs = ((cost100 / DIRECT_CACHED_PER_100) - 1) * 100
        summary.append({"k": k, "in": mi, "out": mo, "lat": ml,
                        "cost100": cost100, "passes": passes})
        print(f"{k:>4}{passes:>18}{mi:>10,.0f}{mo:>9,.0f}{ml:>9,.0f}ms"
              f"{cost100:>9.2f}{vs:>+10.0f}%"
              f"{st.mean(c['chunks'] for c in cases):>8.1f}"
              f"{st.mean(c['docs'] for c in cases):>6.1f}")
    print("-" * 96)
    print(f"{'direct (uncached)':>22}{DIRECT_INPUT_TOKENS:>10,}"
          f"{'':>9}{DIRECT_LATENCY_MS:>9,}ms{DIRECT_UNCACHED_PER_100:>9.2f}")
    print(f"{'direct (cached)':>22}{DIRECT_INPUT_TOKENS:>10,}"
          f"{'':>9}{DIRECT_LATENCY_MS:>9,}ms{DIRECT_CACHED_PER_100:>9.2f}")
    print()

    # ---------------- per-case behaviour ----------------
    print("=" * 96)
    print("PER-CASE PASS RATE (out of 3 runs at each K)")
    print("=" * 96)
    names = [c["name"] for c in CASES]
    print(f"{'CASE':<32}" + "".join(f"{'K='+str(k):>8}" for k in K_VALUES))
    print("-" * 96)
    for n in names:
        cells = []
        for k in K_VALUES:
            rows = [r for r in results if r["k"] == k]
            p = sum(1 for r in rows
                    for c in r["cases"] if c["name"] == n and c["passed"])
            cells.append(f"{p}/3")
        print(f"{n:<32}" + "".join(f"{c:>8}" for c in cells))
    print()

    print("failed checks by case and K:")
    for n in names:
        line = []
        for k in K_VALUES:
            rows = [r for r in results if r["k"] == k]
            ch = sorted({f for r in rows for c in r["cases"]
                         if c["name"] == n for f in c["failed_checks"]})
            line.append(f"K{k}:{','.join(ch) if ch else '-'}")
        if any(":-" not in x for x in line):
            print(f"  {n:<32}{'  '.join(line)}")
    print()

    # ---------------- crossover ----------------
    print("=" * 96)
    print("COST CROSSOVER")
    print("=" * 96)
    mo_all = st.mean(c["out"] for r in results for c in r["cases"])
    budget_cached = (DIRECT_CACHED_PER_100 / 100 - mo_all * OUT_RATE) / IN_RATE
    budget_uncached = (DIRECT_UNCACHED_PER_100 / 100 - mo_all * OUT_RATE) / IN_RATE
    print(f"  mean output tokens across the sweep : {mo_all:,.0f}")
    print(f"  input budget to match cached direct  : {budget_cached:,.0f} tokens")
    print(f"  input budget to match uncached direct: {budget_uncached:,.0f} tokens")
    print()
    for s in summary:
        v_cached = "beats" if s["cost100"] < DIRECT_CACHED_PER_100 else "LOSES to"
        print(f"  K={s['k']:>2}: {s['in']:>6,.0f} in, ${s['cost100']:.2f}/100 "
              f"— {v_cached} cached direct context (${DIRECT_CACHED_PER_100:.2f})")
    print()
    print(f"  wall clock: {elapsed/60:.1f} min")
    print(f"  written   : {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
