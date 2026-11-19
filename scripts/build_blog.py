#!/usr/bin/env python3
"""Build the static blog for isbdomesticstaff.pk.

Inputs
  content/topics.json          queue of topics; entries with "status": "published" are built
  content/blog/<slug>.html     article body (HTML fragment, no <html>/<head>, no <h1>)

Outputs
  blog/<slug>/index.html       one page per published post
  blog/index.html              listing page, newest first
  sitemap.xml, robots.txt

Run from the repository root:
  python3 scripts/build_blog.py                       rebuild everything
  python3 scripts/build_blog.py --next                print the next pending topic
  python3 scripts/build_blog.py --publish SLUG "DESC" mark SLUG published now, then rebuild
"""
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://isbdomesticstaff.pk"
PHONE = "0310 521 4309"
PHONE_TEL = "+923105214309"
WA = "923105214309"
ASSET_V = "7"
MIN_WORDS = 1800

U = "https://images.unsplash.com/"
COVERS = {
    "Maids & Housekeepers": U + "photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=1200&q=75",
    "Cooks & Chefs": U + "photo-1577219491135-ce391730fb2c?auto=format&fit=crop&w=1200&q=75",
    "Drivers": U + "photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&w=1200&q=75",
    "Nannies & Babysitters": U + "photo-1503454537195-1dcabb73ffb9?auto=format&fit=crop&w=1200&q=75",
    "Patient & Elderly Care": U + "photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&w=1200&q=75",
    "Watchmen & Security": U + "photo-1590650516494-0c8e4a4dd67e?auto=format&fit=crop&w=1200&q=75",
    "Office Staff": U + "photo-1560250097-0b93528c311a?auto=format&fit=crop&w=1200&q=75",
    "Cleaners": U + "photo-1527515637462-cff94eecc1ac?auto=format&fit=crop&w=1200&q=75",
    "Gardeners": U + "photo-1416879595882-3373a0480b5b?auto=format&fit=crop&w=1200&q=75",
    "Salaries & Costs": U + "photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=1200&q=75",
    "Hiring Guides": U + "photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1200&q=75",
}
DEFAULT_COVER = "/assets/img/hero-staff.webp"
FALLBACK_KIND = {
    "Maids & Housekeepers": "maid", "Cooks & Chefs": "cook", "Drivers": "driver",
    "Nannies & Babysitters": "babysitter", "Patient & Elderly Care": "care",
    "Watchmen & Security": "watchman", "Office Staff": "office", "Cleaners": "cleaner",
}

e = html.escape


def words(fragment):
    return len(re.sub(r"<[^>]+>", " ", fragment).split())


def fmt_date(iso):
    return datetime.fromisoformat(iso).strftime("%d %B %Y")


def cover_for(t):
    return t.get("image") or COVERS.get(t["category"], DEFAULT_COVER)


def faq_schema(fragment):
    """Build FAQPage JSON-LD from <section class="faq"> with <h3> question + <p> answer pairs."""
    m = re.search(r'<section class="faq"[^>]*>(.*?)</section>', fragment, re.S)
    if not m:
        return ""
    pairs = re.findall(r"<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>", m.group(1), re.S)
    if not pairs:
        return ""
    strip = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip(q),
             "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in pairs
        ],
    }
    return '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False)


def head(title, description, url, image, extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#0b3d7a">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image if image.startswith('http') else SITE + image}">
  <link rel="icon" type="image/png" href="/assets/img/logo-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Caveat:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css?v={ASSET_V}">
  <link rel="stylesheet" href="/assets/css/blog.css?v={ASSET_V}">
  {extra}
</head>
<body class="blog-body">
"""


SPRITE = None


def sprite():
    """Reuse the icon sprite from the home page so blog pages share the same icons."""
    global SPRITE
    if SPRITE is None:
        src = (ROOT / "index.html").read_text(encoding="utf-8")
        m = re.search(r'(<svg width="0" height="0".*?</svg>)', src, re.S)
        SPRITE = m.group(1) if m else ""
    return SPRITE


def header():
    return f"""{sprite()}
<div class="progress" id="progress"></div>
<header class="header" id="header">
  <div class="container header__inner">
    <a href="/" class="brand" aria-label="ISB Domestic Staff home">
      <img src="/assets/img/logo.png" alt="ISB Domestic Staff" class="brand__logo" width="600" height="163">
    </a>
    <nav class="nav" id="nav" aria-label="Main">
      <a href="/" class="nav__link">Home</a>
      <a href="/#why" class="nav__link">About Us</a>
      <a href="/#services" class="nav__link">Our Services</a>
      <a href="/#how" class="nav__link">For Employers</a>
      <a href="/blog/" class="nav__link is-active">Blog</a>
      <a href="/#contact" class="nav__link">Contact</a>
      <a href="/#contact" class="btn btn--primary nav__cta-mobile">Hire Staff Now <svg class="ic"><use href="#i-arrow"/></svg></a>
    </nav>
    <div class="header__actions">
      <a href="tel:{PHONE_TEL}" class="header__phone">
        <span class="header__phone-ic"><svg class="ic"><use href="#i-phone"/></svg></span>
        <span><strong>{PHONE}</strong><small>Mon - Sat 9AM - 8PM</small></span>
      </a>
      <a href="/#contact" class="btn btn--primary btn--glow header__cta">Hire Staff Now <svg class="ic"><use href="#i-arrow"/></svg></a>
      <button class="burger" id="burger" aria-label="Open menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
"""


def footer():
    maps = "https://www.google.com/maps/search/?api=1&amp;query=Chandni+Chowk+Rawalpindi"
    return f"""
<footer class="footer">
  <div class="container footer__top">
    <a href="/" class="brand" aria-label="ISB Domestic Staff home">
      <img src="/assets/img/logo.png" alt="ISB Domestic Staff" class="brand__logo" width="600" height="163" loading="lazy">
    </a>
    <div class="footer__mid">
      <nav class="footer__nav" aria-label="Footer">
        <a href="/">Home</a><a href="/#why">About Us</a><a href="/#services">Our Services</a><a href="/blog/">Blog</a><a href="/#contact">Contact</a>
      </nav>
    </div>
    <div class="footer__tag">
      <p>A Trusted Name in Domestic Staffing<br>in Islamabad &amp; Rawalpindi</p>
      <a href="{maps}" class="footer__addr" target="_blank" rel="noopener"><svg class="ic"><use href="#i-pin"/></svg>Chandni Chowk, Rawalpindi</a>
      <a href="tel:{PHONE_TEL}" class="footer__addr"><svg class="ic"><use href="#i-phone"/></svg>{PHONE}</a>
    </div>
  </div>
  <div class="container footer__bottom">
    <span>&copy; <span id="year">2026</span> ISB Domestic Staff. All rights reserved.</span>
    <span>Made with <svg class="ic ic--fill heart-red"><use href="#i-heart"/></svg> for Stronger Families &middot; Powered by <strong class="powered">RX Direct</strong></span>
  </div>
  <div class="container footer__credit">
    Designed &amp; Developed by <a href="https://inventiveclicks.com/" target="_blank" rel="noopener">Inventive Clicks</a>
  </div>
</footer>
<a href="https://wa.me/{WA}?text=Assalam%20o%20Alaikum%2C%20I%20need%20domestic%20staff." class="fab-wa" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">
  <svg class="ic"><use href="#i-wa"/></svg><span class="fab-wa__tip">Chat with us</span>
</a>
<button class="to-top" id="toTop" aria-label="Back to top"><svg class="ic"><use href="#i-up"/></svg></button>
<script src="/assets/js/main.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


def card(t):
    kind = FALLBACK_KIND.get(t["category"], "family")
    return f"""      <a href="/blog/{t['slug']}/" class="post-card reveal" data-cat="{e(t['category'])}">
        <div class="post-card__img"><img src="{cover_for(t)}" alt="{e(t['title'])}" loading="lazy" data-fallback="{kind}"><span class="post-card__cat">{e(t['category'])}</span></div>
        <div class="post-card__body">
          <span class="post-card__meta">{fmt_date(t['published'])} &middot; {t['readMinutes']} min read</span>
          <h2>{e(t['title'])}</h2>
          <p>{e(t['description'])}</p>
          <span class="post-card__more">Read more <svg class="ic"><use href="#i-arrow"/></svg></span>
        </div>
      </a>"""


def build_post(t, posts):
    fragment = (ROOT / "content/blog" / f"{t['slug']}.html").read_text(encoding="utf-8")
    url = f"{SITE}/blog/{t['slug']}/"
    cover = cover_for(t)
    article_ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": t["title"],
        "description": t["description"],
        "image": cover if cover.startswith("http") else SITE + cover,
        "datePublished": t["published"],
        "dateModified": t.get("updated", t["published"]),
        "mainEntityOfPage": url,
        "author": {"@type": "Organization", "name": "ISB Domestic Staff"},
        "publisher": {"@type": "Organization", "name": "ISB Domestic Staff",
                      "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo.png"}},
    }
    crumbs_ld = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": t["title"], "item": url},
        ],
    }
    extra = ('<script type="application/ld+json">%s</script>\n  <script type="application/ld+json">%s</script>\n  %s'
             % (json.dumps(article_ld, ensure_ascii=False), json.dumps(crumbs_ld, ensure_ascii=False), faq_schema(fragment)))
    related = [p for p in posts if p["slug"] != t["slug"] and p["category"] == t["category"]]
    related += [p for p in posts if p["slug"] != t["slug"] and p not in related]
    related_html = "\n".join(card(p) for p in related[:3])
    kind = FALLBACK_KIND.get(t["category"], "family")
    page = head(f"{t['title']} | ISB Domestic Staff", t["description"], url, cover, extra) + header() + f"""
<main>
  <section class="post-hero">
    <div class="container">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/blog/">Blog</a><span>/</span><span>{e(t['category'])}</span></nav>
      <span class="post-hero__cat">{e(t['category'])}</span>
      <h1>{e(t['title'])}</h1>
      <p class="post-hero__meta"><svg class="ic"><use href="#i-calendar"/></svg>{fmt_date(t['published'])} <span>&middot;</span> <svg class="ic"><use href="#i-clock"/></svg>{t['readMinutes']} min read <span>&middot;</span> ISB Domestic Staff Team</p>
    </div>
  </section>

  <div class="container post-layout">
    <article class="post">
      <div class="post__cover"><img src="{cover}" alt="{e(t['title'])}" data-fallback="{kind}"></div>
      <div class="post__content">
{fragment}
      </div>
      <div class="post-cta">
        <div>
          <h2>Need trusted domestic staff?</h2>
          <p>Verified maids, cooks, drivers, nannies, patient attendants and more in Islamabad &amp; Rawalpindi &mdash; with a replacement guarantee.</p>
        </div>
        <div class="post-cta__btns">
          <a href="https://wa.me/{WA}?text={e('Assalam o Alaikum, I read your article "' + t['title'] + '" and need domestic staff.')}" class="btn btn--primary" target="_blank" rel="noopener">WhatsApp Us <svg class="ic"><use href="#i-wa"/></svg></a>
          <a href="tel:{PHONE_TEL}" class="btn btn--ghost"><svg class="ic"><use href="#i-phone"/></svg> {PHONE}</a>
        </div>
      </div>
    </article>

    <aside class="post-side">
      <div class="side-box side-box--cta">
        <h3>Hire Verified Staff</h3>
        <ul class="ticks">
          <li><svg class="ic"><use href="#i-check"/></svg>Background checked</li>
          <li><svg class="ic"><use href="#i-check"/></svg>Trained &amp; experienced</li>
          <li><svg class="ic"><use href="#i-check"/></svg>Replacement guarantee</li>
        </ul>
        <a href="https://wa.me/{WA}" class="btn btn--primary" target="_blank" rel="noopener">Get Staff Today</a>
        <a href="tel:{PHONE_TEL}" class="side-box__phone"><svg class="ic"><use href="#i-phone"/></svg>{PHONE}</a>
      </div>
      <div class="side-box">
        <h3>Our Services</h3>
        <ul class="side-links">
          <li><a href="/#services">Maids &amp; Housekeepers</a></li>
          <li><a href="/#services">Cooks &amp; Chefs</a></li>
          <li><a href="/#services">Drivers</a></li>
          <li><a href="/#services">Nannies &amp; Babysitters</a></li>
          <li><a href="/#services">Patient &amp; Elderly Care</a></li>
          <li><a href="/#services">Watchmen &amp; Office Boys</a></li>
        </ul>
      </div>
    </aside>
  </div>

  <section class="section related">
    <div class="container">
      <div class="section-head"><p class="eyebrow eyebrow--center">Keep Reading</p><h2>Related Articles</h2></div>
      <div class="post-grid">
{related_html}
      </div>
    </div>
  </section>
</main>
""" + footer()
    out = ROOT / "blog" / t["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def build_index(posts):
    cats = sorted({p["category"] for p in posts})
    chips = '<button class="chip is-active" data-filter="all">All</button>' + "".join(
        f'<button class="chip" data-filter="{e(c)}">{e(c)}</button>' for c in cats)
    cards = "\n".join(card(p) for p in posts) or '      <p class="empty">New articles are on the way. Check back soon!</p>'
    desc = ("Guides and tips on hiring maids, cooks, drivers, nannies, patient attendants and other "
            "domestic staff in Islamabad and Rawalpindi, from ISB Domestic Staff.")
    page = head("Blog | Domestic Staff Hiring Guides | ISB Domestic Staff", desc, SITE + "/blog/", DEFAULT_COVER) + header() + f"""
<main>
  <section class="blog-hero">
    <span class="blob blob--1" aria-hidden="true"></span><span class="blob blob--3" aria-hidden="true"></span>
    <div class="container">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><span>Blog</span></nav>
      <p class="eyebrow">ISB Domestic Staff Blog</p>
      <h1>Domestic Staff <span class="text-grad">Tips, Guides &amp; Advice</span></h1>
      <p class="blog-hero__lead">Everything you need to hire, manage and keep reliable household staff in Islamabad &amp; Rawalpindi.</p>
    </div>
  </section>

  <section class="section blog-list">
    <div class="container">
      <div class="chips" role="toolbar" aria-label="Filter by category">{chips}</div>
      <div class="post-grid" id="postGrid">
{cards}
      </div>
    </div>
  </section>
</main>
<script>
document.querySelectorAll('.chip').forEach(function (c) {{
  c.addEventListener('click', function () {{
    document.querySelectorAll('.chip').forEach(function (x) {{ x.classList.toggle('is-active', x === c); }});
    var f = c.dataset.filter;
    document.querySelectorAll('#postGrid .post-card').forEach(function (p) {{
      p.style.display = (f === 'all' || p.dataset.cat === f) ? '' : 'none';
    }});
  }});
}});
</script>
""" + footer()
    (ROOT / "blog").mkdir(exist_ok=True)
    (ROOT / "blog/index.html").write_text(page, encoding="utf-8")


def build_sitemap(posts):
    today = datetime.now(timezone.utc).date().isoformat()
    urls = [(SITE + "/", today), (SITE + "/blog/", posts[0]["published"][:10] if posts else today)]
    urls += [(f"{SITE}/blog/{p['slug']}/", p.get("updated", p["published"])[:10]) for p in posts]
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nDisallow: /content/\nDisallow: /scripts/\nDisallow: /deploy/\n\n"
        f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def publish(slug, description):
    """Mark a topic as published now (UTC) with its meta description."""
    path = ROOT / "content/topics.json"
    topics = json.loads(path.read_text(encoding="utf-8"))
    t = next(t for t in topics if t["slug"] == slug)
    if not (ROOT / "content/blog" / f"{slug}.html").exists():
        raise SystemExit(f"content/blog/{slug}.html is missing")
    n = words((ROOT / "content/blog" / f"{slug}.html").read_text(encoding="utf-8"))
    if n < MIN_WORDS:
        raise SystemExit(f"{slug}: {n} words, below the {MIN_WORDS}-word minimum; not published")
    if not 120 <= len(description) <= 165:
        raise SystemExit(f"meta description is {len(description)} characters; aim for 140-160")
    t["status"] = "published"
    t["published"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    t["description"] = description
    path.write_text(json.dumps(topics, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def next_topic():
    topics = json.loads((ROOT / "content/topics.json").read_text(encoding="utf-8"))
    t = next((t for t in topics if t["status"] != "published"), None)
    print(json.dumps(t, ensure_ascii=False) if t else "NONE")


def main():
    topics = json.loads((ROOT / "content/topics.json").read_text(encoding="utf-8"))
    for t in topics:
        if t["status"] == "published":
            frag = (ROOT / "content/blog" / f"{t['slug']}.html").read_text(encoding="utf-8")
            t["readMinutes"] = max(1, round(words(frag) / 220))
    posts = sorted((t for t in topics if t["status"] == "published"),
                   key=lambda t: t["published"], reverse=True)
    for t in posts:
        build_post(t, posts)
    build_index(posts)
    build_sitemap(posts)
    pending = sum(1 for t in topics if t["status"] != "published")
    print(f"Built {len(posts)} posts; {pending} topics still pending.")


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["--next"]:
        next_topic()
    elif sys.argv[1:2] == ["--publish"]:
        publish(sys.argv[2], sys.argv[3])
        main()
    else:
        main()
