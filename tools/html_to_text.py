#!/usr/bin/env python3
"""Extract clean text from HTML files/URLs, or HTML pasted into .txt files."""

import argparse
import re
import sys
import textwrap
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
FETCH_TIMEOUT = 15
REMOVE_SELECTORS = ["a", "script", "style", "footer", ".footer", ".sidebar"]
BLOCK_TAGS = ["p", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre"]


def looks_like_html(text: str) -> bool:
    head = text.lstrip()[:1000].lower()
    if head.startswith("<!doctype") or head.startswith("<html"):
        return True
    tag_count = len(re.findall(r"<[a-z!/][^>]*>", head))
    return tag_count >= 5


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for selector in REMOVE_SELECTORS:
        for el in soup.select(selector):
            el.decompose()

    # Use leaf block-level elements as paragraph boundaries so inline tags
    # (<a>, <em>, <span>, ...) inside a block join into one continuous line
    # instead of each fragmenting into its own paragraph.
    blocks = [el for el in soup.find_all(BLOCK_TAGS) if not el.find(BLOCK_TAGS)]
    if not blocks:
        blocks = [soup]

    paragraphs = []
    for block in blocks:
        text = block.get_text(" ", strip=True)
        if text:
            paragraphs.append(textwrap.fill(text, width=100))
    return "\n\n".join(paragraphs)


def fetch_url(url: str) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=FETCH_TIMEOUT)
    response.raise_for_status()
    return response.text


def process_one(item: str, write: bool) -> None:
    if item.startswith("http://") or item.startswith("https://"):
        try:
            html = fetch_url(item)
        except requests.RequestException as exc:
            print(f"warning: failed to fetch {item}: {exc}", file=sys.stderr)
            return
        text = extract_text(html)
        if write:
            out_path = Path(re.sub(r"[^A-Za-z0-9._-]", "_", item)).with_suffix(".txt")
            out_path.write_text(text)
        else:
            print(text)
        return

    path = Path(item)
    if not path.exists():
        print(f"warning: no such file: {item}", file=sys.stderr)
        return

    content = path.read_text(errors="ignore")
    if path.suffix.lower() != ".html" and not looks_like_html(content):
        print(f"warning: not HTML, skipping: {item}", file=sys.stderr)
        return

    text = extract_text(content)
    if write:
        out_path = path.with_suffix(".txt")
        out_path.write_text(text)
        if out_path != path:
            path.unlink()
    else:
        print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract clean text from HTML files or URLs.")
    parser.add_argument("input", nargs="+", help="Local .html file path or http(s):// URL")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write output to <input-stem>.txt next to the source; default is stdout",
    )
    args = parser.parse_args()

    for item in args.input:
        process_one(item, args.write)


if __name__ == "__main__":
    main()
