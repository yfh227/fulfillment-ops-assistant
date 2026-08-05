"""Brute-force similarity search over the embedded Meridian corpus.

Every vector from embed_chunks.py is L2-normalized, so cosine similarity
reduces to a plain dot product. At 363 vectors that is a single (363, 1024)
@ (1024,) matrix-vector product — microseconds, with no index structure and
no dependency beyond NumPy.

Search only. Nothing here is wired into core.ask().
"""

import json
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import boto3
import numpy as np

MODEL_ID = "amazon.titan-embed-text-v2:0"
REGION = "us-east-1"
DIMENSIONS = 1024
INDEX = Path(__file__).parent / "vector_index.npz"


@dataclass
class Hit:
    score: float
    source: str
    section: str
    text: str
    chars: int

    def __repr__(self) -> str:
        return (f"Hit({self.score:.4f} {self.source} "
                f"{self.section[:38]!r})")


@lru_cache(maxsize=1)
def load_index(path: str = None):
    """Load vectors and payload. Cached — the file is read once per process."""
    p = Path(path) if path else INDEX
    if not p.exists():
        raise FileNotFoundError(
            f"{p.name} not found. Run: python embed_chunks.py")
    data = np.load(p, allow_pickle=True)
    embeddings = data["embeddings"]
    payload = json.loads(str(data["payload"]))
    meta = json.loads(str(data["meta"]))
    return embeddings, payload, meta


def get_client(access_key_id=None, secret_access_key=None):
    return boto3.client(
        "bedrock-runtime", region_name=REGION,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
    )


def embed_query(text: str, client=None) -> np.ndarray:
    """Embed a query with the same settings used to build the index."""
    client = client or get_client()
    resp = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({"inputText": text,
                         "dimensions": DIMENSIONS,
                         "normalize": True}),
    )
    vec = json.loads(resp["body"].read())["embedding"]
    return np.asarray(vec, dtype=np.float32)


def search_vec(query_vec: np.ndarray, k: int = 5, embeddings=None,
               payload=None) -> list[Hit]:
    """Top-k by cosine similarity, given an already-embedded query.

    Both sides are unit vectors, so the dot product IS the cosine. No
    normalization step and no distance conversion.
    """
    if embeddings is None or payload is None:
        embeddings, payload, _ = load_index()
    scores = embeddings @ query_vec           # (363, 1024) @ (1024,) -> (363,)
    top = np.argpartition(-scores, min(k, len(scores) - 1))[:k]
    top = top[np.argsort(-scores[top])]
    return [Hit(float(scores[i]), payload[i]["source"],
                payload[i]["section"], payload[i]["text"],
                payload[i]["chars"]) for i in top]


def search(query: str, k: int = 5, client=None) -> list[Hit]:
    """Embed a query string and return the top-k chunks."""
    embeddings, payload, _ = load_index()
    return search_vec(embed_query(query, client), k, embeddings, payload)
