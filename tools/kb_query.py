#!/usr/bin/env python3
"""RAG query: retrieve KB chunks via semantic search, then synthesize an answer
via a local LLM (Ollama / llama.cpp / OpenAI-compatible API).

Usage:
    python tools/kb_query.py "your question here"
    python tools/kb_query.py --top-k 8 --api-url http://192.168.1.50:8080 "question"
    python tools/kb_query.py --model llama3.2:3b "question"
    python tools/kb_query.py --max-tokens 256 "short answer please"
"""

# ── Configurable defaults ────────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434"   # Ollama ≥0.1.24 exposes /v1/chat/completions natively
DEFAULT_MODEL = "phi4-mini"             # best reasoning/speed balance on CPU
# DEFAULT_MODEL = "gemma2:2b"           # fastest on CPU at this quality level
# DEFAULT_MODEL = "llama3.2:3b"         # most community support, longest context
DEFAULT_TOP_K = 5                       # number of KB chunks to retrieve
DEFAULT_MAX_TOKENS = 512                # max tokens in LLM answer
# ──────────────────────────────────────────────────────────────────────────

import argparse
import json
import sys
from pathlib import Path

import requests
import chromadb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import load_config, get_embedding_model, get_collection


def retrieve(cfg, query, top_k):
    """Return top_k (chunk_text, file, heading, score) tuples."""
    model = get_embedding_model(cfg)
    client = chromadb.PersistentClient(path=str(cfg["index_dir"]))
    collection = get_collection(cfg, client)

    query_embedding = list(model.query_embed([query]))[0].tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        score = 1 - dist
        hits.append((doc, meta.get("file", "?"), meta.get("heading", ""), score))
    return hits


def build_prompt(query, hits):
    """Build a chat-style prompt from query and retrieved chunks."""
    lines = [
        "Answer the question concisely in a neutral analytical tone "
        "based solely on the context below. "
        "If the context doesn't contain enough information, say so. "
        "Cite sources as [1], [2] etc.\n"
    ]
    for i, (text, file, heading, score) in enumerate(hits, 1):
        location = file
        if heading:
            location += f" > {heading}"
        lines.append(f"[{i}] ({location})\n{text.strip()}\n")
    lines.append(f"Question: {query}\nAnswer:")
    return "\n\n".join(lines)


def query_llm(api_url, model, prompt, max_tokens=DEFAULT_MAX_TOKENS):
    """Send prompt to an OpenAI-compatible /v1/chat/completions endpoint."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "stream": False,
    }
    resp = requests.post(
        f"{api_url.rstrip('/')}/v1/chat/completions",
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="RAG query over the KB")
    parser.add_argument("query", nargs="+", help="natural language question")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
                        help=f"max tokens in LLM answer (default: {DEFAULT_MAX_TOKENS})")
    parser.add_argument("--api-url", default=OLLAMA_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--config", default=None)
    args = parser.parse_args()

    query = " ".join(args.query)
    cfg = load_config(args.config)

    # 1. Retrieve
    hits = retrieve(cfg, query, args.top_k)
    if not hits:
        print("No relevant chunks found.", file=sys.stderr)
        return 1

    # 2. Build prompt
    prompt = build_prompt(query, hits)

    # 3. Generate
    answer = query_llm(args.api_url, args.model, prompt, args.max_tokens)

    # 4. Output
    print(answer)
    print("\n── Sources ──")
    for i, (_, file, heading, score) in enumerate(hits, 1):
        loc = file
        if heading:
            loc += f" > {heading}"
        print(f"[{i}] {loc} ({score:.2f})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
