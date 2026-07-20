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

## Language Standard

**Concrete over abstract.** Replace abstract nouns with verbs or concrete
nouns that show the action. Then go one step further: show why the thing
produces what it produces. A pattern states what happens. A mechanism states
what happens *and* why. Aim for mechanisms — they're what readers remember.

**Two abstract nouns adjacent: at least one isn't working.** Say what the
thing does, not what it is called.

**No wasted words.** Every word either changes the meaning or comes out. If
removing a word, phrase, or sentence doesn't change what's being said, remove
it. This is different from being terse — the goal is that every word is
pulling weight, not that sentences are short.

**Define technical terms on first use.** When a specialist term is
unavoidable, follow it immediately with a plain explanation — "the default
mode network — active when the mind is idle." After that, the term may be
reused without redefining it.

**Read it out loud — with the right test.** Stumbling is one signal. The
sharper test: would a reader pause to re-read? If yes, the sentence failed.
That includes academic phrasing, but also ambiguity, missing context, and
anything that requires inference the reader hasn't been given. If the same
claim can be made in plainer words without losing precision, use them.

**Name sources directly.** Avoid bare "research shows" or "studies suggest"
— name the study, author, year, or named phenomenon. If no named source
exists, reframe as observation rather than assertion.

### Jargon — Pattern-Based Detection

| Pattern | Detection | Fix |
|---------|-----------|-----|
| **Abstract noun stack** | Two abstract nouns adjacent in a sentence | Replace one with a verb or concrete noun; then check: does it pass on first read without re-parsing? |
| **Nominalization** | Action turned into stiff noun ("failure," "output," "utilization") | Replace with the verb form ("breaks down," "what happens," "using") |
| **Hedge cluster** | "It has been suggested that," "Research indicates" | State the claim directly; name the source |
| **Passive construction** | "X is implicated in," "Y was found to" | Flip to active voice with a named agent |

## Prose Rhythm

The target is Sowell's compression fused with Sagan's clarity discipline.

**Short-to-medium sentences.** Most sentences carry one idea. Two at most.
Long subordinate chains slow the reader without adding precision — break them.
A paragraph of short-to-medium declaratives moves; a paragraph of sprawling
compounds stalls.

**Efficient but not terse.** The prose should move quickly and always keep
the reader oriented. Don't cut so far that the reader has to re-read to
follow the logic. Every sentence should be immediately understandable on first
pass — no jargon, no ambiguity, no moment where the reader asks "what does
that mean?"

**Intelligence through precision, not ornament.** A sentence signals
intelligence by being exact, not by being elaborate. Trim every word that
isn't doing work. If removing it changes the meaning, keep it. If it doesn't,
cut it.

**No dilution.** Plain language is not imprecise language. If a nuance
matters, find plain words for it — don't drop it to keep things simple.
Accessible to broad readers; accurate enough to hold up.

## Filenames

- Kebab-case, no counts (`signs-of-x.md`, not `9-signs-of-x.md`) — counts
  drift as content changes.

## Bullets vs. Prose

Prose is the default. Bullets are for genuine lists: discrete categories,
enumerated stages, schemas. Convert or remove bullet clusters that just
restate what the surrounding prose already says.

## Blockquotes

At most one per file (closing or within a section). Keep a blockquote only
if it adds something the prose doesn't — a memorable distillation, a quote,
vivid framing. Remove ones that just restate surrounding prose in different
words.

One to two sentences maximum. A blockquote that runs to a paragraph is just
prose with extra formatting — flatten it. The function of a blockquote is to
land one thing cleanly; length works against that.

## File Size & Splitting

- Target average size: ~15k chars (~3,800 tokens).
- Files above ~30k chars (~7,500 tokens) are candidates for splitting when
  next touched.
- Split only along genuine seams: a section that's analytically distinct,
  has minimal cross-references into the rest of the file, and is substantial
  enough to merit its own entry.
- Split-off naming: `<parent-filename>-<new-topic>.md`, so it sorts next to
  the parent.
- After splitting: reindex (`tools/index --incremental`) and rebuild
  connections (`tools/connections`) — the graph will link the new files
  automatically. Update any index/overview files that listed the parent's
  content.

## General Hygiene

- No attribution lines referencing source material ("Based on transcript
  from...").
- Prefer extending an existing file over creating a new one for
  narrowly-scoped content — use `tools/kb_search.py` to find the best
  existing home before creating a new file.
