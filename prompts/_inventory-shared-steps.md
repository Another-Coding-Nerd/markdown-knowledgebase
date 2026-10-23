# Shared Inventory Steps

Included by `process-input-files.md` and `process-input-files-dense.md`.
Read this file immediately after completing step 2b in whichever prompt
you are running, then continue with steps c–m below.

## Step 2 (continued)

   c. Cross-check each inventory item against the existing KB via
      `tools/kb_search.py "<point>"` — see `AGENTS.md` for the scoring
      guidance. Do not read every file in `kb/`. **Before running the search**,
      reduce each candidate point to a single plain declarative sentence stating
      the mechanism — stripped of examples, metaphors, delivery framing, and the
      source's own vocabulary. Search on that sentence, not on the source's
      phrasing. The verdict is on the mechanism, not the packaging.
   d. For each item, determine: already covered / partially covered
      (formulation worth adding) / genuinely new. Where the cross-check
      surfaces a related section, apply a fact-vs-wording test before
      deciding covered vs. partial: is this item the *same fact, mechanism,
      example, or figure* as what's already there — or a *different* one (a
      new statistic, a named mechanism not previously discussed, a
      contradicting claim, an example illustrating a different facet)? Same
      mechanism → **covered**, skip it even if the source's phrasing was
      fresh or vivid. Different mechanism → **partial** or **new**, regardless
      of how crude or dramatic the source's register was — a new mechanism
      that arrives in poor or sensationalist packaging still counts as new once
      stripped (see step 2i for how to handle the reframing). The test is
      symmetric: direction matters more than delivery.

      **The test is mechanism novelty, not citation presence.** Uncited
      behavioral observations can be genuinely new if the mechanism is not
      assembled anywhere in the KB. A fresh framing or vivid restatement of a
      covered mechanism is **covered** — not new. A low search score is weak
      evidence of absence (vocabulary mismatch between source and KB), not a
      license to add.

      **To mark an item new or partial, state the delta.** In one sentence,
      name the specific mechanism, fact, or figure it adds that is not in the
      named neighbor file/section. If you cannot articulate that delta after a
      bounded read, classify it as **covered** — skip it. This applies to both
      cited and uncited items.

      **Resolve before presenting.** Do not put "possibly new," "probably new,"
      or "uncertain" in the inventory table — those hedge a step you haven't
      taken yet. If the score is ambiguous (~0.6–0.75), read the snippet; if
      the snippet is still insufficient, read the specific section. Resolve to
      covered / partial / new / off-scope first. (Step 2l's "flag anything
      uncertain" applies to items that remain genuinely ambiguous *after* that
      read — a small set that goes to the user with your lean; it does not
      license skipping the read.)
   e. **Scope filter** — for each item classified as new or partial, apply
      the scope definition from `about.md` as a one-sentence test. Items
      that are authentic but outside scope are marked **off-scope** in the
      inventory table. Off-scope items are listed, not silently dropped —
      user confirms before anything is excluded.
   f. Quality check: if the source claims a specific count (e.g., "5
      reasons", "3 types", "10 signs"), verify the inventory found that many
      distinct items. If there's a mismatch, flag it.
   g. Off-topic content: if the entire file falls outside this KB's scope,
      auto-skip and move it to `inputs/off-topic/`. Note this in the summary.
   h. Mostly-overlapping content with unique elements: the unique material
      is the yield — check whether it can supplement an existing file rather
      than creating a new file or skipping entirely.
   i. Bad-frame content: if the source uses any frame that wraps or distorts
      its underlying content — prescriptive/coaching voice, motivational
      framing, pop-psych register, reductive or crude argument — assess
      whether the frame can be stripped while preserving analytically sound
      content embedded within it. Do not route bad-frame content to 2g
      (off-topic) before applying this test. Test: does the information stand
      independently of the frame? If yes, treat the salvageable content as a
      targeted supplement to an existing file and note the reframing in the
      recommendation.
   j. Duplicate content: auto-skip, move to `inputs/processed/`, note in the
      summary.
   k. New content: if this KB has adopted the Projects/Resources split (see
      `AGENTS.md` — i.e. `kb/projects/` is in use), first apply that test:
      does it have a deliverable or finish line? If so, it belongs in
      `kb/projects/`; otherwise file it as a resource by topic in
      `kb/resources/`. If this KB is flat, skip this and file by topic as
      usual. Then decide whether it fits as a new file or as an addition to
      an existing file. If the source uses named-anecdote framing (e.g.
      "Marcus told me...", "let's call her Anna"), absorb the underlying
      ideas into the nearest analytical section and drop the named frame.
   l. **Present the full inventory** — list every item with: status (covered
      / partial / new / off-scope), proposed target file + section, and a
      one-line rationale. For **partial** items, name the specific detail
      (fact, mechanism, example, figure) being added. Do not summarize or
      cherry-pick. Flag anything uncertain.
   m. **Wait for confirmation** — do not write or edit any `kb/` files until
      the user approves the scope.

## Steps 3–6

3. After processing, move the source file(s) to `inputs/processed/` (or
   `inputs/off-topic/` if off-topic). If the source was split by
   `inputs/fmt_text.sh` into `basename-part-001.txt`, `basename-part-002.txt`,
   etc., treat all parts as one logical unit — process them together and move
   all part files at once when done.
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
