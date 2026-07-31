# Organize kb/ Files into Projects vs. Resources

Pure structural reorganization — sort existing `kb/` files into
`kb/projects/` vs. `kb/resources/` based on content type. No filename
cleanup, no overlap check, no style review. Use this when the files are
already KB-ready and the only task is placement.

For externally-authored files that need cleanup before placement, use
`prompts/adopt-markdown-files.md` instead.

## Workflow

1. List the `.md` files to sort (the newly-added batch, or all of `kb/`'s
   top level if doing a one-off cleanup).
2. For each file, apply the test from `AGENTS.md`: does it describe a
   bounded effort with a deliverable or finish line?
   - **Yes** → belongs in `kb/projects/`.
   - **No** → resource material; move to `kb/resources/` (group into topic
     subdirectories within `kb/resources/` if this KB organizes resources
     that way).
   - **Uncertain** → flag it in the proposed-moves table with a one-sentence
     rationale and leave the destination blank — the user decides at
     confirmation.
3. **Present the proposed moves** — file, destination, one-line rationale —
   and wait for confirmation before moving anything.
4. If this KB maintains a topic index, reading-order file, or other
   navigation file that lists `kb/` paths, update any entries whose paths
   changed.
5. Reindex per `AGENTS.md` — run both steps:
   ```
   tools/index --incremental
   tools/connections
   ```
