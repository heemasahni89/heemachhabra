# SEO audit

## Implemented foundations

- `lang="en-GB"` and viewport metadata.
- One homepage title, description, canonical, Open Graph, and Twitter card metadata.
- Crawlable `robots.txt` allowing normal crawlers, `OAI-SearchBot`, and `PerplexityBot`.
- One canonical HTTPS URL in `sitemap.xml`.
- Custom `404.html` with `noindex` and a home/contact path.
- Factual JSON-LD graph using Organization, Person, WebSite, WebPage, and two Service nodes.
- Visible HCDC identity, London positioning, service categories, design philosophy, process, and enquiry path.
- Existing gallery image alternatives improved without changing image order or animation structure.
- Reduced-motion and keyboard focus enhancements added conservatively.

## Independent browser audit evidence

A temporary Playwright harness tested the immutable baseline and current branch side-by-side in Chromium and WebKit at 320×568, 360×800, 375×667, 390×844, 414×896, 768×1024, 1024×768, 1366×768, 1440×900, 1920×1080 and 844×390. The current branch produced 0 blockers across 22 viewport/engine runs, with no console errors, page errors, failed requests, or document horizontal overflow. About open/close, scroll height, email/Instagram reachability, previous/next controls, visible image loading, reduced-motion preference, and Escape close were exercised. The corrected hydrated DOM retained the full six-stage/service content and HCDC identity.

The gallery inventory found 82 generated desktop/mobile title/subtitle hooks. Because no project facts or asset rights are verified, all are intentionally empty rather than generic or fabricated.

## Known limitations

- Only `/` is a generated Nuxt route; no thin doorway routes were created.
- The original source/build system was unavailable, so generated output was patched directly and hydration consistency is guarded by validation rather than a rebuild.
- Lighthouse/Core Web Vitals measurements are not claimed; the Playwright audit covered rendering, interaction, overflow, console/network and visible image loading but did not run Lighthouse.
- Existing image/font provenance is not verified.
- HTTPS and `www` redirect policy is not yet configured or verified on HostingRaja.

## Competitive research

No competitor copy was copied. External comparative research was not performed in this offline implementation pass; the editorial structure follows the supplied brief: clear identity, service fit, approach, evidence boundary, and frictionless enquiry without unsupported claims.
