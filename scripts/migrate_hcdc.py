from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
SITE_PATH = CONTENT_DIR / "site.json"
PROJECTS_PATH = CONTENT_DIR / "projects.json"

HTML_FILES = [ROOT / "index.html", ROOT / "_nuxt" / "index.html"]
PAYLOAD_FILES = [ROOT / "_nuxt" / "static" / "1679938011" / "payload.js"]
BUNDLE_FILES = list((ROOT / "_nuxt").glob("*.js"))


def load_site() -> dict:
    return json.loads(SITE_PATH.read_text(encoding="utf-8"))


def load_projects() -> dict:
    if PROJECTS_PATH.exists():
        return json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))
    return {"galleryLabel": "Selected Interior Work", "projects": []}


def build_about_content_block(site: dict) -> str:
    intro = site["introduction"]["paragraphs"]
    philosophy = site["philosophy"]
    approach = site["approach"]
    services = site["services"]
    contact = site["contactPage"]

    stages_html = "".join(
        f'<h3>{s["title"]}</h3><p>{s["body"]}</p>' for s in approach["stages"]
    )
    faq_html = "".join(
        f'<h3>{item["q"]}</h3><p>{item["a"]}</p>' for item in site.get("faq", [])
    )

    return (
        '<div class="desc-about tw-font-grotesk-rg tw-text-white tw-text-sm lg:tw-text-xs tw-leading-5 lg:tw-leading-4">'
        f'<p>{intro[0]}</p>'
        f'<p>{intro[1]}</p>'
        f'<p>{intro[2]}</p>'
        f'<h2>{philosophy["heading"]}</h2>'
        f'<p>{philosophy["paragraphs"][0]}</p>'
        f'<p>{philosophy["paragraphs"][1]}</p>'
        f'<h2>{approach["heading"]}</h2>'
        f'<p class="tw-italic tw-opacity-80">{approach["subheading"]}</p>'
        f'<p>{approach["intro"]}</p>'
        f'{stages_html}'
        f'<h2>{services["intro"]["heading"]}</h2>'
        f'<p>{services["intro"]["body"]}</p>'
        f'<h3>{services["residential"]["heading"]}</h3>'
        f'<p>{services["residential"]["body"]}</p>'
        f'<p class="tw-opacity-70">{" \u00b7 ".join(services["residential"]["rooms"])}</p>'
        f'<p class="tw-opacity-60 tw-text-xs">Scope where appropriate: {"; ".join(services["residential"]["scope"])}. {services["residential"]["scopeNote"]}</p>'
        f'<h3>{services["privateResidences"]["heading"]}</h3>'
        f'<p>{services["privateResidences"]["body"]}</p>'
        f'<h3>{services["commercial"]["heading"]}</h3>'
        f'<p>{services["commercial"]["body"]}</p>'
        f'<h3>{services["development"]["heading"]}</h3>'
        f'<p>{services["development"]["body"]}</p>'
        f'<p class="tw-opacity-60 tw-text-xs">{" \u00b7 ".join(services["development"]["scope"])}</p>'
        f'<h2>{site["founder"]["heading"]}</h2>'
        f'<p>{site["founder"]["body"]}</p>'
        f'<h2>{contact["heading"]}</h2>'
        f'<p>{contact["body"]}</p>'
        f'<p><strong>{contact["location"]}</strong> \u2014 {contact["consultationNote"]}</p>'
        f'<p><a href="mailto:{contact["email"]}" class="tw-underline tw-text-white">{contact["email"]}</a> \u00b7 <a href="{contact["instagram"]}" target="_blank" rel="noopener noreferrer" class="tw-underline tw-text-white">Instagram</a></p>'
        f'<h2>Questions</h2>'
        f'{faq_html}'
        '</div>'
    )


def build_about_block(site: dict) -> str:
    content_block = build_about_content_block(site)
    payload_inner = re.search(r'<div class="desc-about[^>]*>(.*)</div>', content_block, re.DOTALL).group(1)
    _ = payload_inner
    email = site["contact"]["email"]
    instagram = site["contact"]["instagram"]
    return (
        '<div class="about tw-fixed tw-right-0 lg:tw-h-screen tw-bg-black tw-z-40" role="dialog" aria-modal="true" aria-labelledby="hcdc-about-title">'
        '<button class="btn-close tw-absolute tw-right-6 lg:tw-right-20 tw-z-20 tw-font-grotesk-rg tw-text-sm tw-text-white focus:tw-outline-none focus:tw-ring-0 nocursor" type="button" aria-label="Close About and Contact panel">Close</button> '
        '<div class="lg:tw-grid tw-grid-cols-8 lg:tw-gap-20 tw-px-6 lg:tw-px-20 tw-py-6 lg:tw-py-20 tw-box-border about-content">'
        '<figure class="tw-w-1/2 lg:tw-w-full lg:tw-col-span-3 jsImage"><img data-src="/_nuxt/img/portrait-hcdc.jpg" alt="Heema Chhabra, founder of HCDC" class="tw-w-full tw-block tw-h-auto lazyLoad"></figure> '
        '<div class="lg:tw-col-span-4 tw-relative tw--top-2 tw-mt-20 lg:tw-mt-0 jsText">'
        '<h2 id="hcdc-about-title" class="tw-font-times-lt tw-text-2xl tw-text-white">Bespoke Interior Design in London</h2> '
        '<div class="tw-block lg:tw-hidden jsActions2">'
        f'<a href="mailto:{email}" rel="nofollow" class="tw-block tw-font-grotesk-rg tw-text-sm tw-text-white tw-underline tw-mt-10">{email}</a> '
        f'<a href="{instagram}" target="_blank" rel="noopener noreferrer" class="tw-block tw-underline tw-font-grotesk-rg tw-text-sm tw-text-white tw-block lg:tw-inline-block tw-mt-4 lg:tw-mt-0"><img data-src="/_nuxt/img/instagram.b6014cf.svg" alt="" class="tw-w-3 tw-h-3 tw-inline-block tw-mr-2 tw-relative lazyLoad" style="top:2px">Follow on Instagram</a></div> '
        f'{content_block}'
        '</div></div> '
        '<div class="actions tw-hidden lg:tw-flex tw-flex-col tw-gap-4 tw-absolute tw-right-20 tw-bottom-20 tw-z-20">'
        f'<a href="mailto:{email}" rel="nofollow" class="tw-font-grotesk-rg tw-text-sm tw-text-white tw-underline">Start a conversation</a>'
        '</div>'
    )


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Missing expected {label}")
    return text.replace(old, new, 1)


def patch_html(path: Path, site: dict) -> None:
    text = path.read_text(encoding="utf-8")
    title = site["seo"]["home"]["title"]
    description = site["seo"]["home"]["description"]
    canonical = site["canonical"]
    email = site["contact"]["email"]
    instagram = site["contact"]["instagram"]
    og_image = f'{canonical.rstrip("/")}/og-image.jpg'

    about_content_block = build_about_content_block(site)
    about_block = build_about_block(site)
    about_payload_html = re.search(r'<div class="desc-about[^>]*>(.*)</div>', about_content_block, re.DOTALL).group(1)
    about_title = "Bespoke Interior Design in London"
    about_description = site["seo"]["about"]["description"]
    generic_caption = ""

    about_content_1 = site["introduction"]["paragraphs"][1]
    about_content_2 = site["introduction"]["paragraphs"][2]

    text = text.replace('<html lang="en"', '<html lang="en-GB"')
    text = text.replace("<title>Heema Sahni - Interior Architecture &amp; Design</title>", f"<title>{title}</title>")
    text = text.replace(
        'name="description" content="Heema Sahni is a India-based Interior Architect with over a decade of experience."',
        f'name="description" content="{description}"',
    )
    text = text.replace(
        "<h2 class=\"tw-font-times-lt tw-text-2xl tw-text-white\">\n      HEEMA <span class=\"tw-font-grotesk-bd\">SAHNI CHHABRA</span> DESIGN\n    </h2>",
        "<h1 class=\"tw-font-times-lt tw-text-2xl tw-text-white\">\n      HEEMA <span class=\"tw-font-grotesk-bd\">CHHABRA</span> DESIGN CONSULTANT\n    </h1>",
    )
    text = text.replace(
        "<h2 class=\"tw-font-times-lt tw-text-2xl tw-text-white\">HEEMA <span class=\"tw-font-grotesk-bd\">SAHNI CHHABRA</span> DESIGN</h2>",
        "<h1 class=\"tw-font-times-lt tw-text-2xl tw-text-white\">HEEMA <span class=\"tw-font-grotesk-bd\">CHHABRA</span> DESIGN CONSULTANT</h1>",
    )
    text = re.sub(
        r'<h2(?P<attrs>[^>]*)>\s*HEEMA\s*<span class="tw-font-grotesk-bd">CHHABRA</span> DESIGN CONSULTANT\s*</h1>',
        r'<h1\g<attrs>>\n      HEEMA <span class="tw-font-grotesk-bd">CHHABRA</span> DESIGN CONSULTANT\n    </h1>',
        text,
        count=1,
    )
    text = text.replace(
        "HEEMA <span class=\"tw-font-grotesk-bd\">SAHNI CHHABRA</span> DESIGN",
        "HEEMA <span class=\"tw-font-grotesk-bd\">CHHABRA</span> DESIGN CONSULTANT",
    )
    text = text.replace('<h1 id="hcdc-about-title"', '<h2 id="hcdc-about-title"')
    text = text.replace('</h1> <div class="tw-block lg:tw-hidden jsActions2">', '</h2> <div class="tw-block lg:tw-hidden jsActions2">')
    text = text.replace("Heema Sahni is a India-based Interior Architect...", description)
    text = text.replace("Heema Sahni Chhabra is a India-based Interior Architect...", description)
    text = re.sub(r'(about:\s*\{\s*slug:\s*"about",\s*description:\s*)"[^"]*"', rf'\1"{about_title}"', text)
    payload_html = json.dumps(about_payload_html, ensure_ascii=False)[1:-1]
    text = re.sub(r'content_1:\s*"[^"]*"', f'content_1: "{payload_html}"', text)
    text = re.sub(r'content_2:\s*"[^"]*"', 'content_2: ""', text)
    text = text.replace("Born and raised in London...", about_content_1)
    text = text.replace("Designing all aspects of interior architecture and loose furnishings...", about_content_2)
    text = text.replace("interior architecture", "interior design")
    text = text.replace("Born and raised", "Our work begins with")
    text = text.replace("Designing all aspects", "Developing interiors through")
    # Avoid corrupting "Interior Architecture" -> "Interior Designerure"
    text = re.sub(r"Interior Architect\b", "Interior Designer", text)
    text = text.replace('alt="Portrait Heema Sahni chhabra"', 'alt="Heema Chhabra, founder of HCDC"')
    text = text.replace("/_nuxt/img/portrait_naguissa.81547ad.jpg", "/_nuxt/img/portrait-hcdc.jpg")

    start = text.find('<div class="about ')
    end = text.find('</div> <div class="cursor ', start)
    if start < 0 or end < 0:
        raise RuntimeError(f"Could not locate About overlay in {path}")
    text = text[:start] + about_block + text[end:]
    text = text.replace(
        'class="about tw-fixed tw-right-0 lg:tw-h-screen tw-bg-black tw-z-40"',
        'class="about tw-fixed tw-right-0 lg:tw-h-screen tw-bg-black tw-z-40"',
    )
    text = text.replace('<nav class="mainnav"', '<nav aria-label="Primary navigation" class="mainnav"')
    text = text.replace(
        'class="tw-absolute tw-left-0 tw-top-0 tw-w-1/2 tw-h-screen tw-bg-transparent tw-z-10 focus:tw-outline-none focus:tw-ring-0 tw-rounded-none nocursor">',
        'class="tw-absolute tw-left-0 tw-top-0 tw-w-1/2 tw-h-screen tw-bg-transparent tw-z-10 focus:tw-outline-none focus:tw-ring-0 tw-rounded-none nocursor" type="button" aria-label="Previous project">',
        1,
    )
    text = text.replace(
        'class="tw-absolute tw-right-0 tw-top-0 tw-w-1/2 tw-h-screen tw-bg-transparent tw-z-10 focus:tw-outline-none focus:tw-ring-0 tw-rounded-none nocursor">',
        'class="tw-absolute tw-right-0 tw-top-0 tw-w-1/2 tw-h-screen tw-bg-transparent tw-z-10 focus:tw-outline-none focus:tw-ring-0 tw-rounded-none nocursor" type="button" aria-label="Next project">',
        1,
    )
    text = text.replace('class="nocursor button-home">Home</button>', 'class="nocursor button-home" type="button" aria-label="Return to home">Home</button>')
    text = text.replace('class="nocursor">About &amp; Contact</button>', 'class="nocursor" type="button" aria-label="Open About and Contact panel">About &amp; Contact</button>')
    text = text.replace('class="btn-close tw-absolute', 'class="btn-close tw-absolute')
    text = text.replace('href="mailto:hello@heemachhabra.com"', f'href="mailto:{email}"').replace(">hello@heemachhabra.com<", f">{email}<")

    gallery_text = [
        "Paris 16ème, France", "Paris 7ème, France", "Paris, France", "Brussels, Belgium", "Uccle, Belgique",
        "Rhode Saint Genèse, Belgium", "Rhode Saint Gen�se, Belgium", "Rhodes Saint Genèse, Belgium", "Rhodes Saint Gen�se, Belgium",
        "Ramatuelle, France", "Biarritz, France", "Galerie Jean-Jacques Dutko", "Design Basel 2012",
        "Selected interior composition", "HCDC — selected interior composition", "HCDC � selected interior composition",
        "Photos: Alexis Toureau", "Photo: Catalina Mesa", "Photos: Catalina Mesa", "Photos: Spectrum", "Photo: Spectrum", "Photos: Caféine",
        "Interior Design: NTD<br>\n        Architecture: Emmanuel Bonnewijn",
        "Interior Design: NTD<br>\n            Architecture: Emmanuel Bonnewijn",
        "In collaboration with: Johanna Amatoury Interior",
    ]
    for old in gallery_text:
        text = text.replace(old, generic_caption)
    text = re.sub(
        r'<(h[34])([^>]*class="[^"]*(?:title|subtitle)[^"]*"[^>]*)>\s*</\1>',
        lambda m: f'<{m.group(1)}{m.group(2)}></{m.group(1)}>',
        text,
    )
    text = text.replace('<img alt="" class="lazyLoad isLoaded"', '<img alt="Interior composition from the HCDC portfolio" class="lazyLoad isLoaded"')
    text = re.sub(r'<img(?![^>]*\balt=)', '<img alt=""', text)
    text = text.replace('<img data-src="', '<img loading="lazy" data-src="')
    text = text.replace('<img src="/_nuxt/img/screen01', '<img fetchpriority="high" src="/_nuxt/img/screen01')

    marker = '<meta data-n-head="ssr" name="viewport" content="width=device-width,initial-scale=1">'
    additions = (
        f'<link data-n-head="ssr" rel="canonical" href="{canonical}">'
        f'<meta data-n-head="ssr" property="og:site_name" content="Heema Chhabra Design Consultant">'
        f'<meta data-n-head="ssr" property="og:type" content="website">'
        f'<meta data-n-head="ssr" property="og:title" content="{title}">'
        f'<meta data-n-head="ssr" property="og:description" content="{description}">'
        f'<meta data-n-head="ssr" property="og:url" content="{canonical}">'
        f'<meta data-n-head="ssr" property="og:locale" content="en_GB">'
        f'<meta data-n-head="ssr" property="og:image" content="{og_image}">'
        f'<meta data-n-head="ssr" property="og:image:width" content="1200">'
        f'<meta data-n-head="ssr" property="og:image:height" content="630">'
        f'<meta data-n-head="ssr" property="og:image:alt" content="Heema Chhabra Design Consultant \u2014 Interior Design London">'
        f'<meta data-n-head="ssr" name="twitter:card" content="summary_large_image">'
        f'<meta data-n-head="ssr" name="twitter:title" content="{title}">'
        f'<meta data-n-head="ssr" name="twitter:description" content="{description}">'
        f'<meta data-n-head="ssr" name="twitter:image" content="{og_image}">'
        f'<meta data-n-head="ssr" name="twitter:image:alt" content="Heema Chhabra Design Consultant \u2014 Interior Design London">'
        f'<link data-n-head="ssr" rel="apple-touch-icon" href="/apple-touch-icon.png">'
    )
    text = re.sub(r'<link data-n-head="ssr" rel="canonical"[^>]*>', "", text)
    text = re.sub(r'<meta data-n-head="ssr" property="og:[^"]+"[^>]*>', "", text)
    text = re.sub(r'<meta data-n-head="ssr" name="twitter:[^"]+"[^>]*>', "", text)
    text = re.sub(r'<link data-n-head="ssr" rel="apple-touch-icon"[^>]*>', "", text)
    text = replace_once(text, marker, marker + additions, "viewport metadata")

    style = (
        '<style id="hcdc-progressive-enhancements">'
        '.about{overflow-y:auto;-webkit-overflow-scrolling:touch}'
        '.about-content{min-height:100%;padding-bottom:8rem}'
        '.about-content h2{margin:0 0 1rem;font-size:1.05rem;line-height:1.45}'
        '.about-content h3{margin:1.25rem 0 .5rem;font-size:.82rem;letter-spacing:.06em;text-transform:uppercase;opacity:.9}'
        '.about-content p{margin:0 0 1rem;font-size:.88rem;line-height:1.6}'
        '@media(min-width:1024px){.about-content p{font-size:.82rem;line-height:1.55}}'
        '.about-content a:focus-visible,.mainnav button:focus-visible,.btn-close:focus-visible{outline:2px solid currentColor;outline-offset:4px}'
        '@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition-duration:.01ms!important;animation-duration:.01ms!important;animation-iteration-count:1!important}}'
        '</style>'
    )
    text = re.sub(r'<style id="hcdc-progressive-enhancements">.*?</style>', "", text, flags=re.DOTALL)
    text = text.replace("</head>", style + "</head>", 1)

    ld = (
        f'<script type="application/ld+json">{{"@context":"https://schema.org","@graph":['
        f'{{"@type":"Organization","@id":"{canonical}#organization","name":"Heema Chhabra Design Consultant","alternateName":"HCDC","url":"{canonical}","description":"{description}","email":"{email}","sameAs":["{instagram}"]}},'
        f'{{"@type":"Person","@id":"{canonical}#heema-chhabra","name":"Heema Chhabra","jobTitle":"Design Consultant","worksFor":{{"@id":"{canonical}#organization"}}}},'
        f'{{"@type":"WebSite","@id":"{canonical}#website","url":"{canonical}","name":"Heema Chhabra Design Consultant","publisher":{{"@id":"{canonical}#organization"}}}},'
        f'{{"@type":"WebPage","@id":"{canonical}#webpage","url":"{canonical}","name":"{title}","isPartOf":{{"@id":"{canonical}#website"}},"about":{{"@id":"{canonical}#organization"}}}},'
        f'{{"@type":"Service","@id":"{canonical}#residential-interior-design","name":"Residential Interior Design","provider":{{"@id":"{canonical}#organization"}}}},'
        f'{{"@type":"Service","@id":"{canonical}#commercial-interior-design","name":"Commercial Interior Design","provider":{{"@id":"{canonical}#organization"}}}},'
        f'{{"@type":"Service","@id":"{canonical}#development-interior-design","name":"Builder & Property Development Interiors","provider":{{"@id":"{canonical}#organization"}}}}'
        f']}}</script>'
    )
    text = re.sub(r'<script type="application/ld\+json">.*?</script>', "", text, flags=re.DOTALL)
    text = text.replace("</head>", ld + "</head>", 1)

    text = text.replace(
        '<nav aria-label="Primary navigation" class="mainnav"',
        '<nav aria-label="Primary navigation" class="mainnav"',
    )

    pass

    path.write_text(text, encoding="utf-8")


def patch_payload(path: Path, site: dict) -> None:
    text = path.read_text(encoding="utf-8")
    description = site["seo"]["home"]["description"]
    about_content_block = build_about_content_block(site)
    about_payload_html = re.search(r'<div class="desc-about[^>]*>(.*)</div>', about_content_block, re.DOTALL).group(1)
    about_content_1 = site["introduction"]["paragraphs"][1]
    about_content_2 = site["introduction"]["paragraphs"][2]
    generic_caption = ""
    replacements = {
        "Heema Sahni Chhabra is a India-based Interior Architect with over a decade of experience.": description,
        "Heema Sahni is a India-based Interior Architect...": description,
        "Born and raised in Paris,": "Based in London,",
        "Heema Sahni Design": "HCDC",
        "Heema Sahni Chhabra Design": "HCDC",
        "Heema Sahni chhabra Design": "HCDC",
        "Naguissa": "HCDC",
        "NTD": "HCDC",
        "India-based": "London-based",
        "Jean Michel Wilmotte": "established design collaborators",
        "Sybille de Margerie": "established design collaborators",
        "Pascal Deprez": "established design collaborators",
        "over a decade of experience": "a client-led design practice",
        "more than 40 projects": "considered interiors",
        "Paris, Monaco, St Tropez and Brussels": "private homes and commercial spaces",
        "French and Japanese heritage": "a client-specific design language",
        "portrait_naguissa.81547ad.jpg": "portrait-hcdc.jpg",
        "img/.81547ad.jpg": "img/portrait-hcdc.jpg",
        "n.exports=e.p+\"img/.81547ad.jpg\"": "n.exports=e.p+\"img/portrait-hcdc.jpg\"",
        "n.exports=e.p+\"\"": "n.exports=e.p+\"img/portrait-hcdc.jpg\"",
        "return t(\"h2\",{staticClass:\"tw-font-grotesk-rg tw-text-black\"},[n._v(\"\\n      HEEMA \"),t(\"span\",{staticClass:\"tw-font-grotesk-bd\"},[n._v(\"CHHABRA\")]),n._v(\" DESIGN\\n    \")])": "return t(\"h1\",{staticClass:\"tw-font-grotesk-rg tw-text-black\"},[n._v(\"\\n      HEEMA \"),t(\"span\",{staticClass:\"tw-font-grotesk-bd\"},[n._v(\"CHHABRA\")]),n._v(\" DESIGN CONSULTANT\\n    \")])",
        "Interior Design: HCDC": generic_caption,
        "http://www.woodage.in/": "https://heemachhabra.com/",
        "https://www.woodage.in/": "https://heemachhabra.com/",
        "http://woodage.in": "https://heemachhabra.com",
        "https://woodage.in": "https://heemachhabra.com",
        "woodage.in": "heemachhabra.com",
        "t(\"h1\",{ref:\"jsText\",staticClass:\"tw-font-times-lt tw-text-2xl tw-text-white\"},[n._v(n._s(n.related.description))])": "t(\"h2\",{ref:\"jsText\",staticClass:\"tw-font-times-lt tw-text-2xl tw-text-white\"},[n._v(\"Bespoke Interior Design in London\")])",
        "staticClass:\"tw-absolute tw-left-0 tw-top-0 tw-w-1/2 tw-h-screen tw-bg-transparent tw-z-10 focus:tw-outline-none focus:tw-ring-0 tw-rounded-none nocursor\",on:{click:t.goToPrevious}": "staticClass:\"tw-absolute tw-left-0 tw-top-0 tw-w-1/2 tw-h-screen tw-bg-transparent tw-z-10 focus:tw-outline-none focus:tw-ring-0 tw-rounded-none nocursor\",attrs:{type:\"button\",\"aria-label\":\"Previous project\"},on:{click:t.goToPrevious}",
        "staticClass:\"tw-absolute tw-right-0 tw-top-0 tw-w-1/2 tw-h-screen tw-bg-transparent tw-z-10 focus:tw-outline-none focus:tw-ring-0 tw-rounded-none nocursor\",on:{click:t.goToNext}": "staticClass:\"tw-absolute tw-right-0 tw-top-0 tw-w-1/2 tw-h-screen tw-bg-transparent tw-z-10 focus:tw-outline-none focus:tw-ring-0 tw-rounded-none nocursor\",attrs:{type:\"button\",\"aria-label\":\"Next project\"},on:{click:t.goToNext}",
        "t(\"h2\",{staticClass:\"tw-font-grotesk-rg tw-text-black\"},[n._v(\"\\n      HEEMA \"),t(\"span\",{staticClass:\"tw-font-grotesk-bd\"},[n._v(\"CHHABRA\")]),n._v(\" DESIGN\\n    \")])": "t(\"h1\",{staticClass:\"tw-font-grotesk-rg tw-text-black\"},[n._v(\"\\n      HEEMA \"),t(\"span\",{staticClass:\"tw-font-grotesk-bd\"},[n._v(\"CHHABRA\")]),n._v(\" DESIGN CONSULTANT\\n    \")])",
        "attrs:{href:\"https://woodage.in\",target:\"_blank\",rel:\"nofollow\"},on:{mouseover:function(t){return n.handleHover(!0)},mouseleave:function(t){return n.handleHover(!1)}}},[n._v(n._s(n.textHover))]": "attrs:{href:\"mailto:info@heemachhabra.com\",rel:\"nofollow\"}},[n._v(\"Start a conversation\") ]",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"Interior Architect\b", "Interior Designer", text)
    payload_html = json.dumps(about_payload_html, ensure_ascii=False)[1:-1]
    text = re.sub(r'content_1:"[^"]*"', f'content_1:"{payload_html}"', text)
    text = re.sub(r'content_2:"[^"]*"', 'content_2:""', text)
    text = text.replace("Born and raised in London...", about_content_1)
    text = text.replace("Designing all aspects of interior architecture and loose furnishings...", about_content_2)
    text = text.replace("designing all aspects of interior architecture and loose furnishings.", about_content_2)
    text = text.replace("interior architecture", "interior design")
    path.write_text(text, encoding="utf-8")


def patch_bundles(site: dict) -> None:
    generic_caption = ""
    replacements = {
        "Heema Sahni Chhabra": "Heema Chhabra",
        "Heema Sahni chhabra": "Heema Chhabra",
        "Heema Sahni Design": "HCDC",
        "Heema Sahni": "Heema Chhabra",
        "SAHNI CHHABRA": "CHHABRA",
        "Naguissa": "HCDC",
        "NTD": "HCDC",
        "Paris 16ème, France": generic_caption,
        "Paris 7ème, France": generic_caption,
        "Brussels, Belgium": generic_caption,
        "Uccle, Belgique": generic_caption,
        "Rhode Saint Genèse, Belgium": generic_caption,
        "Rhode Saint Gen�se, Belgium": generic_caption,
        "Rhodes Saint Genèse, Belgium": generic_caption,
        "Rhodes Saint Gen�se, Belgium": generic_caption,
        "Rhode Saint Genèse, Belgium": generic_caption,
        "Rhode Saint Gen�se, Belgium": generic_caption,
        "Ramatuelle, France": generic_caption,
        "Biarritz, France": generic_caption,
        "Galerie Jean-Jacques Dutko": generic_caption,
        "Design Basel 2012": generic_caption,
        "Selected interior composition": generic_caption,
        "HCDC — selected interior composition": generic_caption,
        "HCDC � selected interior composition": generic_caption,
        "Photos: Alexis Toureau": generic_caption,
        "Photos: Catalina Mesa": generic_caption,
        "Photo: Catalina Mesa": generic_caption,
        "Photos: Caféine": generic_caption,
        "Photo: Caféine": generic_caption,
        "Photos: Spectrum": generic_caption,
        "Photo: Spectrum": generic_caption,
        "Interior Design: NTD": generic_caption,
        "Architecture: Emmanuel Bonnewijn": generic_caption,
        "In collaboration with: Johanna Amatoury Interior": generic_caption,
        "Interior Design: HCDC": generic_caption,
        "India-based Interior Architect": "London-based interior designer",
        "French and Japanese heritage": "a client-specific design language",
    }
    prohibited = [
        "Galerie Jean-Jacques Dutko", "Design Basel 2012", "Born and raised", "Designing all aspects", "interior architecture",
        "Selected interior composition", "HCDC — selected interior composition", "HCDC � selected interior composition", "Interior Design: HCDC",
        "Heema Sahni", "Naguissa", "NTD", "Paris", "Brussels", "Uccle", "Ramatuelle", "Biarritz", "Belgium", "France",
        "Alexis", "Catalina", "Caféine", "Cafeine", "Spectrum", "Emmanuel", "Johanna", "woodage.in", "portrait_naguissa", "img/.81547ad.jpg",
    ]
    for path in BUNDLE_FILES:
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        for old in prohibited:
            text = text.replace(old, generic_caption)
        text = text.replace('n.exports=e.p+""', 'n.exports=e.p+"img/portrait-hcdc.jpg"')
        text = text.replace(
            't("h2",{staticClass:"tw-font-grotesk-rg tw-text-black"},[n._v("\\n      HEEMA "),t("span",{staticClass:"tw-font-grotesk-bd"},[n._v("CHHABRA")]),n._v(" DESIGN\\n    ")])',
            't("h1",{staticClass:"tw-font-grotesk-rg tw-text-black"},[n._v("\\n      HEEMA "),t("span",{staticClass:"tw-font-grotesk-bd"},[n._v("CHHABRA")]),n._v(" DESIGN CONSULTANT\\n    ")])',
        )
        text = text.replace(
            't("div",{staticClass:"about tw-fixed tw-right-0 lg:tw-h-screen tw-bg-black tw-z-40"}',
            't("div",{staticClass:"about tw-fixed tw-right-0 lg:tw-h-screen tw-bg-black tw-z-40",attrs:{role:"dialog","aria-modal":"true","aria-labelledby":"hcdc-about-title"}}'
        )
        text = text.replace(
            'attrs:{href:"mailto:".concat(n.related.contact),rel:"nofollow"}},[n._v(n._s(n.related.contact))])',
            'attrs:{href:"mailto:".concat((n.related||{}).contact||"info@heemachhabra.com"),rel:"nofollow"}},[n._v(n._s((n.related||{}).contact||"info@heemachhabra.com"))])'
        )
        text = text.replace(
            'attrs:{href:n.related.instagram,target:"_blank"',
            'attrs:{href:(n.related||{}).instagram||"https://www.instagram.com/heemachhabradesignconsultant/",target:"_blank"'
        )
        text = text.replace(
            'domProps:{innerHTML:n._s(n.related.content_1+" "+n.related.content_2)}',
            'domProps:{innerHTML:n._s(((n.related||{}).content_1||"")+" "+((n.related||{}).content_2||""))}'
        )
        text = re.sub(r"Interior Architect\b", "Interior Designer", text)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    site = load_site()
    _projects = load_projects()

    for path in HTML_FILES:
        patch_html(path, site)
    for path in PAYLOAD_FILES:
        patch_payload(path, site)
    patch_bundles(site)

    source_portrait = ROOT / "_nuxt" / "img" / "portrait_naguissa.81547ad.jpg"
    target_portrait = ROOT / "_nuxt" / "img" / "portrait-hcdc.jpg"
    if source_portrait.exists() and not target_portrait.exists():
        source_portrait.replace(target_portrait)
    print("HCDC generated-build migration applied (content-driven)")
