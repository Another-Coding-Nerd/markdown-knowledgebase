Audit `kb/` for structural integrity. Run all checks and report findings before making any fixes.

## 1. Broken See Also Links

```bash
cd kb && python3 -c "
import re, os, glob

broken = []
for fpath in sorted(glob.glob('*.md')):
    content = open(fpath).read()
    in_see_also = False
    for line in content.split('\n'):
        if '## See Also' in line:
            in_see_also = True
            continue
        if in_see_also:
            for link in re.findall(r'\]\(([^)]+\.md)\)', line):
                if not os.path.exists(link):
                    broken.append((fpath, link))
for f, l in broken:
    print(f'BROKEN: {f} -> {l}')
if not broken:
    print('OK: All See Also links resolve.')
"
```

## 2. Orphan Files (no inbound See Also links)

```bash
cd kb && python3 -c "
import re, glob

content_files = sorted(glob.glob('*.md'))

inbound = {f: set() for f in content_files}
for fpath in content_files:
    text = open(fpath).read()
    in_see_also = False
    for line in text.split('\n'):
        if '## See Also' in line:
            in_see_also = True
            continue
        if in_see_also:
            for link in re.findall(r'\]\(([^)]+\.md)\)', line):
                if link in inbound:
                    inbound[link].add(fpath)

orphans = [f for f in content_files if not inbound[f]]
for f in orphans:
    print(f'ORPHAN: {f} (zero inbound See Also links)')
if not orphans:
    print('OK: All content files have at least one inbound See Also link.')
"
```

Orphans aren't necessarily broken — treat as a semantic flag (Part 2), not an auto-fix: for each orphan, check via `tools/kb_search.py` whether a thematically related file should link to it, and propose the addition.

If your KB has files that are intentionally link-free (e.g. a glossary), exclude them from this check by adding a `skip = {...}` set.

## 3. Large Files (splitting candidates)

```bash
cd kb && python3 -c "
import glob

content_files = sorted(glob.glob('*.md'))

threshold = 30000
large = [(f, len(open(f).read())) for f in content_files]
large = [(f, size) for f, size in large if size > threshold]
for f, size in large:
    print(f'LARGE: {f} ({size:,} chars, ~{size//4:,} tokens) — review for splittable seams')
if not large:
    print('OK: No content files over the size threshold.')
"
```

Per the File Size & Splitting policy in `CONTENT-STYLE.md`: not necessarily a problem, but a candidate for review. Treat as a semantic flag, not an auto-fix — propose a split only if there's a genuine seam (analytically distinct section, minimal internal cross-references, substantial enough for its own See Also entries).

## Output

Fix broken links (1) immediately if any are found. Report orphans (2) and large files (3) as flags for user review — do not edit `kb/` without approval.
