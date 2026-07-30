#!/usr/bin/env python3
"""Keep the job gallery identical on every page that carries it.

These are the client's own photographs from real jobs, which is the strongest
proof this site has. Edit PHOTOS below and run:

    python3 tools/sync-gallery.py

Each page marks its slot with <!-- gallery:start --> ... <!-- gallery:end -->.

Captions are deliberately instructive rather than decorative: a visitor who
learns that the gearbox fails and not the door is a visitor who understands
the quote. Keep that tone when adding more.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- the client's own photographs. file, dimensions, alt, caption -------------
PHOTOS = [
    ("job-ultion-pair.jpg", 900, 1200,
     "Two chrome Ultion anti-snap cylinders removed from a set of French doors",
     "Ultion anti-snap cylinders on French doors. The guarantee tags stay on the keys."),
    ("job-cylinder-brass.jpg", 900, 1200,
     "A brass euro cylinder held in front of a composite door with a black handle",
     "Euro cylinder swapped on a composite door. New keys, same door furniture."),
    ("job-gearbox-composite.jpg", 900, 1200,
     "A multipoint gearbox removed from a white composite door",
     "The strip that runs the height of the door. This is what fails, not the door."),
    ("job-gearbox-gold.jpg", 900, 1200,
     "A gold multipoint gearbox held beside a white panelled door",
     "Handle gone floppy, key would not throw the bolts. The gearbox, every time."),
    ("job-gearbox-tested.jpg", 900, 900,
     "A tested UK-made multipoint mechanism held against a door with a gold handle",
     "A replacement mechanism, tested and UK made, going into a hardwood door."),
    ("job-mortice-asec.jpg", 756, 756,
     "An Asec five lever mortice sashlock fitted into the edge of a timber door",
     "Five lever mortice sashlock to British Standard, what most insurers ask for."),
]

# Per-page heading, so the same gallery does not read identically three times.
# Headings describe what is in the photographs. Earlier drafts talked about the
# photography itself ("our own, not stock"), which is our concern, not the
# customer's: they want to see the work.
HEADS = {
    "index.html": ("Gallery",
                   "Recent work",
                   "Cylinders, door mechanisms and locks from jobs we have been out to. "
                   "Tap any photo to see it full size."),
    "services.html": ("Gallery",
                      "The parts we fit and replace",
                      "Nearly every job comes down to one component. These are the ones "
                      "that come out and go back in most often."),
    "about.html": ("Gallery",
                   "A closer look at the work",
                   "Anti-snap cylinders, multipoint gearboxes and British Standard mortice "
                   "locks, photographed on the doorstep as we fitted them."),
}

MARK = re.compile(r"<!-- gallery:start -->.*?<!-- gallery:end -->", re.S)


def figure(p):
    """One tile. Captions are deliberately not rendered: the client wanted the
    photographs clean. The caption text stays in PHOTOS because it is worth
    keeping, and putting it back is one <figcaption> line here. The alt text
    carries the description for screen readers and search either way."""
    src, w, h, alt, _cap = p
    return (
        '<figure class="gal-item">'
        f'<img src="images/{src}" width="{w}" height="{h}" alt="{alt}" loading="lazy">'
        "</figure>"
    )


ARROW_L = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m14 6-6 6 6 6"/></svg>')
ARROW_R = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m10 6 6 6-6 6"/></svg>')


def gallery_html(page):
    tag, head, lead = HEADS[page]
    tiles = "".join(figure(p) for p in PHOTOS)
    return (
        '<section class="section" id="gallery">\n'
        '  <div class="container">\n'
        '    <div class="rail rail-photos">\n'
        '      <div class="rail-head">\n'
        '        <div class="section-head">'
        f'<span class="section-tag">{tag}</span><h2>{head}</h2><p>{lead}</p>'
        "</div>\n"
        '        <div class="rail-nav">'
        f'<button class="rail-btn rail-prev" type="button" aria-label="Previous photo">{ARROW_L}</button>'
        f'<button class="rail-btn rail-next" type="button" aria-label="Next photo">{ARROW_R}</button>'
        "</div>\n"
        "      </div>\n"
        '      <div class="rail-track" tabindex="0" role="group" aria-label="Photographs from our jobs">'
        f"{tiles}</div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>"
    )


def main():
    check = "--check" in sys.argv
    touched, missing, stale = [], [], []

    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        page = os.path.basename(path)
        html = open(path, encoding="utf-8").read()
        if "<!-- gallery:start -->" not in html:
            continue
        if page not in HEADS:
            missing.append(page + " (no heading defined)")
            continue

        payload = "<!-- gallery:start -->\n" + gallery_html(page) + "\n<!-- gallery:end -->"
        updated = MARK.sub(lambda _: payload, html, count=1)
        if updated == html:
            continue
        if check:
            stale.append(page)
        else:
            open(path, "w", encoding="utf-8").write(updated)
            touched.append(page)

    for src, _, _, _, _ in PHOTOS:
        if not os.path.exists(os.path.join(ROOT, "images", src)):
            missing.append("images/" + src + " (file not found)")

    if check:
        if stale or missing:
            print("stale: " + ", ".join(stale or ["none"]))
            print("problems: " + ", ".join(missing or ["none"]))
            return 1
        print("every gallery is in sync")
        return 0

    print("{} photos -> {} page(s): {}".format(
        len(PHOTOS), len(touched), ", ".join(touched) or "none already current"))
    if missing:
        print("problems: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
