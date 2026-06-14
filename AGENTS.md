# Markdown Knowledgebase — Agent Instructions

## What this is

A self-contained markdown knowledgebase (`kb/`) plus a local semantic search
index (`.kb-index/`, ChromaDB + `bge-small-en-v1.5` via fastembed, CPU-only,
no network calls at query time once the model is cached).

Tools live in `tools/`, run via the venv:

```
.venv/bin/python tools/kb_index.py              # full rebuild of the index
.venv/bin/python tools/kb_index.py --incremental # only re-index changed/new/deleted files
.venv/bin/python tools/kb_search.py "query" ... # semantic search, ranked hits
```

## Core workflow: checking if something is already covered

**Do not read every file in `kb/` to check for duplication or existing
coverage.** That's the pattern this tool replaces. Instead:

1. For each distinct point/claim to check, run:
   ```
   .venv/bin/python tools/kb_search.py "concise description of the point"
   ```
   Multiple queries can be passed in one call.
2. Look at the top hits (file, heading path, score, snippet). On a
   single-domain KB, scores cluster fairly high even for related-but-distinct
   topics, so don't rely on one fixed cutoff:
   - **~0.75+** with a topically matching heading: usually real overlap —
     read the snippet to confirm before deciding new/duplicate.
   - **~0.6–0.75**: ambiguous — read the snippet; topically adjacent content
     often scores here without actually covering the same point.
   - **below ~0.6**: usually not covered.
3. Only `Read` the specific file(s) that scored highest — and only if the
   snippet isn't enough to decide. Do not fall back to reading the whole KB.

## Processing new input files

`inputs/` holds new source files awaiting triage, with `inputs/processed/`
and `inputs/off-topic/` as destinations after handling. The full workflow —
inventory, cross-check via `kb_search.py`, off-topic/duplicate handling,
presenting the inventory, waiting for confirmation — is in
`prompts/process-input-files.md`. In short:

1. **Full inventory first** — enumerate every analytically distinct point
   before evaluating any of them.
2. **Cross-check each point** via `kb_search.py` (see above), not by reading
   all files.
3. **Present the full inventory** — status (new / partial / covered),
   proposed target file + section, one-line rationale. Flag anything
   uncertain.
4. **Wait for confirmation** before writing/editing any `kb/` files.

For periodic quality review of existing `kb/` files (consistency, register,
redundancy, structure), see `prompts/process-knowledgebase-files.md`.

## Reindexing

The index is **not** updated automatically. After a batch of edits to
`kb/`, run:

```
.venv/bin/python tools/kb_index.py --incremental
```

`--incremental` compares each `kb/*.md` file's mtime against `.kb-index/meta.json`,
re-chunks/embeds only new or changed files, and removes chunks for files
deleted from `kb/`. This is much cheaper than a full rebuild on this
CPU-only host and is the normal day-to-day command. It falls back to a full
rebuild automatically if no index (or a pre-incremental `meta.json`) exists
yet.

Use a plain `tools/kb_index.py` (no flag) for a full rebuild — e.g. after
changing `config.yaml` (chunk size, embedding model) or if the index is
suspected to be out of sync with `kb/`.

`kb_search.py` prints a `[stale index]` warning (to stderr) if any `kb/*.md`
file has been modified more recently than the last index build — if you see
that warning mid-session, mention it and suggest reindexing before relying
further on search results.

When making several edits in one session, batch them and reindex once at
the end rather than after each file.

## Config

`config.yaml` controls the embedding model, chunk size/overlap, KB root, and
index location. One config value (`kb_root`) — no hardcoded paths elsewhere.

## Content conventions

See `CONTENT-STYLE.md` for register, filename, bullet/blockquote, file-size,
and "See Also" conventions for content in `kb/`.
