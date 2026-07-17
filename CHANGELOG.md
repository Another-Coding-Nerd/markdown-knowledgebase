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
