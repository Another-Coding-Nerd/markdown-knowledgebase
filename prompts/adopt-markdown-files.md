# Adopt Externally-Authored Markdown Files

For human-created or externally-maintained `.md` files copied directly into
`kb/`. These files are treated as all-signal — no noise filtering, no
off-topic check, no cross-KB dedup against pre-existing content. The goal
is to get them organized, cleanly named, and flagged for any structural or
style issues before they become part of the working KB.

This is distinct from `prompts/process-input-files.md` (raw source material
with noise and dupes) and `prompts/organize-kb-files.md` (pure PARA placement
of already-clean files).

## Workflow

1. **List the batch** — identify all `.md` files to adopt (the newly-added
   files, or a specific subdirectory). Read each file's title and first
   paragraph to build a topic summary; do not do a full content read yet.

2. **Filename audit** — for each file, check:
   - Is the name kebab-case? (`my-file.md`, not `MyFile.md` or `my_file.md`)
   - Does it embed a count? (`9-signs-of-x.md` → `signs-of-x.md`)
   - Does the name reflect the actual topic?
   Propose a corrected name where needed.

3. **Internal overlap scan** — using the title and first-paragraph summaries
   from step 1, identify any two files in the batch that appear to cover
   substantially the same ground. Do not use `kb_search.py` here — the batch
   files are not indexed yet. For any pair that looks like a match by topic,
   read both files fully to confirm before flagging as a merge candidate.

4. **PARA classification** — for each file, apply the test from `AGENTS.md`:
   does it describe a bounded effort with a specific deliverable or finish
   line?
   - **Yes** → `kb/projects/`
   - **No** → `kb/resources/` (propose a topic subdirectory if this KB uses
     them; otherwise top-level `kb/resources/`)
   - **Uncertain** → flag for user decision

5. **Light style scan** — skim each file for obvious issues. Flag but do not
   fix:
   - Second-person instruction voice ("you should," "do this")
   - Numbered action scripts in prescriptive register
   - Counts embedded in headings ("9 Signs of X")
   - Filename mismatches already caught in step 2
   Note these in the findings table. Deep style editing belongs in
   `prompts/process-knowledgebase-files.md` — run that after adoption if
   needed.

6. **Present findings** — one table covering all files:

   | Current filename | Proposed filename | Destination | Overlap with | Style flags |
   |-----------------|-------------------|-------------|--------------|-------------|

   Flag merge candidates clearly. Note any uncertain PARA classifications.
   Wait for confirmation before making any changes.

7. **Execute** — after confirmation:
   - Rename files as approved
   - Move to approved destinations
   - Merge any files the user approved merging (present merged content for
     review before writing)

8. **Reindex** per `AGENTS.md` — run both steps:
   ```
   tools/index --incremental
   tools/connections
   ```
