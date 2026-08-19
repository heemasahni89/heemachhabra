# Deployment and rollback

## GitHub Actions

Deployment is intended to run from `main` through the `production` environment using these secrets: `HOSTING_HOST`, `HOSTING_PORT`, `HOSTING_USER`, `HOSTING_SSH_KEY`, `HOSTING_KNOWN_HOSTS`, `HOSTING_TARGET_PATH`, and `PRODUCTION_URL`. The private key is never committed or printed.

The workflow uses standard `tar`, `scp`, and `ssh`; it does not use rsync. It stages a release outside the public root, validates required files, backs up the current target, preserves server-managed `.well-known`, and copies the staged release into the verified document root.

## Required preflight

Before enabling deployment, verify through the existing authorised SSH setup:

- host, port, account, and host-key fingerprint;
- exact document root (never assume `public_html`);
- target is non-empty but is not `/`, `$HOME`, or an account root;
- write permission and sufficient disk for staged release plus backup;
- current root contains the expected HCDC/Nuxt site;
- `.well-known/acme-challenge` and `.well-known/pki-validation` are preserved.

The workflow intentionally fails if required secrets are absent or the target path is unsafe.

## Manual rollback

After target verification, set `HOST`, `PORT`, `USER`, `TARGET`, and the private key path from the GitHub environment, then restore the timestamped backup created immediately before deployment. Use a controlled remote copy, not an unguarded recursive delete. The exact command must be recorded here after the real HostingRaja backup directory and document root are verified.

Git rollback remains available locally and remotely:

```powershell
git fetch origin --tags
git switch main
git reset --hard baseline-before-hcdc-refresh-20260819
git push --force-with-lease origin main
```

The force-with-lease command is intentionally documented for an emergency repository rollback only and must not be run casually or against unrelated history.
