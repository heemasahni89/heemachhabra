# Baseline audit

## Architecture

The supplied directory is a statically generated Nuxt/Vue application, not a source repository. It contains root SSR HTML, a duplicate `_nuxt/index.html`, Nuxt static payload/manifest/state files, hashed JavaScript chunks, local fonts, and hashed JPEG assets. No Vue source, package manifest, Nuxt configuration, or reproducible build command was supplied.

Visible content originated from three surfaces: SSR HTML, serialized Nuxt payloads, and compiled Vue render functions. Changing only the root HTML would not have been safe because hydration could restore old strings.

## Baseline recovery

- Commit: `8df58c1`
- Tag: `baseline-before-hcdc-refresh-20260819`
- Remote: `https://github.com/heemasahni89/heemachhabra.git`
- Baseline tree: 91 tracked files, approximately 15.2 MB before Git metadata.

## Runtime baseline

The export served successfully over a local HTTP server at `http://127.0.0.1:8765/` with status 200. The root response was approximately 121 KB; the Nuxt payload returned status 200.

The existing runtime uses a scroll-driven gallery, fixed intro/logo, custom cursor state, desktop and mobile slideshow markup, a fixed-height master surface, and an About/Contact overlay. The baseline markup contains old identity and template project labels in SSR HTML, payload, and compiled chunks.

## Browser and interaction evidence

The requested Chromium/WebKit screenshot and interaction run could not be completed because the `agent-browser` executable is not installed in this environment. No browser results are claimed. Required follow-up matrix: 1440×900, 390×844, 375×667, 768×1024, intro entry, gallery navigation, About open/close/scroll, contact links, resize, refresh, keyboard, reduced motion, console, and network.

## Baseline content findings

The export contained Heema Sahni variants, Naguissa, NTD, French/Belgian locations, third-party photography/architecture/collaboration credits, and an old portrait filename. These were deliberately recorded as baseline findings and are not authoritative HCDC facts.

## Asset observation

The export includes 67 JPEG project images, one portrait, an Instagram SVG, and three local WOFF2 fonts. Ownership/licensing and project metadata were not provided. The asset inventory is maintained in `docs/ASSET-PROVENANCE.md`.
