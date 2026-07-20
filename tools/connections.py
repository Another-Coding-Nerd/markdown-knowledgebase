#!/usr/bin/env python3
"""Build connections.db from ChromaDB embeddings (semantic nearest-neighbor)."""

import argparse
import sqlite3
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import get_collection, load_config

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _get_all_chunks(collection, batch_size=1000):
    """Fetch every chunk's embedding+metadata, paginated.

    collection.get() with no limit issues a single query with one bind
    variable per row in ChromaDB's SQLite backend, which hits SQLite's
    per-statement variable cap on a KB this size (tens of thousands of
    chunks). Fetching in batches keeps each call well under that limit.
    """
    embeddings, metadatas = [], []
    offset = 0
    while True:
        batch = collection.get(include=["embeddings", "metadatas"], limit=batch_size, offset=offset)
        batch_embeddings = batch["embeddings"]
        if batch_embeddings is None or len(batch_embeddings) == 0:
            break
        embeddings.extend(batch_embeddings)
        metadatas.extend(batch["metadatas"])
        offset += len(batch_embeddings)
    return embeddings, metadatas


def _build_db(cfg, show_file=None):
    collection = get_collection(cfg)
    embeddings, metadatas = _get_all_chunks(collection)

    if embeddings is None or len(embeddings) == 0:
        print("No chunks in index. Run tools/index first.", file=sys.stderr)
        sys.exit(1)

    # Group chunk embeddings by file
    file_chunks: dict[str, list] = {}
    for emb, meta in zip(embeddings, metadatas):
        file_chunks.setdefault(meta["file"], []).append(emb)

    files = sorted(file_chunks)
    n = len(files)
    dim = len(embeddings[0])

    # Mean embedding per file, re-normalized to unit vector.
    file_vecs = np.zeros((n, dim), dtype=np.float64)
    for i, f in enumerate(files):
        mean = np.mean(file_chunks[f], axis=0).astype(np.float64)
        norm = np.linalg.norm(mean)
        file_vecs[i] = mean / norm if norm > 0 else mean

    # Pairwise cosine similarity (dot product of unit vectors).
    # On Apple Silicon, numpy's Accelerate BLAS backend raises spurious
    # divide-by-zero/overflow/invalid-value FP warnings on matmuls this
    # size with no actual bad values in the output (verified: no NaN/Inf,
    # all results in valid cosine-similarity range) — suppress the false
    # positive but keep a real check in case that ever isn't true.
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        sim = file_vecs @ file_vecs.T
    assert np.all(np.isfinite(sim)), "non-finite values in similarity matrix"

    top_n = int(cfg.get("connections_top_n", 5))
    min_score = float(cfg.get("connections_min_score", 0.5))

    if show_file:
        if show_file not in file_chunks:
            print(f"Not in index: {show_file}", file=sys.stderr)
            sys.exit(1)
        idx = files.index(show_file)
        ranked = sorted(
            ((files[j], float(sim[idx, j])) for j in range(n) if j != idx),
            key=lambda x: -x[1],
        )[:top_n]
        print(f"Connections for {show_file} (top {top_n}):")
        for target, w in ranked:
            marker = "" if w >= min_score else "  [below threshold]"
            print(f"  {w:.4f}  {target}{marker}")
        return

    # Symmetrized edge set: union of each file's top-N above min_score
    # Both (a→b) and (b→a) are stored for O(1) lookup by source
    print(f"Computing connections for {n} files...")
    edges: dict[tuple, float] = {}
    for i in range(n):
        neighbors = sorted(
            ((j, float(sim[i, j])) for j in range(n) if j != i and sim[i, j] >= min_score),
            key=lambda x: -x[1],
        )[:top_n]
        for j, w in neighbors:
            key = (min(files[i], files[j]), max(files[i], files[j]))
            if key not in edges or w > edges[key]:
                edges[key] = w

    db_path = PROJECT_ROOT / "connections.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS connections;
        CREATE TABLE connections (
            source  TEXT NOT NULL,
            target  TEXT NOT NULL,
            weight  REAL NOT NULL,
            PRIMARY KEY (source, target)
        );
        CREATE INDEX IF NOT EXISTS idx_source ON connections(source);
        CREATE INDEX IF NOT EXISTS idx_target ON connections(target);
    """)

    rows = []
    for (a, b), w in edges.items():
        rows.append((a, b, w))
        rows.append((b, a, w))

    cur.executemany("INSERT OR REPLACE INTO connections VALUES (?,?,?)", rows)
    con.commit()
    con.close()

    print(f"Wrote {len(edges)} edges -> {db_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Build connections.db from ChromaDB embeddings"
    )
    parser.add_argument("--config", default=None, help="path to config.yaml")
    parser.add_argument("--show", metavar="FILE",
                        help="print top-N connections for FILE and exit (debug)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    _build_db(cfg, show_file=args.show)


if __name__ == "__main__":
    main()
