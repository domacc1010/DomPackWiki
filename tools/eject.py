#!/usr/bin/env python3
"""
eject.py — take manual control of any generated page.

Usage:
    python3 tools/eject.py gameplay/items/tms.html
    python3 tools/eject.py --all-static     (ejects every placeholder/template page at once)

Copies the page's CURRENT body (everything inside <main> after the
title/lede) into content/<same-path>. From then on, that file is the page:
edit it freely, rebuild as often as you like — the generators will keep the
sidebar/template fresh around it but will never touch your HTML again.

To hand a page back to the generators, just delete its file from content/.

The one page that can't be ejected is gameplay/pokemon/index.html — it's a
JavaScript app, not a content page. To customize Pokémon cards, edit
assets/data/pokemon-custom.json instead (see assets/data/README.md).
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_common import SITE_ROOT, CONTENT_ROOT  # noqa: E402

_MAIN_RE = re.compile(r"<main>(.*?)</main>", re.S)
_CRUMB_RE = re.compile(r'\s*<div class="crumb">.*?</div>', re.S)
_H1_RE = re.compile(r"\s*<h1>.*?</h1>", re.S)
_LEDE_RE = re.compile(r'\s*<p class="lede">.*?</p>', re.S)

BLOCKED = {"gameplay/pokemon/index.html"}

def eject(page_path):
    page_path = page_path.replace("\\", "/").lstrip("./")
    if page_path in BLOCKED:
        print(f"  SKIP {page_path} — it's the Pokédex app, not a content page.")
        print("       Customize cards via assets/data/pokemon-custom.json instead.")
        return False
    src = os.path.join(SITE_ROOT, page_path)
    if not os.path.isfile(src):
        print(f"  ERROR: {page_path} not found (build the site first).")
        return False
    dst = os.path.join(CONTENT_ROOT, page_path)
    if os.path.isfile(dst):
        print(f"  SKIP {page_path} — already ejected (content/{page_path} exists).")
        return False
    with open(src, "r", encoding="utf-8") as f:
        html = f.read()
    m = _MAIN_RE.search(html)
    if not m:
        print(f"  ERROR: couldn't find <main> in {page_path}.")
        return False
    body = m.group(1)
    body = _CRUMB_RE.sub("", body, count=1)
    body = _H1_RE.sub("", body, count=1)
    body = _LEDE_RE.sub("", body, count=1)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    header = (f"<!-- Hand-written content for {page_path}.\n"
              f"     This file IS the page body now — edit freely, rebuilds never touch it.\n"
              f"     Delete this file to hand the page back to the generators. -->\n")
    with open(dst, "w", encoding="utf-8") as f:
        f.write(header + body.strip() + "\n")
    print(f"  ejected {page_path} -> content/{page_path}")
    return True

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    if sys.argv[1] == "--all-static":
        count = 0
        for dirpath, _, files in os.walk(SITE_ROOT):
            if any(skip in dirpath for skip in (os.sep + "content", os.sep + "tools", os.sep + "assets")):
                continue
            for fn in files:
                if fn.endswith(".html"):
                    rel_path = os.path.relpath(os.path.join(dirpath, fn), SITE_ROOT).replace(os.sep, "/")
                    if eject(rel_path):
                        count += 1
        print(f"\n{count} pages ejected. Run tools/build_all.py to confirm — "
              "each should now report [hand-written].")
        return
    for p in sys.argv[1:]:
        eject(p)
    print("\nDone. Run tools/build_all.py — ejected pages will report [hand-written].")

if __name__ == "__main__":
    main()
