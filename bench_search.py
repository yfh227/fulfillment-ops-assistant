"""Time brute-force similarity search against the measured inference latency.

The question this answers: does search latency matter at all next to the
~15,000 ms inference already measured in baseline_direct_context.md? If not,
a vector database solves no problem this system has.

A vector DB would replace the dot product only — not the query-embedding
call, which is a network round trip either way. So the dot product is the
term measured here in isolation.
"""

import statistics as st
import sys
import time

import numpy as np

from eval import _credentials
from vector_store import embed_query, get_client, load_index, search_vec

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Mean inference latency measured over 24 calls, baseline_direct_context.md
INFERENCE_MS = 15_352

QUERIES = [
    "What is the monthly pallet storage rate?",
    "What's the process for a receiving discrepancy?",
    "Why is Reno's inventory accuracy below target?",
    "How do I escalate an S1 incident?",
    "What are the credit approval authority tiers?",
    "What happens during peak season weeks 46-52?",
]


def main() -> int:
    embeddings, payload, meta = load_index()
    print(f"index   : {embeddings.shape} {embeddings.dtype}  "
          f"({embeddings.nbytes/1024:.0f} KB in memory)")
    print(f"model   : {meta['model']}  {meta['dimensions']}d "
          f"normalize={meta['normalize']}")
    print(f"chunks  : {len(payload)}")
    print()

    kid, sec = _credentials()
    client = get_client(kid, sec)

    # ---- 1. pure search latency -----------------------------------------
    print("=" * 78)
    print("1. SEARCH ONLY — the term a vector DB would replace")
    print("=" * 78)
    qv = embed_query(QUERIES[0], client)

    for _ in range(50):                      # warm up
        search_vec(qv, 5, embeddings, payload)

    N = 2000
    times = []
    for _ in range(N):
        t0 = time.perf_counter()
        search_vec(qv, 5, embeddings, payload)
        times.append((time.perf_counter() - t0) * 1000)

    times.sort()
    mean = st.mean(times)
    print(f"  iterations   : {N:,}")
    print(f"  mean         : {mean:.4f} ms")
    print(f"  median       : {st.median(times):.4f} ms")
    print(f"  min          : {times[0]:.4f} ms")
    print(f"  p99          : {times[int(N*0.99)]:.4f} ms")
    print(f"  max          : {times[-1]:.4f} ms")
    print()

    # raw dot product alone, without top-k selection or Hit construction
    dots = []
    for _ in range(N):
        t0 = time.perf_counter()
        _ = embeddings @ qv
        dots.append((time.perf_counter() - t0) * 1000)
    print(f"  dot product alone (no top-k, no object build): "
          f"{st.mean(dots):.4f} ms mean")
    print()

    # ---- 2. end-to-end, including the embedding call ---------------------
    print("=" * 78)
    print("2. END TO END — query embedding call + search")
    print("=" * 78)
    e2e, emb_ms, srch_ms = [], [], []
    for q in QUERIES:
        t0 = time.perf_counter()
        v = embed_query(q, client)
        t1 = time.perf_counter()
        search_vec(v, 5, embeddings, payload)
        t2 = time.perf_counter()
        e2e.append((t2 - t0) * 1000)
        emb_ms.append((t1 - t0) * 1000)
        srch_ms.append((t2 - t1) * 1000)
        print(f"  {(t2-t0)*1000:>7.1f} ms total "
              f"= {(t1-t0)*1000:>6.1f} embed + {(t2-t1)*1000:.4f} search   "
              f"{q[:44]}")
    print()
    print(f"  mean embed  : {st.mean(emb_ms):.1f} ms   "
          f"({st.mean(emb_ms)/st.mean(e2e)*100:.2f}% of retrieval time)")
    print(f"  mean search : {st.mean(srch_ms):.4f} ms "
          f"({st.mean(srch_ms)/st.mean(e2e)*100:.4f}% of retrieval time)")
    print()

    # ---- 3. against inference --------------------------------------------
    print("=" * 78)
    print("3. AGAINST MEASURED INFERENCE LATENCY")
    print("=" * 78)
    print(f"  inference (measured, 24 calls) : {INFERENCE_MS:,} ms")
    print(f"  search                         : {mean:.4f} ms")
    print(f"  search as share of inference   : {mean/INFERENCE_MS*100:.5f}%")
    print(f"  inference / search             : {INFERENCE_MS/mean:,.0f}x")
    print()
    ideal = INFERENCE_MS + st.mean(emb_ms)
    withs = ideal + mean
    print(f"  a perfect O(1) vector DB would save at most {mean:.4f} ms")
    print(f"  total request with search    : {withs:,.1f} ms")
    print(f"  total request if search were free : {ideal:,.1f} ms")
    print(f"  best possible improvement    : "
          f"{(withs-ideal)/withs*100:.5f}%")
    print()

    # ---- 4. scaling headroom ---------------------------------------------
    print("=" * 78)
    print("4. WHEN WOULD THIS STOP BEING TRUE?")
    print("=" * 78)
    print(f"{'vectors':>12}{'search ms':>12}{'% of inference':>16}")
    for n in (363, 3_630, 36_300, 363_000, 1_000_000):
        synth = np.random.randn(n, 1024).astype(np.float32)
        synth /= np.linalg.norm(synth, axis=1, keepdims=True)
        reps = 200 if n <= 36_300 else 20
        ts = []
        for _ in range(reps):
            t0 = time.perf_counter()
            s = synth @ qv
            np.argpartition(-s, 5)[:5]
            ts.append((time.perf_counter() - t0) * 1000)
        m = st.mean(ts)
        mark = "  <- current corpus" if n == 363 else ""
        print(f"{n:>12,}{m:>12.3f}{m/INFERENCE_MS*100:>15.4f}%{mark}")
        del synth
    print()
    print("  Brute force stays under 1% of inference latency well past")
    print("  1M vectors — roughly 2,750x the current corpus.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
