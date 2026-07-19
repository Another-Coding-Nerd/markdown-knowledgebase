Scan all content `.md` files in `kb/` for second-person register violations and fix them.

## Scope
- Include: all `.md` files under `kb/`
- Exclude: `inputs/`, `prompts/`, `AGENTS.md`, `CONTENT-STYLE.md`, `README.md`

## What to find and fix
Second-person address patterns:
- `you`, `your`, `you're`, `you've`, `you'll`, `you'd`, `you are`, `you have`, `you will`

**Skip these — they are acceptable:**
- Lines starting with `>` (blockquote aphorisms or quoted speech)
- Direct quotations within the text

**Convert to third-person observational** (see register conventions in `CONTENT-STYLE.md`):
- "you" → "a person", "someone who", "the individual", or domain-appropriate equivalent
- "your" → "their", "a person's"
- "you must/should/need to" → "the pattern tends to be...", "people in this situation often..."

## Process
1. Run: `grep -rn "\byou\b\|\byour\b" --include="*.md" kb/` to find all violations
2. Group by file
3. Fix each file — read it fully before editing, fix all violations in a single pass
4. After all files are done, run the grep again to confirm zero remaining violations
5. Batch-reindex: `.venv/bin/python tools/kb_index.py --incremental`
