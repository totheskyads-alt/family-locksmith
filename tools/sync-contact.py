#!/usr/bin/env python3
"""Single source of truth for contact details across the static site.

The site is 20 hand-authored HTML files with duplicated header/footer chrome,
so a phone number lives in ~14 places per file. Edit the constants below and
run this script rather than hand-editing every page.

    python3 tools/sync-contact.py            # apply
    python3 tools/sync-contact.py --check    # report only, exit 1 if stale
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- the only lines you should need to edit ----------------------------------
PHONE_DISPLAY = "07597 379838"
PHONE_HREF = "tel:+447597379838"
WHATSAPP_NUMBER = "447597379838"
WHATSAPP_PREFILL = "Hi, I need a locksmith. I'm in "
# ------------------------------------------------------------------------------

WHATSAPP_HREF = "https://wa.me/{}?text={}".format(
    WHATSAPP_NUMBER,
    WHATSAPP_PREFILL.replace(" ", "%20").replace(",", "%2C").replace("'", "%27"),
)

# Anything that has ever stood in for the real details. Order matters: the more
# specific patterns run first so we never half-rewrite a string.
SUBSTITUTIONS = [
    # only the number is swapped, so per-button prefilled messages survive
    (re.compile(r'(https://wa\.me/)\d+'), r'\g<1>' + WHATSAPP_NUMBER),
    (re.compile(r'tel:\+?\d{7,}'), PHONE_HREF),
    (re.compile(r'\b0800 123 4567\b'), PHONE_DISPLAY),
    (re.compile(r'\b07000 000000\b'), PHONE_DISPLAY),
]


def process(text):
    for pattern, replacement in SUBSTITUTIONS:
        text = pattern.sub(replacement, text)
    return text


def main():
    check_only = "--check" in sys.argv
    stale = []
    changed = []

    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        original = open(path, encoding="utf-8").read()
        updated = process(original)
        if updated == original:
            continue
        name = os.path.basename(path)
        if check_only:
            stale.append(name)
        else:
            open(path, "w", encoding="utf-8").write(updated)
            changed.append(name)

    if check_only:
        if stale:
            print("stale contact details in: " + ", ".join(stale))
            return 1
        print("all pages carry the current contact details")
        return 0

    print("phone    {}  ({})".format(PHONE_DISPLAY, PHONE_HREF))
    print("whatsapp {}".format(WHATSAPP_HREF))
    print("updated  {} file(s): {}".format(len(changed), ", ".join(changed) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
