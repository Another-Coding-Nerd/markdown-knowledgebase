# Process Input Files

Process new source files in `inputs/` into the knowledgebase (`kb/`).

This workflow processes files in `inputs/` only. To sort existing
`kb/**/*.md` files into `kb/projects/` vs `kb/resources/` (the
Projects/Resources split), use `prompts/organize-kb-files.md` instead — do
not run this inventory/dedup workflow against `kb/` content.

## Scope

This KB's scope is defined in `about.md` at the repo root. Read it before
beginning inventory. Use the scope description and out-of-scope list as the
test in steps 2f and 2e. If `about.md` does not exist, stop and ask the user
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
   b. **Full inventory first** — work section-by-section, not the whole
      document at once: one inventory pass per ~100-line segment (or natural
      paragraph breaks if shorter) for plain text files (the common case);
      per H2/H3 section only if the file is already markdown. Within each section/segment, enumerate every
      analytically distinct point/claim before evaluating any of them for
      placement. Do not evaluate, filter, or write KB content until the full
      inventory is complete. The failure mode to prevent: identifying the two
      most obvious points and treating them as the full yield — working
      section-by-section makes it harder to skip subtle points buried in a
      section whose headline point was already captured.
   **Read `prompts/_inventory-shared-steps.md` now** and continue with
   steps c–m, then steps 3–6 and Conventions from that file.
