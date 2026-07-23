# Markdown Knowledgebase — Agent Instructions

## What this is

A self-contained markdown knowledgebase (`kb/`) plus a local semantic search
index (`.kb-index/`, ChromaDB + fastembed, CPU-only,
no network calls at query time once the model is cached).

Tools live in `tools/`, run via the venv:

```
.venv/bin/python tools/kb_index.py              # full rebuild of the index
.venv/bin/python tools/kb_index.py --incremental # only re-index changed/new/deleted files
.venv/bin/python tools/kb_search.py "query" ... # semantic search, ranked hits
.venv/bin/python tools/connections.py           # rebuild connections.db (graph edges)
.venv/bin/python tools/connections.py --show <file> # inspect nearest neighbors for a file
```

Or via wrappers (shorter): `tools/index`, `tools/index --incremental`, `tools/search`, `tools/connections`.

## Initializing a new KB

Run this sequence once after cloning:

1. `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
2. Add initial content to `kb/` (even a few seed files)
3. `tools/index` — full index build (downloads embedding model on first run)
4. `tools/connections` — build graph edges
5. **Generate `about.md`** — ask your agent:
   > "Look at the kb/ files and our conversation so far, then write about.md —
   > 2–3 sentences on what this KB covers, and an explicit out-of-scope list."

   If `kb/` is empty, the agent asks you for the gist and drafts from that
   conversation. Either way, review and commit the result.

`about.md` can be regenerated anytime the KB's scope shifts — just ask the
agent to re-read `kb/` and rewrite it.

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

## Organizing kb/: Projects vs. Resources (optional)

By default, `kb/` is flat: every file lives at the top level (or in topic
subdirectories), organized by topic. No further setup is needed.

If this KB accumulates bounded-effort content — things with a deliverable or
finish line (e.g. "build X", "decide on Y", "set up Z") — and a flat
structure starts to feel cluttered, adopt the Projects/Resources split:

- **`kb/projects/`** — active, bounded efforts as described above. When a
  project is done, either fold any durable findings into the relevant
  resource file(s) and delete the project file, or mark it `status: archived`
  (front matter) if it's worth keeping as a record.
- **`kb/resources/`** — everything else: resource material (techniques,
  facts, guides, lookup tables), organized by topic, optionally using
  subdirectories within `kb/resources/`.

Adopting this split makes **both** `kb/projects/` and `kb/resources/` real
directories — existing top-level files get sorted into one or the other (see
`prompts/organize-kb-files.md`). The flat default layout described above is
only for KBs that don't adopt this split.

A finished project worth keeping as a record gets a one-line front matter
block instead of being deleted:

```yaml
---
status: archived
---
```

There is no separate `kb/archives/` directory in this scheme — an archived
project stays in `kb/projects/` with this front matter flag, nothing gets
moved.

Resource files carry no `status` field — absence of the field is the
default/current state. Don't add `status: active`.

Once adopted, use this two-part test for new content:

1. Does it have a **specific goal** (a concrete deliverable or finish line)?
2. Does it have an **active timeframe** (something is happening on it now or
   soon)?

If yes to both → `kb/projects/`. If no → `kb/resources/`.

The common misclassification: a topic label ("large format photography",
"home networking") looks like a Resource, but if you're actively building or
deciding something specific within it ("build 4x5 large format kit", "set up
home mesh network"), that's a Project. Ask what you're *doing*, not what the
topic *is*.

Use `tools/kb_search.py` to find the best existing home before creating a new
file (see Content conventions below).

When cross-checking coverage (above), a hit with `status: archived` in its
front matter may be superseded — read it to confirm before treating it as
current coverage.

To adopt this split for an existing flat `kb/` (sorting already-present files
into Projects vs. Resources), see `prompts/organize-kb-files.md`. This is a
structural file-placement task, not the `inputs/` triage pipeline — do not
run `prompts/process-input-files.md` against existing `kb/` files.

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
`kb/`, run both steps in order:

```
.venv/bin/python tools/kb_index.py --incremental
.venv/bin/python tools/connections.py
```

Both must run — the index feeds the connections DB. Running index alone
leaves the graph edges stale. Batch all edits first, then run both once.

`--incremental` compares each `kb/**/*.md` file's mtime against `.kb-index/meta.json`,
re-chunks/embeds only new or changed files, and removes chunks for files
deleted from `kb/`. This is much cheaper than a full rebuild on this
CPU-only host and is the normal day-to-day command. It falls back to a full
rebuild automatically if no index (or a pre-incremental `meta.json`) exists
yet.

Use a plain `tools/kb_index.py` (no flag) for a full rebuild — e.g. after
changing `config.yaml` (chunk size, embedding model) or if the index is
suspected to be out of sync with `kb/`.

`kb_search.py` prints a `[stale index]` warning (to stderr) if any `kb/**/*.md`
file has been modified more recently than the last index build — if you see
that warning mid-session, mention it and suggest reindexing before relying
further on search results.

## connections.db

`connections.db` (SQLite, repo root) stores per-file semantic similarity
edges used by the Flask graph. It is built from ChromaDB embeddings by
`tools/connections.py` and is not edited directly.

Do **not** write `## See Also` sections in `kb/` files — graph edges are
computed automatically from the index. To inspect which files are related
to a given file:

```
.venv/bin/python tools/connections.py --show <filename>
```

This prints the top-N nearest neighbors and their similarity scores.

## Config

`config.yaml` controls the embedding model, chunk size/overlap, KB root,
index location, and connections settings (`connections_top_n`,
`connections_min_score`). No hardcoded paths elsewhere.

Two embedding model options are documented in `config.yaml` comments:
`bge-small-en-v1.5` (default, fast, ~130MB) and `bge-large-en-v1.5` (best
quality, slow, ~1.3GB). Changing the model requires deleting `.kb-index/`
and running a full rebuild.

Incremental reindex re-embeds the entire file for any file that changed —
not just the edited sections. On CPU-only hardware this makes the large model
painful for routine editing workflows. Prefer `bge-small` unless search quality
is a confirmed bottleneck.

## Content conventions

See `CONTENT-STYLE.md` for register, filename, bullet/blockquote, and
file-size conventions for content in `kb/`.
