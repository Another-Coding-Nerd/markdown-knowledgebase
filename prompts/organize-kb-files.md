# Organize kb/ Files into Projects vs. Resources

For files added directly to `kb/` without going through
`prompts/process-input-files.md` (e.g. a batch of pre-existing `.md` files
copied straight in), sort them per the Projects vs. Resources convention in
`AGENTS.md`.

## Workflow

1. List the `.md` files to sort (the newly-added batch, or all of `kb/`'s
   top level if doing a one-off cleanup).
2. For each file, apply the test from `AGENTS.md`: does it describe a
   bounded effort with a deliverable or finish line?
   - **Yes** → belongs in `kb/projects/`.
   - **No** → resource material; leave at the top level or group into a
     topic subdirectory if this KB organizes resources that way.
3. **Present the proposed moves** — file, destination, one-line rationale —
   and wait for confirmation before moving anything.
4. After moves, update any `## See Also` links or index/navigation files
   affected (per `CONTENT-STYLE.md`).
5. Reindex per `AGENTS.md` (`kb_index.py --incremental` handles a move as a
   delete+add: the old path's chunks are removed, the new path is indexed).
