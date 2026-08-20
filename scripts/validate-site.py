from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = "https://heemachhabra.com/"
FORBIDDEN = ["Heema Sahni", "SAHNI", "Naguissa", "NTD", "Galerie Jean-Jacques Dutko", "Design Basel 2012", "Paris 16", "Paris 7", "Uccle", "Biarritz", "Ramatuelle", "Brussels, Belgium", "Rhode Saint", "Rhodes Saint", "Belgium", "Alexis Toureau", "Catalina Mesa", "Caféine", "Cafeine", "Spectrum", "Emmanuel Bonnewijn", "Johanna Amatoury", "Born and raised", "Designing all aspects", "interior architecture", "Selected interior composition", "HCDC — selected interior composition", "HCDC � selected interior composition", "Interior Design: HCDC"]
REQUIRED = ["index.html", "robots.txt", "sitemap.xml", "404.html", "_nuxt/index.html", "_nuxt/static/1679938011/payload.js"]

class HTMLChecks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.canonical = []
        self.scripts = []
        self.active_script = None
        self.refs = []
        self.lang = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html": self.lang = attrs.get("lang")
        if tag == "h1": self.h1 += 1
        if tag == "link" and attrs.get("rel") == "canonical": self.canonical.append(attrs.get("href"))
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.scripts.append([])
            self.active_script = len(self.scripts) - 1
        if tag in {"img", "script", "link"}:
            for key in ("src", "data-src", "href"):
                value = attrs.get(key)
                if value and value.startswith("/") and not value.startswith("//"): self.refs.append(value.split("?", 1)[0])
    def handle_endtag(self, tag):
        if tag == "script" and self.active_script is not None:
            self.active_script = None
    def handle_data(self, data):
        if self.active_script is not None: self.scripts[self.active_script].append(data)


def fail(errors, message): errors.append(message)

def main():
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).exists(): fail(errors, f"missing required file: {name}")
    html_paths = [ROOT / "index.html", ROOT / "_nuxt" / "index.html"]
    parsed = []
    for path in html_paths:
        text = path.read_text(encoding="utf-8")
        for item in FORBIDDEN:
            if item in text: fail(errors, f"forbidden production identity in {path.name}: {item}")
        checks = HTMLChecks(); checks.feed(text); parsed.append((path, text, checks))
        if checks.lang != "en-GB": fail(errors, f"{path.name} must declare lang=en-GB")
        if checks.h1 != 1: fail(errors, f"{path.name} must contain exactly one h1")
        if checks.canonical != [CANONICAL]: fail(errors, f"{path.name} canonical mismatch: {checks.canonical}")
        for ref in checks.refs:
            target = ROOT / ref.lstrip("/")
            if not target.exists(): fail(errors, f"missing local reference in {path.name}: {ref}")
        for index, raw in enumerate(checks.scripts):
            try: json.loads("".join(raw))
            except json.JSONDecodeError as exc: fail(errors, f"invalid JSON-LD in {path.name} script {index}: {exc}")
    if len(parsed) == 2 and parsed[0][1] != parsed[1][1]:
        fail(errors, "root index.html and _nuxt/index.html differ; SSR duplicate must remain identical")
    payload = (ROOT / "_nuxt/static/1679938011/payload.js").read_text(encoding="utf-8")
    for item in FORBIDDEN:
        if item in payload: fail(errors, f"forbidden payload identity: {item}")
    for path in (ROOT / "_nuxt").glob("*.js"):
        text = path.read_text(encoding="utf-8")
        for item in FORBIDDEN:
            if item in text: fail(errors, f"forbidden bundle identity in {path.name}: {item}")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Disallow: /" in robots: fail(errors, "robots.txt blocks the entire site")
    if "OAI-SearchBot" not in robots or "PerplexityBot" not in robots: fail(errors, "robots.txt crawler allowances incomplete")
    try:
        sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
        locs = [node.text for node in sitemap.iter() if node.tag.endswith("}loc")]
        expected = [CANONICAL] + [f"{CANONICAL}{p}/" for p in ["about", "services", "approach", "contact"]]
        if locs not in ([CANONICAL], expected): fail(errors, f"sitemap URLs mismatch: {locs}")
        for loc in locs:
            rel = loc.replace(CANONICAL, "").strip("/")
            target = ROOT / rel / "index.html" if rel else ROOT / "index.html"
            if not target.exists():
                fail(errors, f"sitemap URL has no file: {loc}")
            if loc != CANONICAL:
                html = target.read_text(encoding="utf-8")
                if f'rel="canonical" href="{loc}"' not in html and f"rel='canonical' href='{loc}'" not in html:
                    fail(errors, f"sitemap URL canonical mismatch: {loc}")
                checks2 = HTMLChecks(); checks2.feed(html)
                if checks2.h1 != 1:
                    fail(errors, f"{loc} must contain exactly one h1")
        for name in ["about", "services", "approach", "contact"]:
            html = (ROOT / name / "index.html").read_text(encoding="utf-8")
            checks_e = HTMLChecks(); checks_e.feed(html)
            if checks_e.canonical != [f"{CANONICAL}{name}/"]:
                fail(errors, f"{name}/ canonical mismatch: {checks_e.canonical}")
            try: json.loads("".join("".join(s) for s in checks_e.scripts))
            except json.JSONDecodeError as exc: fail(errors, f"invalid JSON-LD in {name}/: {exc}")
            if 'property="og:image" content="https://heemachhabra.com/og-image.jpg"' not in html:
                fail(errors, f"{name}/ missing og:image")
            if 'name="twitter:card" content="summary_large_image"' not in html:
                fail(errors, f"{name}/ missing twitter card")
    except ET.ParseError as exc: fail(errors, f"invalid sitemap XML: {exc}")
    for path in ROOT.rglob("*"):
        if path.is_file() and (".git" in path.parts or ".commandcode" in path.parts): continue
        if path.name.startswith(".env") or path.suffix.lower() in {".pem", ".key"}: fail(errors, f"secret-like file present: {path.relative_to(ROOT)}")
    if errors:
        print("VALIDATION FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("VALIDATION PASSED")
    print(f"- checked {len(html_paths)} SSR HTML copies")
    print(f"- checked {len(list((ROOT / '_nuxt').glob('*.js')))} JavaScript bundles")
    print("- checked canonical, robots, sitemap, JSON-LD, local references, and forbidden identity")
    return 0

if __name__ == "__main__": sys.exit(main())
