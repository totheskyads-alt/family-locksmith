#!/usr/bin/env python3
"""Stamp CSS and JS links with a content hash so browsers cannot serve stale copies.

GitHub Pages sends `cache-control: max-age=600` on HTML and browsers hold onto
stylesheets far longer than that, so a deploy can land while visitors still see
the previous design. Appending a hash of the file's own contents means the URL
changes only when the file does: a new deploy is fetched immediately, an
unchanged one still comes from cache.

Run after any edit to styles.css or a script, before committing:

    python3 tools/sync-assets.py
    python3 tools/sync-assets.py --check   # exit 1 if any stamp is stale
"""
import glob
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS = ["styles.css", "track.js", "rail.js", "gallery.js"]

# Photographs get replaced in place under the same filename, so without a stamp
# a visitor who saw the old one keeps seeing it. Same rule as the CSS: the URL
# changes only when the bytes do.
IMG_SRC = re.compile(r'(src=")(images/[A-Za-z0-9._-]+\.(?:jpg|jpeg|png|webp))(?:\?v=[a-f0-9]+)?(")')


def digest(name):
    path = os.path.join(ROOT, name)
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:8]


def main():
    check = "--check" in sys.argv
    stamps = {}
    for name in ASSETS:
        if not os.path.exists(os.path.join(ROOT, name)):
            print("missing asset: " + name)
            return 1
        stamps[name] = digest(name)

    # href="styles.css" or href="styles.css?v=old" -> href="styles.css?v=new"
    patterns = [(n, re.compile(r'((?:href|src)=")' + re.escape(n) + r'(?:\?v=[a-f0-9]+)?(")'))
                for n in ASSETS]

    def stamp_img(m):
        rel = m.group(2)
        f = os.path.join(ROOT, rel)
        if not os.path.exists(f):
            return m.group(0)
        with open(f, "rb") as fh:
            d = hashlib.sha1(fh.read()).hexdigest()[:8]
        return m.group(1) + rel + "?v=" + d + m.group(3)

    touched, stale = [], []
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        html = open(path, encoding="utf-8").read()
        updated = html
        for name, pat in patterns:
            updated = pat.sub(r"\g<1>" + name + "?v=" + stamps[name] + r"\g<2>", updated)
        updated = IMG_SRC.sub(stamp_img, updated)
        if updated == html:
            continue
        page = os.path.basename(path)
        if check:
            stale.append(page)
        else:
            open(path, "w", encoding="utf-8").write(updated)
            touched.append(page)

    if check:
        if stale:
            print("stale asset stamps in: " + ", ".join(stale))
            return 1
        print("every asset link carries its current hash")
        return 0

    for name in ASSETS:
        print("  {:<12} v={}".format(name, stamps[name]))
    print("  images       stamped by content hash")
    print("restamped {} page(s): {}".format(len(touched), ", ".join(touched) or "none already current"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
