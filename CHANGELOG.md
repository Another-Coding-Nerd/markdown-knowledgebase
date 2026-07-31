## 2026-07-31
### Added
- `prompts/_inventory-shared-steps.md`: shared include (steps c–m, 3–6, Conventions) used by both input-processing prompts — single source of truth, no more drift.
### Changed
- `prompts/process-input-files.md`, `process-input-files-dense.md`: replaced duplicated body with reference to shared include.
### Fixed
- Both input prompts: fix duplicate `f.` sub-step; renumber `d2`→`e` through `l`→`m`; add `about.md` missing-file fallback; fix part-file sentinel to `part-001.txt`.
- `prompts/process-input-files-dense.md`: add missing part-file handling to step 3.
- `prompts/process-knowledgebase-files.md`: add H1 title; add `kb_stats.py` prompt before Review Criteria.
- `prompts/organize-kb-files.md`: add uncertain-classification fallback.
- `AGENTS.md`: link to dense input variant; add `about.md` fallback note.
- `README.md`: note on course/lesson material — don't carry lesson structure into `kb/`.

## 2026-07-30
### Added
- `tools/kb_stats.py`, `tools/stats`: section length diagnostics — flags SHORT/LONG leaf sections.

## 2026-07-28
### Added
- `CONTENT-STYLE.md`: Editing Discipline section; Prose Rhythm additions — "Name the thing, then unpack it," "Mechanisms, not just patterns," "The 8th-grade test."
- `.gitignore`: `STYLE-QUICKREF.md` (working file, not tracked).

## 2026-07-27
### Added
- `CONTENT-STYLE.md`: Prose Rhythm — "Assume intelligent but uninformed," "Find the plain English version that loses nothing."
### Fixed
- `inputs/fmt_text.sh`, `inputs/de-dupe.sh`: part-file guards updated to `%03d` format (`part-001.txt`).

## 2026-07-25
### Changed
- `inputs/fmt_text.sh`: files over 100 lines split into overlapping segments; output named `basename-part-NNN.txt`; re-run safe (skips already-split files).
- `inputs/de-dupe.sh`: part-file aware — checks basename against `processed/` for both whole and split forms.
- `prompts/process-input-files.md`: step 2b leads with 100-line segments; step 3 clarifies part files are one logical unit.
- `AGENTS.md`: reverted redundant embedding model note (lives in `config.yaml`).

## 2026-07-23
### Added
- `index_notes.md`: GraphRAG consideration — why not adopted, when to revisit, Kuzu as lowest-friction path.
- `config.yaml`: note that incremental reindex re-embeds entire changed files — relevant to model choice on CPU.

## 2026-07-20
### Added
- `config.yaml`: `follow_symlinks` boolean — enables indexing symlinked directories; fixes Python 3.12 breakage.
- `kb_common.py`: `iter_kb_files(cfg)` shared traversal helper; `safe_kb_path()` lexical path-traversal check (symlink-safe).
- `connections.py`: paginated ChromaDB fetches to avoid SQLite variable-cap failures on large KBs.
- `tools/templates/page.html`: dark mode CSS fixes for code, tables, and borders.
### Changed
- `kb_index.py`, `kb_search.py`, `kb_app.py`: file discovery replaced with `iter_kb_files(cfg)`.
- `base.html`: wider max-width.

## 2026-07-20
### Added
- `WORKFLOW.md`: day-to-day ingestion workflow — collecting sources, preparing inputs, using prompts, reindexing.
- `CONTENT-STYLE.md`: Language Standard and Prose Rhythm sections.

## 2026-07-19
### Added
- `about.md`: per-repo scope definition; read by both input-processing prompts for on-topic/off-scope decisions.
- `prompts/process-input-files-dense.md`: variant for sentence-level dense input (interview summaries, headingless text).
- `.claude/commands/fix-register.md`, `audit-citation.md`: slash commands for register scan and citation audit.
### Changed
- `AGENTS.md`: added KB init sequence; updated connections.db section; agents must not write `## See Also` (edges are computed).
- `prompts/process-input-files.md`: scope now reads from `about.md`; per-point scope filter added.
- `LICENSE`: MIT → CC BY-NC 4.0.
- `README.md`: First-time setup subsection; prompt comparison table; optional/required labels in layout.

## 2026-07-18
### Added
- `tools/connections.py`, `tools/connections`: builds `connections.db` (SQLite) from ChromaDB embeddings — pairwise cosine similarity, top-N edges per file.
- `tools/serve`: bash wrapper for `kb_app.py`.
- `tools/templates/stats.html`: `/stats` word cloud — top terms across all indexed chunks, click-to-search.
- `tools/kb_app.py`: full Flask web interface — graph, page viewer, semantic search, KB Q&A, stats, dark mode, file sidebar, keyboard shortcuts, recent pages.
- `tools/kb_query.py`: dual token budgets (factual vs. list); reads defaults from `flask_config.yaml`.
- `tools/kb_index.py`: whitelist/blacklist file discovery (`file_patterns`, `skip_files` in `config.yaml`); progress indicators; filters `See Also` sections from index.
- `kb_common.py`: `safe_kb_path()` for path-traversal protection in Flask routes.
- `flask_config.yaml`: `stats_stopwords`, dark mode default, KB Q&A config.
### Changed
- Graph edges source changed from `## See Also` parsing to `connections.db` — all `## See Also` authoring instructions removed from prompts and style guide.
- `config.yaml`: default model set to `bge-small-en-v1.5`; model choice docs point to config.
### Fixed
- Path containment check: `startswith` → `Path.is_relative_to()` in Flask routes.
- `||` → `??` for D3 config fallbacks (treats `0` correctly).
- Sidebar scrolls independently on long pages.

## 2026-07-17
### Added
- `tools/kb_query.py`, `tools/query`: KB Q&A — retrieves top-k chunks, synthesizes answer via local LLM (Ollama or any OpenAI-compatible endpoint).
- `CONTENT-STYLE.md`: Language Standard section (concrete-over-abstract, jargon detection table).
- `communication-levels.md`: QuASAP 7-level audience scale with generic target-level templates.
- `FLASK-APP-PLAN.md`: design spec for the Flask web interface.

## 2026-07-15
### Added
- `index_notes.md`: dedup workflow notes — what was implemented, what was deferred and why.
### Removed
- `dedup-improvement-plan.md`: content absorbed into `prompts/process-input-files.md` and `index_notes.md`.

## 2026-07-06
### Added
- `tools/kb_query.py`, `tools/query`: initial KB Q&A tool.
