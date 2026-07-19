# Roadmap

Future work items for the markdown knowledgebase template. Not a commitment —
a prioritized backlog.

## Now

High-priority improvements to the template itself.

### Docs

- [x] Add `html_to_text.py` to README Layout section (currently undocumented
  alongside the other tools)
- [x] Add default `kb/resources/` directory with `.gitkeep` — matches
  `kb/projects/` and makes the Projects/Resources split feel complete out of
  the box
- [x] Fill in the `## Scope` placeholder in
  `prompts/process-input-files.md` with guidance text instead of leaving it
  empty
- [x] Document the KB Q&A feature (`tools/kb_query.py`) — use case is
  "query the KB + synthesize a short answer" via a local LLM. Needs a quick
  setup section in the README covering Ollama install, model selection, and
  example invocation. Note: after extensive testing, a GPU is required for
  the synthesis step — CPU-only inference is too slow for practical use

### Tooling

- [ ] Add a `tools/validate` wrapper that checks KB structural integrity
  (orphan files, oversized files) — currently only
  available as the `.claude/commands/kb-audit.md` slash command, which
  requires Claude Code. Should also handle oversized files end-to-end:
  flag files over 30K chars, then offer to split them following
  `CONTENT-STYLE.md` rules (find a genuine analytical seam, create a
  `part-2` sibling, reindex, rebuild connections).

## Next

Medium-priority enhancements.

### Tooling

- [ ] Tune non-list LLM prompt — explore suppressing preamble ("no preamble,
  2–4 sentences") and stronger "direct" framing vs. current "concisely in a
  neutral analytical tone". Reference options A/B/C discussed 2026-07-18.
- [x] Configurable index exclusions — `file_patterns` (glob whitelist) and
  `skip_files` (blacklist) in `config.yaml`; `See Also` heading sections also
  filtered at chunk level. All per-repo, no code changes needed.
- [ ] Improve error messages in `kb_index.py` when `config.yaml` is missing
  or malformed (currently a raw Python traceback)
- [ ] Add `--dry-run` flag to `kb_index.py` — show which files would be
  re-indexed without actually embedding
- [ ] Add `--format json` option to `kb_search.py` for programmatic consumption
  (currently stdout-only, human-readable)

### Workflow

- [ ] Implement deferred items from `index_notes.md` (dedup workflow section):
  calibration step for score bands in AGENTS.md, and the detail-check
  decision tree in `prompts/process-input-files.md` step d

### Documentation

- [ ] Document the "Notes" pattern for capturing tried-and-failed approaches
  (see `index_notes.md` for the first example). Add guidance in the template
  so users know to record dead ends with reasoning — prevents repeating
  mistakes across sessions. Notes on embedding-only pre-scans and cheap
  LLM triage tiers are the seed content.

## Later

Lower-priority or larger-scope efforts.

### Bugs

- [x] **`/page/` sidebar not independently scrollable** — on long documents
  the left sidebar (TOC / Related / Backlinks) cannot be scrolled
  independently; it only scrolls after the main content area has been
  scrolled to the bottom. Fix: give the sidebar `overflow-y: auto` with a
  constrained height (e.g. `height: 100vh`, sticky positioning) so it
  scrolls independently of the content column.

### Features

- [x] **Flask app (Obsidian lite)** — lightweight local web UI for browsing
  the KB. Graph visualization (D3.js), semantic search bar, rendered
  markdown pages, KB Q&A question box (retrieve + synthesize via local LLM).
  See `FLASK-APP-PLAN.md` for full spec. Config via `flask_config.yaml`
  (shipped with defaults for port, model, graph layout, theme). Key
  routes: `/` (graph), `/page/<file>` (rendered markdown), `/api/search`
  (ChromaDB query), `/api/ask` (KB Q&A), `/api/graph` (JSON for
  D3.js). Graph edges from `connections.db` (nodes-only fallback if
  absent). KB Q&A requires Ollama or compatible endpoint; works
  without it. Dependencies: Flask + markdown.
- [x] **Dark mode toggle** — nav button toggles `.dark` on `<body>`, persisted in
  `localStorage`; CSS custom properties already support both themes
- [x] **TOC sidebar panel** — on `/page/` views, show document headings above
  Related/Backlinks; `markdown` `toc` extension already extracts this, just
  needs to be passed from the route and rendered in the sidebar
- [x] **Recent pages** — "Recently visited" section in the graph file sidebar,
  stored in `localStorage`; purely frontend, no backend change needed
- [x] **Top terms word cloud** — dedicated `/stats` page; `d3.pack()` circle
  packing layout (deterministic, cleaner than force-directed for this use case),
  circles sized by frequency from `collection.get()` + `Counter` + English
  stopword filter; clicking a term populates the nav search bar and fires
  semantic search — making the cloud a topic navigator, not just decoration
- [x] **Graph "fit to page"** — "⊡ Fit" button overlaid on graph fits all
  nodes into the viewport (0.4× minimum scale floor); dblclick also fits.
- [x] **`connections.py` / `connections.db`** — semantic nearest-neighbor graph
  edges built from ChromaDB embeddings; replaces `## See Also` section parsing.
  `tools/connections` wrapper; `connections_top_n` + `connections_min_score` in
  `config.yaml`. `kb_app.py` reads from DB; fallback is nodes-only (no edges).
- [ ] **UMAP semantic scatter** — on the `/stats` page, project chunk embeddings
  from ChromaDB to 2D via `umap-learn`, plot as a D3 scatter where each dot is
  a chunk colored by file/directory; semantically similar chunks cluster
  together, revealing the KB's topical structure; click a dot → navigate to
  that page/section. Note: `umap-learn` is a heavier dependency (~500MB with
  numpy/scipy) and projection takes a few seconds — cache the result
- [x] **Graph neighborhood highlight** — on node hover, dim all non-adjacent
  nodes and edges to make connection structure legible on dense graphs; pure D3
- [ ] Tagging or metadata system beyond file/directory structure (e.g. YAML
  front matter fields that `kb_index.py` indexes and `kb_search.py` can
  filter on)
- [ ] Integration with Obsidian — detect and preserve Obsidian-style links
  (`[[wikilinks]]`) during chunking, or convert them to standard markdown
  links
- [ ] `kb_search.py --filter` flag to narrow results by directory, file
  pattern, or front matter field

### Docs

- [x] Adapt `CONTENT-STYLE.md` writing quality principles from a companion
  project's style guide — re-evaluate what translates to a generic KB
  template (concrete over abstract, jargon detection patterns, plain English
  test, sentence structure). Port the universal principles as a new
  "Language Standard" section in the template's `CONTENT-STYLE.md`. Skip
  project-specific content: level system, citation placement, the coffee
  test, format-specific rules, and domain examples.

### Infrastructure

- [ ] Optional PostgreSQL or SQLite backend for `kb_search.py` as an
  alternative to ChromaDB (ChromaDB works fine for small-to-medium KBs,
  but some users prefer a familiar database)
