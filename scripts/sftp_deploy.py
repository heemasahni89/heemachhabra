#!/usr/bin/env python3
"""Pure-SFTP HCDC deployer with staged, rollback-safe overlay installation."""
from __future__ import annotations

import argparse
import base64
import hashlib
import os
import posixpath
import socket
import stat
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import uuid

import paramiko

PROTECTED = (".well-known",)
REQUIRED_FILES = ["index.html", "robots.txt", "sitemap.xml", "404.html", "_nuxt/index.html"]
EXPECTED_HOST_KEY = "SHA256:4+VB3nUB/C7jLTNCIwJg8oCG1gjWIu40u6fL7n5ON2o"
HTTP_ATTEMPTS = 4
HTTP_RETRY_DELAY = 3


class DeploymentError(RuntimeError):
    pass


def posix_parts(path: str) -> list[str]:
    return [part for part in path.lstrip("/").split("/") if part]


def is_protected(rel: str) -> bool:
    return any(rel == path or rel.startswith(path + "/") for path in PROTECTED)


def mode_is_directory(mode: int) -> bool:
    return stat.S_ISDIR(mode)


def mode_is_regular(mode: int) -> bool:
    return stat.S_ISREG(mode)


def mode_is_symlink(mode: int) -> bool:
    return stat.S_ISLNK(mode)


def sftp_mkdir_all(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    parts: list[str] = []
    for part in posix_parts(remote_dir):
        parts.append(part)
        candidate = "/" + "/".join(parts)
        try:
            attrs = sftp.lstat(candidate)
        except IOError:
            sftp.mkdir(candidate)
            continue
        if not mode_is_directory(attrs.st_mode) or mode_is_symlink(attrs.st_mode):
            raise DeploymentError(f"Remote path is not a real directory: {candidate}")


def sftp_rmtree(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    try:
        entries = sftp.listdir_attr(remote_dir)
    except IOError:
        return
    for entry in entries:
        full = posixpath.join(remote_dir, entry.filename)
        if mode_is_directory(entry.st_mode) and not mode_is_symlink(entry.st_mode):
            sftp_rmtree(sftp, full)
        else:
            try:
                sftp.remove(full)
            except IOError:
                pass
    try:
        sftp.rmdir(remote_dir)
    except IOError:
        pass


def remote_lstat(sftp: paramiko.SFTPClient, path: str):
    try:
        return sftp.lstat(path)
    except IOError:
        return None


def archive_forbidden_parts(name: str) -> str | None:
    parts = [part for part in name.rstrip("/").split("/") if part]
    for part in parts:
        lower = part.lower()
        if (
            part.startswith(".git")
            or part in {".github", ".commandcode", "docs", "scripts", ".well-known"}
            or part.startswith(".env")
            or lower.endswith((".key", ".pem"))
        ):
            return part
    return None


def safe_tar_members(tar: tarfile.TarFile) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for member in tar.getmembers():
        name = member.name
        if (
            not name
            or name.startswith(("/", "\\"))
            or "\\" in name
            or ".." in name
            or any(part == "" for part in name.rstrip("/").split("/"))
        ):
            raise DeploymentError(f"REJECTED unsafe archive member: {name!r}")
        canonical = name.rstrip("/")
        if canonical in seen:
            raise DeploymentError(f"REJECTED duplicate archive member: {name}")
        seen.add(canonical)
        forbidden = archive_forbidden_parts(name)
        if forbidden:
            raise DeploymentError(f"REJECTED forbidden archive member: {name}")
        if member.issym() or member.islnk():
            raise DeploymentError(f"REJECTED linked archive member: {name}")
        if not member.isdir() and not member.isfile():
            raise DeploymentError(f"REJECTED special archive member: {name}")
        names.append(name)
    return names


def validate_archive(archive_path: str) -> list[str]:
    with tarfile.open(archive_path, "r:gz") as archive:
        names = safe_tar_members(archive)
    missing = [required for required in REQUIRED_FILES if required not in names]
    if missing:
        raise DeploymentError(f"Archive missing required files: {missing}")
    release_files = sorted(name for name in names if not name.endswith("/"))
    release_set = set(release_files)
    for name in release_files:
        parents = posixpath.dirname(name)
        while parents:
            if parents in release_set:
                raise DeploymentError(f"Archive has incompatible file paths: {parents} and {name}")
            parents = posixpath.dirname(parents)
    return names


def fingerprint(key: paramiko.PKey) -> str:
    digest = hashlib.sha256(key.asbytes()).digest()
    return "SHA256:" + base64.b64encode(digest).decode().rstrip("=")


def connect(host: str, port: int, user: str, key_path: str, expected_sha256: str):
    sock = socket.create_connection((host, port), timeout=15)
    sock.settimeout(120)
    transport = paramiko.Transport(sock)
    transport.banner_timeout = 30
    transport.auth_timeout = 30
    transport.channel_timeout = 120
    try:
        transport.start_client(timeout=30)
        remote_key = transport.get_remote_server_key()
        actual = fingerprint(remote_key)
        expected = expected_sha256 or EXPECTED_HOST_KEY
        print(f"Remote host key: {actual}")
        if actual != expected:
            raise DeploymentError(f"Host key fingerprint mismatch for {host}: expected {expected}, got {actual}")
        print("Host-key verification: PASS")
        pkey = paramiko.RSAKey.from_private_key_file(key_path)
        transport.auth_publickey(user, pkey)
        if not transport.is_authenticated():
            raise DeploymentError("SFTP authentication failed")
        print("SFTP authentication: PASS")
        sftp = paramiko.SFTPClient.from_transport(transport)
        if sftp is None:
            raise DeploymentError("Failed to open SFTP channel")
        print("SFTP channel: PASS")
        return transport, sftp
    except Exception:
        transport.close()
        raise


def assert_safe_target(target_path: str, account_home: str) -> str:
    raw = target_path.strip()
    if not raw or raw == "/" or raw in ("$HOME", "$home") or raw.endswith("/"):
        raise DeploymentError(f"REJECTED unsafe deploy target: {target_path!r}")
    if "$" in raw or "\\" in raw or ".." in raw.split("/"):
        raise DeploymentError(f"REJECTED unsafe deploy target: {target_path!r}")
    expected = posixpath.normpath(f"{account_home}/public_html")
    normalized = posixpath.normpath(raw)
    if normalized != expected:
        raise DeploymentError(f"REJECTED deploy target must be {expected}: {target_path!r}")
    return normalized


def inspect_remote_targets(
    sftp: paramiko.SFTPClient, deploy_path: str, release_files: list[str]
) -> tuple[list[str], list[str]]:
    try:
        root = sftp.lstat(deploy_path)
        if not mode_is_directory(root.st_mode) or mode_is_symlink(root.st_mode):
            raise DeploymentError(f"Remote deploy path is not a real directory: {deploy_path}")
        entries = sftp.listdir_attr(deploy_path)
    except IOError as exc:
        raise DeploymentError(f"Cannot read remote deploy path {deploy_path}: {exc}") from exc
    print(f"Target read access: PASS ({len(entries)} immediate entries)")

    overwrites: list[str] = []
    creates: list[str] = []
    for rel in release_files:
        target = posixpath.join(deploy_path, rel)
        attrs = remote_lstat(sftp, target)
        if attrs is not None:
            if not mode_is_regular(attrs.st_mode) or mode_is_symlink(attrs.st_mode):
                raise DeploymentError(f"Incompatible remote target type: {target}")
            overwrites.append(rel)
        else:
            creates.append(rel)
        current = deploy_path
        for part in rel.split("/")[:-1]:
            current = posixpath.join(current, part)
            parent = remote_lstat(sftp, current)
            if parent is not None and (not mode_is_directory(parent.st_mode) or mode_is_symlink(parent.st_mode)):
                raise DeploymentError(f"Incompatible remote parent type: {current}")
    return sorted(overwrites), sorted(creates)


def upload_dir(sftp: paramiko.SFTPClient, local_dir: str, remote_dir: str) -> dict[str, int]:
    uploaded: dict[str, int] = {}
    total = 0
    for root, dirs, files in os.walk(local_dir):
        dirs.sort()
        files.sort()
        for name in files:
            source = os.path.join(root, name)
            rel = os.path.relpath(source, local_dir).replace(os.sep, "/")
            destination = posixpath.join(remote_dir, rel)
            sftp_mkdir_all(sftp, posixpath.dirname(destination))
            print(f"Uploading {rel} ({os.path.getsize(source)} bytes)...")
            sftp.put(source, destination)
            attrs = sftp.stat(destination)
            expected_size = os.path.getsize(source)
            if not mode_is_regular(attrs.st_mode) or attrs.st_size != expected_size:
                raise DeploymentError(f"Staged file verification failed: {rel}")
            uploaded[rel] = expected_size
            total += 1
            if total % 20 == 0:
                print(f"Staged progress: {total} files uploaded")
    return uploaded


def backup_files(
    sftp: paramiko.SFTPClient, deploy_path: str, release_files: list[str], backup_root: str
) -> None:
    for rel in release_files:
        remote = posixpath.join(deploy_path, rel)
        attrs = remote_lstat(sftp, remote)
        if attrs is None or not mode_is_regular(attrs.st_mode) or mode_is_symlink(attrs.st_mode):
            raise DeploymentError(f"Remote overwrite target changed before backup: {remote}")
        local = os.path.join(backup_root, rel)
        os.makedirs(os.path.dirname(local), exist_ok=True)
        sftp.get(remote, local)
        if os.path.getsize(local) != attrs.st_size:
            raise DeploymentError(f"Local backup verification failed: {rel}")


def install_order(release_files: list[str]) -> list[str]:
    priority = {
        "robots.txt": 2,
        "sitemap.xml": 3,
        "404.html": 4,
        ".htaccess": 5,
        "_nuxt/index.html": 6,
        "index.html": 7,
    }

    def sort_key(rel: str) -> tuple[int, str]:
        if rel in priority:
            return priority[rel], rel
        if rel.startswith("_nuxt/"):
            return 0, rel
        return 1, rel

    return sorted(release_files, key=sort_key)


def copy_remote_file(sftp: paramiko.SFTPClient, source: str, destination: str) -> None:
    with sftp.open(source, "rb") as source_file, sftp.open(destination, "wb") as destination_file:
        while True:
            chunk = source_file.read(1024 * 1024)
            if not chunk:
                break
            destination_file.write(chunk)


def install_file(
    sftp: paramiko.SFTPClient, staging: str, deploy_path: str, rel: str
) -> None:
    source = posixpath.join(staging, rel)
    destination = posixpath.join(deploy_path, rel)
    posix_rename = getattr(sftp, "posix_rename", None)
    if callable(posix_rename):
        try:
            posix_rename(source, destination)
            return
        except (IOError, OSError, paramiko.SSHException):
            pass
    copy_remote_file(sftp, source, destination)


def verify_installed_file(
    sftp: paramiko.SFTPClient, deploy_path: str, rel: str, expected_size: int
) -> None:
    attrs = sftp.stat(posixpath.join(deploy_path, rel))
    if not mode_is_regular(attrs.st_mode) or attrs.st_size != expected_size:
        raise DeploymentError(f"Installed file verification failed: {rel}")


def rollback(
    sftp: paramiko.SFTPClient,
    deploy_path: str,
    creates: list[str],
    overwrites: list[str],
    backup_root: str,
) -> None:
    errors: list[str] = []
    for rel in creates:
        remote = posixpath.join(deploy_path, rel)
        attrs = remote_lstat(sftp, remote)
        if attrs is None:
            continue
        if not mode_is_regular(attrs.st_mode) or mode_is_symlink(attrs.st_mode):
            errors.append(f"cannot remove new non-file {rel}")
            continue
        try:
            sftp.remove(remote)
        except IOError as exc:
            errors.append(f"cannot remove new file {rel}: {exc}")
    for rel in overwrites:
        local = os.path.join(backup_root, rel)
        remote = posixpath.join(deploy_path, rel)
        try:
            sftp.put(local, remote)
            expected_size = os.path.getsize(local)
            verify_installed_file(sftp, deploy_path, rel, expected_size)
        except (IOError, OSError, DeploymentError) as exc:
            errors.append(f"cannot restore {rel}: {exc}")
    if errors:
        raise DeploymentError("; ".join(errors))


def http_response(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            return response.getcode(), response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception:
        return 0, ""


def smoke_test(base_url: str) -> tuple[bool, dict[str, int]]:
    last_codes = {"/": 0, "/robots.txt": 0, "/sitemap.xml": 0, "404": 0}
    for attempt in range(HTTP_ATTEMPTS):
        homepage_code, homepage = http_response(base_url + "/")
        robots_code, _ = http_response(base_url + "/robots.txt")
        sitemap_code, _ = http_response(base_url + "/sitemap.xml")
        missing_code, _ = http_response(base_url + "/__hcdc-production-check-missing__")
        last_codes = {"/": homepage_code, "/robots.txt": robots_code, "/sitemap.xml": sitemap_code, "404": missing_code}
        valid = (
            homepage_code == 200
            and robots_code == 200
            and sitemap_code == 200
            and missing_code == 404
            and "Heema Chhabra Design Consultant" in homepage
            and 'href="https://heemachhabra.com/"' in homepage
        )
        if valid:
            return True, last_codes
        if attempt + 1 < HTTP_ATTEMPTS:
            time.sleep(HTTP_RETRY_DELAY)
    return False, last_codes


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

    try:
        account_home = f"/home/{args.user}"
        deploy_path = assert_safe_target(args.deploy_path, account_home)
        names = validate_archive(args.archive)
        release_files = sorted(name for name in names if not name.endswith("/"))
        print(f"Archive OK: {len(release_files)} release files")

        transport, sftp = connect(args.host, args.port, args.user, args.key, args.host_key_sha256)
        transport.set_keepalive(15)
        staging = ""
        try:
            protected = remote_lstat(sftp, posixpath.join(deploy_path, ".well-known")) is not None
            overwrites, creates = inspect_remote_targets(sftp, deploy_path, release_files)
            print("SFTP PREFLIGHT PASSED")
            print(f"Target: {deploy_path}")
            print(f"Release files: {len(release_files)}")
            print(f"OVERWRITE: {len(overwrites)}")
            print(f"CREATE: {len(creates)}")
            print(f".well-known: {'PROTECTED' if protected else 'ABSENT (nothing modified)'}")
            if args.dry_run:
                print("Dry run: zero remote writes performed.")
                return 0

            release_id = uuid.uuid4().hex
            staging = posixpath.join(account_home, ".hcdc-staging", release_id)
            sftp_mkdir_all(sftp, staging)
            with tempfile.TemporaryDirectory(prefix="hcdc-stage-") as extracted_dir, tempfile.TemporaryDirectory(
                prefix="hcdc-backup-"
            ) as backup_root:
                with tarfile.open(args.archive, "r:gz") as archive:
                    safe_tar_members(archive)
                    archive.extractall(extracted_dir)
                staged = upload_dir(sftp, extracted_dir, staging)
                if len(staged) != len(release_files) or set(staged) != set(release_files):
                    raise DeploymentError("Staged release file inventory mismatch")
                for required in REQUIRED_FILES:
                    staged_required = staged.get(required)
                    if staged_required is None or remote_lstat(sftp, posixpath.join(staging, required)) is None:
                        raise DeploymentError(f"Staged missing required file: {required}")
                print(f"Staging verified: {len(staged)} files with matching sizes")

                backup_files(sftp, deploy_path, overwrites, backup_root)
                print(f"Backups verified: {len(overwrites)} files")
                try:
                    for rel in install_order(release_files):
                        destination = posixpath.join(deploy_path, rel)
                        sftp_mkdir_all(sftp, posixpath.dirname(destination))
                        install_file(sftp, staging, deploy_path, rel)
                        verify_installed_file(sftp, deploy_path, rel, staged[rel])
                    print(f"Overlay installed: {len(release_files)} files")

                    sftp_rmtree(sftp, staging)
                    staging = ""
                    smoke_ok, codes = smoke_test(args.production_url.rstrip("/"))
                    for path, code in (("/", codes["/"]), ("/robots.txt", codes["/robots.txt"]), ("/sitemap.xml", codes["/sitemap.xml"])):
                        print(f"{'OK' if code == 200 else 'FAIL'} {path}: HTTP {code}")
                    print(f"{'OK' if codes['404'] == 404 else 'FAIL'} missing URL: HTTP {codes['404']}")
                    if smoke_ok:
                        print("SMOKE TESTS PASSED")
                        print("DEPLOY SUCCEEDED")
                        return 0
                    raise DeploymentError("Production smoke tests failed")
                except Exception as exc:
                    print(f"Deployment failed after production writes: {exc}")
                    try:
                        rollback(sftp, deploy_path, creates, overwrites, backup_root)
                        rollback_code, _ = http_response(args.production_url.rstrip("/") + "/")
                        if rollback_code != 200:
                            raise DeploymentError(f"homepage after rollback returned HTTP {rollback_code}")
                        print("ROLLBACK PASSED")
                    except Exception as rollback_exc:
                        print(f"ROLLBACK FAILED: {rollback_exc}")
                        return 2
                    print("ROLLBACK RESULT: production restored")
                    return 2
        except Exception:
            raise
        finally:
            if staging:
                try:
                    sftp_rmtree(sftp, staging)
                except IOError as exc:
                    print(f"Staging cleanup warning: {exc}")
            sftp.close()
            transport.close()
    except DeploymentError as exc:
        print(f"DEPLOY FAILED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
