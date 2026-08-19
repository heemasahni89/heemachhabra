from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [ROOT / "index.html", ROOT / "_nuxt" / "index.html"]
PAYLOAD_FILES = [ROOT / "_nuxt" / "static" / "1679938011" / "payload.js"]
BUNDLE_FILES = list((ROOT / "_nuxt").glob("*.js"))

TITLE = "Heema Chhabra Design Consultant | Interior Design London"
DESCRIPTION = "London-based interior design studio creating refined residential, commercial and development interiors through thoughtful planning, materials and bespoke detail."
INSTAGRAM = "https://www.instagram.com/heemachhabradesignconsultant/"
EMAIL = "info@heemachhabra.com"
CANONICAL = "https://heemachhabra.com/"

ABOUT_BLOCK = '''<div class="about tw-fixed tw-right-0 lg:tw-h-screen tw-bg-black tw-z-40" role="dialog" aria-modal="true" aria-labelledby="hcdc-about-title"><button class="btn-close tw-absolute tw-right-6 lg:tw-right-20 tw-z-20 tw-font-grotesk-rg tw-text-sm tw-text-white focus:tw-outline-none focus:tw-ring-0 nocursor" type="button" aria-label="Close About and Contact panel">Close</button> <div class="lg:tw-grid tw-grid-cols-8 lg:tw-gap-20 tw-px-6 lg:tw-px-20 tw-py-6 lg:tw-py-20 tw-box-border about-content"><figure class="tw-w-1/2 lg:tw-w-full lg:tw-col-span-3 jsImage"><img data-src="/_nuxt/img/portrait-hcdc.jpg" alt="Heema Chhabra, founder of HCDC" class="tw-w-full tw-block tw-h-auto lazyLoad"></figure> <div class="lg:tw-col-span-4 tw-relative tw--top-2 tw-mt-20 lg:tw-mt-0 jsText"><h1 id="hcdc-about-title" class="tw-font-times-lt tw-text-2xl tw-text-white">Bespoke Interior Design in London</h1> <div class="tw-block lg:tw-hidden jsActions2"><a href="mailto:info@heemachhabra.com" rel="nofollow" class="tw-block tw-font-grotesk-rg tw-text-sm tw-text-white tw-underline tw-mt-10">info@heemachhabra.com</a> <a href="https://www.instagram.com/heemachhabradesignconsultant/" target="_blank" rel="noopener noreferrer" class="tw-block tw-underline tw-font-grotesk-rg tw-text-sm tw-text-white tw-block lg:tw-inline-block tw-mt-4 lg:tw-mt-0"><img data-src="/_nuxt/img/instagram.b6014cf.svg" alt="" class="tw-w-3 tw-h-3 tw-inline-block tw-mr-2 tw-relative lazyLoad" style="top:2px">Follow on Instagram</a></div> <div class="desc-about tw-font-grotesk-rg tw-text-white tw-text-sm lg:tw-text-xs tw-leading-5 lg:tw-leading-4"><h2>Heema Chhabra Design Consultant is a London-based interior design studio creating considered interiors for private homes, commercial spaces and property development projects.</h2><p>We begin with how a space needs to work and how people want to feel within it, then develop a cohesive design through spatial planning, materials, lighting, furniture, bespoke joinery and carefully resolved detail.</p><h2>Beauty with Purpose</h2><p>A successful interior should be as intuitive to live in as it is compelling to look at. Proportion, circulation, light, texture, storage and everyday use are considered as one connected composition.</p><h2>A Considered Approach to Every Project</h2><p>We understand the brief, establish a clear design direction, curate materials and furnishings, resolve the detail, and support a thoughtful handover. The scope is shaped around each property and project.</p><h2>Interior Design Services</h2><p>HCDC offers residential interior design, private residence schemes, commercial interiors and builder or property-development design support where appropriate. Services may include space planning, materials, lighting, joinery, furniture and finishing details.</p><p>Every project begins with a conversation. Tell us where the project is, what you would like to change and the stage you are at.</p></div></div> <div class="actions tw-hidden lg:tw-grid tw-grid-cols-8 lg:tw-gap-20 tw-px-6 lg:tw-px-20 lg:tw-py-20 tw-box-border lg:tw-absolute tw-bottom-0 tw-left-0 tw-w-full tw-mt-20 lg:tw-mt-0 jsActions"><div class="lg:tw-col-start-4 lg:tw-col-span-5 tw-relative"><a href="mailto:info@heemachhabra.com" rel="nofollow" class="btn tw-font-grotesk-rg tw-text-sm tw-text-white tw-underline">info@heemachhabra.com</a> <a href="https://www.instagram.com/heemachhabradesignconsultant/" target="_blank" rel="noopener noreferrer" class="btn tw-underline tw-font-grotesk-rg tw-text-sm tw-text-white tw-block lg:tw-inline-block tw-mt-4 lg:tw-mt-0"><img data-src="/_nuxt/img/instagram.b6014cf.svg" alt="" class="tw-w-3 tw-h-3 tw-inline-block tw-mr-2 tw-relative lazyLoad" style="top:2px">Follow on Instagram</a></div></div> <a href="mailto:info@heemachhabra.com" rel="nofollow" class="tw-relative lg:tw-absolute tw-left-6 lg:tw-left-20 tw-bottom-5 lg:tw-bottom-20 tw-font-grotesk-rg tw-text-sm tw-text-white tw-text-opacity-40 jsCredit">Start a conversation</a></div>'''

GENERIC_CAPTION = "HCDC — selected interior composition"


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Missing expected {label}")
    return text.replace(old, new, 1)


def patch_html(path):
    text = path.read_text(encoding="utf-8")
    text = text.replace("<html lang=\"en\"", "<html lang=\"en-GB\"")
    text = text.replace("<title>Heema Sahni - Interior Architecture &amp; Design</title>", f"<title>{TITLE}</title>")
    text = text.replace('name="description" content="Heema Sahni is a India-based Interior Architect with over a decade of experience."', f'name="description" content="{DESCRIPTION}"')
    text = text.replace("HEEMA <span class=\"tw-font-grotesk-bd\">SAHNI CHHABRA</span> DESIGN", "HEEMA <span class=\"tw-font-grotesk-bd\">CHHABRA</span> DESIGN CONSULTANT")
    text = text.replace("Heema Sahni is a India-based Interior Architect...", DESCRIPTION)
    text = text.replace("Heema Sahni Chhabra is a India-based Interior Architect...", DESCRIPTION)
    text = text.replace('alt="Portrait Heema Sahni chhabra"', 'alt="Heema Chhabra, founder of HCDC"')
    text = text.replace('/_nuxt/img/portrait_naguissa.81547ad.jpg', '/_nuxt/img/portrait-hcdc.jpg')
    start = text.find('<div class="about ')
    end = text.find('</div> <div class="cursor ', start)
    if start < 0 or end < 0:
        raise RuntimeError(f"Could not locate About overlay in {path}")
    text = text[:start] + ABOUT_BLOCK + text[end:]
    text = text.replace('class="about tw-fixed tw-right-0 lg:tw-h-screen tw-bg-black tw-z-40"', 'class="about tw-fixed tw-right-0 lg:tw-h-screen tw-bg-black tw-z-40"')
    text = text.replace("<nav class=\"mainnav\"", '<nav aria-label="Primary navigation" class="mainnav"')
    text = text.replace('class="nocursor button-home">Home</button>', 'class="nocursor button-home" type="button" aria-label="Return to home">Home</button>')
    text = text.replace('class="nocursor">About &amp; Contact</button>', 'class="nocursor" type="button" aria-label="Open About and Contact panel">About &amp; Contact</button>')
    text = text.replace('class="btn-close tw-absolute', 'class="btn-close tw-absolute')
    text = text.replace('href="mailto:hello@heemachhabra.com"', f'href="mailto:{EMAIL}"').replace('>hello@heemachhabra.com<', f'>{EMAIL}<')
    for old in ["Paris 16ème, France", "Paris 7ème, France", "Paris, France", "Brussels, Belgium", "Uccle, Belgique", "Rhode Saint Genèse, Belgium", "Rhode Saint Gen�se, Belgium", "Rhodes Saint Genèse, Belgium", "Rhodes Saint Gen�se, Belgium", "Ramatuelle, France", "Biarritz, France"]:
        text = text.replace(old, GENERIC_CAPTION)
    for old in ["Photos: Alexis Toureau", "Photo: Catalina Mesa", "Photos: Catalina Mesa", "Photos: Spectrum", "Photo: Spectrum", "Photos: Caféine", "Interior Design: NTD<br>\n        Architecture: Emmanuel Bonnewijn", "Interior Design: NTD<br>\n            Architecture: Emmanuel Bonnewijn", "In collaboration with: Johanna Amatoury Interior"]:
        text = text.replace(old, GENERIC_CAPTION)
    text = text.replace('<img alt="" class="lazyLoad isLoaded"', '<img alt="Interior composition from the HCDC portfolio" class="lazyLoad isLoaded"')
    text = re.sub(r'<img(?![^>]*\balt=)', '<img alt=""', text)
    text = text.replace('<img data-src="', '<img loading="lazy" data-src="')
    text = text.replace('<img src="/_nuxt/img/screen01', '<img fetchpriority="high" src="/_nuxt/img/screen01')
    marker = '<meta data-n-head="ssr" name="viewport" content="width=device-width,initial-scale=1">'
    additions = f'<link data-n-head="ssr" rel="canonical" href="{CANONICAL}"><meta data-n-head="ssr" property="og:site_name" content="Heema Chhabra Design Consultant"><meta data-n-head="ssr" property="og:type" content="website"><meta data-n-head="ssr" property="og:title" content="{TITLE}"><meta data-n-head="ssr" property="og:description" content="{DESCRIPTION}"><meta data-n-head="ssr" property="og:url" content="{CANONICAL}"><meta data-n-head="ssr" name="twitter:card" content="summary"><meta data-n-head="ssr" name="twitter:title" content="{TITLE}"><meta data-n-head="ssr" name="twitter:description" content="{DESCRIPTION}">'
    text = re.sub(r'<link data-n-head="ssr" rel="canonical"[^>]*>', '', text)
    text = re.sub(r'<meta data-n-head="ssr" property="og:[^"]+"[^>]*>', '', text)
    text = re.sub(r'<meta data-n-head="ssr" name="twitter:[^"]+"[^>]*>', '', text)
    text = replace_once(text, marker, marker + additions, "viewport metadata")
    style = '<style id="hcdc-progressive-enhancements">.about{overflow-y:auto;-webkit-overflow-scrolling:touch}.about-content{min-height:100%;padding-bottom:8rem}.about-content h2{margin:0 0 1rem}.about-content p{margin:0 0 1.25rem}.about-content a:focus-visible,.mainnav button:focus-visible,.btn-close:focus-visible{outline:2px solid currentColor;outline-offset:4px}@media (prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition-duration:.01ms!important;animation-duration:.01ms!important;animation-iteration-count:1!important}}</style>'
    text = re.sub(r'<style id="hcdc-progressive-enhancements">.*?</style>', '', text, flags=re.DOTALL)
    text = text.replace('</head>', style + '</head>', 1)
    ld = f'<script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":"Organization","@id":"{CANONICAL}#organization","name":"Heema Chhabra Design Consultant","alternateName":"HCDC","url":"{CANONICAL}","description":"{DESCRIPTION}"}},{{"@type":"Person","@id":"{CANONICAL}#heema-chhabra","name":"Heema Chhabra","jobTitle":"Design Consultant","worksFor":{{"@id":"{CANONICAL}#organization"}}}},{{"@type":"WebSite","@id":"{CANONICAL}#website","url":"{CANONICAL}","name":"Heema Chhabra Design Consultant","publisher":{{"@id":"{CANONICAL}#organization"}}}},{{"@type":"WebPage","@id":"{CANONICAL}#webpage","url":"{CANONICAL}","name":"{TITLE}","isPartOf":{{"@id":"{CANONICAL}#website"}},"about":{{"@id":"{CANONICAL}#organization"}}}},{{"@type":"Service","@id":"{CANONICAL}#residential-interior-design","name":"Residential Interior Design","provider":{{"@id":"{CANONICAL}#organization"}}}},{{"@type":"Service","@id":"{CANONICAL}#commercial-interior-design","name":"Commercial Interior Design","provider":{{"@id":"{CANONICAL}#organization"}}}}]}}</script>'
    text = re.sub(r'<script type="application/ld\+json">.*?</script>', '', text, flags=re.DOTALL)
    text = text.replace('</head>', ld + '</head>', 1)
    path.write_text(text, encoding="utf-8")


def patch_payload(path):
    text = path.read_text(encoding="utf-8")
    replacements = {
        "Heema Sahni Chhabra is a India-based Interior Architect with over a decade of experience.": DESCRIPTION,
        "Heema Sahni is a India-based Interior Architect...": DESCRIPTION,
        "Born and raised in Paris,": "Based in London,",
        "Heema Sahni Design": "HCDC",
        "Heema Sahni Chhabra Design": "HCDC",
        "Heema Sahni chhabra Design": "HCDC",
        "Naguissa": "HCDC",
        "NTD": "HCDC",
        "India-based": "London-based",
        "Interior Architect": "Interior Designer",
        "Jean Michel Wilmotte": "established design collaborators",
        "Sybille de Margerie": "established design collaborators",
        "Pascal Deprez": "established design collaborators",
        "over a decade of experience": "a client-led design practice",
        "more than 40 projects": "considered interiors",
        "Paris, Monaco, St Tropez and Brussels": "private homes and commercial spaces",
        "French and Japanese heritage": "a client-specific design language",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def patch_bundles():
    replacements = {
        "Heema Sahni Chhabra": "Heema Chhabra",
        "Heema Sahni chhabra": "Heema Chhabra",
        "Heema Sahni Design": "HCDC",
        "Heema Sahni": "Heema Chhabra",
        "SAHNI CHHABRA": "CHHABRA",
        "Naguissa": "HCDC",
        "NTD": "HCDC",
        "Paris 16ème, France": GENERIC_CAPTION,
        "Paris 7ème, France": GENERIC_CAPTION,
        "Brussels, Belgium": GENERIC_CAPTION,
        "Uccle, Belgique": GENERIC_CAPTION,
        "Rhode Saint Genèse, Belgium": GENERIC_CAPTION,
        "Rhode Saint Gen�se, Belgium": GENERIC_CAPTION,
        "Rhodes Saint Genèse, Belgium": GENERIC_CAPTION,
        "Rhodes Saint Gen�se, Belgium": GENERIC_CAPTION,
        "Rhode Saint Genèse, Belgium": GENERIC_CAPTION,
        "Rhode Saint Gen�se, Belgium": GENERIC_CAPTION,
        "Ramatuelle, France": GENERIC_CAPTION,
        "Biarritz, France": GENERIC_CAPTION,
        "Photos: Alexis Toureau": GENERIC_CAPTION,
        "Photos: Catalina Mesa": GENERIC_CAPTION,
        "Photo: Catalina Mesa": GENERIC_CAPTION,
        "Photos: Caféine": GENERIC_CAPTION,
        "Photo: Caféine": GENERIC_CAPTION,
        "Photos: Spectrum": GENERIC_CAPTION,
        "Photo: Spectrum": GENERIC_CAPTION,
        "Interior Design: NTD": GENERIC_CAPTION,
        "Architecture: Emmanuel Bonnewijn": GENERIC_CAPTION,
        "In collaboration with: Johanna Amatoury Interior": GENERIC_CAPTION,
        "India-based Interior Architect": "London-based interior designer",
        "Interior Architect": "Interior Designer",
        "French and Japanese heritage": "a client-specific design language",
    }
    for path in BUNDLE_FILES:
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


for path in HTML_FILES:
    patch_html(path)
for path in PAYLOAD_FILES:
    patch_payload(path)
patch_bundles()

source_portrait = ROOT / "_nuxt" / "img" / "portrait_naguissa.81547ad.jpg"
target_portrait = ROOT / "_nuxt" / "img" / "portrait-hcdc.jpg"
if source_portrait.exists() and not target_portrait.exists():
    source_portrait.replace(target_portrait)
print("HCDC generated-build migration applied")
