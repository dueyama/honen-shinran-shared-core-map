#!/usr/bin/env python3
"""Prepare clean SAT kanbun-basis texts for local analysis.

This script does not call embedding APIs. It fetches/parses SAT HTML, extracts
text rows, validates that no parser garbage remains, and writes local-only
processed text files under ignored data/.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "sat_kanbun"
OUT_DIR = ROOT / "data" / "processed" / "sat_kanbun"
MANIFEST_PATH = OUT_DIR / "manifest.json"

WORKS = [
    {
        "id": "honen_t2608_senchakushu",
        "author": "法然",
        "work": "選択本願念仏集",
        "sat_id": "T2608",
        "title_original": "選擇本願念佛集",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T2608.html",
        "source_note": "SAT T2608.",
    },
    {
        "id": "shinran_t2646_kyogyoshinsho",
        "author": "親鸞",
        "work": "教行信証",
        "sat_id": "T2646",
        "title_original": "顯淨土眞實教行證文類",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T2646_,83,0589a01:2646_,83,0643c29.html",
        "source_note": "SAT T2646 full range 83:0589a01-0643c29.",
    },
]

BAD_PATTERNS = [
    ("replacement_character", re.compile("\ufffd")),
    ("html_tag", re.compile(r"</?\w+")),
    ("html_entity", re.compile(r"&(?:[A-Za-z]+|#[0-9]+|#x[0-9A-Fa-f]+);")),
    ("image_placeholder", re.compile(r"Image:")),
    ("button_label", re.compile(r"\[?Button:?")),
    ("sat_line_ref_in_body", re.compile(r"T\d{4}[A-Z]?_\.\d{2}\.\d{4}[abcx]\d{2}:?")),
    ("control_character", re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")),
]


@dataclass(frozen=True)
class PreparedLine:
    line_ref: str
    text: str


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def fetch_url(url: str, path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    request = urllib.request.Request(url, headers={"User-Agent": "Okyou2 research script"})
    with urllib.request.urlopen(request, timeout=120) as response:
        raw = response.read().decode("utf-8", errors="replace")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw, encoding="utf-8")
    return raw


def clean_body(body_html: str) -> str:
    body_html = re.sub(
        r"<button\b.*?</button>",
        "",
        body_html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    body_html = re.sub(r"<vbr\s*/?>", "", body_html, flags=re.IGNORECASE)
    body = re.sub(r"<[^>]+>", "", body_html)
    body = html.unescape(body).replace("\xa0", " ")
    body = re.sub(r"Image:\s*&[^;]+;", "", body)
    body = re.sub(r"\s+", "", body)
    return body


def validate_text(label: str, text: str) -> list[dict[str, str]]:
    issues = []
    if not text:
        issues.append({"type": "empty_text", "sample": ""})
    for issue_type, pattern in BAD_PATTERNS:
        match = pattern.search(text)
        if match:
            start = max(match.start() - 20, 0)
            end = min(match.end() + 20, len(text))
            issues.append({"type": issue_type, "sample": text[start:end]})
    return issues


def parse_sat_lines(source: str) -> tuple[list[PreparedLine], list[dict[str, str]]]:
    rows = re.findall(
        r'<span style="color:black">(T[^<]+)</span><a name="[^"]*">(.*?)</a><br\s*/?>',
        source,
        flags=re.DOTALL,
    )
    lines: list[PreparedLine] = []
    issues: list[dict[str, str]] = []
    for line_ref, body_html in rows:
        line_ref = line_ref.rstrip(": ")
        body = clean_body(body_html)
        if not body or body.startswith("No."):
            continue
        for issue in validate_text(line_ref, body):
            issues.append({"line_ref": line_ref, **issue})
        lines.append(PreparedLine(line_ref=line_ref, text=body))
    if not lines:
        issues.append({"line_ref": "", "type": "no_lines_parsed", "sample": ""})
    return lines, issues


def write_lines(work: dict[str, str], lines: list[PreparedLine]) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    txt_path = OUT_DIR / f"{work['id']}.txt"
    jsonl_path = OUT_DIR / f"{work['id']}.lines.jsonl"
    joined = "\n".join(line.text for line in lines) + "\n"
    txt_path.write_text(joined, encoding="utf-8")
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for index, line in enumerate(lines):
            handle.write(
                json.dumps(
                    {
                        "index": index,
                        "line_ref": line.line_ref,
                        "text": line.text,
                        "text_sha256": sha256_text(line.text),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    compact = "".join(line.text for line in lines)
    return {
        "txt_path": str(txt_path.relative_to(ROOT)),
        "jsonl_path": str(jsonl_path.relative_to(ROOT)),
        "line_count": len(lines),
        "char_count_with_newlines": len(joined),
        "char_count_compact": len(compact),
        "compact_sha256": sha256_text(compact),
        "first_line_ref": lines[0].line_ref,
        "last_line_ref": lines[-1].line_ref,
    }


def prepare_work(work: dict[str, str]) -> dict[str, Any]:
    raw_path = RAW_DIR / f"{work['id']}.html"
    source = fetch_url(work["source_url"], raw_path)
    lines, issues = parse_sat_lines(source)
    compact = "".join(line.text for line in lines)
    issues.extend({"line_ref": "", **issue} for issue in validate_text(work["sat_id"], compact))
    output = write_lines(work, lines) if not issues else None
    return {
        **work,
        "raw_path": str(raw_path.relative_to(ROOT)),
        "raw_sha256": sha256_text(source),
        "status": "ok" if not issues else "blocked",
        "quality_issues": issues,
        "output": output,
    }


def main() -> None:
    records = [prepare_work(work) for work in WORKS]
    manifest = {
        "title": "Prepared SAT kanbun-basis texts for Okyou2 local analysis",
        "raw_text_policy": "data/ is ignored; prepared text files are local-only and must not be committed or published.",
        "parser_policy": "SAT line bodies only; line refs are kept in JSONL metadata, not in body text.",
        "quality_checks": [name for name, _ in BAD_PATTERNS] + ["empty_text", "no_lines_parsed"],
        "works": records,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {MANIFEST_PATH}")
    for record in records:
        output = record["output"] or {}
        print(
            record["sat_id"],
            record["status"],
            "lines",
            output.get("line_count"),
            "chars",
            output.get("char_count_compact"),
            "issues",
            len(record["quality_issues"]),
        )
    if any(record["status"] != "ok" for record in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
