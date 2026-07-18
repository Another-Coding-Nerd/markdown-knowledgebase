# Flask App Plan: Obsidian Lite

A lightweight Flask web application for browsing the knowledge base — graph
visualization, semantic search, and rendered markdown pages. Replaces the
need for Obsidian or any external tool.

## Overview

The Flask app serves as a local web interface for the KB. It leverages
existing infrastructure (ChromaDB index, markdown files, connections DB)
and adds a browsable UI on top. Includes a KB Q&A (Retrieve & Synthesize)
question box that synthesizes answers from KB content using a local LLM.

Graph edges come exclusively from `connections.db` (SQLite), built by
`connections.py` from ChromaDB embeddings (semantic nearest-neighbor).
There are no static `## See Also` sections in KB files — the app computes
and injects related-file links dynamically from the DB.

**Dependencies:** Flask + markdown + existing chromadb/fastembed (no new
packages beyond Flask and markdown).

**Usage:**

```bash
.venv/bin/python tools/kb_app.py                     # uses flask_config.yaml
.venv/bin/python tools/kb_app.py --config my.yaml    # custom config
.venv/bin/python tools/kb_app.py --port 8080         # override port
```

**Configuration:** `flask_config.yaml` (shipped with defaults). See the
file for all options: server host/port, search top-k, KB Q&A settings
(model, API URL, max tokens), graph layout, and theme.

## Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Graph visualization (D3.js force-directed graph) |
| `/page/<path:filename>` | GET | Rendered markdown for a specific KB file |
| `/api/graph` | GET | JSON graph data (nodes + edges) for D3.js |
| `/api/search?q=<query>&top_k=<n>` | GET | Semantic search via ChromaDB |
| `/api/ask` | POST | KB Q&A: retrieve + LLM answer |
| `/api/files` | GET | List all KB files with metadata |
| `/api/connections/<filename>` | GET | Get connections for a specific file |

## Architecture

```
tools/
├── kb_app.py              # Flask application
├── connections.py         # Build connections.db from ChromaDB embeddings
├── connections            # Thin bash wrapper (like tools/index)
├── templates/
│   ├── base.html          # Shared layout (nav, search bar, CSS)
│   ├── graph.html         # D3.js graph + KB Q&A panel (folded in)
│   └── page.html          # Individual KB page renderer
└── static/                # (optional, if CSS grows beyond inline)
```

## Feature 1: Graph Visualization

**Route:** `/`

**Implementation:**
- D3.js v7 loaded from CDN (~300KB, cached after first load)
- Force-directed layout with draggable nodes
- Node size = number of connections (degree centrality)
- Node color = directory/topic (or file type)
- Edge thickness = relationship strength
- Click node → navigate to `/page/<filename>`
- Hover node → show tooltip with title + snippet
- Zoom/pan/drag standard D3 interactions

**Data source:** `connections.db` (SQLite), built by `connections.py`.
Falls back to an empty graph if the DB hasn't been built yet.

**Graph data format:**

```json
{
  "nodes": [
    {
      "id": "topic-a.md",
      "title": "Topic A",
      "size": 5,
      "color": "#4a90d9",
      "tags": ["tag1", "tag2"]
    }
  ],
  "edges": [
    {
      "source": "topic-a.md",
      "target": "topic-b.md",
      "weight": 0.923
    }
  ]
}
```

**Layout:** Nodes with no connections (orphans) are clustered to the side.
Connected clusters form naturally via force simulation.

## Feature 2: Page Viewer

**Route:** `/page/<path:filename>`

**Implementation:**
- Read `kb/{filename}` as raw markdown
- Convert to HTML using Python `markdown` library
- Render in `page.html` template with navigation sidebar
- Sidebar shows: file title, related files (from connections.db),
  backlinks (inbound connections), breadcrumb navigation
- Click "Graph" → return to graph view
- Click related file → navigate to that page

**Template layout:**

```
┌──────────────────────────────────────────────────────┐
│  [← Graph]  [Search: ___________]  topic-a.md        │
├──────────┬───────────────────────────────────────────┤
│ Related  │                                           │
│ ───────  │  # Topic A                                │
│ file-b   │                                           │
│ file-c   │  Content rendered from markdown...         │
│          │                                           │
│ Backlinks│                                           │
│ ───────  │                                           │
│ file-x   │                                           │
│ file-y   │                                           │
└──────────┴───────────────────────────────────────────┘
```
Related files and backlinks in sidebar come from `connections.db`.
No `## See Also` section in the rendered document body.

**Markdown extensions enabled:**
- Tables
- Fenced code blocks with syntax highlighting (via `codehilite`)
- TOC generation
- Wiki-style links (optional, future)

## Feature 3: Semantic Search

**Route:** `/api/search?q=<query>&top_k=<n>`

**Implementation:**
- Embed query using `fastembed` (same model as `kb_search.py`)
- Query ChromaDB collection
- Return JSON with ranked results:

```json
{
  "query": "some query",
  "results": [
    {
      "file": "topic-a.md",
      "heading": "Section Title",
      "score": 0.892,
      "snippet": "First 300 chars of matching chunk..."
    }
  ]
}
```

**UI integration:**
- Search bar in header (present on all pages)
- Results displayed as a dropdown or overlay
- Click result → navigate to `/page/<filename>#<heading-anchor>`
- Keyboard shortcut: `/` to focus search, `Esc` to close

**Reuses:** `kb_common.py` for config, embedding model, and ChromaDB
collection access. Same logic as `kb_search.py` but returns JSON instead
of printing to stdout.

## Feature 4: Graph Data API

**Route:** `/api/graph`

**Implementation:** Read edges from `connections.db` (SQLite). If the DB
is absent (user hasn't run `tools/connections` yet), returns nodes-only
with no edges rather than attempting on-the-fly parsing.

`connections.db` is built by `connections.py` using per-file semantic
nearest-neighbor from ChromaDB embeddings. No `## See Also` sections are
parsed — those have been removed from KB files and the relationship is
fully DB-driven.

## Feature 5: File Listing API

**Route:** `/api/files`

**Implementation:**
- Scan `kb/**/*.md` for all markdown files
- Return JSON with file metadata:

```json
{
  "files": [
    {
      "name": "topic-a.md",
      "title": "Topic A",
      "path": "topic-a.md",
      "size": 15234,
      "last_modified": "2026-07-15T10:30:00",
      "connections": 5
    }
  ]
}
```

Used by the graph (node list) and could power a file browser view.

## Feature 6: Connections API

**Route:** `/api/connections/<filename>`

**Implementation:** Query `connections.db` for all edges involving this
file — both outgoing (this file → others) and incoming (others → this
file). Returns empty lists if DB is absent. Used by the page viewer
sidebar to show related files and backlinks.

## Tool: connections.py

Builds `connections.db` (SQLite) from ChromaDB embeddings. Run after
`tools/index` whenever KB content changes.

**Usage:**
```bash
tools/connections               # full rebuild (always; incremental not supported)
tools/connections --show <file> # print connections for one file (debug)
```

**Algorithm:**
1. Load all chunk embeddings + metadata from ChromaDB via `collection.get(include=['embeddings','metadatas'])`
2. Group chunks by source file; compute mean embedding per file, re-normalized
3. For each file, compute dot product (= cosine similarity on unit vectors) against all other files
4. Keep top-N neighbors above min-score threshold; symmetrize (if A picks B, edge exists even if B didn't pick A)
5. Write edges to `connections.db`; replace table on each run

**Schema:**
```sql
CREATE TABLE connections (
    source  TEXT NOT NULL,
    target  TEXT NOT NULL,
    weight  REAL NOT NULL,
    PRIMARY KEY (source, target)
);
CREATE INDEX idx_source ON connections(source);
CREATE INDEX idx_target ON connections(target);
```

**Config** (`config.yaml`):
```yaml
connections_top_n: 5        # nearest neighbors per file
connections_min_score: 0.5  # minimum cosine similarity to include edge
```

**Output:** `connections.db` at the repo root (same level as `config.yaml`).

## Feature 7: KB Q&A (Retrieve & Synthesize)

**Route:** `/api/ask`

**Implementation:**
- Accept a single natural language question
- Retrieve top-k relevant chunks from ChromaDB (same logic as `kb_query.py`)
- Send chunks + question to a local LLM (Ollama / OpenAI-compatible endpoint)
- Return synthesized answer with source citations
- **Not conversational** — one question, one answer, no chat thread or
  follow-up questions. Each request is independent.

**Request:**

```json
POST /api/ask
{
  "question": "What are the key findings about X?",
  "top_k": 5
}
```

**Response:**

```json
{
  "answer": "Based on the KB, the key findings are...",
  "sources": [
    {"file": "topic-a.md", "heading": "Section", "score": 0.89},
    {"file": "topic-b.md", "heading": "Another", "score": 0.84}
  ]
}
```

**Reuses:** `kb_query.py` logic — `retrieve()` function for ChromaDB lookup,
`build_prompt()` for LLM prompt construction, `query_llm()` for API call.
Extracted into shared helpers or imported directly.

**UI integration:**
- Q&A panel folded into the graph page (`/`) as a collapsible section below
  the graph — no separate `/ask` route or `ask.html` template needed.
- Text input + submit button; results replace panel content in place.
- Results: synthesized answer (rendered markdown) + numbered source list.
- Source links clickable → navigate to `/page/<file>`.
- Loading indicator while LLM generates.
- **Not a chat interface** — each question is a fresh, independent request.
  No conversation history, no follow-up threading.

**Panel layout (bottom of graph page):**

```
┌─────────────────────────────────────────────────────────┐
│  [📊 Graph]  [🔍 Search bar ___________]                │
├─────────────────────────────────────────────────────────┤
│  (D3.js force graph)                                     │
├─────────────────────────────────────────────────────────┤
│  ▼ Ask your KB                                           │
│  [________________________________] [Ask]                │
│                                                          │
│  Based on the knowledge base, the key findings are...    │
│  Sources: 1. topic-a.md > Section (0.89)                 │
└─────────────────────────────────────────────────────────┘
```

**Dependencies:** Requires a running Ollama instance (≥ 0.1.24) or any
OpenAI-compatible `/v1/chat/completions` endpoint. Default model:
`phi4-mini` (configurable via `--model` flag or config).

**Proxy compatibility:** Any OpenAI-compatible proxy works without code
changes — point `api_url` in `flask_config.yaml` at it. Examples:
[LiteLLM](https://github.com/BerriAI/litellm) can front AWS Bedrock,
Anthropic, OpenRouter, Azure OpenAI, and 100+ other providers behind the
same interface (`litellm --model bedrock/anthropic.claude-...`).

**Note:** After extensive testing, a GPU is required for the synthesis step.
CPU-only inference is too slow for practical use. The search/retrieval part
works fine on CPU (fastembed is CPU-only by design).

**Graceful degradation:** If no LLM endpoint is available, the `/api/ask`
route returns an error message explaining the requirement. The rest of the
app (graph, search, page viewer) works without it.

## Implementation Details

### kb_app.py structure

```python
#!/usr/bin/env python3
"""Lightweight Flask app for browsing the knowledge base."""

import argparse
import yaml
from flask import Flask, render_template, jsonify, request
import markdown
from pathlib import Path

app = Flask(__name__)

def load_flask_config(path="flask_config.yaml"):
    """Load Flask app config, falling back to defaults."""
    defaults = {"host": "localhost", "port": 5000, "debug": False,
                "search_top_k": 5, "kb_qa": {"enabled": True, "api_url": "...",
                "model": "phi4-mini", "top_k": 5, "max_tokens": 512}}
    if Path(path).exists():
        with open(path) as f:
            return {**defaults, **yaml.safe_load(f)}
    return defaults

flask_cfg = load_flask_config()
kb_cfg = load_config()  # existing KB config
kb_root = kb_cfg["kb_root"]

@app.route('/')
def graph():
    return render_template('graph.html')

@app.route('/page/<path:filename>')
def page(filename):
    md_path = kb_root / filename
    if not md_path.exists():
        return "File not found", 404
    md_text = md_path.read_text(encoding='utf-8')
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])
    return render_template('page.html', content=html_content, filename=filename)

@app.route('/api/graph')
def api_graph():
    data = get_graph_data()
    return jsonify(data)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    top_k = int(request.args.get('top_k', flask_cfg["search_top_k"]))
    results = search_kb(query, top_k)
    return jsonify(results)

@app.route('/api/ask', methods=['POST'])
def api_ask():
    data = request.get_json()
    question = data.get('question', '')
    top_k = data.get('top_k', flask_cfg["kb_qa"]["top_k"])
    max_tokens = data.get('max_tokens', flask_cfg["kb_qa"]["max_tokens"])
    answer, sources = rag_query(question, top_k, max_tokens)
    return jsonify({"answer": answer, "sources": sources})

@app.route('/api/files')
def api_files():
    files = list_kb_files()
    return jsonify(files)

@app.route('/api/connections/<filename>')
def api_connections(filename):
    connections = get_connections(filename)
    return jsonify(connections)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="flask_config.yaml")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--host", default=None)
    args = parser.parse_args()

    flask_cfg = load_flask_config(args.config)
    if args.port: flask_cfg["port"] = args.port
    if args.host: flask_cfg["host"] = args.host

    app.run(host=flask_cfg["host"], port=flask_cfg["port"],
            debug=flask_cfg["debug"])
```

### HTML templates

**base.html:**
- Foundation XY Grid for layout
- Top-bar for navigation (Graph, Pages, Search, Ask)
- Search bar in the top-bar
- Foundation components: buttons, cards, callouts
- CSS custom properties (`--bg`, `--surface`, `--text`, etc.) mapped to
  Tailwind palette values, toggled via `:root` / `.dark` on `<body>`
- No additional CSS framework beyond Foundation + Tailwind color tokens

**graph.html:**
- D3.js force-directed graph
- Loads data from `/api/graph`
- Click handler → window.location = `/page/<filename>`
- Zoom/pan/drag controls
- Legend for node colors/sizes

**page.html:**
- Rendered markdown content
- Sidebar with related files and backlinks
- "Back to Graph" link
- Previous/Next file navigation

### Dependencies to add

```
flask
markdown
pygments
```

`pygments` is required by `markdown`'s `codehilite` extension for syntax
highlighting in rendered code blocks. `requests` is already in
`requirements.txt` (used by `kb_query.py` for LLM API calls).

## UI/UX Details

### Search behavior
- Search bar always visible in header
- Type query → debounced API call (300ms) → results dropdown
- Results show: filename, heading, score, snippet (first 100 chars)
- Click result → navigate to `/page/<file>#<heading>`
- Press `/` to focus search from anywhere
- Press `Esc` to close results

### Graph interactions
- **Click node** → navigate to page viewer
- **Hover node** → tooltip with title + connection count
- **Drag node** → reposition (rearrange layout)
- **Scroll** → zoom in/out
- **Click edge** → highlight connected nodes
- **Double-click background** → reset zoom

### Page viewer navigation
- Sidebar shows related files (from connections.db)
- Click related file → navigate to that page
- "Back to Graph" button in header
- Breadcrumb: Graph > topic-a.md
- Optional: Previous/Next file (alphabetical or reading order)

## Styling

**Foundation 6.9.0** via CDN for layout (XY Grid) and components (top-bar,
buttons, callouts, forms). Color palette extracted statically from Tailwind
v3 — no Tailwind CDN needed, just CSS custom properties hardcoded in
`base.html`.

```html
<!-- Foundation -->
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/foundation-sites@6.9.0/dist/css/foundation.min.css">
<script src="https://cdn.jsdelivr.net/npm/foundation-sites@6.9.0/dist/js/foundation.min.js"></script>
```

**CSS custom properties (inline in `base.html`):**

```css
:root {
  --bg:        #ffffff;   /* white */
  --surface:   #f8fafc;   /* slate-50 */
  --text:      #0f172a;   /* slate-900 */
  --text-muted:#64748b;   /* slate-500 */
  --border:    #e2e8f0;   /* slate-200 */
  --primary:   #2563eb;   /* blue-600 */
  --primary-h: #1d4ed8;   /* blue-700 */
  --success:   #16a34a;   /* green-600 */
  --error:     #dc2626;   /* red-600 */
  --code-bg:   #f1f5f9;   /* slate-100 */
}
.dark {
  --bg:        #0f172a;   /* slate-900 */
  --surface:   #1e293b;   /* slate-800 */
  --text:      #f8fafc;   /* slate-50 */
  --text-muted:#94a3b8;   /* slate-400 */
  --border:    #334155;   /* slate-700 */
  --primary:   #3b82f6;   /* blue-500 */
  --primary-h: #60a5fa;   /* blue-400 */
  --success:   #22c55e;   /* green-500 */
  --error:     #ef4444;   /* red-500 */
  --code-bg:   #1e293b;   /* slate-800 */
}
```

Theme toggle via `<body class="dark">` or config default.

## File Structure (final)

```
tools/
├── kb_app.py              # Main Flask application
├── connections.py         # Build connections.db from ChromaDB embeddings
├── connections            # Thin bash wrapper
├── templates/
│   ├── base.html          # Shared layout + CSS custom properties
│   ├── graph.html         # Graph visualization + KB Q&A panel
│   └── page.html          # KB page viewer

flask_config.yaml          # Flask app configuration (shipped with defaults)
connections.db             # SQLite graph edges (built by tools/connections)
```

No `static/` directory needed — all CSS/JS inline or loaded from CDN.

## Startup Flow

```bash
# 1. Build the vector index
tools/index                     # or: tools/index --incremental

# 2. Build the connections DB (graph edges)
tools/connections               # reads ChromaDB, writes connections.db

# 3. (Optional, for KB Q&A) Start Ollama with a model
ollama serve  # in a separate terminal
ollama pull phi4-mini  # or your preferred model

# 4. Start the Flask app
tools/serve
# → Running on http://localhost:5000
```

If `tools/connections` hasn't been run yet, the graph shows nodes but no
edges. If Ollama isn't running, the KB Q&A panel returns an error; the
rest of the app (graph, search, page viewer) works without it.

## What this replaces

| Before | After |
|---|---|
| `kb_search.py` CLI for search | Web UI search bar |
| `kb_query.py` CLI for one-shot KB Q&A | Web UI question box |
| Reading .md files manually | Rendered markdown in browser |
| No visualization | Interactive graph |
| No navigation | Sidebar with related files |
| Obsidian (external tool) | Self-contained Flask app |

## Not in scope

- Multi-user / collaboration
- Write/edit KB from the web UI
- Authentication
- Deployment to production (local use only)
- Plugin system
- Mobile app
- Streaming LLM responses (future enhancement)

These can be added later if needed.
