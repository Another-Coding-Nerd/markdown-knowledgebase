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
