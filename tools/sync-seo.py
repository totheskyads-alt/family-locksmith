#!/usr/bin/env python3
"""Keep canonical URLs, social cards, structured data and the sitemap in sync.

Everything derives from BASE_URL, so pointing the site at a real domain later is
a one-line change followed by `python3 tools/sync-seo.py`.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- edit these when the business details or the domain change -----------------
BASE_URL = "https://totheskyads-alt.github.io/family-locksmith"
BUSINESS = "Family Locksmith"
PHONE_E164 = "+447597379838"
AREA_SERVED = "England"
OG_IMAGE = "images/og-card.jpg"
# -------------------------------------------------------------------------------

# Pages that should not be indexed or listed.
EXCLUDE = {"hero-options.html"}

# Rough priority hints for the sitemap.
PRIORITY = {"index.html": "1.0", "services.html": "0.9", "contact.html": "0.9", "areas.html": "0.8"}

SCHEMA = """<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Locksmith","@id":"{base}/#business",
"name":"{name}","url":"{base}/","image":"{base}/{og}","telephone":"{phone}",
"priceRange":"££","areaServed":{{"@type":"AdministrativeArea","name":"{area}"}},
"address":{{"@type":"PostalAddress","addressCountry":"GB","addressRegion":"{area}"}},
"openingHoursSpecification":[{{"@type":"OpeningHoursSpecification",
"dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
"opens":"00:00","closes":"23:59"}}],
"contactPoint":{{"@type":"ContactPoint","telephone":"{phone}","contactType":"emergency",
"availableLanguage":"English","areaServed":"GB"}}}}
</script>"""


def head_block(page, title, description):
    canonical = f"{BASE_URL}/" if page == "index.html" else f"{BASE_URL}/{page}"
    block = [
        f'<link rel="canonical" href="{canonical}">',
        '<meta name="robots" content="index,follow">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{BUSINESS}">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{description}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:image" content="{BASE_URL}/{OG_IMAGE}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{description}">',
        f'<meta name="twitter:image" content="{BASE_URL}/{OG_IMAGE}">',
    ]
    if page == "index.html":
        block.append(SCHEMA.format(base=BASE_URL, name=BUSINESS, phone=PHONE_E164,
                                   area=AREA_SERVED, og=OG_IMAGE))
    return "\n".join(block)


MARK_OPEN, MARK_CLOSE = "<!-- seo:start -->", "<!-- seo:end -->"


def main():
    pages = []
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        page = os.path.basename(path)
        if page in EXCLUDE:
            continue
        html = open(path, encoding="utf-8").read()

        title = re.search(r"<title>(.*?)</title>", html, re.S)
        desc = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
        title = title.group(1).strip() if title else BUSINESS
        desc = desc.group(1).strip() if desc else ""

        payload = f"{MARK_OPEN}\n{head_block(page, title, desc)}\n{MARK_CLOSE}"

        if MARK_OPEN in html:
            html = re.sub(re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE),
                          payload, html, flags=re.S)
        else:
            html = html.replace("</head>", payload + "\n</head>", 1)

        open(path, "w", encoding="utf-8").write(html)
        pages.append(page)

    # sitemap
    urls = []
    for page in pages:
        loc = f"{BASE_URL}/" if page == "index.html" else f"{BASE_URL}/{page}"
        urls.append(f"  <url><loc>{loc}</loc><priority>{PRIORITY.get(page,'0.7')}</priority></url>")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)

    disallow = "".join("Disallow: /{}\n".format(p) for p in sorted(EXCLUDE))
    robots = ("User-agent: *\nAllow: /\n" + disallow +
              "\nSitemap: {}/sitemap.xml\n".format(BASE_URL))
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(robots)

    print(f"canonical + social + schema written to {len(pages)} pages")
    print(f"sitemap.xml: {len(urls)} urls | robots.txt written")


if __name__ == "__main__":
    main()
