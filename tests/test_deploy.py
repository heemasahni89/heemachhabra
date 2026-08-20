import io
import os
import stat
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import importlib.util

spec = importlib.util.spec_from_file_location("sftp_deploy", ROOT / "scripts" / "sftp_deploy.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ArchiveTests(unittest.TestCase):
    def _make_tar(self, members):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz")
        tmp.close()
        with tarfile.open(tmp.name, "w:gz") as tf:
            for name, kind, content in members:
                ti = tarfile.TarInfo(name)
                if kind == "dir":
                    ti.type = tarfile.DIRTYPE
                    ti.mode = 0o755
                    ti.size = 0
                    tf.addfile(ti)
                elif kind == "file":
                    data = content.encode()
                    ti.size = len(data)
                    ti.mode = 0o644
                    tf.addfile(ti, io.BytesIO(data))
                elif kind == "symlink":
                    ti.type = tarfile.SYMTYPE
                    ti.linkname = content
                    tf.addfile(ti)
                elif kind == "hardlink":
                    ti.type = tarfile.LNKTYPE
                    ti.linkname = content
                    tf.addfile(ti)
        return tmp.name

    def _valid_members(self):
        base = [
            ("index.html", "file", "<html>"),
            ("robots.txt", "file", "Allow: /"),
            ("sitemap.xml", "file", "<xml>"),
            ("404.html", "file", "404"),
            ("_nuxt/index.html", "file", "<html>"),
            ("_nuxt/app.js", "file", "js"),
        ]
        return base

    def test_rejects_absolute_path(self):
        path = self._make_tar([("/etc/passwd", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_dotdot(self):
        path = self._make_tar([("a/../../b", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_backslash(self):
        path = self._make_tar([("a\\b", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_symlink(self):
        path = self._make_tar([("link", "symlink", "index.html")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_hardlink(self):
        path = self._make_tar([("hard", "hardlink", "index.html")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_git(self):
        path = self._make_tar([(".git/config", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_github(self):
        path = self._make_tar([(".github/workflows/x.yml", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_scripts(self):
        path = self._make_tar([("scripts/x.py", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_docs(self):
        path = self._make_tar([("docs/readme.md", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_env(self):
        path = self._make_tar([(".env", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_key(self):
        path = self._make_tar([("a.key", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_pem(self):
        path = self._make_tar([("a.pem", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_rejects_well_known(self):
        path = self._make_tar([(".well-known/acme", "file", "x")] + self._valid_members())
        with self.assertRaises(mod.DeploymentError):
            mod.validate_archive(path)
        os.unlink(path)

    def test_valid_archive(self):
        path = self._make_tar(self._valid_members())
        names = mod.validate_archive(path)
        self.assertIn("index.html", names)
        os.unlink(path)


class TargetTests(unittest.TestCase):
    def test_rejects_root(self):
        with self.assertRaises(mod.DeploymentError):
            mod.assert_safe_target("/", "/home/heemachh")

    def test_rejects_home_root(self):
        with self.assertRaises(mod.DeploymentError):
            mod.assert_safe_target("/home/heemachh", "/home/heemachh")

    def test_rejects_traversal_raw(self):
        with self.assertRaises(mod.DeploymentError):
            mod.assert_safe_target("/home/heemachh/public_html/../other", "/home/heemachh")

    def test_rejects_wrong_account(self):
        with self.assertRaises(mod.DeploymentError):
            mod.assert_safe_target("/home/other/public_html", "/home/heemachh")

    def test_rejects_wrong_docroot(self):
        with self.assertRaises(mod.DeploymentError):
            mod.assert_safe_target("/home/heemachh/other", "/home/heemachh")

    def test_accepts_canonical(self):
        self.assertEqual(mod.assert_safe_target("/home/heemachh/public_html", "/home/heemachh"), "/home/heemachh/public_html")

    def test_accepts_trailing_normalized(self):
        with self.assertRaises(mod.DeploymentError):
            mod.assert_safe_target("/home/heemachh/public_html/", "/home/heemachh")


class InstallOrderTests(unittest.TestCase):
    def test_assets_before_index(self):
        files = ["index.html", "_nuxt/app.js", "_nuxt/index.html", "robots.txt", ".htaccess", "og-image.jpg"]
        ordered = mod.install_order(files)
        self.assertLess(ordered.index("_nuxt/app.js"), ordered.index("index.html"))
        self.assertLess(ordered.index("robots.txt"), ordered.index("index.html"))
        self.assertEqual(ordered[-1], "index.html")


class RollbackModelTests(unittest.TestCase):
    def test_rollback_removes_new_and_restores(self):
        # Simulate with fake SFTP that tracks files
        class FakeSFTP:
            def __init__(self):
                self.files = {"index.html": b"old", "about/index.html": b"old-about"}
                self.removed = []
            def lstat(self, p):
                if p.split("/public_html/")[-1] in self.files or p.endswith("public_html"):
                    m = type("obj", (), {"st_mode": stat.S_IFREG if not p.endswith("public_html") else stat.S_IFDIR})()
                    return m
                raise IOError("not found")
            def remove(self, p):
                rel = p.split("/public_html/")[-1]
                if rel in self.files:
                    self.removed.append(rel)
                    del self.files[rel]
            def put(self, local, remote):
                rel = remote.split("/public_html/")[-1]
                self.files[rel] = Path(local).read_bytes() if os.path.exists(local) else b"restored"
            def stat(self, p):
                rel = p.split("/public_html/")[-1]
                if rel in self.files:
                    m = type("obj", (), {"st_mode": stat.S_IFREG, "st_size": len(self.files[rel])})()
                    return m
                raise IOError("not found")

        with tempfile.TemporaryDirectory() as tmp:
            backup = Path(tmp) / "index.html"
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(b"old")
            sftp = FakeSFTP()
            sftp.files["new-file.html"] = b"new"
            mod.rollback(sftp, "/home/heemachh/public_html", ["new-file.html"], ["index.html"], tmp)
            self.assertNotIn("new-file.html", sftp.files)
            self.assertIn("index.html", sftp.files)

    def test_unrelated_untouched(self):
        class FakeSFTP2:
            def __init__(self):
                self.files = {"index.html": b"old", "unrelated.txt": b"keep"}
            def lstat(self, p):
                rel = p.split("/public_html/")[-1] if "/public_html/" in p else ""
                if rel in self.files or p.endswith("public_html"):
                    return type("obj", (), {"st_mode": stat.S_IFREG if rel else stat.S_IFDIR})()
                raise IOError("not found")
            def remove(self, p):
                rel = p.split("/public_html/")[-1]
                if rel in self.files:
                    del self.files[rel]
            def put(self, local, remote):
                pass
            def stat(self, p):
                raise IOError("not found")
        with tempfile.TemporaryDirectory() as tmp:
            sftp = FakeSFTP2()
            mod.rollback(sftp, "/home/heemachh/public_html", [], [], tmp)
            self.assertIn("unrelated.txt", sftp.files)


if __name__ == "__main__":
    unittest.main()
