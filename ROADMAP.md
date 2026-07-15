# Roadmap

Future work items for the markdown knowledgebase template. Not a commitment —
a prioritized backlog.

## Now

High-priority improvements to the template itself.

### Docs

- [ ] Add `html_to_text.py` to README Layout section (currently undocumented
  alongside the other tools)
- [ ] Add default `kb/resources/` directory with `.gitkeep` — matches
  `kb/projects/` and makes the Projects/Resources split feel complete out of
  the box
- [ ] Fill in the `## Scope` placeholder in
  `prompts/process-input-files.md` with guidance text instead of leaving it
  empty
- [ ] Document the KB Q&A feature (`tools/kb_query.py`) — use case is
  "query the KB + synthesize a short answer" via a local LLM. Needs a quick
  setup section in the README covering Ollama install, model selection, and
  example invocation. Note: after extensive testing, a GPU is required for
  the synthesis step — CPU-only inference is too slow for practical use

### Tooling

- [ ] Add a `tools/validate` wrapper that checks KB structural integrity
  (broken See Also links, orphan files, oversized files) — currently only
  available as the `.claude/commands/kb-audit.md` slash command, which
  requires Claude Code. Should also handle oversized files end-to-end:
  flag files over 30K chars, then offer to split them following
  `CONTENT-STYLE.md` rules (find a genuine analytical seam, create a
  `part-2` sibling, update See Also cross-references, reindex).

## Next

Medium-priority enhancements.

### Tooling

- [ ] Improve error messages in `kb_index.py` when `config.yaml` is missing
  or malformed (currently a raw Python traceback)
- [ ] Add `--dry-run` flag to `kb_index.py` — show which files would be
  re-indexed without actually embedding
- [ ] Add `--format json` option to `kb_search.py` for programmatic consumption
  (currently stdout-only, human-readable)

### Workflow

- [ ] Implement deferred items from `dedup-improvement-plan.md`: calibration
  step for score bands in AGENTS.md, and the detail-check decision tree in
  `prompts/process-input-files.md` step d

### Documentation

- [ ] Document the "Notes" pattern for capturing tried-and-failed approaches
  (see `index_notes.md` for the first example). Add guidance in the template
  so users know to record dead ends with reasoning — prevents repeating
  mistakes across sessions. The fem-kb notes on embedding-only pre-scans
  and cheap LLM triage tiers are the seed content.

## Later

Lower-priority or larger-scope efforts.

### Features

- [ ] **Flask app (Obsidian lite)** — lightweight local web UI for browsing
  the KB. Graph visualization (D3.js), semantic search bar, rendered
  markdown pages, KB Q&A question box (retrieve + synthesize via local LLM).
  See `FLASK-APP-PLAN.md` for full spec. Config via `flask_config.yaml`
  (shipped with defaults for port, model, graph layout, theme). Key
  routes: `/` (graph), `/page/<file>` (rendered markdown), `/api/search`
  (ChromaDB query), `/api/ask` (KB Q&A), `/api/graph` (JSON for
  D3.js). Falls back to parsing See Also sections if connections.db
  doesn't exist. KB Q&A requires Ollama or compatible endpoint; works
  without it. Dependencies: Flask + markdown.
- [ ] Tagging or metadata system beyond file/directory structure (e.g. YAML
  front matter fields that `kb_index.py` indexes and `kb_search.py` can
  filter on)
- [ ] Integration with Obsidian — detect and preserve Obsidian-style links
  (`[[wikilinks]]`) during chunking, or convert them to standard markdown
  links
- [ ] `kb_search.py --filter` flag to narrow results by directory, file
  pattern, or front matter field

### Infrastructure

- [ ] Optional PostgreSQL or SQLite backend for `kb_search.py` as an
  alternative to ChromaDB (ChromaDB works fine for small-to-medium KBs,
  but some users prefer a familiar database)
