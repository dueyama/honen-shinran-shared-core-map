#!/usr/bin/env python3
"""Pre-publication safety checks for Okyou2.

This script checks the files that Git would publish: tracked files plus
untracked files not excluded by .gitignore. It intentionally does not inspect
ignored private corpora except to confirm that they are not publication
candidates.
"""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MAX_PUBLIC_FILE_SIZE = 20 * 1024 * 1024
PUBLIC_PAPER_PDF = "honen-shinran-shared-core-paper.pdf"
PUBLIC_PAPER_EN_PDF = "honen-shinran-shared-core-paper-en.pdf"

FORBIDDEN_PREFIXES = (
    "data/",
    "tmp/",
    "お経/",
    "埋め込みお経/",
    "埋め込みテスト/",
)
FORBIDDEN_SUFFIXES = (
    ".aux",
    ".dvi",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".synctex.gz",
    ".toc",
    ".pyc",
    ".npy",
    ".npz",
    ".pkl",
    ".pickle",
    ".parquet",
    ".feather",
    ".sqlite",
    ".sqlite3",
    ".db",
)

SECRET_PATTERNS = {
    "openai_key_like": re.compile(rb"sk-(?:proj-)?[A-Za-z0-9_\-]{20,}"),
    "github_token_like": re.compile(rb"(?:ghp|github_pat)_[A-Za-z0-9_]{20,}"),
    "google_api_key_like": re.compile(rb"AIza[0-9A-Za-z_\-]{20,}"),
    "aws_access_key_like": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "private_key_block": re.compile(
        rb"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"
    ),
    "env_secret_assignment": re.compile(
        rb"(?im)^(?:OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|GH_TOKEN|"
        rb"AWS_SECRET_ACCESS_KEY|DATABASE_URL)="
    ),
}

LONG_FLOAT_VECTOR = re.compile(rb"\[(?:\s*-?\d+\.\d+(?:e[-+]?\d+)?\s*,){40,}", re.I)
LOCAL_PATH_MARKERS = (
    "/" + "Users/",
    "/" + "private/",
    "file" + "://",
)
REQUIRED_PUBLIC_FILES = (
    "README.md",
    "AI_RESEARCHER_GUIDE.md",
    "LICENSE",
    "LICENSE-CODE",
    "LICENSE-CONTENT",
    "docs/index.html",
    "docs/en/index.html",
    "docs/paper/index.html",
    "docs/paper/en/index.html",
    "docs/paper/honen-shinran-shared-core-paper.pdf",
    "docs/paper/honen-shinran-shared-core-paper.tex",
    "docs/paper/honen-shinran-shared-core-paper-en.pdf",
    "docs/paper/honen-shinran-shared-core-paper-en.tex",
    "docs/checksums.txt",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        for key in ("href", "src"):
            value = attr_map.get(key)
            if value:
                self.refs.append((tag, key, value))
        for key in ("id", "name"):
            value = attr_map.get(key)
            if value:
                self.ids.add(value)


class NavLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.nav_depth = 0
        self.current_link: dict[str, str] | None = None
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag == "nav":
            self.nav_depth += 1
        elif self.nav_depth and tag == "a":
            self.current_link = {"href": attr_map.get("href") or "", "text": ""}
            self.links.append(self.current_link)

    def handle_data(self, data: str) -> None:
        if self.current_link is not None:
            self.current_link["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.current_link = None
        elif tag == "nav" and self.nav_depth:
            self.nav_depth -= 1


def run_git(args: list[str]) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def git_files(args: list[str]) -> list[str]:
    output = run_git(args)
    return [item.decode("utf-8") for item in output.split(b"\0") if item]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_checksum_file(path: Path) -> dict[str, str]:
    current_path: str | None = None
    checksums: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("Path: "):
            current_path = line.removeprefix("Path: ").strip()
        elif line.startswith("SHA-256: ") and current_path:
            checksums[current_path] = line.removeprefix("SHA-256: ").strip()
            current_path = None
    return checksums


def collect_html_ids(path: Path) -> set[str]:
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.ids


def check_html_links() -> list[str]:
    errors: list[str] = []
    html_ids: dict[Path, set[str]] = {}
    for html_path in sorted(DOCS.rglob("*.html")):
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for _tag, _key, value in parser.refs:
            if not value or value.startswith(
                ("http://", "https://", "mailto:", "tel:", "javascript:")
            ):
                continue
            parsed = urlparse(value)
            if parsed.scheme and parsed.scheme != "file":
                continue
            if parsed.path == "" and parsed.fragment:
                target = html_path
            else:
                raw_path = unquote(parsed.path)
                if raw_path.startswith("/"):
                    errors.append(f"{html_path.relative_to(ROOT)} -> {value}: root-relative")
                    continue
                target = (html_path.parent / raw_path).resolve()
                if target.is_dir() or value.endswith("/"):
                    target = target / "index.html"
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{html_path.relative_to(ROOT)} -> {value}: outside repo")
                continue
            if not target.exists():
                errors.append(f"{html_path.relative_to(ROOT)} -> {value}: missing target")
                continue
            if parsed.fragment and target.suffix == ".html":
                if target not in html_ids:
                    html_ids[target] = collect_html_ids(target)
                if parsed.fragment not in html_ids[target]:
                    errors.append(
                        f"{html_path.relative_to(ROOT)} -> {value}: missing fragment"
                    )
    return errors


def check_nav_links() -> list[str]:
    errors: list[str] = []
    expected_targets = {
        "GitHub": lambda href: href == "https://github.com/dueyama/honen-shinran-shared-core-map",
        "PDF JP": lambda href: href.endswith(PUBLIC_PAPER_PDF),
        "PDF EN": lambda href: href.endswith(PUBLIC_PAPER_EN_PDF),
    }
    for html_path in sorted(DOCS.rglob("*.html")):
        parser = NavLinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        if not parser.links:
            continue
        rel = html_path.relative_to(ROOT)
        by_text = {link["text"].strip(): link["href"] for link in parser.links}
        for text, matcher in expected_targets.items():
            href = by_text.get(text)
            if href is None:
                errors.append(f"{rel}: missing nav link {text}")
            elif not matcher(href):
                errors.append(f"{rel}: unexpected nav link {text} -> {href}")
    return errors


def is_public_text_file(path: Path) -> bool:
    return path.suffix.lower() in {".html", ".md", ".tex", ".txt", ".css", ".js"}


def main() -> int:
    tracked = git_files(["ls-files", "-z"])
    others = git_files(["ls-files", "--others", "--exclude-standard", "-z"])
    candidates = sorted(set(tracked + others))

    errors: list[str] = []
    warnings: list[str] = []

    for required in REQUIRED_PUBLIC_FILES:
        if required not in candidates:
            errors.append(f"required public file is not a git candidate: {required}")

    for rel in candidates:
        path = ROOT / rel
        if (
            rel == ".env"
            or rel.startswith(FORBIDDEN_PREFIXES)
            or rel.endswith(FORBIDDEN_SUFFIXES)
            or "/__pycache__/" in rel
            or rel.startswith("__pycache__/")
        ):
            errors.append(f"forbidden path is a git candidate: {rel}")
            continue
        if not path.exists() or path.is_dir():
            continue

        data = path.read_bytes()
        if path.stat().st_size > MAX_PUBLIC_FILE_SIZE:
            errors.append(f"public candidate exceeds size limit: {rel}")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                errors.append(f"secret-like pattern {name} in {rel}")
        if LONG_FLOAT_VECTOR.search(data):
            errors.append(f"long float vector-like data in {rel}")
        if rel.startswith("docs/") and is_public_text_file(path):
            text = data.decode("utf-8", errors="ignore")
            for marker in LOCAL_PATH_MARKERS:
                if marker in text:
                    errors.append(f"local path marker {marker!r} in public doc {rel}")

    checksum_path = ROOT / "docs/checksums.txt"
    if checksum_path.exists():
        for rel, expected in parse_checksum_file(checksum_path).items():
            path = ROOT / rel
            if not path.exists():
                errors.append(f"checksum target is missing: {rel}")
                continue
            actual = sha256(path)
            if actual != expected:
                errors.append(f"checksum mismatch: {rel}")
    else:
        errors.append("docs/checksums.txt is missing")

    errors.extend(check_html_links())
    errors.extend(check_nav_links())

    predecessor = ROOT.parent / "Okyou"
    if predecessor.exists():
        status = subprocess.check_output(
            ["git", "-C", str(predecessor), "status", "--short"]
        ).decode("utf-8")
        if status.strip():
            warnings.append("predecessor Okyou has local changes; inspect before release")

    print(f"checked git candidates: {len(candidates)}")
    print(f"tracked: {len(tracked)}")
    print(f"untracked publication candidates: {len(others)}")
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print("FAILED publication safety checks:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("OK publication safety checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
