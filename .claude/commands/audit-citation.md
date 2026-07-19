Audit `kb/*.md` for unattributed or unverifiable research/study claims. Verify each via WebSearch before fixing — report findings as you go rather than batching a final report, since this is typically a long-running pass.

## 1. Find candidate claims

```bash
cd kb && grep -rniE "studies (show|suggest|have shown|indicate|link|find|reveal)|research (shows|suggests|has shown|indicates)|scientists (have found|say|found)|experts (say|agree|have found)|a study (found|shows)|surveys (show|find)|the data (shows|suggests)" *.md
```

This catches unattributed-claim phrasing specifically — it will not catch every
citation issue (a wrong year, a misattributed author, an invented statistic with
no trigger phrase). Treat it as a starting net, not a complete sweep; skim
adjacent paragraphs around each hit for nearby uncited numbers too.

## 2. Filter obvious non-issues

Skip matches that are:
- Already followed by a named author/study/year in the same sentence or the next
  (e.g. "Frederick et al. (2018)", "Davis et al.'s 2019 *Lancet* meta-analysis")
- Section headings ("## What the Data Shows") rather than claims
- Already explicitly flagged as unverified in the surrounding prose

## 3. For each remaining candidate, verify via WebSearch

Search for the specific claim as stated (the named study, the named mechanism,
the specific number). If that search comes up empty, broaden to the underlying
phenomenon before concluding it's unverifiable — the specific citation is
sometimes wrong while the underlying claim is real.

Distinguish three outcomes:
1. **Verified as stated** — leave as is, or add the citation if it's missing one
   even though the claim is true.
2. **Real phenomenon, wrong/missing/overstated specifics** — fix the citation,
   correct the figure, or add a hedge (e.g. "effect sizes were small to moderate"
   rather than an unqualified "studies show X").
3. **Unverifiable / contradicted by the literature** — soften to a rule-of-thumb
   framing, or remove the specific number/study reference while keeping the
   underlying observation if it still holds without the bad citation.

## 4. Fix in place

Edit the file directly once verified — don't batch all fixes to the end. Name
what's solid, name what's contested; don't delete a claim wholesale if the core
observation is still worth keeping.

## 5. Reindex

```bash
.venv/bin/python tools/kb_index.py --incremental
```

## Output

Report each claim checked, its verification outcome, and the fix applied (or
"no fix needed") — don't wait until the end to surface findings, since this
audit can run long and the user may want to redirect mid-pass.
