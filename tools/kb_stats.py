#!/usr/bin/env python3
"""
kb_stats.py — section length diagnostics for KB files.

Counts lines in each leaf section (sections with no child headings).
Flags SHORT and LONG outliers for review.

Usage:
    .venv/bin/python tools/kb_stats.py kb/some-file.md
    .venv/bin/python tools/kb_stats.py kb/some-file.md --short 4 --long 25
"""

import argparse
import re
import sys


DEFAULT_SHORT = 4
DEFAULT_LONG = 25


def analyze(filepath, short_threshold, long_threshold):
    with open(filepath) as f:
        lines = f.readlines()

    sections = []
    for i, line in enumerate(lines):
        m = re.match(r'^(#+)\s+(.+)$', line)
        if m:
            sections.append({'depth': len(m.group(1)), 'title': m.group(2), 'line': i})

    leaf_sections = []
    for idx, sec in enumerate(sections):
        end = sections[idx + 1]['line'] if idx + 1 < len(sections) else len(lines)
        has_children = any(
            s['line'] < end and s['depth'] > sec['depth']
            for s in sections[idx + 1:]
            if s['line'] < end
        )
        if not has_children:
            count = end - (sec['line'] + 1)
            leaf_sections.append({'title': sec['title'], 'lines': count, 'depth': sec['depth']})

    leaf_sections.sort(key=lambda x: x['lines'])

    print(f"\nSection length diagnostics: {filepath}\n")
    print(f"{'Flag':<6} {'Section':<40} {'Lines':<7} {'Level'}")
    print('-' * 60)

    for s in leaf_sections:
        if s['lines'] <= short_threshold:
            flag = 'SHORT'
        elif s['lines'] >= long_threshold:
            flag = 'LONG'
        else:
            flag = ''
        print(f"{flag:<6} {s['title'][:40]:<40} {s['lines']:<7} H{s['depth']}")

    if leaf_sections:
        avg = sum(s['lines'] for s in leaf_sections) / len(leaf_sections)
        shorts = [s for s in leaf_sections if s['lines'] <= short_threshold]
        longs = [s for s in leaf_sections if s['lines'] >= long_threshold]
        print(f"\nAvg: {avg:.1f} lines  |  {len(shorts)} SHORT (≤{short_threshold})  |  {len(longs)} LONG (≥{long_threshold})")


def main():
    parser = argparse.ArgumentParser(description='KB section length diagnostics')
    parser.add_argument('file', help='Path to markdown file')
    parser.add_argument('--short', type=int, default=DEFAULT_SHORT,
                        help=f'Flag sections at or below this line count (default {DEFAULT_SHORT})')
    parser.add_argument('--long', type=int, default=DEFAULT_LONG,
                        help=f'Flag sections at or above this line count (default {DEFAULT_LONG})')
    args = parser.parse_args()
    analyze(args.file, args.short, args.long)


if __name__ == '__main__':
    main()
