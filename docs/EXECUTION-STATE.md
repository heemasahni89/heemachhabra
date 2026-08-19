# Execution state

- **Current phase:** local release gate complete; production deployment blocked on verified HostingRaja configuration, browser tooling, and asset approval
- **Baseline commit:** `8df58c1` (`chore: import current production website`)
- **Baseline tag:** `baseline-before-hcdc-refresh-20260819`
- **Working branch:** `production/hcdc-content-seo-refresh`
- **Remote:** `https://github.com/heemasahni89/heemachhabra.git`
- **Canonical host selected:** `https://heemachhabra.com/` because both HTTPS host variants currently serve the same site; redirect behaviour is not yet configured or verified.
- **Architecture:** static Nuxt/Vue generated export; no source/build project included.
- **SSH key:** existing `~/.ssh/heema_github_actions` material detected; no new key created.
- **Browser tooling:** `agent-browser` command unavailable in this environment; browser screenshots/hydration checks remain outstanding.
- **Hosting target:** not yet verified; no deployment attempted. No `production` environment secrets are currently configured in GitHub.
- **Image provenance:** not verified; deployment workflow is explicitly blocked by `Production approval: NO` until the owner confirms rights.
- **Known SSH host:** `190.92.174.186` is present in local known_hosts, but it does not match the public domain A record (`103.92.235.110`) and cannot be assumed to be HostingRaja for this site.

## Completed checks

- Local HTTP baseline server returned 200 for `/` and the Nuxt payload.
- GitHub CLI active account verified as `heemasahni89` with repository write scope.
- Empty remote verified before baseline push.
- Baseline commit and tag pushed to GitHub.
- Migration script runs idempotently.
- Patched HTML div counts remain balanced.
- Local deterministic validation passed; 94-file production archive packaged without repository/docs/script metadata.
- GitHub Actions validation run `32230224003` passed on the working branch.
- Local HTTP checks passed for homepage, robots, sitemap, required assets, and true 404.
- Live pre-deployment comparison: homepage 200, robots/sitemap 404, proving the new release was not deployed.
- Local baseline HTTP server stopped after testing.

## Current blockers

1. Browser automation/screenshot tooling is unavailable.
2. HostingRaja SSH host/user/port/document root/known-host fingerprint are not yet verified from this session.
3. Production ownership/licensing of downloaded project and portrait imagery is not documented.

## Rollback point

Local/Git rollback: checkout tag `baseline-before-hcdc-refresh-20260819` or commit `8df58c1`. Remote rollback procedure will be recorded after the real HostingRaja document root and backup layout are verified.
