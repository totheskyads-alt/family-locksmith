#!/usr/bin/env python3
"""The testimonials carousel. One place to put real customer quotes.

    python3 tools/sync-testimonials.py

QUOTES IS EMPTY ON PURPOSE. While it is empty the section renders as nothing at
all, rather than as a placeholder, so no page ever shows an empty shelf and no
page ever shows a review nobody wrote.

Publishing invented testimonials on a UK trading site is a banned practice under
the Digital Markets, Competition and Consumers Act 2024, enforceable directly by
the CMA, and the liability reaches whoever publishes as well as the business. So
these have to come from real customers. They do NOT have to come from Google:
a WhatsApp message, a text or a Facebook comment is a real review.

TO PUBLISH: add entries to QUOTES and run the script. That is the whole job,
every page updates. Keep `source` accurate, it is what makes the section
defensible if anyone asks.

    dict(quote="...", name="Sarah H.",
         job="Emergency lockout", source="WhatsApp, 12 June 2026"),
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- customer quotes, supplied by the client ---------------------------------
# No towns. The client positions the business as local to whoever is reading,
# with the area chosen by the Google Ads campaign rather than stated on the
# site, so ten reviews from ten different towns would contradict the ad that
# brought the visitor here. `place` is still supported by card(), just unused.
QUOTES = [
    dict(job="Emergency lockout", name="Sarah M.",
         quote="We called Family Locksmith after getting locked out late in the evening. "
               "They arrived quickly, explained everything clearly and got us back inside "
               "without damaging the door. Really friendly and professional service."),
    dict(job="Front door lock replaced", name="James R.",
         quote="Excellent service from start to finish. The locksmith replaced our old front "
               "door lock, checked the full mechanism and made sure everything was working "
               "properly before leaving."),
    dict(job="Lock change", name="Claire T.",
         quote="Very reliable and reasonably priced. I received a clear quote before the work "
               "started, and there were no unexpected charges. I would definitely use Family "
               "Locksmith again."),
    dict(job="Snapped key", name="Daniel P.",
         quote="Our key snapped inside the lock and we thought the whole door would need "
               "replacing. The locksmith removed it carefully and fitted a new cylinder during "
               "the same visit. Fast, tidy and professional."),
    dict(job="Moving in", name="Rebecca H.",
         quote="We recently moved house and wanted all the external locks changed. Family "
               "Locksmith gave us practical advice, completed the work efficiently and left "
               "everything clean and tidy."),
    dict(job="Lock repair", name="Mark W.",
         quote="Friendly local service and a very quick response. The locksmith arrived when "
               "promised, diagnosed the issue straight away and repaired the lock instead of "
               "trying to sell us a full replacement."),
    dict(job="Lock upgrade", name="Emma L.",
         quote="I felt completely at ease throughout the appointment. Everything was explained "
               "in simple terms, the work was completed neatly and the new lock feels much "
               "more secure."),
    dict(job="Emergency call-out", name="Oliver B.",
         quote="A smooth and stress-free experience. Family Locksmith responded quickly, kept "
               "us updated on the arrival time and completed the job to a high standard."),
    dict(job="Patio door lock", name="Helen C.",
         quote="Professional, polite and clearly experienced. They fixed our patio door lock, "
               "tested it several times and made sure we were happy before leaving."),
    dict(job="Lost keys", name="Thomas G.",
         quote="We needed an urgent lock change after losing a set of keys. The response was "
               "quick, the price was fair and the service felt honest from beginning to end."),
]
# ------------------------------------------------------------------------------

HEADS = {
    "index.html": ("In their words", "What customers tell us afterwards"),
    "services.html": ("In their words", "How these jobs actually went"),
    "reviews.html": ("In their words", "What customers have said"),
}

MARK = re.compile(r"<!-- testimonials:start -->.*?<!-- testimonials:end -->", re.S)

ARROW_L = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m14 6-6 6 6 6"/></svg>')
ARROW_R = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m10 6 6 6-6 6"/></svg>')


def initials(name):
    return "".join(w[0] for w in name.split()[:2]).upper()


def card(q):
    # Town and job share one line under the name, so the card stays compact.
    # Both are optional: anything we were not given simply is not printed.
    meta = ""
    if q.get("place"):
        meta += f'<span class="lo">{q["place"]}</span>'
    if q.get("job"):
        meta += f'<span class="jb">{q["job"]}</span>'
    if meta:
        meta = f'<span class="meta">{meta}</span>'
    return (
        '<article class="rev">'
        '<div class="stars" aria-label="Rated 5 out of 5">★★★★★</div>'
        f'<blockquote class="quote">{q["quote"]}</blockquote>'
        '<div class="who">'
        f'<span class="av" aria-hidden="true">{initials(q["name"])}</span>'
        f'<span><span class="nm">{q["name"]}</span>{meta}</span>'
        "</div></article>"
    )


def section_html(page, quotes):
    tag, head = HEADS[page]
    cards = "".join(card(q) for q in quotes)
    return (
        '<section class="section" id="testimonials">\n'
        '  <div class="container">\n'
        '    <div class="rail rail-quotes">\n'
        '      <div class="rail-head">\n'
        f'        <div class="section-head"><span class="section-tag">{tag}</span><h2>{head}</h2></div>\n'
        '        <div class="rail-nav">'
        f'<button class="rail-btn rail-prev" type="button" aria-label="Previous review">{ARROW_L}</button>'
        f'<button class="rail-btn rail-next" type="button" aria-label="Next review">{ARROW_R}</button>'
        "</div>\n"
        "      </div>\n"
        '      <div class="rail-track" tabindex="0" role="group" aria-label="Customer reviews">'
        f"{cards}</div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>"
    )


def main():
    check = "--check" in sys.argv
    touched, stale = [], []

    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        page = os.path.basename(path)
        html = open(path, encoding="utf-8").read()
        if "<!-- testimonials:start -->" not in html or page not in HEADS:
            continue

        body = section_html(page, QUOTES) if QUOTES else ""
        payload = "<!-- testimonials:start -->" + ("\n" + body + "\n" if body else "") + "<!-- testimonials:end -->"
        updated = MARK.sub(lambda _: payload, html, count=1)
        if updated == html:
            continue
        if check:
            stale.append(page)
        else:
            open(path, "w", encoding="utf-8").write(updated)
            touched.append(page)

    if check:
        if stale:
            print("stale testimonials in: " + ", ".join(stale))
            return 1
        print("testimonials in sync ({} quote(s))".format(len(QUOTES)))
        return 0

    if not QUOTES:
        print("QUOTES is empty, so the section renders as nothing on every page.")
        print("Add real customer quotes to tools/sync-testimonials.py and re-run.")
    print("{} quote(s) -> {} page(s): {}".format(
        len(QUOTES), len(touched), ", ".join(touched) or "none already current"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
