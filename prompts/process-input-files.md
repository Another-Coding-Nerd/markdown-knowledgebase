# Process Input Files

Process new source files in `inputs/` into the knowledgebase (`kb/`).

## Scope

<!-- Define this KB's topical scope here so step 2f (off-topic detection) has
a concrete test, e.g. "Dating, relationships, female psychology, and male
strategy." -->

## Workflow

1. Check `inputs/` for any files not already in `inputs/processed/` or
   `inputs/off-topic/`. (`inputs/fmt_text.sh` can be run first to reflow raw
   `.txt` files to 100 columns.)
2. For each file found:
   a. Read it fully.
   b. **Full inventory first** — enumerate every analytically distinct
      point/claim in the file before evaluating any of them for placement.
      Do not evaluate, filter, or write KB content until the inventory is
      complete. The failure mode to prevent: identifying the two most
      obvious points and treating them as the full yield.
   c. Cross-check each inventory item against the existing KB via
      `tools/kb_search.py "<point>"` — see `CLAUDE.md` for the scoring
      guidance. Do not read every file in `kb/`.
   d. For each item, determine: already covered / partially covered
      (formulation worth adding) / genuinely new.
   e. Quality check: if the source claims a specific count (e.g., "5
      reasons", "3 types", "10 signs"), verify the inventory found that many
      distinct items. If there's a mismatch, flag it.
   f. Off-topic content: if the file falls outside this KB's scope (defined
      above), auto-skip and move it to `inputs/off-topic/`. Note this in the
      summary.
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
   j. New content: decide whether it fits as a new file or as an addition to
      an existing file. If the source uses named-anecdote framing (e.g.
      "Marcus told me...", "let's call her Anna"), absorb the underlying
      ideas into the nearest analytical section and drop the named frame.
   k. **Present the full inventory** — list every item with: status (covered
      / partial / new), proposed target file + section, and a one-line
      rationale. Do not summarize or cherry-pick. Flag anything uncertain.
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
6. After a batch of edits to `kb/`, reindex per `CLAUDE.md`.

## Conventions

Register, filenames, bullets/prose, blockquotes, file size/splitting, and
"See Also" conventions for anything written or edited in this workflow are
in `CONTENT-STYLE.md`.
