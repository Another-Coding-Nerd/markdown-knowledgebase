## Notes: triage shortcuts tried at scale (don't repeat)

When a large batch (190 files) arrived at a point where the KB was already
near-saturated, we tried to find a cheap pre-scan to avoid full per-file
processing on files likely already covered. Two approaches were tried and
ruled out; the conclusion is there's no shortcut around the full per-file
inventory in `prompts/process-input-files.md` — only the batching/approval
granularity can be tuned, not the depth.

1. **Embedding-only pre-scan (comparing raw transcripts directly against
   `kb/*.md` via cosine similarity, no LLM paraphrase step).** Tried with an
   external tool (`quick_compare/compare.py`) repointed at `kb/*.md`.
   Result: 0 of 190 files had a `kb/*.md` file as their top semantic match —
   every file matched another raw transcript instead, regardless of actual
   topical overlap. Cause: a register/surface-form gap. A conversational
   transcript chunk's nearest neighbor in embedding space is always another
   transcript chunk (same phrasing, "sign one/two..." scaffolding); analytical
   KB prose never gets close. This is not a threshold-tuning problem — don't
   retry pure-embedding pre-scanning on raw source text against this KB.

2. **Cheap LLM triage tier (Haiku paraphrases each file's claims into
   analytical register, then runs `kb_search.py` per claim, returning only a
   covered/ambiguous verdict — skipping inventory write-up/placement).**
   Validated against manual full-workflow ground truth on 10 sample files:
   got 7/10 right, but **3 of the 7 files it called "covered" actually had
   real partial/new content** (a ~43% false-covered rate on the covered
   bucket). The misses were specific secondary facts/examples that differ
   from the KB's existing treatment of the same general topic — exactly the
   kind of buried point step `b` of the input-files workflow warns about
   losing. A per-claim similarity threshold can't fix this; the paraphrase
   step itself doesn't reliably surface secondary claims at the granularity
   needed. Don't trust a cheap/capped LLM triage tier to gate bulk-skip
   decisions — full inventory depth is required either way.

**What actually worked**: batching the *user-approval* step (not the
per-file depth) into groups of ~8–10 files — full inventory + cross-check
per file, one consolidated inventory presented per batch, one reindex after
writing each batch's approved additions. This is the approach in use for
the remaining files in the current 190-file batch.

## Notes: dedup workflow improvements — what was tried, what was deferred

Two improvements to `prompts/process-input-files.md` were implemented
(commit `1e8b6eb`, validated against a 9-file real batch):

- **Section-by-section inventory** (step b): one pass per H2/H3 section or
  ~100-line segment instead of whole-document at once.
- **Fact-vs-wording bar** (step d): same fact reworded → covered; different
  fact on same topic → partial. Keeps the 3-way new/partial/covered
  vocabulary rather than a heavier 5-way scheme.

Three further items were considered and deferred — don't revisit without
new data:

1. **Calibration step + provisional score bands in AGENTS.md** — judged too
   heavyweight for a generic template. The existing ~0.75/~0.6 bands are
   labelled as starting points in AGENTS.md. Revisit only if score bands
   prove unreliable in a specific deployed KB.

2. **5-way replace/supplement/keep-both/skip vocabulary** — superseded by
   the lighter fact-vs-wording bar above. The 3-way vocabulary with the
   fact/wording distinction handles the same problem without adding a new
   status tier.

3. **Addendum B (calibration as dated, topic-scoped snapshot)** — depends
   on item 1; deferred with it.

**Why `kb_pipeline.sh`'s similarity thresholds (0.85/0.95) don't transfer:**
Those thresholds are calibrated for `mxbai-embed-large` at per-line
granularity, comparing point-embedding vs. point-embedding. This KB uses
`bge-small-en-v1.5` at ~450-token section granularity, comparing a
point's embedding against a mixed-content section embedding. The section
embedding is pulled toward the centroid of everything in that section
("dilution effect"), so the same underlying answer ("is this covered?")
produces different scores depending on section length and topic density.
No fixed cutoff cleanly separates covered/new — don't port the raw numbers.
