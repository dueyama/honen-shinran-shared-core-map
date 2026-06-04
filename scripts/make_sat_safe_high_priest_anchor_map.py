#!/usr/bin/env python3
"""Build the SAT kanbun safe-chunk Honen/Shinran map with patriarch anchors."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import tiktoken


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compare_sat_chunking_strategies import (  # noqa: E402
    MAX_TOKENS,
    MODEL,
    OVERLAP,
    get_embeddings as get_focus_embeddings,
    load_works,
    make_safe_chunks,
    request_embeddings,
    rounded,
)
from sat_safe_map_renderer import (  # noqa: E402
    ANCHOR_AUTHORS,
    FOCUS_AUTHORS,
    render_sat_safe_map_png,
)


RAW_DIR = ROOT / "data" / "raw" / "sat_anchors"
CACHE_DIR = ROOT / "data" / "cache"
OUT_DIR = ROOT / "data" / "outputs"
CACHE_PATH = CACHE_DIR / f"sat_safe_high_priest_anchor_embeddings_{MODEL}_{MAX_TOKENS}_{OVERLAP}.json"
META_PATH = OUT_DIR / f"sat_safe_honen_shinran_high_priest_anchor_map_{MODEL}_{MAX_TOKENS}_{OVERLAP}.json"
PNG_PATH = OUT_DIR / f"sat_safe_honen_shinran_high_priest_anchor_map_{MODEL}_{MAX_TOKENS}_{OVERLAP}.png"
DOC_FIGURE_PATH = ROOT / "docs/figures/sat-safe-honen-shinran-high-priest-anchor-map.png"
BATCH_SIZE = int(os.getenv("OKYOU2_EMBEDDING_BATCH_SIZE", "64"))


ANCHORS = [
    {
        "id": "nagarjuna_easy_practice",
        "author": "龍樹",
        "work": "十住毘婆沙論 易行品",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T1521_,26,0038a25:1521_,26,0040a22.html",
        "source_note": "SAT range for T1521 易行品 candidate range.",
    },
    {
        "id": "vasubandhu_jodoron",
        "author": "天親",
        "work": "無量寿経優波提舎願生偈",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T1524.html",
        "source_note": "SAT T1524.",
    },
    {
        "id": "tanluan_jodoronchu",
        "author": "曇鸞",
        "work": "往生論註",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T1819.html",
        "source_note": "SAT T1819.",
    },
    {
        "id": "daochuo_anleji",
        "author": "道綽",
        "work": "安楽集",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T1958.html",
        "source_note": "SAT T1958.",
    },
    {
        "id": "shandao_guanjingshu",
        "author": "善導",
        "work": "観無量寿仏経疏",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T1753.html",
        "source_note": "SAT T1753.",
    },
    {
        "id": "genshin_ojoyoshu",
        "author": "源信",
        "work": "往生要集",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T2682.html",
        "source_note": "SAT T2682.",
    },
]


BAD_TEXT_PATTERNS = [
    ("replacement_character", re.compile("\ufffd")),
    ("html_tag", re.compile(r"</?\w+")),
    ("html_entity", re.compile(r"&(?:[A-Za-z]+|#[0-9]+|#x[0-9A-Fa-f]+);")),
    ("image_placeholder", re.compile(r"Image:")),
    ("button_label", re.compile(r"\[?Button:?")),
    ("sat_line_ref_in_body", re.compile(r"T\d{4}[A-Z]?_\.\d{2}\.\d{4}[abcx]\d{2}:?")),
    ("control_character", re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")),
]


@dataclass
class AnchorLine:
    line_ref: str
    text: str
    char_start: int
    char_end: int


@dataclass
class AnchorText:
    id: str
    author: str
    work: str
    source_url: str
    source_note: str
    raw_path: Path
    lines: list[AnchorLine]
    body: str


@dataclass
class AnchorChunk:
    chunk_id: str
    author: str
    work: str
    anchor_id: str
    chunk_index: int
    text: str
    char_start: int
    char_end: int
    token_start: int
    token_end: int
    source_token_count: int
    actual_token_count: int
    line_start: str
    line_end: str
    source_url: str
    source_note: str


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
    return re.sub(r"\s+", "", body)


def validate_text(label: str, text: str) -> None:
    if not text:
        raise ValueError(f"{label}: empty text")
    for name, pattern in BAD_TEXT_PATTERNS:
        match = pattern.search(text)
        if match:
            start = max(match.start() - 24, 0)
            end = min(match.end() + 24, len(text))
            raise ValueError(f"{label}: invalid pattern {name}: {text[start:end]!r}")


def parse_sat_lines(source: str) -> list[tuple[str, str]]:
    rows = re.findall(
        r'<span style="color:black">(T[^<]+)</span><a name="[^"]*">(.*?)</a><br\s*/?>',
        source,
        flags=re.DOTALL,
    )
    parsed: list[tuple[str, str]] = []
    for line_ref, body_html in rows:
        line_ref = line_ref.rstrip(": ")
        body = clean_body(body_html)
        if not body or body.startswith("No."):
            continue
        validate_text(line_ref, body)
        parsed.append((line_ref, body))
    if not parsed:
        raise ValueError("no SAT lines parsed")
    return parsed


def line_for_char(lines: list[AnchorLine], char_pos: int) -> str:
    if lines and char_pos >= lines[-1].char_end:
        return lines[-1].line_ref
    lo = 0
    hi = len(lines) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        line = lines[mid]
        if line.char_start <= char_pos < line.char_end:
            return line.line_ref
        if char_pos < line.char_start:
            hi = mid - 1
        else:
            lo = mid + 1
    return lines[max(0, min(lo, len(lines) - 1))].line_ref


def load_anchor_text(anchor: dict[str, str]) -> AnchorText:
    raw_path = RAW_DIR / f"{anchor['id']}.html"
    source = fetch_url(anchor["source_url"], raw_path)
    parsed = parse_sat_lines(source)
    lines: list[AnchorLine] = []
    char_cursor = 0
    body_parts: list[str] = []
    for line_ref, text in parsed:
        line = AnchorLine(
            line_ref=line_ref,
            text=text,
            char_start=char_cursor,
            char_end=char_cursor + len(text),
        )
        lines.append(line)
        body_parts.append(text)
        char_cursor = line.char_end
    body = "".join(body_parts)
    validate_text(anchor["id"], body)
    return AnchorText(
        id=anchor["id"],
        author=anchor["author"],
        work=anchor["work"],
        source_url=anchor["source_url"],
        source_note=anchor["source_note"],
        raw_path=raw_path,
        lines=lines,
        body=body,
    )


def make_anchor_chunks(anchor: AnchorText, encoder: tiktoken.Encoding) -> list[AnchorChunk]:
    step = MAX_TOKENS - OVERLAP
    tokens = encoder.encode(anchor.body)
    decoded, offsets = encoder.decode_with_offsets(tokens)
    if decoded != anchor.body:
        raise ValueError(f"{anchor.id}: decode_with_offsets did not round-trip")

    chunks: list[AnchorChunk] = []
    for chunk_index, token_start in enumerate(range(0, len(tokens), step)):
        token_end = min(token_start + MAX_TOKENS, len(tokens))
        char_start = offsets[token_start] if token_start < len(tokens) else len(anchor.body)
        char_end = offsets[token_end] if token_end < len(tokens) else len(anchor.body)
        while char_end <= char_start and token_end < len(tokens):
            token_end += 1
            char_end = offsets[token_end] if token_end < len(tokens) else len(anchor.body)
        text = anchor.body[char_start:char_end].strip()
        actual_token_count = len(encoder.encode(text))
        while actual_token_count > MAX_TOKENS and token_end > token_start:
            token_end -= 1
            char_end = offsets[token_end] if token_end < len(tokens) else len(anchor.body)
            text = anchor.body[char_start:char_end].strip()
            actual_token_count = len(encoder.encode(text))
        if actual_token_count < MAX_TOKENS // 4 and chunks:
            break
        validate_text(f"{anchor.id} chunk_{chunk_index:04d}", text)
        line_start = line_for_char(anchor.lines, char_start)
        line_end = line_for_char(anchor.lines, max(char_start, char_end - 1))
        chunks.append(
            AnchorChunk(
                chunk_id=f"anchor_safe_unicode_700:{anchor.author}:{anchor.work}:chunk_{chunk_index:04d}",
                author=anchor.author,
                work=anchor.work,
                anchor_id=anchor.id,
                chunk_index=chunk_index,
                text=text,
                char_start=char_start,
                char_end=char_end,
                token_start=token_start,
                token_end=token_end,
                source_token_count=token_end - token_start,
                actual_token_count=actual_token_count,
                line_start=line_start,
                line_end=line_end,
                source_url=anchor.source_url,
                source_note=anchor.source_note,
            )
        )
    return chunks


def load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {"model": MODEL, "max_tokens": MAX_TOKENS, "overlap": OVERLAP, "embeddings": {}}
    data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    if data.get("model") != MODEL or data.get("max_tokens") != MAX_TOKENS or data.get("overlap") != OVERLAP:
        return {"model": MODEL, "max_tokens": MAX_TOKENS, "overlap": OVERLAP, "embeddings": {}}
    data.setdefault("embeddings", {})
    return data


def save_cache(cache: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    tmp.replace(CACHE_PATH)


def get_anchor_embeddings(chunks: list[AnchorChunk]) -> np.ndarray:
    cache = load_cache()
    embeddings: dict[str, Any] = cache["embeddings"]
    missing: list[AnchorChunk] = []
    for chunk in chunks:
        text_hash = sha256_text(chunk.text)
        record = embeddings.get(chunk.chunk_id)
        if not record or record.get("text_sha256") != text_hash:
            missing.append(chunk)

    if missing:
        print(f"anchor embedding missing chunks: {len(missing)}")
    for start in range(0, len(missing), BATCH_SIZE):
        batch = missing[start : start + BATCH_SIZE]
        vectors = request_embeddings([chunk.text for chunk in batch])
        for chunk, vector in zip(batch, vectors):
            embeddings[chunk.chunk_id] = {
                "text_sha256": sha256_text(chunk.text),
                "author": chunk.author,
                "work": chunk.work,
                "anchor_id": chunk.anchor_id,
                "chunk_index": chunk.chunk_index,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "source_token_count": chunk.source_token_count,
                "actual_token_count": chunk.actual_token_count,
                "embedding": vector,
            }
        save_cache(cache)
        done = min(start + len(batch), len(missing))
        print(f"embedded anchors {done}/{len(missing)} missing chunks")
        if done < len(missing):
            time.sleep(0.3)
    return np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float)


def fit_pca(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[float]]:
    mean = matrix.mean(axis=0, keepdims=True)
    centered = matrix - mean
    _u, s, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[:2].T
    variances = s**2
    total = float(np.sum(variances)) or 1.0
    ratio = [float(variances[0] / total), float(variances[1] / total)]
    return mean, components, ratio


def project(matrix: np.ndarray, mean: np.ndarray, components: np.ndarray) -> np.ndarray:
    return (matrix - mean) @ components


def focus_records(chunks: list[Any], coords: np.ndarray) -> list[dict[str, Any]]:
    records = []
    for chunk, coord in zip(chunks, coords):
        records.append(
            {
                "chunk_id": chunk.chunk_id,
                "author": chunk.author,
                "work": chunk.work,
                "role": "focus",
                "chunk_index": chunk.chunk_index,
                "sat_id": chunk.sat_id,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "source_url": chunk.source_url,
                "text_sha256": sha256_text(chunk.text),
                "replacement_chars": chunk.text.count("\ufffd"),
                "actual_token_count": chunk.actual_token_count,
                "x": float(coord[0]),
                "y": float(coord[1]),
            }
        )
    return records


def anchor_records(chunks: list[AnchorChunk], coords: np.ndarray) -> list[dict[str, Any]]:
    return [
        {
            "chunk_id": chunk.chunk_id,
            "author": chunk.author,
            "work": chunk.work,
            "role": "anchor",
            "anchor_id": chunk.anchor_id,
            "chunk_index": chunk.chunk_index,
            "line_start": chunk.line_start,
            "line_end": chunk.line_end,
            "source_url": chunk.source_url,
            "text_sha256": sha256_text(chunk.text),
            "replacement_chars": chunk.text.count("\ufffd"),
            "actual_token_count": chunk.actual_token_count,
            "x": float(coord[0]),
            "y": float(coord[1]),
        }
        for chunk, coord in zip(chunks, coords)
    ]


def author_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["author"]].append(record)
    centers: dict[str, np.ndarray] = {}
    stats: dict[str, Any] = {}
    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        centers[author] = center
        distances = np.linalg.norm(pts - center, axis=1)
        stats[author] = {
            "chunk_count": len(rows),
            "centroid": [rounded(float(center[0])), rounded(float(center[1]))],
            "rms_radius": rounded(float(np.sqrt(np.mean(distances**2)))),
            "p90_radius": rounded(float(np.quantile(distances, 0.9))),
        }
    if "法然" in centers and "親鸞" in centers:
        for author, center in centers.items():
            stats[author]["distance_to_honen_centroid"] = rounded(float(np.linalg.norm(center - centers["法然"])))
            stats[author]["distance_to_shinran_centroid"] = rounded(float(np.linalg.norm(center - centers["親鸞"])))
    return stats


def source_records(anchor_texts: list[AnchorText], anchor_chunks: list[AnchorChunk]) -> list[dict[str, Any]]:
    counts = Counter(chunk.anchor_id for chunk in anchor_chunks)
    return [
        {
            "id": anchor.id,
            "author": anchor.author,
            "work": anchor.work,
            "source_url": anchor.source_url,
            "source_note": anchor.source_note,
            "raw_path": str(anchor.raw_path.relative_to(ROOT)),
            "line_count": len(anchor.lines),
            "char_count": len(anchor.body),
            "body_sha256": sha256_text(anchor.body),
            "chunk_count": counts[anchor.id],
        }
        for anchor in anchor_texts
    ]


def build_summary(
    records: list[dict[str, Any]],
    anchors: list[AnchorText],
    anchor_chunks: list[AnchorChunk],
    pca_ratio: list[float],
    render_stats: dict[str, Any],
) -> dict[str, Any]:
    return {
        "title": "SAT kanbun Unicode-safe Honen/Shinran semantic map with Pure Land patriarch anchors",
        "method": {
            "text_basis": "SAT kanbun-basis prepared text",
            "focus_texts": ["SAT T2608 選擇本願念佛集", "SAT T2646 顯淨土眞實教行證文類"],
            "embedding_model": MODEL,
            "tokenizer": "tiktoken cl100k_base",
            "max_tokens": MAX_TOKENS,
            "overlap": OVERLAP,
            "chunking": "Unicode-safe near-700-token chunks via decode_with_offsets; SAT line refs retained as provenance metadata",
            "pca_fit_scope": "focus chunks only: 法然 and 親鸞",
            "anchor_projection": "anchor chunks projected into the fixed focus PCA plane",
            "display_extent": "fitted to Honen/Shinran chunks; identical renderer to the focus-only paper figure",
            "paper_figure": str(DOC_FIGURE_PATH.relative_to(ROOT)),
            "paper_figure_renderer": "scripts/sat_safe_map_renderer.py",
            "pca_explained_variance_ratio_on_fit_scope": [rounded(value) for value in pca_ratio],
            "raw_text_policy": "public metadata excludes raw/chunk text; raw and processed text remain local-only under data/",
        },
        "figure_rendering": render_stats.get("_figure", {}),
        "anchor_sources": source_records(anchors, anchor_chunks),
        "author_stats": {
            author: {
                **stats,
                **({"rendered_ellipse": render_stats[author]} if author in render_stats else {}),
            }
            for author, stats in author_stats(records).items()
        },
        "chunks": [
            {
                key: (rounded(value) if key in {"x", "y"} and isinstance(value, float) else value)
                for key, value in record.items()
                if key not in {"text", "embedding"}
            }
            for record in records
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if MAX_TOKENS <= OVERLAP:
        raise ValueError("MAX_TOKENS must be larger than OVERLAP")
    encoder = tiktoken.get_encoding("cl100k_base")
    focus_chunks = []
    for work in load_works(encoder):
        focus_chunks.extend(make_safe_chunks(work, encoder))
    anchor_texts = [load_anchor_text(anchor) for anchor in ANCHORS]
    anchor_chunks = []
    for anchor in anchor_texts:
        anchor_chunks.extend(make_anchor_chunks(anchor, encoder))

    if args.validate_only:
        print("focus chunks:", dict(Counter(chunk.author for chunk in focus_chunks)))
        print("anchor chunks:", dict(Counter(chunk.author for chunk in anchor_chunks)))
        print("anchor sources:", [(anchor.author, len(anchor.lines), len(anchor.body)) for anchor in anchor_texts])
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    focus_vectors = get_focus_embeddings(focus_chunks)
    mean, components, pca_ratio = fit_pca(focus_vectors)
    focus_coords = project(focus_vectors, mean, components)
    anchor_vectors = get_anchor_embeddings(anchor_chunks)
    anchor_coords = project(anchor_vectors, mean, components)
    records = focus_records(focus_chunks, focus_coords) + anchor_records(anchor_chunks, anchor_coords)
    paper_records = [
        {**record, "x": rounded(record["x"]), "y": rounded(record["y"])}
        for record in records
    ]
    render_stats = render_sat_safe_map_png(
        paper_records,
        DOC_FIGURE_PATH,
        title="SAT漢文 Unicode-safeチャンク地図: 法然・親鸞・祖師文献",
        subtitle=f"PCA fit=法然/親鸞。祖師文献は同じ面へ投影。model={MODEL}, {MAX_TOKENS}/{OVERLAP} token, PC1+PC2={sum(pca_ratio)*100:.1f}%。",
        legend_order=list(FOCUS_AUTHORS) + list(ANCHOR_AUTHORS),
        show_anchor_note=True,
    )
    PNG_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DOC_FIGURE_PATH, PNG_PATH)

    # Paper figures use the shared PNG renderer. The older SVG renderer is not
    # emitted here because its rotation semantics can diverge visually.
    META_PATH.write_text(
        json.dumps(build_summary(paper_records, anchor_texts, anchor_chunks, pca_ratio, render_stats), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {DOC_FIGURE_PATH.relative_to(ROOT)}")
    print(f"wrote {PNG_PATH.relative_to(ROOT)}")
    print(f"wrote {META_PATH.relative_to(ROOT)}")
    print("chunks:", dict(Counter(record["author"] for record in records)))


if __name__ == "__main__":
    main()
