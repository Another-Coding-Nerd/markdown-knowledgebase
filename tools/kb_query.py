#!/usr/bin/env python3
"""KB Q&A: retrieve KB chunks via semantic search, then synthesize an answer
via a local LLM (Ollama / llama.cpp / OpenAI-compatible API).

Usage:
    python tools/kb_query.py "your question here"
    python tools/kb_query.py --top-k 8 --api-url http://192.168.1.50:8080 "question"
    python tools/kb_query.py --model llama3.2:3b "question"
    python tools/kb_query.py --max-tokens 256 "short answer please"
"""

# ── Hardcoded fallbacks (overridden by flask_config.yaml when present) ───
_FALLBACK_API_URL   = "http://localhost:11434"
_FALLBACK_MODEL     = "phi4-mini"
_FALLBACK_TOP_K     = 5
_FALLBACK_MAX_TOKENS      = 384   # explanation/factual answers
_FALLBACK_MAX_TOKENS_LIST = 768   # list/enumeration answers
# ──────────────────────────────────────────────────────────────────────────

import argparse
import json
import re
import sys
from pathlib import Path

import requests
import chromadb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import load_config, get_embedding_model, get_collection


def _load_flask_qa_cfg() -> dict:
    """Optionally read kb_qa section from flask_config.yaml; empty dict if absent/unreadable."""
    config_path = Path(__file__).resolve().parent.parent / "flask_config.yaml"
    if not config_path.exists():
        return {}
    try:
        import yaml
        with open(config_path) as f:
            return (yaml.safe_load(f) or {}).get("kb_qa", {})
    except Exception:
        return {}


_qa_cfg = _load_flask_qa_cfg()
OLLAMA_URL          = _qa_cfg.get("api_url",         _FALLBACK_API_URL)
DEFAULT_MODEL       = _qa_cfg.get("model",            _FALLBACK_MODEL)
DEFAULT_TOP_K       = _qa_cfg.get("top_k",            _FALLBACK_TOP_K)
DEFAULT_MAX_TOKENS      = _qa_cfg.get("max_tokens",       _FALLBACK_MAX_TOKENS)
DEFAULT_MAX_TOKENS_LIST = _qa_cfg.get("max_tokens_list",  _FALLBACK_MAX_TOKENS_LIST)


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


_LIST_RE = re.compile(
    r'\b(list|what are|what were|name|give me|enumerate|how many|'
    r'red flags?|signs?|reasons?|ways?|steps?|tips?|examples?|'
    r'\d+\s+\w+)\b',
    re.IGNORECASE,
)

def _is_list_query(query: str) -> bool:
    return bool(_LIST_RE.search(query))


def build_prompt(query, hits):
    """Build a chat-style prompt from query and retrieved chunks."""
    if _is_list_query(query):
        instruction = (
            "The question asks for a list. "
            "Scan ALL excerpts below and enumerate every distinct item that answers the question. "
            "Format as a numbered list. List each distinct item only once — do not repeat. "
            "Use only information from the excerpts. Cite sources as [1], [2] etc.\n"
        )
    else:
        instruction = (
            "Answer the question concisely in a neutral analytical tone "
            "based solely on the excerpts below. "
            "If the excerpts don't contain enough information, say so. "
            "Cite sources as [1], [2] etc.\n"
        )
    lines = [instruction]
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
    parser = argparse.ArgumentParser(description="KB Q&A over the KB")
    parser.add_argument("query", nargs="+", help="natural language question")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--max-tokens", type=int, default=None,
                        help=f"max tokens in LLM answer (default: {DEFAULT_MAX_TOKENS} / {DEFAULT_MAX_TOKENS_LIST} for list queries)")
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

    # 3. Generate — auto-select token budget unless explicitly overridden
    if args.max_tokens is not None:
        max_tokens = args.max_tokens
    else:
        max_tokens = DEFAULT_MAX_TOKENS_LIST if _is_list_query(query) else DEFAULT_MAX_TOKENS
    answer = query_llm(args.api_url, args.model, prompt, max_tokens)

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
