from pathlib import Path
import argparse
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "site-release.tar.gz"
REQUIRED = ["index.html", "robots.txt", "sitemap.xml", "404.html", "_nuxt"]
EXCLUDED_PARTS = {".git", ".github", ".commandcode", ".well-known", "docs", "scripts", "node_modules", "content", "tests"}
EXCLUDED_NAMES = {"README.md", "website.pptx", "website.ppt", ".gitignore", ".gitattributes", "site-release.tar.gz"}


def include(path):
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.name.startswith(".env") or path.name == ".gitignore":
        return False
    if path.suffix.lower() in {".rar", ".zip", ".log", ".key", ".pem"}:
        return False
    return path.is_file()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    missing = [name for name in REQUIRED if not (ROOT / name).exists()]
    if missing:
        raise SystemExit(f"Missing required production files: {', '.join(missing)}")
    files = sorted(path for path in ROOT.rglob("*") if include(path))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, "w:gz") as archive:
        for path in files:
            archive.add(path, arcname=path.relative_to(ROOT).as_posix(), recursive=False)
    with tarfile.open(args.output, "r:gz") as archive:
        names = archive.getnames()
    forbidden = [name for name in names if name.startswith((".git/", ".github/", "docs/", "scripts/")) or name in {".git", ".github", "README.md", "website.pptx"}]
    if forbidden:
        raise SystemExit(f"Forbidden archive entries: {forbidden}")
    print(f"Packaged {len(names)} production files into {args.output}")


if __name__ == "__main__":
    main()
