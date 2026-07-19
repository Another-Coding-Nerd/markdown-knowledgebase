# Process Input Files — Dense Format

Process dense input files into the knowledgebase (`kb/`). Use this variant
when the source is a compressed interview summary, transcript digest, or
de-duplicated notes where each sentence carries a distinct claim — typically
headingless, one long block of text, ~1 point per sentence.

For normal prose, structured articles, or files with headings, use
`prompts/process-input-files.md` instead.

This workflow processes files in `inputs/` only. To sort existing
`kb/**/*.md` files into `kb/projects/` vs `kb/resources/` (the
Projects/Resources split), use `prompts/organize-kb-files.md` instead — do
not run this inventory/dedup workflow against `kb/` content.

## Scope

This KB's scope is defined in `about.md` at the repo root. Read it before
beginning inventory. Use the scope description and out-of-scope list as the
test in steps 2f and 2d2.

## Workflow

1. Check `inputs/` for any files not already in `inputs/processed/` or
   `inputs/off-topic/`. (`inputs/fmt_text.sh` can be run first to reflow raw
   `.txt` files to 100 columns.)
   a. If any `.html` files are present, or any `.txt` files contain pasted
      HTML markup rather than plain text, convert them to clean text first:
      `python3 tools/html_to_text.py --write <file>` (the script also
      detects and cleans HTML pasted into a `.txt` file). It overwrites
      `.txt` files in place and converts `.html` files to a `.txt` of the
      same name, deleting the original. Then continue with step 2 as usual.
2. For each file found:
   a. Read it fully.
   b. **Full inventory first — sentence-level granularity** — dense files
      have no headings or paragraph breaks to segment by; treat each sentence
      as a candidate inventory item. Work through the file in passes of
      ~20 sentences at a time. Within each pass, enumerate every distinct
      claim before evaluating any of them. After completing all passes,
      consolidate claims that are genuinely the same point stated twice into
      a single entry; do not consolidate points that are merely on the same
      topic. Do not evaluate, filter, or write KB content until the full
      inventory across all passes is complete.

      The failure mode to prevent in dense files: conflating two distinct
      claims because they appear adjacent and share a subject. A sentence
      that says "X is unpredictable" and the next that says "X masquerades
      as Y early on" are two separate inventory items, not one. Default to
      more entries, not fewer — deduplication happens at the consolidation
      step, not the enumeration step.
   c. Cross-check each inventory item against the existing KB via
      `tools/kb_search.py "<point>"` — see `AGENTS.md` for the scoring
      guidance. Do not read every file in `kb/`.
   d. For each item, determine: already covered / partially covered
      (formulation worth adding) / genuinely new. Where the cross-check
      surfaces a related section, apply a fact-vs-wording test before
      deciding covered vs. partial: is this item the *same fact, mechanism,
      example, or figure* as what's already there, just reworded (different
      synonym, year, or phrasing for the same claim) — or a *different* one
      (a new statistic, a named mechanism not previously discussed, a
      contradicting claim, an example illustrating a different facet)? Same
      fact reworded → **covered**, skip it even if the wording differs.
      Different fact on the same topic → **partial**, naming the specific
      detail to add.
   d2. **Scope filter** — for each item classified as new or partial, apply
       the scope definition from `about.md` as a one-sentence test. Items
       that are authentic but outside scope are marked **off-scope** in the
       inventory table. Off-scope items are listed, not silently dropped —
       user confirms before anything is excluded.
   e. Quality check: if the source claims a specific count (e.g., "5
      reasons", "3 types", "10 signs"), verify the inventory found that many
      distinct items. If there's a mismatch, flag it.
   f. Off-topic content: if the entire file falls outside this KB's scope,
      auto-skip and move it to `inputs/off-topic/`. Note this in the summary.
   g. Mostly-overlapping content with unique elements: the unique material
      is the yield — check whether it can supplement an existing file rather
      than creating a new file or skipping entirely.
   h. Bad-frame content: if the source's core argument is reductive, crude,
      or off-register, assess whether the frame can be stripped while
      preserving analytically sound content embedded within it. Test: does
      the information stand independently of the frame? If yes, treat the
      salvageable content as a targeted supplement to an existing file and
      note the reframing in the recommendation.
   i. Duplicate content: auto-skip, move to `inputs/processed/`, note in the
      summary.
   j. New content: if this KB has adopted the Projects/Resources split (see
      `AGENTS.md` — i.e. `kb/projects/` is in use), first apply that test:
      does it have a deliverable or finish line? If so, it belongs in
      `kb/projects/`; otherwise file it as a resource by topic in
      `kb/resources/`. If this KB is flat, skip this and file by topic as
      usual. Then decide whether it fits as a new file or as an addition to
      an existing file. If the source uses named-anecdote framing (e.g.
      "Marcus told me...", "let's call her Anna"), absorb the underlying
      ideas into the nearest analytical section and drop the named frame.
   k. **Present the full inventory** — list every item with: status (covered
      / partial / new / off-scope), proposed target file + section, and a
      one-line rationale. For **partial** items, name the specific detail
      (fact, mechanism, example, figure) being added. Do not summarize or
      cherry-pick. Flag anything uncertain.
   l. **Wait for confirmation** — do not write or edit any `kb/` files until
      the user approves the scope.
3. After processing, move the source file to `inputs/processed/` (or
   `inputs/off-topic/` if off-topic).
4. After any new file is created or an existing file is renamed, update any
   navigation/index files this KB maintains (e.g. a topic listing in
   `README.md`, a glossary, a situational index) that reference the changed
   content.
5. At the end, provide a summary of what was created, what was skipped as
   dupes, and what was moved to `inputs/off-topic/`.
6. After a batch of edits to `kb/`, reindex per `AGENTS.md`.

## Conventions

Register, filenames, bullets/prose, blockquotes, and file size/splitting
conventions for anything written or edited in this workflow are in
`CONTENT-STYLE.md`.
