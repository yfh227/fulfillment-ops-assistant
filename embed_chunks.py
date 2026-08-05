"""Embed the chunked Meridian corpus with Titan Text Embeddings V2.

Persists vectors plus each chunk's text and source metadata to a single .npz
so re-embedding is not needed on every run. The index is regenerable from
docs/ and is therefore gitignored, like usage.db.

Embedding and persistence only — no retrieval, no similarity search.

    python embed_chunks.py            # embed, skip if index is current
    python embed_chunks.py --force    # re-embed regardless
"""

import json
import sys
import time
from pathlib import Path

import boto3
import numpy as np

from chunking import chunk_document
from eval import _credentials

MODEL_ID = "amazon.titan-embed-text-v2:0"
REGION = "us-east-1"
DIMENSIONS = 1024
NORMALIZE = True

# Titan Text Embeddings V2 accepts 8,192 input tokens.
TOKEN_LIMIT = 8192
# Conservative chars-per-token for the pre-flight check. The corpus measures
# ~3.5 chars/token; 3.0 over-estimates the token count so the guard errs
# toward flagging rather than toward a failed call.
CHARS_PER_TOKEN_CONSERVATIVE = 3.0

# $0.02 per million input tokens. Published rates for this model disagree
# across sources ($0.02, $0.11, $0.20 per million); at this corpus size the
# difference is fractions of a cent, so the reported figure states its rate.
PRICE_PER_MTOK = 0.02

DOCS = Path(__file__).parent / "docs"
INDEX = Path(__file__).parent / "vector_index.npz"

MAX_RETRIES = 5


def load_chunks():
    docs = sorted((p.name, p.read_text(encoding="utf-8"))
                  for p in DOCS.glob("*.md"))
    chunks = []
    for name, text in docs:
        chunks.extend(chunk_document(name, text))
    return docs, chunks


def preflight(chunks) -> list[dict]:
    """Flag any chunk that could exceed the model's input limit.

    Reported rather than sent — a chunk over the limit should surface here,
    not as a failed API call halfway through the run.
    """
    over = []
    for i, c in enumerate(chunks):
        est = len(c.text) / CHARS_PER_TOKEN_CONSERVATIVE
        if est > TOKEN_LIMIT:
            over.append({"index": i, "source": c.source,
                         "chars": len(c.text), "est_tokens": round(est)})
    return over


def embed_one(client, text: str) -> tuple[list[float], int]:
    body = json.dumps({
        "inputText": text,
        "dimensions": DIMENSIONS,
        "normalize": NORMALIZE,
    })
    delay = 1.0
    last = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.invoke_model(modelId=MODEL_ID, body=body)
            payload = json.loads(resp["body"].read())
            return payload["embedding"], payload.get("inputTextTokenCount", 0)
        except Exception as e:  # noqa: BLE001 - retry on throttling only
            last = e
            if "Throttl" not in type(e).__name__ and "Throttl" not in str(e):
                raise
            if attempt == MAX_RETRIES - 1:
                break
            time.sleep(delay)
            delay *= 2
    raise last


def main() -> int:
    force = "--force" in sys.argv
    if INDEX.exists() and not force:
        existing = np.load(INDEX, allow_pickle=False)
        print(f"index exists: {INDEX.name} "
              f"({existing['embeddings'].shape[0]} vectors). "
              f"Use --force to re-embed.")
        return 0

    docs, chunks = load_chunks()
    print(f"documents : {len(docs)}")
    print(f"chunks    : {len(chunks)}")
    print(f"model     : {MODEL_ID}  ({DIMENSIONS}d, normalize={NORMALIZE})")
    print()

    # ---- pre-flight: token limit ----------------------------------------
    print("=" * 78)
    print(f"PRE-FLIGHT — chunks against the {TOKEN_LIMIT:,}-token input limit")
    print("=" * 78)
    over = preflight(chunks)
    longest = max(chunks, key=lambda c: len(c.text))
    print(f"  longest chunk        : {len(longest.text):,} chars "
          f"(~{len(longest.text)/CHARS_PER_TOKEN_CONSERVATIVE:,.0f} tokens, "
          f"conservative)")
    print(f"  limit                : {TOKEN_LIMIT:,} tokens")
    print(f"  headroom on longest  : "
          f"{TOKEN_LIMIT - len(longest.text)/CHARS_PER_TOKEN_CONSERVATIVE:,.0f} tokens")
    print(f"  chunks over limit    : {len(over)}")
    if over:
        for o in over:
            print(f"      {o['source']} chunk {o['index']}: "
                  f"{o['chars']:,} chars, ~{o['est_tokens']:,} tokens")
        print()
        print("  ABORTING — chunks exceed the input limit. Reduce MAX_CHARS")
        print("  in chunking.py or split the offending sections.")
        return 1
    print("  PASS — every chunk fits, nothing sent that would fail")
    print()

    kid, sec = _credentials()
    client = boto3.client("bedrock-runtime", region_name=REGION,
                          aws_access_key_id=kid, aws_secret_access_key=sec)

    # ---- embed -----------------------------------------------------------
    print("=" * 78)
    print("EMBEDDING")
    print("=" * 78)
    vectors, payload, failures = [], [], []
    total_tokens = 0
    t0 = time.perf_counter()

    for i, c in enumerate(chunks):
        try:
            emb, ntok = embed_one(client, c.text)
            vectors.append(emb)
            total_tokens += ntok
            payload.append({
                "source": c.metadata["source"],
                "doc_title": c.metadata["doc_title"],
                "section": c.metadata["section"],
                "chunk_index": c.metadata["chunk_index"],
                "chars": len(c.text),
                "tokens": ntok,
                "text": c.text,
            })
        except Exception as e:  # noqa: BLE001
            failures.append({"index": i, "source": c.source,
                             "error": f"{type(e).__name__}: {e}"})
            print(f"  FAILED chunk {i} ({c.source}): {type(e).__name__}: {e}")

        if (i + 1) % 50 == 0 or i + 1 == len(chunks):
            el = time.perf_counter() - t0
            print(f"  {i+1:>4}/{len(chunks)}  {el:>6.1f}s  "
                  f"{total_tokens:>7,} tokens  {len(failures)} failed")

    elapsed = time.perf_counter() - t0

    if not vectors:
        print("\n  no vectors produced — nothing to persist")
        return 1

    # ---- persist ---------------------------------------------------------
    arr = np.asarray(vectors, dtype=np.float32)
    np.savez_compressed(
        INDEX,
        embeddings=arr,
        payload=np.array(json.dumps(payload), dtype=object),
        meta=np.array(json.dumps({
            "model": MODEL_ID, "region": REGION, "dimensions": DIMENSIONS,
            "normalize": NORMALIZE, "chunks": len(payload),
            "total_tokens": total_tokens,
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }), dtype=object),
        allow_pickle=True,
    )

    cost = total_tokens / 1e6 * PRICE_PER_MTOK

    print()
    print("=" * 78)
    print("RESULT")
    print("=" * 78)
    print(f"  chunks embedded  : {len(vectors)} / {len(chunks)}")
    print(f"  failures         : {len(failures)}")
    for f in failures:
        print(f"      chunk {f['index']} ({f['source']}): {f['error']}")
    print(f"  input tokens     : {total_tokens:,}")
    print(f"  tokens/chunk     : min {min(p['tokens'] for p in payload)}, "
          f"mean {total_tokens/len(payload):.0f}, "
          f"max {max(p['tokens'] for p in payload)}")
    print(f"  wall clock       : {elapsed:.1f}s "
          f"({elapsed/len(vectors)*1000:.0f} ms/chunk)")
    print(f"  cost @ ${PRICE_PER_MTOK}/M tokens : ${cost:.6f}")
    print(f"  vector array     : {arr.shape} {arr.dtype}")
    print(f"  index written    : {INDEX.name} "
          f"({INDEX.stat().st_size/1024:.0f} KB)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
