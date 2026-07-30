#!/usr/bin/env python3
"""Keep the job rail identical on every page that carries it.

The rail appears on the home, services and reviews pages. Rather than editing
the same markup in three files, edit CARDS below and run:

    python3 tools/sync-rail.py

Each page marks its slot with <!-- rail:start --> ... <!-- rail:end -->, and the
heading above the rail is per-page so the section reads naturally in context.

WHEN REAL REVIEWS ARRIVE: this is the file to change. Swap CARDS for the real
quotes (tag = where they are, title = the short version, body = the quote,
foot = the job we did) and re-run. Nothing else on the site needs touching.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- the content. Every line here is something the business actually does. ----
CARDS = [
    dict(tag="Emergency lockout", icon="clock",
         title="The door shut behind you",
         body="Keys on the kitchen table and it is half eleven at night. We open the "
              "great majority of doors without drilling, so you keep the lock you "
              "already had and pay for the callout, not a new cylinder.",
         foot="With you in around 25 minutes"),
    dict(tag="uPVC and composite", icon="wrench",
         title="The handle lifts but the key will not turn",
         body="That is nearly always the multipoint gearbox rather than the door "
              "itself. We carry the mechanisms that fail most often, so it is usually "
              "sorted in one visit instead of two.",
         foot="Most repairs done the same day"),
    dict(tag="Burglary repair", icon="shield",
         title="Someone has been through the door",
         body="We make the property secure first, board up if the frame has gone, and "
              "book the permanent repair once you have spoken to your insurer. You are "
              "not left waiting overnight with a door that will not shut.",
         foot="Same evening, seven days a week"),
    dict(tag="Moving in", icon="key",
         title="You do not know who still has a key",
         body="Previous owners, their family, a builder, whoever held the spare. "
              "Changing the cylinders on the external doors settles the question on "
              "your first day rather than your first scare.",
         foot="Usually under an hour"),
    dict(tag="Insurance work", icon="doc",
         title="Your policy asks for anti-snap locks",
         body="Normally BS3621 or TS007 three star, depending on how the wording runs. "
              "We fit to the specification and confirm what went in, in writing, so you "
              "can forward it straight to the insurer.",
         foot="Documented for your insurer"),
    dict(tag="Landlords and agents", icon="building",
         title="New tenant moving in on Monday",
         body="Cylinder changes between tenancies, keyed alike where you want one key "
              "per property, and invoiced to the agency rather than the tenant. We work "
              "around the changeover date.",
         foot="Booked around your changeover"),
    dict(tag="Snapped key", icon="key",
         title="Half the key is still in the lock",
         body="Do not push the other half back in, that is what turns a ten minute job "
              "into a new lock. We extract the broken section and, if the lock came "
              "through it, cut you a fresh set from what is left.",
         foot="Extracted without drilling, usually"),
    dict(tag="Shops and offices", icon="building",
         title="The shutter lock has gone and you cannot open up",
         body="Aluminium doors, roller shutters and master suited systems where one key "
              "needs to open several doors. We know what closing for the morning costs "
              "you, so commercial calls go to the front.",
         foot="Trading again the same morning"),
]

# Per-page heading, so the same rail does not read identically three times.
HEADS = {
    "index.html": ("What we get called out for",
                   "The calls we take most weeks",
                   "Locksmith work is fairly predictable. These are the jobs that fill "
                   "the diary, and what tends to happen on each one."),
    "services.html": ("Straight from the job sheet",
                      "What these services look like in practice",
                      "The service list above is the menu. This is what the visit "
                      "actually involves once we are at your door."),
    "reviews.html": ("How we work",
                     "The jobs behind the recommendations",
                     "Most of our work comes through people passing our number on. "
                     "These are the calls that earn it."),
}

ICONS = {
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7.2v5.1l3.2 1.9"/>',
    "wrench": '<path d="M15.5 3.8a5.2 5.2 0 0 0-6.1 6.8L3.6 16.4a2 2 0 1 0 2.8 2.8l5.8-5.8a5.2 5.2 0 0 0 6.8-6.1l-3 3-2.5-2.5z"/>',
    "shield": '<path d="M12 3l7.5 3v5.4c0 4.6-3.1 8.2-7.5 9.6-4.4-1.4-7.5-5-7.5-9.6V6z"/><path d="m9.2 12.2 2 2 3.6-3.8"/>',
    "key": '<circle cx="8.2" cy="8.2" r="4.2"/><path d="m11.4 11.4 8 8"/><path d="m17.2 17.2 2-2M14.6 14.6l1.8-1.8"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9.2 13h5.6M9.2 16.4h4"/>',
    "building": '<path d="M4 21V6.5a1.5 1.5 0 0 1 1.5-1.5h6A1.5 1.5 0 0 1 13 6.5V21"/><path d="M13 10h5.5A1.5 1.5 0 0 1 20 11.5V21"/><path d="M2.5 21h19"/><path d="M7 9h2.5M7 13h2.5M16 14h1.5"/>',
}

ARROW_L = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m14 6-6 6 6 6"/></svg>')
ARROW_R = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m10 6 6 6-6 6"/></svg>')


def card_html(c):
    icon = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + ICONS[c["icon"]] + "</svg>")
    return (
        '<article class="rail-card">'
        f'<span class="rc-tag">{c["tag"]}</span>'
        f'<h3>{c["title"]}</h3>'
        f'<p>{c["body"]}</p>'
        f'<div class="rc-foot">{icon}<span>{c["foot"]}</span></div>'
        "</article>"
    )


def rail_html(page):
    tag, head, lead = HEADS[page]
    cards = "".join(card_html(c) for c in CARDS)
    return (
        '<section class="section" id="jobs">\n'
        '  <div class="container">\n'
        '    <div class="rail">\n'
        '      <div class="rail-head">\n'
        '        <div class="section-head">'
        f'<span class="section-tag">{tag}</span>'
        f"<h2>{head}</h2>"
        f"<p>{lead}</p>"
        "</div>\n"
        '        <div class="rail-nav">'
        f'<button class="rail-btn rail-prev" type="button" aria-label="Previous">{ARROW_L}</button>'
        f'<button class="rail-btn rail-next" type="button" aria-label="Next">{ARROW_R}</button>'
        "</div>\n"
        "      </div>\n"
        '      <div class="rail-track" tabindex="0" role="group" aria-label="Jobs we are called out for">'
        f"{cards}</div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>"
    )


MARK = re.compile(r"<!-- rail:start -->.*?<!-- rail:end -->", re.S)


def main():
    check = "--check" in sys.argv
    touched, missing, stale = [], [], []

    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        page = os.path.basename(path)
        html = open(path, encoding="utf-8").read()
        if "<!-- rail:start -->" not in html:
            if page in HEADS:
                missing.append(page)
            continue
        if page not in HEADS:
            missing.append(page + " (no heading defined)")
            continue

        payload = "<!-- rail:start -->\n" + rail_html(page) + "\n<!-- rail:end -->"
        updated = MARK.sub(lambda _: payload, html, count=1)
        if updated == html:
            continue
        if check:
            stale.append(page)
        else:
            open(path, "w", encoding="utf-8").write(updated)
            touched.append(page)

    if check:
        if stale or missing:
            print("stale: " + ", ".join(stale or ["none"]))
            print("missing slot: " + ", ".join(missing or ["none"]))
            return 1
        print("every rail is in sync")
        return 0

    print("{} cards -> {} page(s): {}".format(
        len(CARDS), len(touched), ", ".join(touched) or "none already current"))
    if missing:
        print("no <!-- rail:start --> slot in: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
