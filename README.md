# Heema Chhabra Design Consultant

This repository contains the generated static Nuxt/Vue export for Heema Chhabra Design Consultant (HCDC), a London-based interior design studio. The original Nuxt source and build configuration were not included in the supplied site download, so this repository preserves the generated runtime and applies deterministic, minimal content patches.

## Local validation

Requires Python 3. Run:

```powershell
python scripts/validate-site.py
python scripts/package-site.py
```

Serve the directory over HTTP for runtime checks; do not use `file://`.

## Release model

The `main` branch is the production release branch. Substantive changes are developed on `production/hcdc-content-seo-refresh` or a later feature branch, validated, reviewed, and then merged. GitHub Actions packages only production web assets and deploys them over SSH/SCP/tar after validation.

The first recovery point is tag `baseline-before-hcdc-refresh-20260819`.

## Verified facts used in the site

- Brand: Heema Chhabra Design Consultant
- Abbreviation: HCDC
- Person: Heema Chhabra
- Positioning: London-based interior design studio/design consultancy
- Contact: info@heemachhabra.com
- Instagram: https://www.instagram.com/heemachhabradesignconsultant/

Project locations, photography credits, awards, qualifications, address, telephone number, and image licensing are not asserted without separate verification.
