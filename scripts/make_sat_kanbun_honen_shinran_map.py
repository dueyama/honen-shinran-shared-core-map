#!/usr/bin/env python3
"""Build a Honen/Shinran map from SAT Taisho kanbun-basis texts.

This is a separate baseline from the seiten Japanese-reading map. It uses:

- T2608 選擇本願念佛集
- T2646 顯淨土眞實教行證文類

Raw text and private chunk indexes are written only under ignored data/.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import argparse
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import tiktoken


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from make_predecessor_style_embedding_map import (  # noqa: E402
    API_URL,
    MAX_TOKENS,
    MODEL,
    OVERLAP,
    request_embeddings,
)
from make_simple_2d_map import covariance_ellipse, svg_escape  # noqa: E402


RAW_DIR = ROOT / "data" / "raw" / "sat_kanbun"
CACHE_DIR = ROOT / "data" / "cache"
OUT_DIR = ROOT / "data" / "outputs"
CACHE_PATH = CACHE_DIR / f"honen_shinran_sat_kanbun_embeddings_{MODEL}_{MAX_TOKENS}_{OVERLAP}.json"
META_PATH = OUT_DIR / "honen_shinran_sat_kanbun_embedding_map_meta.json"
SVG_PATH = OUT_DIR / "honen_shinran_sat_kanbun_embedding_map.svg"
PRIVATE_INDEX_PATH = OUT_DIR / f"PRIVATE_sat_kanbun_chunk_text_index_{MODEL}_{MAX_TOKENS}_{OVERLAP}.jsonl"
BATCH_SIZE = int(os.getenv("OKYOU2_EMBEDDING_BATCH_SIZE", "64"))
BAD_TEXT_PATTERNS = [
    ("replacement character", re.compile("\ufffd")),
    ("html tag", re.compile(r"</?\w+")),
    ("html entity", re.compile(r"&(?:[A-Za-z]+|#[0-9]+|#x[0-9A-Fa-f]+);")),
    ("image placeholder", re.compile(r"Image:")),
    ("button label", re.compile(r"\[?Button:?")),
    ("SAT line ref in body", re.compile(r"T\d{4}[A-Z]?_\.\d{2}\.\d{4}[abcx]\d{2}:?")),
]

WORKS = [
    {
        "id": "honen_t2608_senchakushu",
        "author": "法然",
        "work": "選択本願念仏集",
        "sat_id": "T2608",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T2608.html",
        "source_note": "SAT T2608 選擇本願念佛集.",
    },
    {
        "id": "shinran_t2646_kyogyoshinsho",
        "author": "親鸞",
        "work": "教行信証",
        "sat_id": "T2646",
        "source_url": "https://21dzk.l.u-tokyo.ac.jp/SAT/T2646_,83,0589a01:2646_,83,0643c29.html",
        "source_note": "SAT T2646 顯淨土眞實教行證文類 full range 83:0589a01-0643c29.",
    },
]


@dataclass
class SatRow:
    line_ref: str
    text: str
    token_start: int = 0
    token_end: int = 0
    token_count: int = 0


@dataclass
class SatChunk:
    chunk_id: str
    author: str
    work: str
    sat_id: str
    source_url: str
    source_note: str
    chunk_index: int
    token_start: int
    token_end: int
    line_start: str
    line_end: str
    text: str


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_clean_text(label: str, text: str) -> None:
    for name, pattern in BAD_TEXT_PATTERNS:
        match = pattern.search(text)
        if match:
            start = max(match.start() - 24, 0)
            end = min(match.end() + 24, len(text))
            sample = text[start:end]
            raise ValueError(f"{label}: invalid text pattern {name}: {sample!r}")
    if not text.strip():
        raise ValueError(f"{label}: empty text")


def fetch_url(url: str, path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers={"User-Agent": "Okyou2 research script"})
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read().decode("utf-8", errors="replace")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw, encoding="utf-8")
    return raw


def parse_sat_rows(source: str) -> list[SatRow]:
    html_rows = re.findall(
        r'<span style="color:black">(T[^<]+)</span><a name="[^"]*">(.*?)</a><br\s*/?>',
        source,
        flags=re.DOTALL,
    )
    rows: list[SatRow] = []
    for line_ref, body_html in html_rows:
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
        if not body or body.startswith("No."):
            continue
        validate_clean_text(line_ref, body)
        rows.append(SatRow(line_ref=line_ref.rstrip(": "), text=body))
    return rows


def load_rows() -> tuple[dict[str, list[SatRow]], list[dict[str, Any]]]:
    work_rows: dict[str, list[SatRow]] = {}
    source_records = []
    for work in WORKS:
        raw_path = RAW_DIR / f"{work['id']}.html"
        source = fetch_url(work["source_url"], raw_path)
        rows = parse_sat_rows(source)
        if not rows:
            raise ValueError(f"{work['sat_id']}: no SAT text rows parsed from {work['source_url']}")
        body = "".join(row.text for row in rows)
        validate_clean_text(work["sat_id"], body)
        work_rows[work["id"]] = rows
        source_records.append(
            {
                **work,
                "raw_path": str(raw_path.relative_to(ROOT)),
                "row_count": len(rows),
                "char_count": len(body),
                "body_sha256": sha256_text(body),
            }
        )
    return work_rows, source_records


def make_chunks() -> tuple[list[SatChunk], list[dict[str, Any]]]:
    if MAX_TOKENS <= OVERLAP:
        raise ValueError("MAX_TOKENS must be larger than OVERLAP.")
    encoder = tiktoken.get_encoding("cl100k_base")
    work_rows, source_records = load_rows()
    chunks: list[SatChunk] = []

    for work in WORKS:
        rows = work_rows[work["id"]]
        for row in rows:
            tokens = encoder.encode(row.text)
            row.token_count = len(tokens)

        cursor = 0
        for row in rows:
            row.token_start = cursor
            cursor += row.token_count
            row.token_end = cursor

        chunk_index = 0
        start_row = 0
        while start_row < len(rows):
            end_row = start_row
            token_count = 0
            while end_row < len(rows):
                row_tokens = rows[end_row].token_count
                if token_count and token_count + row_tokens > MAX_TOKENS:
                    break
                token_count += row_tokens
                end_row += 1
                if token_count >= MAX_TOKENS:
                    break
            if token_count < MAX_TOKENS // 4 and chunk_index:
                break
            chunk_rows = rows[start_row:end_row]
            text = "".join(row.text for row in chunk_rows).strip()
            if not text:
                start_row = end_row
                continue
            validate_clean_text(
                f"{work['sat_id']} chunk_{chunk_index:04d} {chunk_rows[0].line_ref}-{chunk_rows[-1].line_ref}",
                text,
            )
            chunks.append(
                SatChunk(
                    chunk_id=f"{work['author']}:{work['sat_id']}:{work['work']}:chunk_{chunk_index:04d}",
                    author=work["author"],
                    work=work["work"],
                    sat_id=work["sat_id"],
                    source_url=work["source_url"],
                    source_note=work["source_note"],
                    chunk_index=chunk_index,
                    token_start=chunk_rows[0].token_start,
                    token_end=chunk_rows[-1].token_end,
                    line_start=chunk_rows[0].line_ref,
                    line_end=chunk_rows[-1].line_ref,
                    text=text,
                )
            )
            chunk_index += 1
            overlap_tokens = 0
            next_start = end_row
            while next_start > start_row and overlap_tokens < OVERLAP:
                next_start -= 1
                overlap_tokens += rows[next_start].token_count
            if next_start <= start_row:
                next_start = end_row
            start_row = next_start
    source_by_id = {record["id"]: record for record in source_records}
    for work in WORKS:
        source_by_id[work["id"]]["chunk_count"] = sum(1 for chunk in chunks if chunk.sat_id == work["sat_id"])
    if not chunks:
        raise ValueError("no chunks created")
    return chunks, list(source_by_id.values())


def load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {"model": MODEL, "max_tokens": MAX_TOKENS, "overlap": OVERLAP, "embeddings": {}}
    data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    if (
        data.get("model") != MODEL
        or data.get("max_tokens") != MAX_TOKENS
        or data.get("overlap") != OVERLAP
    ):
        return {"model": MODEL, "max_tokens": MAX_TOKENS, "overlap": OVERLAP, "embeddings": {}}
    data.setdefault("embeddings", {})
    return data


def save_cache(cache: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    tmp.replace(CACHE_PATH)


def get_embeddings(chunks: list[SatChunk]) -> np.ndarray:
    cache = load_cache()
    embeddings = cache["embeddings"]
    missing = []
    for chunk in chunks:
        text_hash = sha256_text(chunk.text)
        record = embeddings.get(chunk.chunk_id)
        if not record or record.get("text_sha256") != text_hash:
            missing.append(chunk)
    if missing:
        print(f"embedding missing chunks: {len(missing)}")
    for start in range(0, len(missing), BATCH_SIZE):
        batch = missing[start : start + BATCH_SIZE]
        vectors = request_embeddings([chunk.text for chunk in batch])
        for chunk, vector in zip(batch, vectors):
            embeddings[chunk.chunk_id] = {
                "text_sha256": sha256_text(chunk.text),
                "author": chunk.author,
                "work": chunk.work,
                "sat_id": chunk.sat_id,
                "chunk_index": chunk.chunk_index,
                "token_start": chunk.token_start,
                "token_end": chunk.token_end,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "source_url": chunk.source_url,
                "embedding": vector,
            }
        save_cache(cache)
        done = min(start + len(batch), len(missing))
        print(f"embedded {done}/{len(missing)} missing chunks")
        if done < len(missing):
            time.sleep(0.3)
    return np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float)


def pca_2d(matrix: np.ndarray) -> tuple[np.ndarray, list[float]]:
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :2] * s[:2]
    variances = s**2
    total = float(np.sum(variances)) or 1.0
    return coords, [float(variances[0] / total), float(variances[1] / total)]


COLORS = {"法然": "#1f78b4", "親鸞": "#d63f3f"}


def render_svg(chunks: list[SatChunk], coords: np.ndarray, ratio: list[float]) -> str:
    width, height = 1500, 980
    pad_l, pad_r, pad_t, pad_b = 90, 260, 110, 86
    bg = "#fbfaf7"
    text = "#25221d"
    xs = coords[:, 0]
    ys = coords[:, 1]
    x_min, x_max = float(xs.min()), float(xs.max())
    y_min, y_max = float(ys.min()), float(ys.max())
    x_pad = max((x_max - x_min) * 0.08, 0.03)
    y_pad = max((y_max - y_min) * 0.08, 0.03)
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    def sx(x: float) -> float:
        return pad_l + (x - x_min) / (x_max - x_min) * plot_w

    def sy(y: float) -> float:
        return pad_t + (y_max - y) / (y_max - y_min) * plot_h

    records = [
        {"chunk": chunk, "x": float(coord[0]), "y": float(coord[1])}
        for chunk, coord in zip(chunks, coords)
    ]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["chunk"].author].append(record)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        f'<text x="{pad_l}" y="48" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="30" font-weight="700" fill="{text}">SAT漢文系本文: 法然・親鸞 semantic map</text>',
        f'<text x="{pad_l}" y="80" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="15" fill="#686158">T2608 選擇本願念佛集 / T2646 顯淨土眞實教行證文類。model={MODEL}、700-token chunks、PC1+PC2={sum(ratio)*100:.1f}%。</text>',
        f'<rect x="{pad_l}" y="{pad_t}" width="{plot_w}" height="{plot_h}" rx="8" fill="#ffffff" stroke="#ddd6ca"/>',
    ]
    if x_min < 0 < x_max:
        lines.append(f'<line x1="{sx(0):.1f}" y1="{pad_t+20}" x2="{sx(0):.1f}" y2="{pad_t+plot_h-20}" stroke="#d8d2c5"/>')
    if y_min < 0 < y_max:
        lines.append(f'<line x1="{pad_l+20}" y1="{sy(0):.1f}" x2="{pad_l+plot_w-20}" y2="{sy(0):.1f}" stroke="#d8d2c5"/>')

    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        ew, eh, angle = covariance_ellipse(pts, center, radius=1.45)
        color = COLORS[author]
        rx = max(ew / (x_max - x_min) * plot_w, 12.0)
        ry = max(eh / (y_max - y_min) * plot_h, 12.0)
        lines.append(
            f'<ellipse cx="{sx(center[0]):.1f}" cy="{sy(center[1]):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'transform="rotate({-angle:.1f} {sx(center[0]):.1f} {sy(center[1]):.1f})" fill="{color}" fill-opacity="0.10" '
            f'stroke="{color}" stroke-opacity="0.45" stroke-width="2"/>'
        )

    for record in records:
        chunk = record["chunk"]
        color = COLORS[chunk.author]
        lines.append(
            f'<circle cx="{sx(record["x"]):.1f}" cy="{sy(record["y"]):.1f}" r="5.3" fill="{color}" fill-opacity="0.64">'
            f'<title>{svg_escape(chunk.chunk_id + " " + chunk.line_start + "-" + chunk.line_end)}</title></circle>'
        )

    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        color = COLORS[author]
        lines.append(f'<circle cx="{sx(center[0]):.1f}" cy="{sy(center[1]):.1f}" r="12" fill="{color}" stroke="#ffffff" stroke-width="3"/>')
        dx = 14 if author == "親鸞" else -70
        lines.append(
            f'<text x="{sx(center[0])+dx:.1f}" y="{sy(center[1])-14:.1f}" font-family="Hiragino Sans, Yu Gothic, sans-serif" '
            f'font-size="16" font-weight="700" fill="{color}">{svg_escape(author)} 重心</text>'
        )

    lx = width - pad_r + 36
    ly = pad_t + 20
    lines.append(f'<g font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="15" fill="{text}">')
    lines.append(f'<text x="{lx}" y="{ly}" font-size="18" font-weight="700">凡例</text>')
    y = ly + 34
    for author in ["法然", "親鸞"]:
        color = COLORS[author]
        count = len(groups[author])
        lines.append(f'<circle cx="{lx+8}" cy="{y-5}" r="7" fill="{color}" fill-opacity="0.72"/>')
        lines.append(f'<text x="{lx+26}" y="{y}">{svg_escape(author)} n={count}</text>')
        y += 28
    lines.append(f'<text x="{lx}" y="{y+22}" font-size="13" fill="#686158">点=700-token chunk</text>')
    lines.append(f'<text x="{lx}" y="{y+44}" font-size="13" fill="#686158">本文は図・公開メタに含めない</text>')
    lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines)


def write_private_index(chunks: list[SatChunk]) -> None:
    with PRIVATE_INDEX_PATH.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(
                json.dumps(
                    {
                        "chunk_id": chunk.chunk_id,
                        "author": chunk.author,
                        "work": chunk.work,
                        "sat_id": chunk.sat_id,
                        "source_url": chunk.source_url,
                        "line_start": chunk.line_start,
                        "line_end": chunk.line_end,
                        "token_start": chunk.token_start,
                        "token_end": chunk.token_end,
                        "text_sha256": sha256_text(chunk.text),
                        "text_char_count": len(chunk.text),
                        "text": chunk.text,
                        "private_policy": "local-only raw chunk text; do not commit or publish",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def summarize(chunks: list[SatChunk], coords: np.ndarray, vectors: np.ndarray, ratio: list[float], sources: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[int]] = defaultdict(list)
    for i, chunk in enumerate(chunks):
        groups[chunk.author].append(i)
    stats = {}
    centroids = {}
    for author, indices in groups.items():
        pts = coords[indices]
        center = pts.mean(axis=0)
        centroids[author] = center
        distances = np.linalg.norm(pts - center, axis=1)
        stats[author] = {
            "chunk_count": len(indices),
            "work": chunks[indices[0]].work,
            "centroid": [round(float(center[0]), 6), round(float(center[1]), 6)],
            "rms_radius": round(float(np.sqrt(np.mean(distances**2))), 6),
            "p90_radius": round(float(np.quantile(distances, 0.9)), 6),
        }
    centroid_distance = None
    if {"法然", "親鸞"}.issubset(centroids):
        centroid_distance = round(float(np.linalg.norm(centroids["法然"] - centroids["親鸞"])), 6)
    return {
        "title": "SAT kanbun-basis Honen/Shinran semantic map",
        "method": {
            "text_basis": "SAT Taisho kanbun-basis text, not seiten Japanese reading text",
            "embedding_model": MODEL,
            "embedding_api_url": API_URL,
            "embedding_dimension": int(vectors.shape[1]),
            "tokenizer": "tiktoken cl100k_base",
            "max_tokens": MAX_TOKENS,
            "overlap": OVERLAP,
            "projection": "PCA via centered NumPy SVD",
            "pca_explained_variance_ratio": [round(float(value), 6) for value in ratio],
            "raw_text_policy": "public metadata excludes raw text; private chunk index under data/outputs/PRIVATE_* contains raw text and must not be published",
        },
        "sources": sources,
        "author_stats": stats,
        "centroid_distance": centroid_distance,
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "author": chunk.author,
                "work": chunk.work,
                "sat_id": chunk.sat_id,
                "chunk_index": chunk.chunk_index,
                "source_url": chunk.source_url,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "token_start": chunk.token_start,
                "token_end": chunk.token_end,
                "text_sha256": sha256_text(chunk.text),
                "x": round(float(coords[i, 0]), 6),
                "y": round(float(coords[i, 1]), 6),
            }
            for i, chunk in enumerate(chunks)
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Fetch/parse/chunk/validate text, write no embeddings or outputs.",
    )
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chunks, sources = make_chunks()
    if args.validate_only:
        print("validated SAT kanbun-basis chunks")
        print("chunks:", dict(Counter(chunk.author for chunk in chunks)))
        print("sources:", [(item["sat_id"], item["char_count"], item["row_count"], item["chunk_count"]) for item in sources])
        return
    vectors = get_embeddings(chunks)
    coords, ratio = pca_2d(vectors)
    SVG_PATH.write_text(render_svg(chunks, coords, ratio), encoding="utf-8")
    META_PATH.write_text(
        json.dumps(summarize(chunks, coords, vectors, ratio, sources), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_private_index(chunks)
    print(f"wrote {SVG_PATH}")
    print(f"wrote {META_PATH}")
    print(f"wrote {PRIVATE_INDEX_PATH}")
    print("chunks:", dict(Counter(chunk.author for chunk in chunks)))


if __name__ == "__main__":
    main()
