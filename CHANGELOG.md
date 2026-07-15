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
  under Later → Docs — tracks re-evaluating and porting universal
  principles from `fem-media/deep-style/CONTENT-STYLE-v2.md` into the
  template's content style guide once the v2 guide is finalized.

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
