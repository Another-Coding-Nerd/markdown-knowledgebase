Audit `kb/` for structural integrity. Run all checks and report findings before making any fixes.

## 1. Stale See Also Sections

Graph edges are computed automatically from `connections.db`. Manually written
`## See Also` sections are obsolete and should be removed.

```bash
cd kb && python3 -c "
import glob

hits = []
for fpath in sorted(glob.glob('**/*.md', recursive=True)):
    if '## See Also' in open(fpath).read():
        hits.append(fpath)
for f in hits:
    print(f'SEE ALSO: {f} — section can be removed')
if not hits:
    print('OK: No stale See Also sections found.')
"
```

If hits are found, remove the `## See Also` heading and its link list from each
file. Do not remove any other content.

## 2. Orphan Files (no connections.db edges)

Files with no semantic neighbors may be under-indexed or too short/narrow to
embed meaningfully. Requires `connections.db` to exist — run `tools/connections`
first if absent.

```bash
python3 -c "
import sqlite3, glob, os, sys

db = 'connections.db'
if not os.path.exists(db):
    print('SKIP: connections.db not found — run tools/connections first')
    sys.exit(0)

con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
connected = set()
for row in con.execute('SELECT source FROM connections').fetchall():
    connected.add(row[0])
for row in con.execute('SELECT target FROM connections').fetchall():
    connected.add(row[0])
con.close()

kb_files = sorted(glob.glob('kb/**/*.md', recursive=True))
orphans = [f for f in kb_files if os.path.relpath(f, 'kb') not in connected]
for f in orphans:
    print(f'ORPHAN: {f} (no edges in connections.db)')
if not orphans:
    print('OK: All files have at least one connection.')
"
```

Orphans aren't necessarily broken — treat as a semantic flag, not an auto-fix.
A file may be too short, too narrow, or simply a new addition not yet connected.
Use `tools/connections --show <file>` to inspect its nearest neighbors and score.

## 3. Large Files (splitting candidates)

```bash
cd kb && python3 -c "
import glob

content_files = sorted(glob.glob('**/*.md', recursive=True))
threshold = 30000
large = [(f, len(open(f).read())) for f in content_files]
large = [(f, size) for f, size in large if size > threshold]
for f, size in large:
    print(f'LARGE: {f} ({size:,} chars, ~{size//4:,} tokens) — review for splittable seams')
if not large:
    print('OK: No content files over the size threshold.')
"
```

Per the File Size & Splitting policy in `CONTENT-STYLE.md`: not necessarily a
problem, but a candidate for review. Treat as a semantic flag, not an auto-fix
— propose a split only if there's a genuine seam (analytically distinct section,
minimal internal cross-references, substantial enough to stand alone).

## Output

Fix stale See Also sections (1) immediately if found. Report orphans (2) and
large files (3) as flags for user review — do not edit `kb/` content without
approval.
