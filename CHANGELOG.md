## 2026-07-18 (12)
### Added
- `tools/connections.py` and `tools/connections` wrapper copied to all
  derivative repos; `connections_top_n` and `connections_min_score` added
  to each repo's `config.yaml`.

## 2026-07-18 (11)
### Added
- `tools/connections.py`: builds `connections.db` (SQLite) from ChromaDB
  embeddings — per-file mean embedding re-normalized, pairwise cosine
  similarity, symmetrized top-N edges above min-score threshold written to DB.
  `--show <file>` flag prints nearest neighbors for debugging.
- `tools/connections`: bash wrapper (matches `tools/index` / `tools/search` pattern).
- `config.yaml`: `connections_top_n` (default 5) and `connections_min_score`
  (default 0.5) — controls edges per file and similarity floor.
### Changed
- `tools/kb_app.py`: graph edges, page sidebar connections, and file connection
  counts now read from `connections.db` via `_db_connect()`. Removed
  `_parse_see_also()` and `_SEE_ALSO_RE` entirely — See Also section parsing
  is no longer used anywhere in the app. Falls back gracefully (empty edges /
  empty connections) when `connections.db` hasn't been built yet.

## 2026-07-18 (10)
### Changed
- `FLASK-APP-PLAN.md`: promoted `connections.db` / `connections.py` from
  "v2 future" to current design — graph edges now come exclusively from
  ChromaDB semantic nearest-neighbor, not `## See Also` section parsing.
  Added `Tool: connections.py` spec section (algorithm, schema, config,
  CLI). Added `Agent Instructions` section specifying required AGENTS.md
  and CONTENT-STYLE.md changes, the two-step `index → connections` workflow,
  and the one-time `kb_strip_see_also.py` cleanup for derivative repos.
  Removed all v1/v2 framing; updated startup flow, architecture diagram,
  page viewer layout, and "Not in scope" list accordingly.

## 2026-07-18 (9)
### Added
- `tools/kb_app.py`: `_iter_kb_files()` — unified file discovery respecting
  `file_patterns` (whitelist) and `skip_files` (blacklist) from `config.yaml`,
  matching `kb_index.py` logic. Applied to graph data, file sidebar, and
  backlink scanning — skipped files no longer appear as isolated graph nodes.
- `tools/templates/graph.html`: "⊡ Fit" button overlaid on graph — fits all
  nodes into the viewport with a 0.4× minimum scale floor; dblclick also fits.
### Changed
- `tools/kb_app.py`: all three `rglob("*.md")` call sites replaced with
  `_iter_kb_files()` — graph, sidebar, and connections now all respect the
  same file discovery config. Eliminates isolated orphan nodes from skipped
  navigation files (e.g. glossary.md) that were blowing out the graph bounds.
- All derivative repos now run identical code; per-repo differences are
  entirely config-driven (`config.yaml` + `flask_config.yaml`).

## 2026-07-18 (8)
### Added
- `tools/kb_index.py`: whitelist/blacklist file discovery — `file_patterns`
  (glob whitelist, defaults to `**/*.md`) and `skip_files` (blacklist, fnmatch)
  in `config.yaml`. Replaces custom file-discovery code in derivative repos;
  all repos now use the same indexer, configured per-repo via `config.yaml`.
- `tools/kb_index.py`: progress indicators — live `[x/y]` file counter during
  chunking and `x/y chunks embedded` counter during embedding, both using `\r`
  in-place updates.
- `tools/kb_index.py`: filter `See Also` sections from index — heading-level
  chunks whose final heading is `See Also` are skipped before embedding.
- `config.yaml`: documented `file_patterns` and `skip_files` params with examples.
### Changed
- `tools/kb_query.py`: list prompt tightened — removed "stop when done" clause
  that was causing early termination; `max_tokens_list` raised to 1500 as the
  natural ceiling. Added `concisely` back to factual prompt.
- `flask_config.yaml`: `top_k` 12→15, `max_context_chars` 6000→20000,
  `max_tokens_list` 768→1500 across all repos.

## 2026-07-18 (7)
### Added
- `tools/kb_query.py`: dual token budgets — `max_tokens` (384) for factual
  answers and `max_tokens_list` (768) for list/enumeration answers, auto-selected
  via `_is_list_query()` regex. CLI `--max-tokens` still overrides both.
- `tools/kb_query.py`: soft-reads `flask_config.yaml` at startup for LLM
  defaults (`api_url`, `model`, `top_k`, `max_tokens`, `max_tokens_list`) —
  CLI tool now stays in sync with Flask app config without manual duplication.
  Falls back to hardcoded defaults if the file is absent.
- `flask_config.yaml`: added `max_tokens_list: 768` param.
### Changed
- `tools/kb_app.py`: `rag_query()` now auto-selects token budget via
  `_is_list_query()` — list questions get more room to enumerate all items.
- `flask_config.yaml`: `max_tokens` reduced from 512 → 384 (factual answers
  don't need the extra headroom; list answers use `max_tokens_list` instead).

## 2026-07-18 (6)
### Removed
- `tools/templates/graph.html`: removed "Requires a running Ollama instance…"
  note from Ask your KB panel — noise for users who already have it configured.

## 2026-07-18 (5)
### Added
- `tools/templates/graph.html`: file filter input below sidebar header — type
  to narrow the file list by name or title client-side; no server round-trip.
  Article-aware alphabetical sort (`the`/`a`/`an` stripped from sort key) on
  all file lists.
- `tools/templates/graph.html`: three keyboard shortcuts — `s` focuses content
  search, `a` opens and focuses Ask your KB, `f` focuses file filter. Shortcuts
  fire only when no input/textarea is active.
- `tools/templates/graph.html`: Ask your KB panel moved above the graph and
  collapsed by default; shortcut hint `(a)` shown in the summary.
- `tools/kb_app.py`: `_LinkRewriter` Markdown treeprocessor — rewrites
  `[text](foo.md)` links and backtick-wrapped `.md` filenames to `/page/` routes
  so intra-KB links are clickable in the page viewer. Fixed `getparent()` lxml
  incompatibility (stdlib ElementTree has no such method) using a parent map
  and index-based replacement.

### Changed
- `tools/templates/base.html`: content search placeholder updated to
  `Content search… (s)`; `s` replaces `/` as the keyboard shortcut (removed
  `/` alias for consistency with the `a`/`f` letter-key convention).

## 2026-07-18 (4)
### Added
- `tools/kb_app.py`: `_ensure_instance_id()` — generates a UUID4 on first
  startup and appends `instance_id: <uuid>` to `flask_config.yaml`; subsequent
  starts read the persisted value. Passed to all templates via
  `app.jinja_env.globals`.
- `tools/templates/page.html`, `graph.html`: localStorage key for recent pages
  changed from `kb-recent` to `kb-recent-<instance_id>` — isolates each KB
  instance's visit history so two KBs on the same port no longer bleed
  recently-visited entries into each other.

## 2026-07-18 (3)
### Added
- `tools/serve`: thin bash wrapper for `kb_app.py` — resolves repo root from its
  own path so it works from any directory; matches the `tools/index` /
  `tools/search` / `tools/query` pattern. Usage: `tools/serve`,
  `tools/serve --port 8080`, `tools/serve --config my.yaml`.
- `flask_config.yaml`: comment on `host` explaining that `0.0.0.0` binds all
  interfaces (makes the app accessible from other machines on the network).
- README.md: updated all `kb_app.py` invocation examples to use `tools/serve`;
  added `tools/serve` to wrapper scripts description with usage examples.

## 2026-07-18 (2)
### Added
- `tools/templates/stats.html`: new `/stats` page — `d3.pack()` word cloud of
  top terms across all indexed chunks, circle size proportional to frequency;
  ranked sidebar list with frequency bars; clicking any term or bubble fires
  semantic search via the nav bar. Accessible via "stats" link in the graph
  file sidebar header.
- `tools/kb_app.py`: `get_top_terms()` — scans all chunk text via
  `collection.get()`, counts with `Counter`, filters `_STOPWORDS` plus optional
  user-configured `stats_stopwords` from `flask_config.yaml`. New routes:
  `/stats` and `/api/stats/terms`.
- `tools/kb_app.py`: `_STOPWORDS` list — ~100 common English function words,
  adverbs, and determiners. Added missing entries: `than`, `even`, `every`,
  `much`, `never`, `roughly`.
- `flask_config.yaml`: `stats_stopwords` key (commented out with examples) —
  lets users filter domain-specific high-frequency/low-signal words from the
  word cloud without touching Python.
- `tools/templates/base.html`: dark mode toggle button in nav bar — toggles
  `.dark` on `<body>`, persists preference to `localStorage`; server-set
  default (`theme` in `flask_config.yaml`) applies on first visit.
- `tools/templates/page.html`: TOC sidebar section — Contents panel above
  Related/Backlinks, generated from `md.toc` (python-markdown `toc` extension);
  only shown when the document has headings. Recent pages saved to
  `localStorage` on every page visit.
- `tools/templates/graph.html`: Recent pages section at top of file sidebar,
  loaded from `localStorage`. Graph neighborhood highlight on node hover — dims
  non-adjacent nodes and edges to reveal connection structure on dense graphs.
  "stats" link in file sidebar header.
- README.md: rewrote Flask feature table to cover all current features
  (stats page, file sidebar, recent pages, TOC panel, dark mode toggle, graph
  neighborhood highlight, search snippet/scroll behavior). Added config options
  table. Added `stats_stopwords` documentation.

## 2026-07-18
### Added
- `tools/templates/graph.html`: left file sidebar (220px) listing all KB files
  grouped by directory (top-level / projects / resources), loaded from
  `/api/files`; replaces the "Files" nav link that pointed at raw JSON.
  Two-column grid layout (sidebar + graph/Q&A right column).
- `tools/templates/page.html`: exact phrase highlight on arrival from search —
  TreeWalker wraps matched text in `<mark>` elements and smooth-scrolls to the
  first hit. Fallback when the phrase isn't literally present: subtly highlights
  the entire matched section (amber tint + left border accent on the heading)
  using the `#anchor` already in the URL — so semantic matches that don't
  contain the exact query string still get a clear visual indicator.
- `tools/templates/base.html`: search dropdown now shows 3-line snippet of the
  matching chunk (not a single truncated line); result URLs include `?q=` param
  so the page can highlight on arrival; `slugify()` aligned with python-markdown
  `toc` extension to ensure anchor links land on the right heading.
- ROADMAP.md: six new Later → Features items — dark mode toggle, TOC sidebar
  panel on page view, recent pages in file sidebar, top terms word cloud
  (`d3.pack()`, click-to-search), UMAP semantic scatter (heavier dep, cache
  recommended), graph neighborhood highlight on hover.

### Changed
- `tools/templates/base.html`: removed nav links div (Graph / Files) — graph
  is the home page, file browsing moved to the graph sidebar.
- `tools/templates/graph.html`: `||` → `??` for D3 `charge_strength` and
  `link_distance` config fallbacks — `||` would override a valid `0` value.

## 2026-07-17 (5)
### Added
- README.md: "Flask Web Interface" section — setup steps, feature table
  (graph/page viewer/search/KB Q&A), config options, Ollama setup, and
  proxy compatibility note. Added `flask_config.yaml` and `tools/templates/`
  to the Layout section; added `tools/kb_app.py` to the tools listing.

### Changed
- ROADMAP.md: Flask app item marked complete under Later → Features.

## 2026-07-17 (4)
### Fixed
- `tools/kb_app.py`: path containment check changed from `startswith` to
  `Path.is_relative_to()` in both `page()` and `get_connections()` — the
  string prefix check could allow paths from a directory whose name shares
  a prefix with `kb_root` (e.g. `/home/user/kb-extra/...`).
- `tools/kb_app.py`: `get_connections()` now resolves raw See Also hrefs to
  `kb_root`-relative paths before returning them. Previously, relative links
  like `../projects/foo.md` would produce broken `/page/../projects/foo.md`
  URLs in the page sidebar; now they resolve correctly to `/page/projects/foo.md`.
- `tools/kb_app.py`: moved `import markdown as mdlib` from inside the `page()`
  route function to module top.
- `tools/templates/graph.html`: replaced `||` with `??` (nullish coalescing)
  for D3 `charge_strength` and `link_distance` config fallbacks — `||` treats
  `0` as falsy and overrides a valid user-set value of 0.

## 2026-07-17 (3)
### Added
- `tools/kb_app.py`: Flask web interface implementing all routes from
  `FLASK-APP-PLAN.md` — graph visualization (`/`), page viewer
  (`/page/<path>`), semantic search (`/api/search`), KB Q&A (`/api/ask`),
  file listing (`/api/files`), connections (`/api/connections/<path>`).
  Reuses `build_prompt()` and `query_llm()` from `kb_query.py`;
  `load_config()`, `get_embedding_model()`, `get_collection()` from
  `kb_common.py`. Embedding model and Chroma collection loaded once at
  startup (not per-request). Path containment check on `/page/` prevents
  directory traversal. Graceful degradation on LLM errors.
- `tools/templates/base.html`: shared layout — Foundation 6.9.0 CDN,
  Tailwind v3 color palette as static CSS custom properties (no Tailwind
  CDN), debounced search bar (300ms, `/` shortcut, `Esc` to close), dark
  theme support via `body.dark`.
- `tools/templates/graph.html`: D3.js v7 force-directed graph — nodes
  colored by directory (projects/resources/top-level), degree-scaled node
  sizes, zoom/pan/drag, double-click to reset, edge-click to highlight
  connected nodes, collapsible KB Q&A panel below graph.
- `tools/templates/page.html`: two-column markdown viewer — sidebar with
  outgoing (See Also) and incoming (backlinks) connections, rendered
  markdown via Python `markdown` library with codehilite/fenced_code/
  tables/toc extensions, breadcrumb navigation.
- `requirements.txt`: added `flask`, `markdown`, `pygments`.

## 2026-07-17 (2)
### Added
- `kb/resources/.gitkeep`: creates the `kb/resources/` directory in the
  template so the Projects/Resources split feels complete out of the box.
- README.md Layout: added `html_to_text.py` entry (was missing alongside
  the other tools).
- `prompts/process-input-files.md`: replaced HTML comment `## Scope`
  placeholder with visible guidance text — rendered markdown now shows the
  instruction rather than hiding it in a comment.
- ROADMAP.md: marked all three Now → Docs items complete.

## 2026-07-17
### Added
- `CONTENT-STYLE.md`: new `## Language Standard` section — concrete-over-abstract
  rule, adjacent abstract noun test, define-on-first-use, read-aloud test,
  jargon pattern-detection table, and sentence structure rules. Ported from
  a companion project's style guide; domain-specific content excluded.
- `communication-levels.md`: QuASAP 7-level audience scale with two generic
  target-level templates (Level 4 / Level 5) as a starting point for KBs
  that produce audience-targeted content. Domain-specific content removed;
  users replace the target levels to match their format and audience.
- README.md: note pointing to `communication-levels.md` in Getting Started
  step 1; added to Layout section.
- FLASK-APP-PLAN.md: proxy compatibility note — any OpenAI-compatible proxy
  (LiteLLM, OpenRouter, etc.) works via `api_url` config; covers Bedrock,
  Anthropic, Azure OpenAI without code changes.
- `tools/kb_query.py`: updated `OLLAMA_URL` comment to mention proxy support.

### Changed
- ROADMAP.md: marked CONTENT-STYLE.md language standard item complete;
  updated dedup workflow item to reference `index_notes.md` (plan file
  deleted); removed external project path references from all entries.
- CHANGELOG.md: removed external project path reference from earlier entry.

## 2026-07-15 (2)
### Added
- `index_notes.md`: consolidated dedup workflow notes from
  `dedup-improvement-plan.md` — what was implemented, what was deferred
  and why, and why `kb_pipeline.sh`'s similarity thresholds don't transfer
  to this KB's section-granularity embeddings.

### Removed
- `dedup-improvement-plan.md`: implementation specs are now live in
  `prompts/process-input-files.md`; durable rationale moved to
  `index_notes.md`.

## 2026-07-15
### Changed
- FLASK-APP-PLAN.md: resolved ambiguities and tightened v1 scope
  - v1 is explicitly See-Also-only; `connections.db`/`connections.py`
    moved to v2 (not yet built) and added to "Not in scope (v1)"
  - KB Q&A panel folded into graph page — `ask.html` removed, no
    separate `/ask` route needed
  - `/api/connections` fallback behavior specified for when connections.db
    is absent (outgoing from See Also, incoming via file scan)
  - `pygments` added to dependencies (required by markdown's codehilite)
  - Tailwind CDN replaced with static CSS custom properties block —
    hex values extracted from Tailwind v3 palette, inlined in base.html
  - Startup flow simplified: `connections.py init` step removed

### Added
- ROADMAP.md: added "Adapt CONTENT-STYLE.md writing quality principles"
  under Later → Docs — tracks porting universal language principles from a
  companion project's style guide into the template's content style guide.

## 2026-07-06
### Added
- `tools/kb_query.py`: KB Q&A tool — retrieves top-k KB chunks via semantic
  search and synthesizes an answer using any OpenAI-compatible LLM endpoint
  (Ollama ≥ 0.1.24 by default). Default model `phi4-mini` (best reasoning/speed
  on CPU); `gemma2:2b` and `llama3.2:3b` included as commented-out alternatives.
- `tools/query`: thin bash wrapper for `kb_query.py`, resolves repo root from
  its own path so it works from any directory (matches `tools/index` /
  `tools/search` pattern).
- README.md: documented `tools/query` usage with example invocations, Ollama
  version requirement, and all three wrappers in the Layout section.
