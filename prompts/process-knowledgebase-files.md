Review each `.md` file in `kb/` against these criteria and present
findings. Process files one at a time. For each file: report findings, make
specific recommendations, ask for approval before applying any changes.

## Review Criteria

### 1. Title and filename accuracy
Two checks: **(a)** Does the filename reflect the topic without embedding a
point count? (e.g., prefer `traps-men-fall-into.md` over
`9-traps-men-fall-into.md` — see `CONTENT-STYLE.md`). **(b)** Do the actual
items match any number in the title? Flag mismatches. If no count is in the
title, note that.

### 2. Single topic or multiple?
Does the file contain clearly distinct topics that would be better as
separate files? Do not cross-reference other files — judge on the content of
this file alone.

### 3. Internal consistency
Do any entries within the same file contradict each other? Does the framing
of one section undermine another? Look for logical conflicts, not different
perspectives.

### 4. Parallel structure
All entries in a numbered list should follow the same format. Flag entries
that switch between paragraph style and sub-bullet style, entries with
drastically different length/depth, or entries missing bold headers when
others have them. When recommending length normalization, identify specific
content that would be removed and assess whether it is redundant phrasing or
a distinct concept. Only recommend cutting redundant phrasing — distinct
ideas should be condensed, not dropped.

### 5. Redundancy
Do any entries within this file repeat or overlap the same concept using
different words? Do not cross-reference other files.

**Block quotes**: Check each block quote (epigraphs, inline callouts, footer
aphorisms) against the body text, per the blockquote policy in
`CONTENT-STYLE.md`. Three cases: **(a) Verbatim or near-verbatim repeat** of
body text → remove. **(b) Paraphrase of body text with a distinct phrase or
framing** → absorb the distinct element into the nearest relevant body
paragraph, then remove the quote. **(c) Standalone aphorism with no body
equivalent** → keep if it adds something the prose doesn't; remove if it
merely summarizes what was just said.

### 6. Seams
Can you spot where supplemented content was stitched in from a different
source? Do transitions between sections feel natural, or does added content
sit awkwardly adjacent to original material? Flag abrupt shifts in structure
or framing mid-file.

A common pattern in piecemeal files: the original section is
observational/analytical and a later addition is prescriptive/tactical
(numbered scripts, "say this," "do this"). Flag register mismatches
separately from tone shifts — the fix is to rewrite the add-on in the
matching register while preserving all underlying ideas, not to remove it.

### 7. Tone and register consistency
Target register is defined in `CONTENT-STYLE.md`. Does the voice stay
consistent with that throughout? Watch for shifts in formality, directness,
aggressiveness, or perspective. Supplemented sections often carry a slightly
different tone than the original.

Also watch for register shifts: a section that moves from analytical
observation to direct instruction (or vice versa) without transition.
Register is distinct from tone — a file can be consistently firm in tone but
shift between describing what happens and prescribing what to do.

### 8. Incomplete entries
Any vague language, placeholder text, TODO markers, ideas that trail off
unfinished, or unsupported claims? Flag anything that reads like a draft, not
a final entry.

### 9. Clarity
Can someone unfamiliar with the source material understand each entry
without needing context from other files? Flag jargon, unexplained
references, or entries that assume the reader already agrees with a premise.

## Output format
For each file, present findings grouped by severity:

**Critical** (breaks readability or accuracy): title count mismatch,
contradictory entries, major structural breaks
**Moderate** (reduces quality): non-parallel structure, noticeable seams,
tone shifts, significant but fixable redundancy
**Minor** (polish): vague language, minor consistency issues

For each finding, provide:
- What the problem is (with specific quotes/examples)
- Why it matters
- Your recommended fix
- Ask for approval before applying

After all findings, note which criteria surfaced the most problems and
anything the file does well structurally.
