# Process Input Files

Process new source files in `inputs/` into the knowledgebase (`kb/`).

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
   `inputs/off-topic/`. **Before inventorying anything**, run both ingest
   scripts from inside the `inputs/` directory:
   ```
   cd inputs/ && bash fmt_text.sh && bash de-dupe.sh
   ```
   `fmt_text.sh` reflows `.txt` files to 100 columns and **splits files over
   100 lines** into overlapping 100-line part files (`basename-part-001.txt`,
   etc.). `de-dupe.sh` removes files already present in `inputs/processed/`.
   Inventory the resulting files — not the originals. Both scripts must be
   invoked from inside `inputs/` (they glob `*.txt` in the current directory
   and ignore any file-path argument).
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
      placement. Each of the following counts as a separate inventory item: a
      named phenomenon or pattern, a specific mechanism or cause-effect chain,
      a statistic or data point, a behavioral observation, a counter-argument
      or nuance that modifies another claim, a framing distinction (e.g. "X is
      not Y, it is Z"). A single paragraph commonly contains 3–5 distinct
      items. After completing the first pass on a segment, re-read it once more
      specifically hunting for sub-claims not listed on the first pass — the
      second pass catches what the first pass collapsed into a headline. Do not
      evaluate, filter, or write KB content until the full inventory is
      complete. The failure mode to prevent: identifying the two most obvious
      points and treating them as the full yield — working section-by-section
      makes it harder to skip subtle points buried in a section whose headline
      point was already captured.
   **Read `prompts/_inventory-shared-steps.md` now** and continue with
   steps c–m, then steps 3–6 and Conventions from that file.
