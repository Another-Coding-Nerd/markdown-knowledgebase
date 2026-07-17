# Content Style Guide (template)

This file holds content-authoring conventions for `kb/` — separate from
`AGENTS.md`, which covers the search/reindex tooling and workflow. Edit or
delete sections to fit your KB's domain; nothing here is required by the
tooling itself.

## Register

Pick one voice and apply it consistently across `kb/`:

- **Third-person observational** (default): describe patterns, mechanisms,
  and behaviors in the third person ("a developer," "teams that," "the
  pattern"). No second-person instruction ("you should," "you must"), no
  prescriptive scripts or numbered action steps.
- **Hedging**: for claims broader than the evidence, use "tends to," "often,"
  or "in most cases" — but don't hedge every sentence, only where the claim
  is genuinely contested or general.

## Filenames

- Kebab-case, no counts (`signs-of-x.md`, not `9-signs-of-x.md`) — counts
  drift as content changes.

## Bullets vs. Prose

Prose is the default. Bullets are for genuine lists: discrete categories,
enumerated stages, schemas. Convert or remove bullet clusters that just
restate what the surrounding prose already says.

## Blockquotes

At most one per file. Keep a blockquote only if it adds something the prose
doesn't — a memorable distillation, a quote, vivid framing. Remove ones that
just restate surrounding prose in different words.

## File Size & Splitting

- Target average size: ~15k chars (~3,800 tokens).
- Files above ~30k chars (~7,500 tokens) are candidates for splitting when
  next touched.
- Split only along genuine seams: a section that's analytically distinct,
  has minimal cross-references into the rest of the file, and is substantial
  enough to merit its own entry.
- Split-off naming: `<parent-filename>-<new-topic>.md`, so it sorts next to
  the parent.
- After splitting: add reciprocal `## See Also` links between parent and new
  file, and update any index/overview files that listed the parent's content.

## See Also

`## See Also` sections link 2–4 thematically related files, each with one
clause explaining the relationship — not just a bare link.

## Language Standard

**Concrete over abstract.** Replace abstract nouns with verbs or concrete
nouns that show the action. If a sentence requires domain expertise to parse,
it fails.

**Two abstract nouns adjacent: at least one isn't working.** Say what the
thing does, not what it is called.

**Define technical terms on first use.** When a specialist term is
unavoidable, follow it immediately with a plain explanation — "the default
mode network — active when the mind is idle." After that, the term may be
reused without redefining it.

**Read it out loud.** If you stumble, it still has academic phrasing. If the
same claim can be made in plainer words without losing precision, use them.

### Jargon — Pattern-Based Detection

A static word list doesn't scale. Detect jargon by pattern instead:

| Pattern | Detection | Fix |
|---------|-----------|-----|
| **Abstract noun stack** | Two abstract nouns adjacent in a sentence | Replace one with a verb or concrete noun |
| **Nominalization** | Action turned into stiff noun ("failure," "output," "utilization") | Replace with the verb form ("breaks down," "what happens," "using") |
| **Hedge cluster** | "It has been suggested that," "Research indicates" | State the claim directly; name the source |
| **Passive construction** | "X is implicated in," "Y was found to" | Flip to active voice with a named agent |

### Sentence Structure

- **One idea per sentence.** Long sentences earn their length only when the
  idea genuinely can't be split.
- **Prefer active voice.**
- **Name sources directly.** Avoid bare "research shows" — name the study,
  year, or phenomenon. Reframe as observation if no named source exists.

## General Hygiene

- No attribution lines referencing source material ("Based on transcript
  from...").
- Prefer extending an existing file over creating a new one for
  narrowly-scoped content — use `tools/kb_search.py` to find the best
  existing home before creating a new file.
