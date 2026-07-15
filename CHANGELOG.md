## 2026-07-15
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
