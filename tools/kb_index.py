#!/usr/bin/env python3
"""Rebuild the semantic search index over kb/**/*.md.

Usage:
    python tools/kb_index.py [--config config.yaml]
    python tools/kb_index.py --incremental [--config config.yaml]

Default mode is a full rebuild: the existing 'kb_chunks' collection is
dropped and recreated, and every file is re-chunked and re-embedded.

--incremental only re-chunks/embeds files that are new or modified since the
last index (by mtime), and removes chunks for files deleted from kb/. It
falls back to a full rebuild if no prior index exists, or if the existing
meta.json predates per-file mtime tracking.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import chromadb

from chunking import chunk_markdown
from kb_common import load_config, get_embedding_model, iter_kb_files


def chunk_file(path, kb_root, cfg, tokenizer):
    rel = str(path.relative_to(kb_root))
    text = path.read_text(encoding="utf-8")
    chunks = chunk_markdown(text, cfg["max_tokens"], cfg["overlap_tokens"], tokenizer)
    ids, docs, metas = [], [], []
    for i, (heading_path, chunk_text) in enumerate(chunks):
        if heading_path.split(" > ")[-1].strip() == "See Also":
            continue
        ids.append(f"{rel}::{i}")
        docs.append(chunk_text)
        metas.append({
            "file": rel,
            "heading": heading_path,
            "chunk_index": i,
        })
    return ids, docs, metas


def embed_and_add(collection, model, ids, docs, metas, batch_size):
    total = len(docs)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch_embeddings = [e.tolist() for e in model.embed(docs[start:end], batch_size=batch_size)]
        collection.add(
            ids=ids[start:end],
            documents=docs[start:end],
            embeddings=batch_embeddings,
            metadatas=metas[start:end],
        )
        print(f"\r  {end}/{total} chunks embedded", end="", flush=True)
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    parser.add_argument("--incremental", action="store_true",
                         help="Only re-index files that are new or modified since the last "
                              "run, and remove chunks for files deleted from kb/. Falls back "
                              "to a full rebuild if no prior index exists.")
    args = parser.parse_args()

    cfg = load_config(args.config)
    kb_root = cfg["kb_root"]
    index_dir = cfg["index_dir"]
    index_dir.mkdir(parents=True, exist_ok=True)

    md_files = iter_kb_files(cfg)
    if not md_files:
        print(f"No .md files found under {kb_root}", file=sys.stderr)

    current_mtimes = {str(p.relative_to(kb_root)): p.stat().st_mtime for p in md_files}

    meta_path = index_dir / "meta.json"
    prev_meta = None
    if args.incremental and meta_path.exists():
        with open(meta_path) as f:
            prev_meta = json.load(f)
        if "file_mtimes" not in prev_meta:
            print("meta.json predates incremental tracking; doing a full rebuild.")
            prev_meta = None

    client = chromadb.PersistentClient(path=str(index_dir))

    if prev_meta is None:
        try:
            client.delete_collection("kb_chunks")
        except Exception:
            pass
        collection = client.create_collection(name="kb_chunks", metadata={"hnsw:space": "cosine"})
        to_process = md_files
        to_delete_rels = []
    else:
        collection = client.get_collection("kb_chunks")
        prev_mtimes = prev_meta["file_mtimes"]
        to_process = [
            p for p in md_files
            if current_mtimes[str(p.relative_to(kb_root))] != prev_mtimes.get(str(p.relative_to(kb_root)))
        ]
        to_delete_rels = [rel for rel in prev_mtimes if rel not in current_mtimes]

        for rel in to_delete_rels:
            collection.delete(where={"file": rel})
        for path in to_process:
            collection.delete(where={"file": str(path.relative_to(kb_root))})

        if not to_process and not to_delete_rels:
            print("No changes detected, index is up to date.")
            return

    all_ids, all_docs, all_metas = [], [], []
    if to_process:
        print(f"Loading embedding model: {cfg['embedding_model']} ...")
        model = get_embedding_model(cfg)
        tokenizer = model.model.tokenizer
        # The tokenizer truncates at the model's max sequence length (512) by
        # default, which caps len(encode(text).ids) at 512 regardless of true
        # length — breaking size checks for sections/paragraphs longer than
        # that. Disable truncation so chunking sees true token counts.
        tokenizer.no_truncation()

        total_files = len(to_process)
        for i, path in enumerate(to_process, 1):
            print(f"\r  [{i}/{total_files}] {path.name}", end="", flush=True)
            ids, docs, metas = chunk_file(path, kb_root, cfg, tokenizer)
            all_ids.extend(ids)
            all_docs.extend(docs)
            all_metas.extend(metas)
        print()

        print(f"Chunked {total_files} file(s) into {len(all_docs)} chunks")

        if all_docs:
            print("Embedding chunks...")
            embed_and_add(collection, model, all_ids, all_docs, all_metas, batch_size=16)

    if to_delete_rels:
        print(f"Removed chunks for {len(to_delete_rels)} deleted file(s)")

    meta = {
        "indexed_at": time.time(),
        "files": len(md_files),
        "chunks": collection.count(),
        "embedding_model": cfg["embedding_model"],
        "file_mtimes": current_mtimes,
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Indexed {meta['files']} files / {meta['chunks']} chunks -> {index_dir}")


if __name__ == "__main__":
    main()
