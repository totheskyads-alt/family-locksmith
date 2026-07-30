#!/usr/bin/env python3
"""The ticker band that sits directly under the hero on every page.

    python3 tools/sync-ticker.py
    python3 tools/sync-ticker.py --check

Edit ITEMS below and re-run. The list is emitted COPIES times: the rail animates
to translateX(-50%), so the back half is what the front half turns into and the
loop has no seam. COPIES must stay even.

The band is decorative and aria-hidden. It deliberately carries no links, both
because a link sliding under the cursor is a link nobody can click, and because
duplicating every link would double them for search engines and screen readers.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- what scrolls past: the services, nothing else --------------------------
ITEMS = [
    "Emergency lockout",
    "uPVC &amp; composite doors",
    "Lock changes &amp; repairs",
    "Burglary repair",
    "Security upgrades",
    "Commercial locksmith",
    "Landlord &amp; letting agent",
]

# The rail travels -50%, so half of what we emit has to be at least as wide as
# the widest screen or a gap opens at the wrap. Seven short items make one set
# roughly 1700px, so we emit four sets: half is then two sets, about 3400px,
# which covers an ultra-wide monitor.
COPIES = 4

# Pages that should not carry it.
EXCLUDE = {"hero-options.html", "testimonials-preview.html"}

MARK = re.compile(r"<!-- ticker:start -->.*?<!-- ticker:end -->", re.S)

# The hero is the first <section> on every page, whether it is the home hero or
# an inner page-hero, so we anchor on the close of that first section.
HERO_OPEN = re.compile(r'<section class="(?:hero|page-hero)[^"]*"')


def band():
    items = "".join(f'<span class="ticker-item">{t}</span>' for t in ITEMS)
    return ('<div class="ticker" aria-hidden="true">'
            f'<div class="ticker-rail">{items * COPIES}</div>'
            "</div>")


def close_of_first_section(html, start):
    """Index just past the </section> that closes the section opened at start."""
    depth = 0
    for m in re.finditer(r"<section\b|</section>", html[start:]):
        depth += 1 if m.group(0).startswith("<section") else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced <section>")


def main():
    check = "--check" in sys.argv
    touched, stale, skipped = [], [], []

    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        page = os.path.basename(path)
        if page in EXCLUDE:
            continue
        html = open(path, encoding="utf-8").read()
        payload = "<!-- ticker:start -->" + band() + "<!-- ticker:end -->"

        if MARK.search(html):
            updated = MARK.sub(lambda _: payload, html, count=1)
        else:
            m = HERO_OPEN.search(html)
            if not m:
                skipped.append(page)
                continue
            cut = close_of_first_section(html, m.start())
            updated = html[:cut] + "\n" + payload + html[cut:]

        if updated == html:
            continue
        if check:
            stale.append(page)
        else:
            open(path, "w", encoding="utf-8").write(updated)
            touched.append(page)

    if check:
        if stale:
            print("stale ticker on: " + ", ".join(stale))
            return 1
        print("ticker in sync ({} items)".format(len(ITEMS)))
        return 0

    print("{} items -> {} page(s): {}".format(
        len(ITEMS), len(touched), ", ".join(touched) or "none already current"))
    if skipped:
        print("no hero found on: " + ", ".join(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
