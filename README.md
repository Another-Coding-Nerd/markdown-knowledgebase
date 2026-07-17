# Markdown Knowledgebase + Semantic Search

A self-contained system for maintaining a markdown knowledgebase (`kb/`)
with local semantic search, designed to avoid reading the entire KB into
context every time new content needs to be cross-checked against existing
material.

## Getting Started

This is a template for a Claude-Code-maintained knowledgebase: markdown
content lives in `kb/`, and Claude searches it semantically
(`tools/kb_search.py`) instead of reading every file to check for
duplication or existing coverage.

After completing Setup below:

1. **Define the KB's scope** — edit `CONTENT-STYLE.md` for this KB's content
   conventions, and fill in the `## Scope` placeholder in
   `prompts/process-input-files.md`. If your KB produces content for a
   specific audience, `communication-levels.md` provides a 7-level scale
   (QuASAP framework) with two default target levels as a starting point —
   adjust or replace them to match your output format and audience.
2. **Choose a layout** — `kb/` is flat by default: every file at the top
   level (or in topic subdirectories), organized by topic. If this KB has
   bounded-effort content (a deliverable or finish line, e.g. "build X",
   "decide on Y"), adopt the Projects/Resources split described in
   `AGENTS.md`. This can be decided later, too — just tell Claude:
   > I want to adopt the Projects/Resources split for this kb/ — see
   > AGENTS.md and run prompts/organize-kb-files.md to sort the existing
   > kb/\*\*/\*.md files into kb/projects/ and kb/resources/.

   No files need editing to switch.
3. **Add content** — drop files directly into `kb/`, or stage raw source
   material in `inputs/` and have Claude run the
   `prompts/process-input-files.md` workflow to triage it.
4. **Build the index** — `.venv/bin/python tools/kb_index.py`.
5. **Work with your AI agent** — `AGENTS.md` defines the search-first
   workflow (Claude Code reads it via the `CLAUDE.md` import; other agents
   that follow the AGENTS.md convention read it directly) for checking
   coverage, processing new input, and reindexing after edits.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

First run of `kb_index.py` downloads the `BAAI/bge-small-en-v1.5` embedding
model (~130MB, cached under `~/.cache/`).

## Usage

```bash
# Update the index after editing kb/**/*.md (run after a batch of edits)
.venv/bin/python tools/kb_index.py --incremental

# Full rebuild (e.g. after changing config.yaml's chunking/embedding settings)
.venv/bin/python tools/kb_index.py

# Search
.venv/bin/python tools/kb_search.py "some query" "another query" --top-k 5
```

`tools/index`, `tools/search`, and `tools/query` are thin wrapper scripts —
shorter to type, and they resolve the repo root from their own path so they
work from any directory.

**KB Q&A (Retrieve & Synthesize)** (optional) — retrieve KB chunks and synthesize an answer
via a local LLM:

```bash
tools/query "what do I know about X?"
tools/query --top-k 8 --model phi4-mini "question"
tools/query --max-tokens 256 "short answer please"
```

Requires a running [Ollama](https://ollama.com) instance (≥ 0.1.24) or any
OpenAI-compatible `/v1/chat/completions` endpoint. **Not required** for
indexing or search — `tools/index` and `tools/search` work with zero
server dependencies.

## Design Philosophy

**CLI/agent first, UI optional.** Every feature works from the terminal —
no GUI required, no app that needs to be running on your machine.

- **Agents** use the CLI tools directly (`kb_search.py`, `kb_query.py`,
  `kb_index.py`) — no browser, no server, no wrapper.
- **Humans** can work the same way, or optionally launch a lightweight
  Flask app (`tools/kb_app.py`) for visual browsing, graph exploration,
  and search in a browser.
- **The data works without the UI.** Markdown files, the vector index,
  and the connections graph are all usable from the command line. The
  Flask app is one interface among several, not a requirement.

This is the opposite of app-first systems (Obsidian, Notion) where the
GUI is the primary interface and CLI access is an afterthought. Here the
tools are the product. The UI is a convenience layer.

## How it works

- `kb/**/*.md` files are split into chunks at H1/H2/H3 heading boundaries.
- Sections exceeding `max_tokens` (config.yaml) are sub-split into
  overlapping pieces by paragraph/sentence, so embeddings never silently
  truncate.
- Chunks are embedded with `bge-small-en-v1.5` (ONNX/CPU via fastembed, no
  PyTorch) and stored in a local ChromaDB collection under `.kb-index/`.
- `kb_index.py --incremental` compares each file's mtime against
  `.kb-index/meta.json`, re-chunking/embedding only new or changed files and
  removing chunks for deleted files. It falls back to a full rebuild if no
  index (or a pre-incremental `meta.json`) exists. Plain `kb_index.py` always
  does a full rebuild.
- `kb_search.py` embeds each query, returns ranked chunks (file, heading
  path, similarity score, snippet), and warns if any `kb/**/*.md` file has
  changed since the last index build.

## Flask Web Interface (optional)

A lightweight local web UI — graph visualization, semantic search, rendered
markdown pages, and a KB Q&A question box.

```bash
# 1. Build the vector index (if not already done)
.venv/bin/python tools/kb_index.py

# 2. Start the app
.venv/bin/python tools/kb_app.py
# → App URL: http://localhost:5000
```

**What it provides:**

| Page | URL | Description |
|------|-----|-------------|
| Graph | `/` | D3.js force-directed graph of KB connections (from See Also links). Click a node to open the page. |
| Page viewer | `/page/<file>` | Rendered markdown with sidebar showing related files and backlinks. |
| Search | header bar | Debounced semantic search — press `/` to focus, `Esc` to close. |
| Ask your KB | panel on `/` | One-shot Q&A: retrieves relevant chunks, sends to a local LLM, returns a synthesized answer with citations. |

**Configuration:** `flask_config.yaml` (shipped with defaults). Options:
port, host, theme (`dark`/`light`), `search_top_k`, graph layout
(`charge_strength`, `link_distance`, node sizes), and KB Q&A settings
(`api_url`, `model`, `top_k`, `max_tokens`).

```bash
.venv/bin/python tools/kb_app.py --port 8080   # override port
.venv/bin/python tools/kb_app.py --config my.yaml  # custom config file
```

**KB Q&A requires** a running [Ollama](https://ollama.com) instance
(≥ 0.1.24) or any OpenAI-compatible `/v1/chat/completions` endpoint. The
rest of the app (graph, search, page viewer) works without it.

```bash
# Start Ollama in a separate terminal, then pull a model:
ollama serve
ollama pull phi4-mini   # default; gemma2:2b or llama3.2:3b also work
```

Any OpenAI-compatible proxy works via `api_url` in `flask_config.yaml` —
[LiteLLM](https://github.com/BerriAI/litellm) can front AWS Bedrock,
Anthropic, Azure OpenAI, and others with no code changes.

## Layout

```
config.yaml              # kb_root, embedding model, chunk size/overlap, top_k
flask_config.yaml        # Flask app config (port, theme, graph layout, KB Q&A)
communication-levels.md  # optional: QuASAP 7-level scale + target level templates
kb/               # the markdown knowledgebase content
  projects/       # optional Projects/Resources split (see AGENTS.md);
  resources/      # both dirs are created together when adopted;
                  # kb/ is flat by default if unused
inputs/           # new source files awaiting triage
  fmt_text.sh     # reflow raw .txt files to 100 columns
  processed/      # files already absorbed into kb/
  off-topic/      # files outside this KB's scope
prompts/
  process-input-files.md       # triage inputs/ into kb/
  organize-kb-files.md          # sort kb/ files into Projects vs. Resources
  process-knowledgebase-files.md # periodic quality review of kb/
tools/
  kb_app.py       # Flask web interface (graph, search, page viewer, KB Q&A)
  kb_index.py     # rebuild the index
  kb_search.py    # query the index
  kb_query.py     # KB Q&A: retrieve + synthesize via local LLM
  html_to_text.py # convert .html files / pasted HTML in .txt to plain text
  chunking.py     # heading-based + token-budget chunking
  kb_common.py    # shared config/model/collection helpers
  templates/      # Jinja2 templates for the Flask app
  index           # wrapper → kb_index.py
  search          # wrapper → kb_search.py
  query           # wrapper → kb_query.py
.kb-index/        # ChromaDB persistent store (gitignored)
```

See `AGENTS.md` for the workflow your AI agent should follow when maintaining
this KB, and `CONTENT-STYLE.md` for content-authoring conventions.
