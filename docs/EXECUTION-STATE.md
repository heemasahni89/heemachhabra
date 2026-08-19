# Execution state

- **Current phase:** generated-build HCDC migration and release framework
- **Baseline commit:** `8df58c1` (`chore: import current production website`)
- **Baseline tag:** `baseline-before-hcdc-refresh-20260819`
- **Working branch:** `production/hcdc-content-seo-refresh`
- **Remote:** `https://github.com/heemasahni89/heemachhabra.git`
- **Canonical host selected:** `https://heemachhabra.com/` because both HTTPS host variants currently serve the same site; redirect behaviour is not yet configured or verified.
- **Architecture:** static Nuxt/Vue generated export; no source/build project included.
- **SSH key:** existing `~/.ssh/heema_github_actions` material detected; no new key created.
- **Browser tooling:** `agent-browser` command unavailable in this environment; browser screenshots/hydration checks remain outstanding.
- **Hosting target:** not yet verified; no deployment attempted.
- **Image provenance:** not verified; existing downloaded images are retained only to preserve the baseline visual template and must be confirmed before production publication.

## Completed checks

- Local HTTP baseline server returned 200 for `/` and the Nuxt payload.
- GitHub CLI active account verified as `heemasahni89` with repository write scope.
- Empty remote verified before baseline push.
- Baseline commit and tag pushed to GitHub.
- Migration script runs idempotently.
- Patched HTML div counts remain balanced.

## Current blockers

1. Browser automation/screenshot tooling is unavailable.
2. HostingRaja SSH host/user/port/document root/known-host fingerprint are not yet verified from this session.
3. Production ownership/licensing of downloaded project and portrait imagery is not documented.

## Rollback point

Local/Git rollback: checkout tag `baseline-before-hcdc-refresh-20260819` or commit `8df58c1`. Remote rollback procedure will be recorded after the real HostingRaja document root and backup layout are verified.
