#!/usr/bin/env python3
"""Overlay Pure Land patriarch/source anchors on the Honen/Shinran semantic map.

The PCA plane is fit only on Honen/Shinran chunks, then anchor texts are
projected into that fixed plane. This preserves the "rightward Shinran spread"
seen in the first predecessor-style map.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import numpy as np
import tiktoken


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from make_predecessor_style_embedding_map import (  # noqa: E402
    MAX_TOKENS,
    MODEL,
    OVERLAP,
    get_embeddings as get_base_embeddings,
    make_token_chunks as make_base_token_chunks,
    request_embeddings,
)
from make_simple_2d_map import covariance_ellipse, svg_escape  # noqa: E402


RAW_DIR = ROOT / "data" / "raw" / "sat_anchors"
CACHE_DIR = ROOT / "data" / "cache"
OUT_DIR = ROOT / "data" / "outputs"
SVG_PATH = OUT_DIR / "honen_shinran_high_priest_anchor_map.svg"
PNG_PATH = OUT_DIR / "honen_shinran_high_priest_anchor_map.png"
META_PATH = OUT_DIR / "honen_shinran_high_priest_anchor_map_meta.json"
CACHE_PATH = CACHE_DIR / f"high_priest_anchor_embeddings_{MODEL}_{MAX_TOKENS}_{OVERLAP}.json"
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


@dataclass
class TextChunk:
    chunk_id: str
    author: str
    work: str
    role: str
    anchor_id: str
    chunk_index: int
    token_start: int
    token_end: int
    text: str
    source_url: str
    source_note: str


class SatTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "form", "button"}:
            self._skip_depth += 1
        if tag == "br" and not self._skip_depth:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "form", "button"} and self._skip_depth:
            self._skip_depth -= 1
        if tag in {"div", "p", "tr", "li", "td", "span", "a"} and not self._skip_depth:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.parts.append(data)

    @property
    def text(self) -> str:
        return "".join(self.parts)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def fetch_url(url: str, path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers={"User-Agent": "Okyou2 research script"})
    with urllib.request.urlopen(req, timeout=90) as response:
        raw = response.read().decode("utf-8", errors="replace")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw, encoding="utf-8")
    return raw


def clean_sat_text(source: str) -> str:
    html_rows = re.findall(
        r'<span style="color:black">(T[^<]+)</span><a name="[^"]*">(.*?)</a><br\s*/?>',
        source,
        flags=re.DOTALL,
    )
    rows: list[str] = []
    if html_rows:
        for _, body_html in html_rows:
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
            if body and not body.startswith("No."):
                rows.append(body)
        return "".join(rows)

    parser = SatTextParser()
    parser.feed(source)
    text = html.unescape(parser.text).replace("\xa0", " ")
    line_pattern = re.compile(r"(?:T\d{4}[A-Z]?_?\.\d{2}\.\d{4}[abcx]\d{2}:?)\s*(.*)")
    for raw_line in text.splitlines():
        raw_line = re.sub(r"\s+", " ", raw_line).strip()
        if not raw_line:
            continue
        match = line_pattern.search(raw_line)
        if not match:
            continue
        body = match.group(1)
        body = re.sub(r"\[Button:[^\]]+\]", "", body)
        body = re.sub(r"Image:\s*&[^;]+;", "", body)
        body = re.sub(r"\s+", "", body)
        if body and not body.startswith("Footnote"):
            rows.append(body)
    return "".join(rows)


def chunk_text(anchor: dict[str, str], text: str) -> list[TextChunk]:
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    step = MAX_TOKENS - OVERLAP
    chunks: list[TextChunk] = []
    for index, start in enumerate(range(0, len(tokens), step)):
        end = min(start + MAX_TOKENS, len(tokens))
        if end - start < MAX_TOKENS // 4 and chunks:
            break
        chunk_text_value = encoder.decode(tokens[start:end]).strip()
        if not chunk_text_value:
            continue
        chunks.append(
            TextChunk(
                chunk_id=f"{anchor['author']}:{anchor['work']}:chunk_{index:04d}",
                author=anchor["author"],
                work=anchor["work"],
                role="anchor",
                anchor_id=anchor["id"],
                chunk_index=index,
                token_start=start,
                token_end=end,
                text=chunk_text_value,
                source_url=anchor["source_url"],
                source_note=anchor["source_note"],
            )
        )
    return chunks


def load_anchor_chunks() -> tuple[list[TextChunk], list[dict[str, Any]]]:
    all_chunks: list[TextChunk] = []
    source_records: list[dict[str, Any]] = []
    for anchor in ANCHORS:
        raw_path = RAW_DIR / f"{anchor['id']}.html"
        source = fetch_url(anchor["source_url"], raw_path)
        body = clean_sat_text(source)
        body_hash = sha256_text(body)
        chunks = chunk_text(anchor, body)
        all_chunks.extend(chunks)
        source_records.append(
            {
                **anchor,
                "raw_path": str(raw_path.relative_to(ROOT)),
                "body_sha256": body_hash,
                "char_count": len(body),
                "chunk_count": len(chunks),
            }
        )
    return all_chunks, source_records


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


def get_anchor_embeddings(chunks: list[TextChunk]) -> np.ndarray:
    cache = load_cache()
    embeddings: dict[str, Any] = cache["embeddings"]
    missing = []
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
                "token_start": chunk.token_start,
                "token_end": chunk.token_end,
                "source_url": chunk.source_url,
                "embedding": vector,
            }
        save_cache(cache)
        done = min(start + len(batch), len(missing))
        print(f"embedded anchors {done}/{len(missing)} missing chunks")
        if done < len(missing):
            time.sleep(0.3)
    return np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float)


def fit_base_pca(base_vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[float]]:
    mean = base_vectors.mean(axis=0, keepdims=True)
    centered = base_vectors - mean
    _, s, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[:2].T
    variances = s**2
    total = float(np.sum(variances)) or 1.0
    ratio = [float(variances[0] / total), float(variances[1] / total)]
    return mean, components, ratio


def project(vectors: np.ndarray, mean: np.ndarray, components: np.ndarray) -> np.ndarray:
    return (vectors - mean) @ components


def base_render_records(base_chunks: list[Any], coords: np.ndarray) -> list[dict[str, Any]]:
    records = []
    for item, coord in zip(base_chunks, coords):
        records.append(
            {
                "chunk_id": item.chunk.chunk_id,
                "author": item.chunk.author,
                "work": item.chunk.work,
                "role": "focus",
                "x": float(coord[0]),
                "y": float(coord[1]),
                "source": "seiten",
            }
        )
    return records


def anchor_render_records(anchor_chunks: list[TextChunk], coords: np.ndarray) -> list[dict[str, Any]]:
    return [
        {
            "chunk_id": chunk.chunk_id,
            "author": chunk.author,
            "work": chunk.work,
            "role": "anchor",
            "anchor_id": chunk.anchor_id,
            "chunk_index": chunk.chunk_index,
            "x": float(coord[0]),
            "y": float(coord[1]),
            "source_url": chunk.source_url,
            "text_sha256": sha256_text(chunk.text),
        }
        for chunk, coord in zip(anchor_chunks, coords)
    ]


COLORS = {
    "法然": "#1f78b4",
    "親鸞": "#d63f3f",
    "龍樹": "#8b5cf6",
    "天親": "#0f9f9a",
    "曇鸞": "#2f8f4e",
    "道綽": "#b7791f",
    "善導": "#6d5bd0",
    "源信": "#e26d2f",
}


def render_svg(records: list[dict[str, Any]], pca_ratio: list[float]) -> str:
    width, height = 1800, 1160
    pad_l, pad_r, pad_t, pad_b = 90, 360, 120, 96
    bg = "#fbfaf7"
    text = "#25221d"
    axis = "#d8d2c5"
    xs = [r["x"] for r in records]
    ys = [r["y"] for r in records]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
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

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["author"]].append(record)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        f'<text x="{pad_l}" y="50" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="30" font-weight="700" fill="{text}">法然・親鸞 map に高僧文献アンカーを投影</text>',
        f'<text x="{pad_l}" y="82" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="15" fill="#686158">PCA は法然・親鸞 700-token chunks のみで fit。高僧文献は同じ軸へ投影。model={MODEL}、PC1+PC2={sum(pca_ratio)*100:.1f}%。</text>',
        f'<rect x="{pad_l}" y="{pad_t}" width="{plot_w}" height="{plot_h}" rx="8" fill="#ffffff" stroke="#ddd6ca"/>',
    ]
    if x_min < 0 < x_max:
        lines.append(f'<line x1="{sx(0):.1f}" y1="{pad_t+28}" x2="{sx(0):.1f}" y2="{pad_t+plot_h-28}" stroke="{axis}" stroke-width="1"/>')
    if y_min < 0 < y_max:
        lines.append(f'<line x1="{pad_l+28}" y1="{sy(0):.1f}" x2="{pad_l+plot_w-28}" y2="{sy(0):.1f}" stroke="{axis}" stroke-width="1"/>')

    # Ellipses.
    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        ew, eh, angle = covariance_ellipse(pts, center, radius=1.3)
        color = COLORS.get(author, "#64748b")
        rx = max(ew / (x_max - x_min) * plot_w, 12.0)
        ry = max(eh / (y_max - y_min) * plot_h, 12.0)
        opacity = "0.11" if author in {"法然", "親鸞"} else "0.07"
        lines.append(
            f'<ellipse cx="{sx(center[0]):.1f}" cy="{sy(center[1]):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'transform="rotate({-angle:.1f} {sx(center[0]):.1f} {sy(center[1]):.1f})" '
            f'fill="{color}" fill-opacity="{opacity}" stroke="{color}" stroke-opacity="0.42" stroke-width="2"/>'
        )

    # Points.
    for record in records:
        color = COLORS.get(record["author"], "#64748b")
        radius = 5.4 if record["author"] in {"法然", "親鸞"} else 4.0
        alpha = "0.62" if record["author"] in {"法然", "親鸞"} else "0.42"
        lines.append(
            f'<circle cx="{sx(record["x"]):.1f}" cy="{sy(record["y"]):.1f}" r="{radius:.1f}" fill="{color}" fill-opacity="{alpha}">'
            f'<title>{svg_escape(record["author"] + " " + record["work"] + " " + record["chunk_id"])}</title></circle>'
        )

    # Centroids.
    label_offsets = {
        "法然": (-54, -18),
        "親鸞": (12, -18),
        "龍樹": (12, -12),
        "天親": (12, 24),
        "曇鸞": (12, -16),
        "道綽": (12, 22),
        "善導": (12, -16),
        "源信": (12, 22),
    }
    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        color = COLORS.get(author, "#64748b")
        r = 12 if author in {"法然", "親鸞"} else 9
        lines.append(f'<circle cx="{sx(center[0]):.1f}" cy="{sy(center[1]):.1f}" r="{r}" fill="{color}" stroke="#ffffff" stroke-width="3"/>')
        dx, dy = label_offsets.get(author, (12, -12))
        label = f"{author} 重心" if author in {"法然", "親鸞"} else author
        lines.append(
            f'<text x="{sx(center[0])+dx:.1f}" y="{sy(center[1])+dy:.1f}" font-family="Hiragino Sans, Yu Gothic, sans-serif" '
            f'font-size="16" font-weight="700" fill="{color}">{svg_escape(label)}</text>'
        )

    # Legend.
    lx = width - pad_r + 42
    ly = pad_t + 10
    lines.append(f'<g font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="15" fill="{text}">')
    lines.append(f'<text x="{lx}" y="{ly}" font-size="18" font-weight="700">凡例</text>')
    y = ly + 34
    for author in ["法然", "親鸞", "龍樹", "天親", "曇鸞", "道綽", "善導", "源信"]:
        if author not in groups:
            continue
        color = COLORS.get(author, "#64748b")
        count = len(groups[author])
        lines.append(f'<circle cx="{lx+8}" cy="{y-5}" r="7" fill="{color}" fill-opacity="0.7"/>')
        lines.append(f'<text x="{lx+26}" y="{y}">{svg_escape(author)} n={count}</text>')
        y += 28
    lines.append(f'<text x="{lx}" y="{y+22}" font-size="13" fill="#686158">点=700-token chunk</text>')
    lines.append(f'<text x="{lx}" y="{y+44}" font-size="13" fill="#686158">楕円=各文献群の広がり</text>')
    lines.append(f'<text x="{lx}" y="{y+66}" font-size="13" fill="#686158">本文は図・メタに含めない</text>')
    lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines)


def summarize(records: list[dict[str, Any]], source_records: list[dict[str, Any]], pca_ratio: list[float]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["author"]].append(record)
    stats = {}
    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        distances = np.linalg.norm(pts - center, axis=1)
        stats[author] = {
            "chunk_count": len(rows),
            "centroid": [round(float(center[0]), 6), round(float(center[1]), 6)],
            "rms_radius": round(float(np.sqrt(np.mean(distances**2))), 6),
            "p90_radius": round(float(np.quantile(distances, 0.9)), 6),
        }
    return {
        "title": "Honen/Shinran semantic map with Pure Land patriarch anchors",
        "method": {
            "embedding_model": MODEL,
            "tokenizer": "tiktoken cl100k_base",
            "max_tokens": MAX_TOKENS,
            "overlap": OVERLAP,
            "pca_fit_scope": "法然『選択集』 and 親鸞『教行信証』 chunks only",
            "anchor_projection": "anchor chunks projected into the fixed Honen/Shinran PCA plane",
            "pca_explained_variance_ratio_on_fit_scope": [round(float(v), 6) for v in pca_ratio],
        },
        "sources": source_records,
        "author_stats": stats,
        "chunks": [
            {
                key: (round(value, 6) if key in {"x", "y"} and isinstance(value, float) else value)
                for key, value in record.items()
                if key not in {"embedding", "text"}
            }
            for record in records
        ],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base_token_chunks = make_base_token_chunks()
    base_vectors = get_base_embeddings(base_token_chunks)
    mean, components, ratio = fit_base_pca(base_vectors)
    base_coords = project(base_vectors, mean, components)
    base_records = base_render_records(base_token_chunks, base_coords)

    anchor_chunks, source_records = load_anchor_chunks()
    anchor_vectors = get_anchor_embeddings(anchor_chunks)
    anchor_coords = project(anchor_vectors, mean, components)
    anchor_records = anchor_render_records(anchor_chunks, anchor_coords)

    records = base_records + anchor_records
    SVG_PATH.write_text(render_svg(records, ratio), encoding="utf-8")
    META_PATH.write_text(
        json.dumps(summarize(records, source_records, ratio), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {SVG_PATH}")
    print(f"wrote {META_PATH}")
    print("chunks:", dict(Counter(record["author"] for record in records)))


if __name__ == "__main__":
    main()
