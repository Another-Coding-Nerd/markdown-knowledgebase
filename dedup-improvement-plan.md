# Plan: Improve markdown-KB dedup, informed by kb_pipeline's thresholds

## Status (as of 2026-06-15)

- **#3 (section-by-section inventory)** — **Implemented**, commit `1e8b6eb`
  (`prompts/process-input-files.md` step b).
- **Addendum A (fact-vs-wording bar)** — **Implemented**, commit `1e8b6eb`,
  folded into the existing 3-way `new/partial/covered` vocabulary
  (`prompts/process-input-files.md` step d) rather than the 5-way scheme
  below. Validated against a 9-file real batch.
- **#1 (calibration step + provisional score bands in AGENTS.md)** —
  **Deferred**. Judged too heavyweight for a generic template; revisit if
  this KB's score bands prove unreliable in practice.
- **#2 (5-way replace/supplement/keep-both/skip vocabulary)** —
  **Deferred/rejected**. Superseded by the lighter fact-vs-wording bar
  (Addendum A) within the existing 3-way vocabulary.
- **Addendum B (calibration as dated, topic-scoped snapshot)** —
  **Deferred**, depends on #1.

## Context

This KB's input-processing workflow (`prompts/process-input-files.md` +
`AGENTS.md`) was compared against a separate scripted pipeline
(`kb_pipeline.sh` in `/home/ubuntu/source/knowledgebase`) that achieves ~81%
retention of source points into its curated "_short" KB. Two structural gaps
in this KB's workflow were identified as likely causes of lower retention:

1. The inventory step (`process-input-files.md` step 2b) reads a whole input
   file in one pass, which is more prone to missing subtle/secondary points
   than per-segment exhaustive extraction.
2. The dedup step (step 2d) fully discards any point classified "covered"
   (topically overlaps existing KB content), even if that point carries a
   specific detail (number, date, example) the existing KB entry lacks.

A follow-up question was whether `kb_pipeline.sh`'s similarity thresholds —
specifically `kb_sync_file_embed.rb`'s two-tier scheme (similarity ≥0.85 =
"omit/covered"; ≥0.95 = "quality_review", which prompts a human to pick
replace/keep-existing/keep-both/delete) — could inform this KB's dedup.

**Answer**: the raw numbers (0.81/0.85/0.95) don't transfer — they're
calibrated for `mxbai-embed-large` at per-line granularity against an
OpenWebUI/ChromaDB backend, whereas this KB uses `bge-small-en-v1.5` at
~450-token section granularity with an empty, uncalibrated index. There's also
a deeper reason scores here can't be read the same way at all: the other
pipeline's thresholds compare a point's embedding against another point's
embedding — two short, single-claim objects of comparable size. Here, a
point's embedding is compared against a ~450-token section's embedding — a
much larger, mixed-content object. Even when the section fully covers the
point, the section embedding is pulled toward the centroid of everything else
in that section, "diluting" the score by an amount that varies with the
section's length and topic density. So the same underlying answer ("is this
covered?") can produce different scores depending on how much else is in the
matched section — no fixed cutoff can fully separate covered/new on score
alone. But the
**structural pattern** transfers: a two-tier judgment (likely-covered vs.
needs-reconciliation) where the upper tier triggers an explicit
replace/supplement/keep-both/skip decision instead of a flat discard. Here,
"needs reconciliation" isn't gated by a similarity number (there's no
cheap-vs-expensive-review distinction — Claude reads everything) but by
Claude actually reading the matched KB section and checking whether the
*specific detail* is present, not just the general topic.

This plan makes three prompt/instruction-only edits (no tooling changes) to
close both gaps, reusing the other pipeline's reconciliation vocabulary
(replace / supplement / keep-both / skip) in place of the current flat
new/partial/covered.

## Changes

All edits are to markdown files in this repo. No changes to
`tools/kb_search.py`, `tools/kb_index.py`, `tools/chunking.py`, or
`config.yaml` — the existing `file` + `heading` metadata returned by
`kb_search.py` is sufficient for Claude to `Read` the full matched section
directly (more complete than the 300-char snippet or a single ~450-token
chunk).

### 1. `AGENTS.md` — relabel score bands as provisional + add calibration step

Replace the scoring-guidance bullet list (current lines ~27-34) to:
- Explicitly label the ~0.75+ / ~0.6-0.75 / <0.6 bands as **provisional,
  uncalibrated** (the index is currently empty — 0 files, 0 chunks).
- Add a one-time **calibration step**: after the first `kb_index.py` run on
  real content (~5-10 files / 30+ chunks), run `kb_search.py` on ~10 known-
  covered points and ~10 known-new points, observe the score separation, and
  adjust the bands if needed. Note the calibration date/chunk-count. Re-run
  if `config.yaml`'s embedding model or chunk size changes (piggybacking on
  the existing full-rebuild trigger for that event).
- For the ~0.75+ band, add: don't stop at the score — Read the matched
  section and run the detail-check decision tree (see #2 below).

Also update the "Processing new input files" summary (current lines ~98-105),
step 3, to use the new status vocabulary: `new / supplement / replace /
keep-both / covered` (was `new / partial / covered`).

### 2. `prompts/process-input-files.md` — detail-check decision tree

Replace step **d** (current lines ~31-32, flat "covered / partial / new")
with a decision tree:

- **Top hit < ~0.6**: classify **new**, no further check. Note: per the
  dilution effect above, this floor is the riskier edge — a genuinely-covered
  point can get diluted below it if the matching section is long/dense, which
  silently produces a duplicate rather than a wasted read. Treat ~0.6 as a
  starting point that errs toward over-reading, not a calibrated safe cutoff;
  if in doubt for a point that's clearly within this KB's core topic scope, a
  quick `Read` costs little.
- **Top hit ≥ ~0.6 with topically matching heading**: `Read` the matched
  section in full (via the hit's `file` + `heading` metadata — do not rely
  on the snippet alone). Check whether the existing section already contains
  the *specific detail* from the inventory item (number, date, named
  example, mechanism, formulation), not just the same general topic. Then
  classify:
  - **covered** — specific detail already present, essentially equivalent.
    Skip; note which file/section covers it.
  - **supplement** — general point covered, but this item adds a specific
    detail the existing section lacks. Recommend integrating that detail
    into the existing section.
  - **replace** — this item's formulation/detail supersedes what's there
    (more precise/current/better example). Recommend replacing that part of
    the existing section.
  - **keep-both** — both formulations are independently useful (e.g. two
    valid examples/framings for different contexts). Recommend adding
    alongside the existing content, with a note distinguishing when each
    applies.
  - **new** — top hit was a false positive (topical adjacency only); treat
    as new content per step (j).

Update step **g** (mostly-overlapping content) to reference **supplement** /
**keep-both** from the new tree.

Update step **i** (duplicate content) to clarify dedup is per inventory item:
items classified **covered** are skipped individually; the source *file*
moves to `inputs/processed/` once all its items have been triaged (same as
today, just made explicit that this is per-item then per-file).

Update step **k** (present full inventory) to use the new status vocabulary
(`new / supplement / replace / keep-both / covered`) and require naming the
specific detail being added/changed for supplement/replace/keep-both items.

### 3. `prompts/process-input-files.md` — section-by-section inventory (step 2b)

Replace step **b** ("Full inventory first") to require working
section-by-section rather than whole-document:
- If the file has H1/H2/H3 headings: one inventory pass per H2/H3 section
  (matches the index's own chunking unit).
- If headingless (e.g. raw `.txt` reflowed by `inputs/fmt_text.sh`): split
  into ~100-line segments (matching the other pipeline's `smart_split`
  granularity) or natural paragraph breaks if shorter.

Keep the existing "failure mode to prevent" framing, extended to note that
section/segment-by-segment processing makes it harder to skip subtle points
buried in a section whose headline point was already captured.

## Sequencing

All three changes are independent prompt edits — can be made in any order or
together in one pass. The calibration step in #1 is a documented future
action (triggered by the first real `kb_index.py` run), not a blocker for
these edits.

## Addendum: two follow-on gaps for a generic-ish KB system

The decision tree in #2 fixes the main problem (informational loss from flat
`covered → skip`), but discussion surfaced two further gaps that matter for a
KB meant to be reusable across topic domains, not tuned for one corpus:

### A. "Meaningfully new" bar in step 2d's detail-check

As written, step 2d's detail-check ("does the existing section already
contain this specific detail?") has no floor for what counts as a *different*
detail vs. a *reworded* one. Real text almost never repeats a point in
identical form — a different year for the same statistic, a synonym for the
same mechanism, a rephrased example illustrating the same point. Without a
bar, the tree's natural tendency on a maturing KB is to call most
topically-adjacent points `supplement` (different wording = "new detail"),
turning `supplement` into the dumping ground that flat `covered` used to be
— except now on the "keep and integrate" side, causing files to absorb a
steady stream of marginal variants and hit `CONTENT-STYLE.md`'s split
threshold faster than warranted.

**Add to step 2d**, before the covered/supplement/replace/keep-both branch: a
threshold question — is this a *different fact, mechanism, example, or
figure*, or the *same one in different words*? Give the agent two or three
domain-neutral illustrative pairs so it generalizes correctly regardless of
the KB's topic:

- Same fact, reworded → **covered** (a different phrasing/year/synonym for
  the same underlying point, e.g. "costs rose 12% in 2023" vs. "prices were
  up about a tenth in 2023" — same claim, not a new data point).
- Different fact about the same topic → **supplement** (a new statistic, a
  named mechanism not previously discussed, a contradicting claim, an
  example illustrating a different facet of the same principle).

This keeps the bar generic — it's about fact-vs-wording, not about any
specific subject matter — so it applies the same way whether the KB covers
software architecture, cooking, or anything else.

### B. Calibration as a dated, topic-scoped snapshot — not a one-time constant

The AGENTS.md calibration step (in #1) is framed as a single event after the
first real index build. But score distributions for "same topic, different
detail" vs. "true duplicate" likely tighten as a topic area accumulates more
chunks — a calibration done when a topic has 2 files may not hold once it has
10. For a KB that's meant to grow indefinitely across many topic areas, a
single global calibration constant will silently go stale in whichever areas
grow the most, without any signal that it's happened.

**Revise the AGENTS.md calibration note** to frame it as a snapshot, not a
constant:
- Record the calibration alongside the chunk count it was taken against
  (already planned), but explicitly note that the bands are *most reliable
  for topic areas of similar density* to what was calibrated, and may need a
  quick spot-check in areas that have grown substantially since.
- Fold the spot-check into the existing periodic review
  (`prompts/process-knowledgebase-files.md`): when reviewing a topic area
  that has grown noticeably since the bands were last checked, run 2-3 known
  covered/new pairs from *that area* through `kb_search.py` and confirm the
  bands still separate them. If not, note a per-area adjustment rather than
  changing the global default.

This keeps the mechanism lightweight (no new tooling, no scheduled tasks) —
it just rides along with review work that already happens, and avoids
assuming one global number is valid forever across a KB that may end up
spanning very differently-sized topic clusters.

## Verification

This is a documentation/prompt change with no executable code — verification
is by review:
1. Read back the edited `AGENTS.md` and `prompts/process-input-files.md` to
   confirm the decision tree, status vocabulary, and section-by-section
   inventory instructions are internally consistent (vocabulary matches
   across both files; step references — g, i, k — still make sense given the
   new step d).
2. Functional test (after some real content exists in `kb/` and is indexed):
   run through `process-input-files.md` on a real input file and confirm the
   presented inventory uses the new five-way classification with named
   specific-detail rationales for supplement/replace/keep-both items, and
   that the calibration note in AGENTS.md gets filled in with real
   score-band observations.
