# Quickstart

1. **Clone the repo**

   ```bash
   git clone https://github.com/Another-Coding-Nerd/markdown-knowledgebase.git my-kb
   cd my-kb
   ```

2. **Open Claude Code**

   ```bash
   claude .
   ```

3. **Tell the agent to set up**

   > "Read AGENTS.md and follow the Initializing a new KB steps."

   The agent will install dependencies, build the index, and then ask what
   this KB is for. **Answer in one or two sentences** — this becomes the
   scope filter every input-processing prompt uses to decide what belongs in
   the KB and what doesn't. Be specific about what's in scope and what isn't.
   The agent writes `about.md` from your answer.

4. **Add content**

   Drop source files into `inputs/`, then tell the agent which prompt to run:

   | Source type | Say to agent |
   |-------------|--------------|
   | Articles, essays, structured notes | "Process inputs using prompts/process-input-files.md" |
   | Compressed summaries, bullet-point digests | "Process inputs using prompts/process-input-files-dense.md" |

   The agent inventories every point, cross-checks against existing KB content,
   and presents a full list for your approval before writing anything.

5. **Search**

   ```bash
   tools/search "your query"
   ```

   Or ask the agent directly — it uses the same search tool internally.

---

**Optional:** build the graph and launch the web UI:

```bash
tools/connections   # build semantic graph (needed for Flask UI)
tools/serve         # http://localhost:5000
```

See `README.md` for full documentation, configuration options, and the KB Q&A
feature (local LLM required).
