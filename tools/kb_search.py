#!/usr/bin/env python3
"""Semantic search over the KB index.

Usage:
    python tools/kb_search.py "query one" "query two" ...
    python tools/kb_search.py --top-k 8 "does anything cover breadcrumbing?"

Prints ranked hits per query: file, heading path, similarity score, and a
text snippet. Intended to replace "read all KB files" when checking whether
new material is already covered.
"""

import argparse
import json
import sys

import chromadb

from kb_common import load_config, get_embedding_model, get_collection

SNIPPET_LEN = 300


def check_staleness(cfg):
    meta_path = cfg["index_dir"] / "meta.json"
    if not meta_path.exists():
        print("No index found. Run: python tools/kb_index.py", file=sys.stderr)
        return

    meta = json.loads(meta_path.read_text())
    indexed_at = meta.get("indexed_at", 0)

    stale_files = []
    for path in cfg["kb_root"].rglob("*.md"):
        if path.stat().st_mtime > indexed_at:
            stale_files.append(str(path.relative_to(cfg["kb_root"])))

    if stale_files:
        print(
            f"[stale index] {len(stale_files)} file(s) modified since last reindex "
            f"(run python tools/kb_index.py): {', '.join(stale_files[:5])}"
            + (", ..." if len(stale_files) > 5 else ""),
            file=sys.stderr,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("queries", nargs="+", help="one or more search queries")
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--config", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    check_staleness(cfg)

    top_k = args.top_k or cfg["top_k"]

    client = chromadb.PersistentClient(path=str(cfg["index_dir"]))
    collection = get_collection(cfg, client)
    if collection.count() == 0:
        print("Index is empty. Run: python tools/kb_index.py", file=sys.stderr)
        return

    model = get_embedding_model(cfg)

    for query in args.queries:
        query_embedding = list(model.query_embed([query]))[0].tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
        )

        print(f'\n=== Query: "{query}" ===')
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for rank, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
            score = 1 - dist
            location = meta["file"]
            if meta.get("heading"):
                location += f" > {meta['heading']}"
            snippet = doc.strip().replace("\n", " ")
            if len(snippet) > SNIPPET_LEN:
                snippet = snippet[:SNIPPET_LEN] + "..."
            print(f"[{rank}] score={score:.3f}  {location}")
            print(f"    {snippet}")


if __name__ == "__main__":
    main()


