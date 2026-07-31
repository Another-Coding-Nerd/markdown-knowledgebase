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
test in steps 2e and 2g. If `about.md` does not exist, stop and ask the user
to describe the KB's scope before continuing — do not proceed without it.

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
   **Read `prompts/_inventory-shared-steps.md` now** and continue with
   steps c–m, then steps 3–6 and Conventions from that file.
