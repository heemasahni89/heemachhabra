# Release checklist

- [ ] `python scripts/validate-site.py` passes.
- [ ] Asset ownership/licensing confirmed for every production image and font.
- [ ] HCDC email and Instagram confirmed by owner.
- [ ] Chromium/WebKit responsive and hydration tests pass at required viewports.
- [ ] No console errors, rejected promises, critical 4xx/5xx assets, overflow, clipping, dead controls, or overlay traps.
- [ ] Canonical host, TLS, redirects, Apache document root, and SSH host key verified.
- [ ] GitHub Actions production secrets configured in environment `production`.
- [ ] Staged release, archive contents, backup, target path, and `.well-known` preservation verified.
- [ ] Production smoke checks pass for `/`, `/robots.txt`, `/sitemap.xml`, critical assets, and a true 404.
- [ ] Raw HTML and hydrated DOM contain the same HCDC identity.
- [ ] Rollback backup verified and rollback command documented.
