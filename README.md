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
   `prompts/process-input-files.md`.
2. **Add content** — drop files directly into `kb/`, or stage raw source
   material in `inputs/` and have Claude run the
   `prompts/process-input-files.md` workflow to triage it.
3. **Build the index** — `.venv/bin/python tools/kb_index.py`.
4. **Work with your AI agent** — `AGENTS.md` defines the search-first
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
# Update the index after editing kb/*.md (run after a batch of edits)
.venv/bin/python tools/kb_index.py --incremental

# Full rebuild (e.g. after changing config.yaml's chunking/embedding settings)
.venv/bin/python tools/kb_index.py

# Search
.venv/bin/python tools/kb_search.py "some query" "another query" --top-k 5
```

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
  path, similarity score, snippet), and warns if any `kb/*.md` file has
  changed since the last index build.

## Layout

```
config.yaml       # kb_root, embedding model, chunk size/overlap, top_k
kb/               # the markdown knowledgebase content
inputs/           # new source files awaiting triage
  fmt_text.sh     # reflow raw .txt files to 100 columns
  processed/      # files already absorbed into kb/
  off-topic/      # files outside this KB's scope
prompts/
  process-input-files.md       # triage inputs/ into kb/
  process-knowledgebase-files.md # periodic quality review of kb/
tools/
  kb_index.py     # rebuild the index
  kb_search.py    # query the index
  chunking.py     # heading-based + token-budget chunking
  kb_common.py    # shared config/model/collection helpers
.kb-index/        # ChromaDB persistent store (gitignored)
```

See `AGENTS.md` for the workflow your AI agent should follow when maintaining
this KB, and `CONTENT-STYLE.md` for content-authoring conventions.
