from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))

CANONICAL = SITE["canonical"].rstrip("/") + "/"
BRAND = SITE["brand"]["name"]
EMAIL = SITE["contact"]["email"]
INSTA = SITE["contact"]["instagram"]

PAGES = {
    "about": {
        "path": ROOT / "about" / "index.html",
        "canonical": CANONICAL + "about/",
        "seo": SITE["seo"]["about"],
        "eyebrow": "London · Interior Design",
        "h1": "About Heema Chhabra Design Consultant",
        "lead": SITE["seo"]["about"]["description"],
        "body": lambda s: f"""
<p>{s['introduction']['paragraphs'][0]}</p>
<p>{s['introduction']['paragraphs'][1]}</p>
<p>{s['introduction']['paragraphs'][2]}</p>
<h2>{s['philosophy']['heading']}</h2>
<p>{s['philosophy']['paragraphs'][0]}</p>
<p>{s['philosophy']['paragraphs'][1]}</p>
<h2>{s['founder']['heading']}</h2>
<p>{s['founder']['body']}</p>
<p class="hcdc-meta">Based in {s['location']['label']}. {s['location']['consultationNote']}</p>
""",
    },
    "services": {
        "path": ROOT / "services" / "index.html",
        "canonical": CANONICAL + "services/",
        "seo": SITE["seo"]["services"],
        "eyebrow": "Scope · Tailored per brief",
        "h1": "Interior Design Services",
        "lead": SITE["services"]["intro"]["body"],
        "body": lambda s: f"""
<h2>{s['services']['residential']['heading']}</h2>
<p>{s['services']['residential']['body']}</p>
<ul>{"".join(f"<li>{x}</li>" for x in s['services']['residential']['rooms'])}</ul>
<p class="hcdc-meta">Scope where appropriate: {"; ".join(s['services']['residential']['scope'])}. {s['services']['residential']['scopeNote']}</p>
<h2>{s['services']['privateResidences']['heading']}</h2>
<p>{s['services']['privateResidences']['body']}</p>
<h2>{s['services']['commercial']['heading']}</h2>
<p>{s['services']['commercial']['body']}</p>
<h2>{s['services']['development']['heading']}</h2>
<p>{s['services']['development']['body']}</p>
<ul>{"".join(f"<li>{x}</li>" for x in s['services']['development']['scope'])}</ul>
""",
    },
    "approach": {
        "path": ROOT / "approach" / "index.html",
        "canonical": CANONICAL + "approach/",
        "seo": SITE["seo"]["approach"],
        "eyebrow": SITE["approach"]["subheading"],
        "h1": SITE["approach"]["heading"],
        "lead": SITE["approach"]["intro"],
        "body": lambda s: "".join(
            f"<h2>{stage['label']}</h2><h3>{stage['title']}</h3><p>{stage['body']}</p>"
            for stage in s["approach"]["stages"]
        ),
    },
    "contact": {
        "path": ROOT / "contact" / "index.html",
        "canonical": CANONICAL + "contact/",
        "seo": SITE["seo"]["contact"],
        "eyebrow": "Enquiries · By appointment",
        "h1": SITE["contactPage"]["heading"],
        "lead": SITE["contactPage"]["body"],
        "body": lambda s: f"""
<p><strong>{s['contactPage']['location']}</strong> — {s['contactPage']['consultationNote']}</p>
<p>Email: <a href="mailto:{s['contactPage']['email']}">{s['contactPage']['email']}</a><br>
Instagram: <a href="{s['contactPage']['instagram']}" target="_blank" rel="noopener noreferrer">{s['contactPage']['instagram']}</a></p>
<h2>What to include in your enquiry</h2>
<ul><li>Project location</li><li>Property or space type</li><li>What you would like to change</li><li>Current stage of the project</li></ul>
<h2>Questions</h2>
<dl class="hcdc-faq">{"".join(f"<dt>{item['q']}</dt><dd>{item['a']}</dd>" for item in s['faq'])}</dl>
""",
    },
}


def render(page_key: str) -> str:
    cfg = PAGES[page_key]
    seo = cfg["seo"]
    ey = cfg["eyebrow"]
    h1 = cfg["h1"]
    lead = cfg["lead"]
    body = cfg["body"](SITE)
    canonical = cfg["canonical"]
    title = seo["title"]
    desc = seo["description"]
    og_image = CANONICAL + "og-image.jpg"

    nav = "".join(
        f'<a href="/{k}/"{" aria-current=\"page\"" if k==page_key else ""}>{k.title()}</a>'
        for k in ["about", "services", "approach", "contact"]
    )

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "@id": CANONICAL + "#organization", "name": BRAND, "alternateName": "HCDC", "url": CANONICAL, "sameAs": [INSTA]},
            {"@type": "Person", "@id": CANONICAL + "#heema-chhabra", "name": "Heema Chhabra", "jobTitle": "Design Consultant", "worksFor": {"@id": CANONICAL + "#organization"}},
            {"@type": "WebSite", "@id": CANONICAL + "#website", "url": CANONICAL, "name": BRAND, "publisher": {"@id": CANONICAL + "#organization"}},
            {"@type": "WebPage", "@id": canonical + "#webpage", "url": canonical, "name": title, "isPartOf": {"@id": CANONICAL + "#website"}, "about": {"@id": CANONICAL + "#organization"}},
        ],
    }
    if page_key == "services":
        ld["@graph"].extend([
            {"@type": "Service", "@id": CANONICAL + "#residential-interior-design", "name": "Residential Interior Design", "provider": {"@id": CANONICAL + "#organization"}},
            {"@type": "Service", "@id": CANONICAL + "#commercial-interior-design", "name": "Commercial Interior Design", "provider": {"@id": CANONICAL + "#organization"}},
            {"@type": "Service", "@id": CANONICAL + "#development-interior-design", "name": "Builder & Property Development Interiors", "provider": {"@id": CANONICAL + "#organization"}},
        ])
    ld_json = json.dumps(ld, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{BRAND} — Interior Design London">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_image}">
<meta name="twitter:image:alt" content="{BRAND} — Interior Design London">
<link rel="icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/hcdc-editorial.css">
<script type="application/ld+json">{ld_json}</script>
</head>
<body>
<a class="hcdc-skip" href="#main">Skip to content</a>
<header class="hcdc-header">
<div class="hcdc-header__inner">
<a class="hcdc-brand" href="/">{BRAND.replace("Heema Chhabra ", 'Heema <span>Chhabra</span> ')}</a>
<nav class="hcdc-nav" aria-label="Primary">{nav}<a href="/">Home</a></nav>
</div>
</header>
<main id="main" class="hcdc-main">
<article class="hcdc-article">
<p class="hcdc-eyebrow">{ey}</p>
<h1 class="hcdc-h1">{h1}</h1>
<p class="hcdc-lead">{lead}</p>
<div class="hcdc-prose">{body}</div>
<div class="hcdc-cta-row"><a class="hcdc-cta" href="mailto:{EMAIL}">Start a conversation</a><a class="hcdc-cta hcdc-cta--ghost" href="/">Explore the gallery</a></div>
</article>
</main>
<footer class="hcdc-footer"><div class="hcdc-footer__inner"><span>{BRAND} · {SITE['location']['label']}</span><span><a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{INSTA}" target="_blank" rel="noopener noreferrer">Instagram</a></span></div></footer>
</body>
</html>
"""


def main() -> None:
    for key, cfg in PAGES.items():
        html = render(key)
        cfg["path"].parent.mkdir(parents=True, exist_ok=True)
        cfg["path"].write_text(html, encoding="utf-8")
        print(f"wrote {cfg['path']}")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8") if (ROOT / "sitemap.xml").exists() else ""
    urls = [CANONICAL, CANONICAL + "about/", CANONICAL + "services/", CANONICAL + "approach/", CANONICAL + "contact/"]
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls) + "\n</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    print("sitemap updated:", len(urls), "urls")


if __name__ == "__main__":
    main()
