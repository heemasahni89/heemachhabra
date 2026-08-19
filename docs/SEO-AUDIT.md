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

## Known limitations

- Only `/` is a generated Nuxt route; no thin doorway routes were created.
- The original source/build system was unavailable, so generated output was patched directly and hydration consistency is guarded by validation rather than a rebuild.
- No Lighthouse/Core Web Vitals measurements are claimed because browser automation is unavailable.
- Existing image/font provenance is not verified.
- HTTPS and `www` redirect policy is not yet configured or verified on HostingRaja.

## Competitive research

No competitor copy was copied. External comparative research was not performed in this offline implementation pass; the editorial structure follows the supplied brief: clear identity, service fit, approach, evidence boundary, and frictionless enquiry without unsupported claims.
