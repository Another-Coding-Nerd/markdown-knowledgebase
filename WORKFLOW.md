# Typical Workflow

The core use case: you collect things worth knowing — blog posts, YouTube
transcripts, conference talks, short papers, tip-and-trick threads, interview
notes — and you want the useful knowledge extracted, checked against what you
already know, and stored without duplication.

This system handles that. Here's what it looks like in practice.

## Day-to-day ingestion

**1. Drop the source file into `inputs/`.**

Save or paste the content as a `.txt` or `.md` file. For HTML pages,
`tools/html_to_text.py` strips the markup. For raw `.txt` files with poor line
wrapping, `inputs/fmt_text.sh` reflows to 100 columns.

**2. Tell the agent which prompt to run.**

| Source type | Command |
|-------------|---------|
| Blog post, article, paper, structured notes | `"Process inputs using prompts/process-input-files.md"` |
| YouTube transcript, interview digest, dense bullet notes | `"Process inputs using prompts/process-input-files-dense.md"` |

The dense variant is designed for content that's one claim per sentence with
no headings — transcripts and summaries in particular.

**3. The agent works through the file systematically:**

- Enumerates every analytically distinct claim or point — full inventory
  before evaluating anything
- Checks each point against `about.md` to filter off-scope items
- Runs a semantic search against the existing KB for each in-scope point,
  scoring it as new, partial overlap, or already covered
- Presents the full inventory — every point, its status, and the proposed
  target file and section — and waits for your approval
- Writes nothing until you confirm

**4. After ingestion, reindex:**

```bash
tools/index --incremental
tools/connections
```

Both steps every time — the connections graph feeds off the index.

## Searching what you've built

```bash
tools/search "query"
```

Pass multiple quoted queries in one call to compare results across topics.
Or ask the agent — it uses the same semantic search internally and can
synthesize an answer from the relevant KB chunks.

## Browsing the KB in a browser

```bash
tools/serve           # default port
tools/serve --port 8080
```

Starts the Flask UI at `http://localhost:5000` (or the port you specify).
Features: file list, rendered markdown per file, semantic graph (nodes =
files, edges = similarity from `connections.db`), and an LLM-backed
question-answer interface over the indexed KB. Requires the index and
connections DB to be current before launching.

## Inspecting graph edges

```bash
tools/connections --show <filename>
```

Prints the top-N nearest neighbors for a file and their similarity scores —
useful for spotting which files are semantically close before reorganizing or
merging content.

## Diagnosing section length

```bash
tools/stats kb/<file>.md
tools/stats kb/<file>.md --short 4 --long 25
```

Flags SHORT (≤N lines) and LONG (≥N lines) leaf sections — sections with no
child headings. Use it when reviewing a file for sections that may need
expansion or trimming. Thresholds default to 4/25 and are adjustable.

## Periodic quality review

```
"Review kb/ using prompts/process-knowledgebase-files.md"
```

Checks consistency, register, redundancy, and structure across existing KB
files. Run when the KB has grown enough that drift between files is likely.

## Reorganizing into Projects / Resources

```
"Organize kb/ files using prompts/organize-kb-files.md"
```

Sorts existing flat `kb/` files into `kb/projects/` (bounded efforts with a
finish line) and `kb/resources/` (reference material). See `AGENTS.md` for
the two-part test (specific goal + active timeframe = project; otherwise
resource).

## What you end up with

A KB where every item was deliberately placed, cross-checked on the way in,
and is semantically searchable without reading the whole thing. The agent does
the triage; you make the calls.
