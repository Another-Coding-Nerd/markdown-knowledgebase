#!/usr/bin/env python3
"""Lightweight Flask app for browsing the knowledge base.

Usage:
    .venv/bin/python tools/kb_app.py
    .venv/bin/python tools/kb_app.py --config my.yaml
    .venv/bin/python tools/kb_app.py --port 8080
"""

import argparse
import re
import sqlite3
import sys
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

import chromadb
import markdown as mdlib
from markdown.treeprocessors import Treeprocessor
import requests
import yaml
from flask import Flask, abort, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kb_common import get_collection, get_embedding_model, iter_kb_files, load_config
from kb_query import build_prompt, query_llm, _is_list_query

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_STOPWORDS = frozenset({
    'the', 'this', 'that', 'these', 'those', 'its',
    'about', 'above', 'across', 'after', 'against', 'along', 'among',
    'around', 'before', 'behind', 'below', 'beneath', 'between', 'beyond',
    'during', 'except', 'from', 'into', 'near', 'off', 'onto', 'out',
    'outside', 'over', 'past', 'since', 'through', 'throughout', 'under',
    'until', 'upon', 'via', 'with', 'within', 'without',
    'and', 'but', 'for', 'nor', 'yet', 'both', 'either', 'neither',
    'although', 'because', 'unless', 'while', 'though', 'whereas',
    'whether', 'however', 'therefore', 'thus', 'hence',
    'all', 'any', 'each', 'few', 'many', 'more', 'most', 'other', 'some',
    'such', 'who', 'whom', 'whose', 'what', 'which', 'when', 'where',
    'why', 'how', 'her', 'him', 'his', 'our', 'own', 'she', 'their',
    'them', 'they', 'you', 'your',
    'are', 'been', 'being', 'can', 'cannot', 'could', 'did', 'does',
    'doing', 'done', 'had', 'has', 'have', 'having', 'may', 'might',
    'must', 'need', 'ought', 'shall', 'should', 'was', 'were', 'will',
    'would',
    'also', 'back', 'come', 'get', 'give', 'got', 'just', 'keep',
    'let', 'like', 'look', 'made', 'make', 'new', 'not', 'now', 'only',
    'put', 'run', 'say', 'see', 'set', 'show', 'take', 'try', 'use',
    'used', 'using', 'very', 'well', 'work',
    'actually', 'already', 'always', 'even', 'every', 'much', 'never',
    'often', 'really', 'roughly', 'same', 'still', 'than', 'then',
    'there', 'too', 'usually', 'way',
    'example', 'note', 'section', 'page', 'file', 'item', 'list',
    'part', 'type', 'value', 'number', 'one', 'two', 'three', 'etc',
})

_WORD_RE = re.compile(r'\b[a-z]{3,}\b')

# ── Config ───────────────────────────────────────────────────────────────────

def load_flask_config(path=None):
    defaults = {
        "host": "localhost",
        "port": 5000,
        "debug": False,
        "search_top_k": 5,
        "kb_qa": {
            "enabled": True,
            "api_url": "http://localhost:11434",
            "model": "phi4-mini",
            "top_k": 12,
            "max_tokens": 512,
            "max_context_chars": 6000,
        },
        "graph": {
            "node_min_size": 4,
            "node_max_size": 20,
            "charge_strength": -120,
            "link_distance": 80,
        },
        "theme": "dark",
    }
    config_path = Path(path) if path else PROJECT_ROOT / "flask_config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            user = yaml.safe_load(f) or {}
        for key in ("kb_qa", "graph"):
            if key in user and isinstance(user[key], dict):
                defaults[key] = {**defaults[key], **user[key]}
                del user[key]
        return {**defaults, **user}
    return defaults


def _ensure_instance_id(config_path: Path) -> str:
    """Return instance_id from flask_config.yaml, generating and persisting one if absent."""
    if config_path.exists():
        text = config_path.read_text()
        for line in text.splitlines():
            if line.startswith("instance_id:"):
                return line.split(":", 1)[1].strip()
        new_id = str(uuid.uuid4())
        with open(config_path, "a") as f:
            f.write(f"\ninstance_id: {new_id}\n")
        return new_id
    return str(uuid.uuid4())


flask_cfg = load_flask_config()
kb_cfg = load_config()
kb_root = Path(kb_cfg["kb_root"])

def _iter_kb_files():
    yield from iter_kb_files(kb_cfg)

_config_path = Path(flask_cfg.get("_config_path", PROJECT_ROOT / "flask_config.yaml"))
_instance_id = flask_cfg.get("instance_id") or _ensure_instance_id(PROJECT_ROOT / "flask_config.yaml")

# Load embedding model and collection once at startup
_embedding_model = get_embedding_model(kb_cfg)
_chroma_client = chromadb.PersistentClient(path=str(kb_cfg["index_dir"]))
_collection = get_collection(kb_cfg, _chroma_client)

app = Flask(__name__)
app.jinja_env.globals["instance_id"] = _instance_id

# ── KB helpers ────────────────────────────────────────────────────────────────

def _file_title(md_path: Path) -> str:
    """Return the first H1 heading, or a title-cased stem."""
    try:
        for line in md_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return md_path.stem.replace("-", " ").title()


def _rel(md_path: Path) -> str:
    """Path relative to kb_root as a stable node/file ID."""
    return str(md_path.relative_to(kb_root))


_DB_PATH = PROJECT_ROOT / "connections.db"

def _db_connect():
    """Return a read-only sqlite3 connection to connections.db, or None if absent."""
    if not _DB_PATH.exists():
        return None
    return sqlite3.connect(f"file:{_DB_PATH}?mode=ro", uri=True)

_NODE_COLORS = {
    "projects": "#f59e0b",
    "resources": "#22c55e",
}

def _node_color(rel_path: str) -> str:
    first = rel_path.split("/")[0] if "/" in rel_path else ""
    return _NODE_COLORS.get(first, "#3b82f6")

# ── Data functions ────────────────────────────────────────────────────────────

def get_graph_data() -> dict:
    all_files = list(_iter_kb_files())
    node_map = {}
    for f in all_files:
        nid = _rel(f)
        node_map[nid] = {
            "id": nid,
            "title": _file_title(f),
            "color": _node_color(nid),
            "size": 0,
        }

    edges = []
    degree: dict[str, int] = {nid: 0 for nid in node_map}

    con = _db_connect()
    if con:
        try:
            # source < target gives one row per undirected pair (both directions stored)
            rows = con.execute(
                "SELECT source, target, weight FROM connections WHERE source < target"
            ).fetchall()
            for src, tgt, w in rows:
                if src not in node_map or tgt not in node_map:
                    continue
                edges.append({"source": src, "target": tgt, "weight": round(w, 4)})
                degree[src] = degree.get(src, 0) + 1
                degree[tgt] = degree.get(tgt, 0) + 1
        finally:
            con.close()

    g_cfg = flask_cfg.get("graph", {})
    min_sz = g_cfg.get("node_min_size", 4)
    max_sz = g_cfg.get("node_max_size", 20)
    max_deg = max(degree.values(), default=1) or 1
    for nid, node in node_map.items():
        d = degree[nid]
        node["size"] = min_sz + (max_sz - min_sz) * (d / max_deg)

    return {"nodes": list(node_map.values()), "edges": edges}


def retrieve(query: str, top_k: int) -> list[tuple]:
    """Embed query and return top_k (text, file, heading, score) hits."""
    count = _collection.count()
    if count == 0:
        return []
    embedding = list(_embedding_model.query_embed([query]))[0].tolist()
    results = _collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, count),
    )
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append((doc, meta.get("file", "?"), meta.get("heading", ""), 1 - dist))
    return hits


def search_kb(query: str, top_k: int) -> dict:
    hits = retrieve(query, top_k)
    return {
        "query": query,
        "results": [
            {"file": f, "heading": h, "score": round(s, 4), "snippet": t[:300]}
            for t, f, h, s in hits
        ],
    }


def rag_query(question: str, top_k: int) -> tuple[str, list]:
    hits = retrieve(question, top_k)
    if not hits:
        return "No relevant content found in the knowledge base.", []
    qa_cfg = flask_cfg.get("kb_qa", {})
    max_chars = qa_cfg.get("max_context_chars", 6000)
    trimmed, budget = [], max_chars
    for hit in hits:
        if len(hit[0]) > budget:
            break
        trimmed.append(hit)
        budget -= len(hit[0])
    hits = trimmed or hits[:1]
    prompt = build_prompt(question, hits)
    if _is_list_query(question):
        max_tokens = qa_cfg.get("max_tokens_list", 768)
    else:
        max_tokens = qa_cfg.get("max_tokens", 384)
    try:
        answer = query_llm(
            qa_cfg.get("api_url", "http://localhost:11434"),
            qa_cfg.get("model", "phi4-mini"),
            prompt,
            max_tokens,
        )
    except requests.exceptions.ConnectionError:
        answer = (
            "LLM endpoint not available. "
            "Start Ollama (ollama serve) or set api_url in flask_config.yaml."
        )
    except requests.exceptions.Timeout:
        answer = "LLM request timed out."
    except requests.exceptions.HTTPError as e:
        answer = f"LLM returned an error: {e}"
    sources = [{"file": f, "heading": h, "score": round(s, 4)} for _, f, h, s in hits]
    return answer, sources


def list_kb_files() -> dict:
    degree: dict[str, int] = {}
    con = _db_connect()
    if con:
        try:
            rows = con.execute(
                "SELECT source, COUNT(*) FROM connections GROUP BY source"
            ).fetchall()
            degree = {r[0]: r[1] for r in rows}
        finally:
            con.close()

    files = []
    for f in _iter_kb_files():
        stat = f.stat()
        nid = _rel(f)
        files.append({
            "name": f.name,
            "title": _file_title(f),
            "path": nid,
            "size": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "connections": degree.get(nid, 0),
        })
    return {"files": files}


def get_top_terms(n: int = 40) -> list[dict]:
    extra = frozenset(w.lower() for w in flask_cfg.get("stats_stopwords", []))
    stop = _STOPWORDS | extra
    result = _collection.get(include=["documents"])
    counter: Counter = Counter()
    for doc in (result.get("documents") or []):
        for word in _WORD_RE.findall(doc.lower()):
            if word not in stop:
                counter[word] += 1
    return [{"term": t, "count": c} for t, c in counter.most_common(n)]


def get_connections(filename: str) -> dict:
    kb_resolved = kb_root.resolve()
    target = (kb_root / filename).resolve()
    if not target.is_relative_to(kb_resolved):
        return {"outgoing": [], "incoming": []}

    rel = str(target.relative_to(kb_resolved))
    con = _db_connect()
    if not con:
        return {"outgoing": [], "incoming": []}

    try:
        rows = con.execute(
            "SELECT target, weight FROM connections WHERE source = ? ORDER BY weight DESC",
            (rel,),
        ).fetchall()
    finally:
        con.close()

    return {"outgoing": [r[0] for r in rows], "incoming": []}

class _LinkRewriter(Treeprocessor):
    """Rewrite [text](foo.md) → /page/foo.md so intra-KB links work.

    Also converts `` `foo.md` `` (backtick-wrapped filenames in <code>) to
    clickable links when the text looks like a markdown filename.
    """
    _MD_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9._-]*\.md$")

    def run(self, root):
        for el in root.iter("a"):
            href = el.get("href", "")
            if href and href.endswith(".md") and not href.startswith(("/", "http://", "https://")):
                el.set("href", f"/page/{href}")
        parent_map = {child: parent for parent in root.iter() for child in parent}
        for code_el in list(root.iter("code")):
            text = (code_el.text or "").strip()
            if self._MD_RE.match(text):
                parent = parent_map.get(code_el)
                if parent is None:
                    continue
                import xml.etree.ElementTree as _etree
                link = _etree.Element("a")
                link.set("href", f"/page/{text}")
                link.text = text
                parent[list(parent).index(code_el)] = link


class _LinkRewriteExtension(mdlib.Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(_LinkRewriter(md), "link_rewriter", priority=15)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def graph():
    return render_template(
        "graph.html",
        theme=flask_cfg.get("theme", "dark"),
        graph_config=flask_cfg.get("graph", {}),
    )


@app.route("/page/<path:filename>")
def page(filename):
    kb_resolved = kb_root.resolve()
    target = (kb_root / filename).resolve()
    if not target.is_relative_to(kb_resolved):
        abort(403)
    if not target.exists():
        abort(404)
    md_text = target.read_text(encoding="utf-8", errors="replace")
    md = mdlib.Markdown(
        extensions=["tables", "fenced_code", "codehilite", "toc", _LinkRewriteExtension()],
        extension_configs={"codehilite": {"guess_lang": False, "noclasses": True}},
    )
    html_content = md.convert(md_text)
    toc = md.toc if "<li>" in md.toc else ""
    connections = get_connections(filename)
    return render_template(
        "page.html",
        content=html_content,
        toc=toc,
        filename=filename,
        title=_file_title(target),
        connections=connections,
        theme=flask_cfg.get("theme", "dark"),
    )


@app.route("/api/graph")
def api_graph():
    return jsonify(get_graph_data())


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"query": "", "results": []})
    top_k = int(request.args.get("top_k", flask_cfg.get("search_top_k", 5)))
    return jsonify(search_kb(query, top_k))


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"answer": "No question provided.", "sources": []})
    qa_cfg = flask_cfg.get("kb_qa", {})
    top_k = data.get("top_k", qa_cfg.get("top_k", 5))
    answer, sources = rag_query(question, top_k)
    return jsonify({"answer": answer, "sources": sources})


@app.route("/api/files")
def api_files():
    return jsonify(list_kb_files())


@app.route("/api/connections/<path:filename>")
def api_connections(filename):
    return jsonify(get_connections(filename))


@app.route("/stats")
def stats():
    return render_template("stats.html", theme=flask_cfg.get("theme", "dark"))


@app.route("/api/stats/terms")
def api_stats_terms():
    n = min(int(request.args.get("n", 40)), 100)
    return jsonify({"terms": get_top_terms(n)})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KB web interface")
    parser.add_argument("--config", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--host", default=None)
    args = parser.parse_args()

    if args.config:
        flask_cfg = load_flask_config(args.config)
    if args.port:
        flask_cfg["port"] = args.port
    if args.host:
        flask_cfg["host"] = args.host

    print(f"KB root:      {kb_root}")
    print(f"Index chunks: {_collection.count()}")
    print(f"App URL:      http://{flask_cfg['host']}:{flask_cfg['port']}")
    app.run(
        host=flask_cfg["host"],
        port=flask_cfg["port"],
        debug=flask_cfg.get("debug", False),
    )
