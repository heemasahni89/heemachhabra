#!/usr/bin/env python3
"""Pure-SFTP HCDC deployer.

Deploys site-release.tar.gz to a HostingRaja-style account that has shell
access DISABLED but permits SFTP (the case here). No rsync, no shell, no
unguarded rm -rf. The immutable git tag `baseline-before-hcdc-refresh-20260819`
is the definitive rollback point.

Usage:
    python3 scripts/sftp_deploy.py \
        --host 103.92.235.110 --port 22 \
        --user heemachh --deploy-path /home/heemachh/public_html \
        --key ~/.ssh/deploy_key \
        --archive site-release.tar.gz \
        [--host-key-sha256 SHA256:xxx] \
        [--production-url https://heemachhabra.com] \
        [--dry-run]
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import os
import posixpath
import tarfile
import tempfile
import urllib.error
import urllib.request

import paramiko

PROTECTED = (".well-known",)
REQUIRED_FILES = ["index.html", "robots.txt", "sitemap.xml", "404.html", "_nuxt/index.html"]


def posix_parts(path: str) -> list[str]:
    return [p for p in path.lstrip("/").split("/") if p]


def sftp_mkdir_all(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    parts: list[str] = []
    for part in posix_parts(remote_dir):
        parts.append(part)
        candidate = "/" + "/".join(parts)
        try:
            sftp.stat(candidate)
        except IOError:
            sftp.mkdir(candidate)


def sftp_rmtree(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    def walk(path: str) -> None:
        try:
            for entry in sftp.listdir_attr(path):
                full = posixpath.join(path, entry.filename)
                if entry.st_mode is not None and (entry.st_mode & 0o170000) == 0o040000:
                    walk(full)
                else:
                    try:
                        sftp.remove(full)
                    except IOError:
                        pass
        except IOError:
            pass
    walk(remote_dir)
    try:
        sftp.rmdir(remote_dir)
    except IOError:
        pass


def is_dir(sftp: paramiko.SFTPClient, path: str) -> bool:
    try:
        return (sftp.stat(path).st_mode & 0o170000) == 0o040000
    except IOError:
        return False


def path_exists(sftp: paramiko.SFTPClient, path: str) -> bool:
    try:
        sftp.stat(path)
        return True
    except IOError:
        return False


def assert_safe_target(target_path: str, account_home: str) -> str:
    t = target_path.strip()
    if not t or t == "/" or t in ("$HOME", "$home") or t.endswith("/"):
        raise SystemExit(f"REJECTED unsafe deploy target: {target_path!r}")
    if "$" in t:
        raise SystemExit(f"REJECTED shell-variable target: {target_path!r}")
    if not t.startswith(account_home + "/"):
        raise SystemExit(f"REJECTED target not under hosting account home {account_home}: {target_path!r}")
    return t


def validate_archive(archive_path: str) -> list[str]:
    with tarfile.open(archive_path, "r:gz") as archive:
        names = archive.getnames()
    missing = [f for f in REQUIRED_FILES if f not in names]
    if missing:
        raise SystemExit(f"Archive missing required files: {missing}")
    forbidden = [n for n in names
                 if n.startswith((".git", ".github", "docs", "scripts"))
                 or n in {"README.md", "website.pptx", "website.ppt"}]
    if forbidden:
        raise SystemExit(f"Archive contains forbidden entries: {forbidden}")
    return names


def connect(host: str, port: int, user: str, key_path: str, expected_sha256: str):
    transport = paramiko.Transport((host, port))
    pkey = paramiko.RSAKey.from_private_key_file(key_path)
    transport.connect(username=user, pkey=pkey)
    sftp = paramiko.SFTPClient.from_transport(transport)
    if sftp is None:
        transport.close()
        raise SystemExit("Failed to open SFTP channel")
    key = transport.get_remote_server_key()
    digest = hashlib.sha256(key.asbytes()).digest()
    actual = "SHA256:" + base64.b64encode(digest).decode().rstrip("=")
    print(f"Remote host key: {actual}")
    if expected_sha256 and actual != expected_sha256:
        sftp.close(); transport.close()
        raise SystemExit(f"Host key fingerprint mismatch for {host}: expected {expected_sha256}, got {actual}")
    return transport, sftp


def upload_dir(sftp: paramiko.SFTPClient, local_dir: str, remote_dir: str) -> int:
    count = 0
    for root, dirs, files in os.walk(local_dir):
        dirs[:] = [d for d in dirs if d not in (".git", ".github", "docs", "scripts") and not d.startswith(".git")]
        for name in files:
            src = os.path.join(root, name)
            rel = os.path.relpath(src, local_dir).replace(os.sep, "/")
            dst = posixpath.join(remote_dir, rel)
            sftp_mkdir_all(sftp, posixpath.dirname(dst))
            sftp.put(src, dst)
            count += 1
    return count


def http_code(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return resp.getcode()
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return 0


def text_contains(url: str, needle: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return needle in resp.read().decode("utf-8", "replace")
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--user", required=True)
    parser.add_argument("--deploy-path", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--host-key-sha256", default="")
    parser.add_argument("--archive", required=True)
    parser.add_argument("--production-url", default="https://heemachhabra.com")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    account_home = f"/home/{args.user}"
    deploy_path = assert_safe_target(args.deploy_path, account_home)
    names = validate_archive(args.archive)
    print(f"Archive OK: {len(names)} entries, target {deploy_path}")

    if args.dry_run:
        print("Dry run: skipping network operations.")
        return 0

    transport, sftp = connect(args.host, args.port, args.user, args.key, args.host_key_sha256)
    transport.set_keepalive(15)

    if not is_dir(sftp, deploy_path):
        sftp.close(); transport.close()
        raise SystemExit(f"Remote deploy path is not a directory: {deploy_path}")

    staging = posixpath.join(account_home, ".hcdc-staging")
    sftp_rmtree(sftp, staging)
    sftp_mkdir_all(sftp, staging)

    extracted_dir = tempfile.mkdtemp(prefix="hcdc-stage-")
    with tarfile.open(args.archive, "r:gz") as archive:
        archive.extractall(extracted_dir)

    print("Uploading staged release...")
    stage_count = upload_dir(sftp, extracted_dir, staging)
    print(f"Uploaded {stage_count} staged files.")
    for f in REQUIRED_FILES:
        if not path_exists(sftp, posixpath.join(staging, f)):
            sftp.close(); transport.close()
            raise SystemExit(f"Staged missing required file: {f}")

    print("Installing release (preserving .well-known)...")
    for entry in sftp.listdir_attr(deploy_path):
        if entry.filename in PROTECTED:
            continue
        full = posixpath.join(deploy_path, entry.filename)
        if entry.st_mode is not None and (entry.st_mode & 0o170000) == 0o040000:
            sftp_rmtree(sftp, full)
        else:
            try:
                sftp.remove(full)
            except IOError:
                pass
    for entry in sftp.listdir_attr(staging):
        sftp.rename(posixpath.join(staging, entry.filename), posixpath.join(deploy_path, entry.filename))
    sftp_rmtree(sftp, staging)
    print("Deploy complete. Running smoke tests...")

    ok = True
    for path in ["/", "/robots.txt", "/sitemap.xml"]:
        code = http_code(args.production_url + path)
        print(f"{'OK' if code == 200 else 'FAIL'} {path}: HTTP {code}")
        ok = ok and code == 200
    missing_code = http_code(args.production_url + "/__hcdc_missing_check__")
    print(f"{'OK' if missing_code == 404 else 'FAIL'} missing URL: HTTP {missing_code}")
    ok = ok and missing_code == 404
    ok = text_contains(args.production_url + "/", "Heema Chhabra Design Consultant") and ok

    if ok:
        print("DEPLOY SUCCEEDED")
        sftp.close(); transport.close()
        return 0
    print("Smoke test failed; clearing deploy target. Restore from git tag baseline-before-hcdc-refresh-20260819 or re-run deploy.")
    for entry in sftp.listdir_attr(deploy_path):
        if entry.filename in PROTECTED:
            continue
        full = posixpath.join(deploy_path, entry.filename)
        if entry.st_mode is not None and (entry.st_mode & 0o170000) == 0o040000:
            sftp_rmtree(sftp, full)
        else:
            try:
                sftp.remove(full)
            except IOError:
                pass
    sftp.close(); transport.close()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
