#!/usr/bin/env python3
"""Build a local-only simple 2D map for Honen/Shinran page chunks.

This first pass deliberately avoids publishing raw text. It reads downloaded
seiten HTML pages from data/raw/, extracts page-level chunks, builds a
character n-gram TF-IDF matrix, projects it with NumPy SVD, and writes an SVG.
"""

from __future__ import annotations

import html
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "seiten"
OUT_DIR = ROOT / "data" / "outputs"
SVG_PATH = OUT_DIR / "honen_shinran_simple_2d.svg"
ZOOM_SVG_PATH = OUT_DIR / "honen_shinran_simple_2d_with_zoom.svg"
META_PATH = OUT_DIR / "honen_shinran_simple_2d_meta.json"


@dataclass
class Chunk:
    chunk_id: str
    author: str
    work: str
    page: str
    text: str


class SeitenParser(HTMLParser):
    def __init__(self, allowed_classes: set[str]) -> None:
        super().__init__(convert_charrefs=True)
        self.allowed_classes = allowed_classes
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._in_title = False
        self._collect_depth = 0
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k: v or "" for k, v in attrs}
        if tag in {"script", "style", "form"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        class_names = set(attrs_dict.get("class", "").split())
        if tag == "div" and class_names.intersection(self.allowed_classes):
            self._collect_depth += 1
        if tag == "br" and self._collect_depth and not self._skip_depth:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "form"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag == "div" and self._collect_depth:
            self._collect_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._collect_depth and not self._skip_depth:
            self.text_parts.append(data)

    @property
    def title(self) -> str:
        return normalize_space("".join(self.title_parts))

    @property
    def text(self) -> str:
        return normalize_space("".join(self.text_parts))


def normalize_space(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\ufeff", "")
    text = re.sub(r"Image:\s*[A-Za-z0-9_]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_chunks() -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(RAW_DIR.glob("*.html")):
        raw = path.read_text(encoding="utf-8", errors="ignore")

        # Use Japanese reading text for both works in this rough first map.
        parser = SeitenParser({"honbun", "s_sage", "l_nobegaki"})
        parser.feed(raw)
        title = parser.title

        if "選擇本願念佛集" in title:
            author = "法然"
            work = "選択本願念仏集"
        elif "教行信証" in title or "顕浄土" in title:
            author = "親鸞"
            work = "教行信証"
        else:
            continue

        text = parser.text
        if len(text) < 120:
            continue
        page = path.stem
        chunks.append(
            Chunk(
                chunk_id=f"{author}:{page}",
                author=author,
                work=work,
                page=page,
                text=text,
            )
        )
    return chunks


def char_ngrams(text: str, min_n: int = 2, max_n: int = 4) -> Counter[str]:
    compact = re.sub(r"\s+", "", text)
    counts: Counter[str] = Counter()
    for n in range(min_n, max_n + 1):
        for i in range(0, max(0, len(compact) - n + 1)):
            gram = compact[i : i + n]
            if re.search(r"[一-龯ぁ-んァ-ヴー]", gram):
                counts[gram] += 1
    return counts


def build_matrix(chunks: list[Chunk], vocab_size: int = 1800) -> np.ndarray:
    doc_counts = [char_ngrams(chunk.text) for chunk in chunks]
    df: Counter[str] = Counter()
    for counts in doc_counts:
        df.update(counts.keys())

    # Drop singletons and overly-common grams, then keep the most frequent.
    max_df = int(len(chunks) * 0.88)
    candidates = {
        term: freq
        for term, freq in df.items()
        if 2 <= freq <= max_df
    }
    vocab = [
        term
        for term, _ in Counter(candidates).most_common(vocab_size)
    ]
    index = {term: i for i, term in enumerate(vocab)}

    x = np.zeros((len(chunks), len(vocab)), dtype=float)
    for row, counts in enumerate(doc_counts):
        total = sum(counts.values()) or 1
        for term, count in counts.items():
            col = index.get(term)
            if col is not None:
                tf = count / total
                idf = math.log((1 + len(chunks)) / (1 + df[term])) + 1
                x[row, col] = tf * idf
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


def project_2d(x: np.ndarray) -> np.ndarray:
    centered = x - x.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :2] * s[:2]
    coords -= coords.mean(axis=0, keepdims=True)
    scale = np.max(np.abs(coords)) or 1.0
    return coords / scale


def covariance_ellipse(points: np.ndarray, center: np.ndarray, radius: float = 1.55) -> tuple[float, float, float]:
    if len(points) < 3:
        return (0.05, 0.05, 0.0)
    cov = np.cov(points.T)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    width = math.sqrt(max(vals[0], 1e-9)) * radius
    height = math.sqrt(max(vals[1], 1e-9)) * radius
    angle = math.degrees(math.atan2(vecs[1, 0], vecs[0, 0]))
    return width, height, angle


def chunk_source_url(chunk: Chunk) -> str:
    return f"https://seiten.icho.gr.jp/html/{chunk.page}.html"


def summarize(chunks: list[Chunk], coords: np.ndarray) -> dict[str, object]:
    groups: dict[str, list[int]] = defaultdict(list)
    for i, chunk in enumerate(chunks):
        groups[chunk.author].append(i)

    author_stats: dict[str, object] = {}
    centroids: dict[str, np.ndarray] = {}
    for author, indices in groups.items():
        pts = coords[indices]
        center = pts.mean(axis=0)
        centroids[author] = center
        distances = np.linalg.norm(pts - center, axis=1)
        ew, eh, angle = covariance_ellipse(pts, center)
        pages = [chunks[i].page for i in indices]
        author_stats[author] = {
            "chunk_count": len(indices),
            "work": chunks[indices[0]].work,
            "centroid": [round(float(center[0]), 6), round(float(center[1]), 6)],
            "rms_radius": round(float(np.sqrt(np.mean(distances**2))), 6),
            "p90_radius": round(float(np.quantile(distances, 0.9)), 6),
            "ellipse_radius_scale": 1.55,
            "ellipse_width": round(float(ew), 6),
            "ellipse_height": round(float(eh), 6),
            "ellipse_angle_degrees": round(float(angle), 3),
            "page_min": min(pages),
            "page_max": max(pages),
        }

    centroid_distance = None
    if {"法然", "親鸞"}.issubset(centroids):
        centroid_distance = round(float(np.linalg.norm(centroids["法然"] - centroids["親鸞"])), 6)

    return {
        "title": "法然『選択集』と親鸞『教行信証』の単純2Dマップ",
        "created_from": "local downloaded seiten HTML; raw text is not included in this metadata",
        "source_site": "聖教電子化研究会",
        "source_urls": [
            "https://seiten.icho.gr.jp/html/z1-[920-1005].html",
            "https://seiten.icho.gr.jp/html/[152-430].html",
        ],
        "method": {
            "chunk_unit": "seiten page",
            "text_basis": "Japanese reading text extracted from honbun/s_sage/l_nobegaki; r_kanbun excluded in this first rough map",
            "vectorizer": "character 2-4 gram TF-IDF, vocabulary size up to 1800",
            "projection": "centered SVD, first two components, scaled by max absolute coordinate",
            "status": "rough exploratory map; not a final semantic embedding result",
        },
        "author_stats": author_stats,
        "centroid_distance": centroid_distance,
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "author": chunk.author,
                "work": chunk.work,
                "page": chunk.page,
                "source_url": chunk_source_url(chunk),
                "x": round(float(coords[i, 0]), 6),
                "y": round(float(coords[i, 1]), 6),
            }
            for i, chunk in enumerate(chunks)
        ],
    }


def svg_escape(value: str) -> str:
    return html.escape(value, quote=True)


def render_svg(chunks: list[Chunk], coords: np.ndarray) -> str:
    width, height = 1200, 820
    pad = 82
    colors = {
        "法然": "#1f78b4",
        "親鸞": "#d63f3f",
    }
    bg = "#fbfaf7"
    axis = "#d8d2c5"
    text = "#25221d"

    def sx(x: float) -> float:
        return pad + (x + 1.08) / 2.16 * (width - 2 * pad)

    def sy(y: float) -> float:
        return height - pad - (y + 1.08) / 2.16 * (height - 2 * pad)

    groups: dict[str, list[int]] = defaultdict(list)
    for i, chunk in enumerate(chunks):
        groups[chunk.author].append(i)

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        f'<text x="{pad}" y="44" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="24" font-weight="700" fill="{text}">法然『選択集』と親鸞『教行信証』の単純2Dマップ</text>',
        f'<text x="{pad}" y="72" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="14" fill="#686158">ページ単位。char n-gram TF-IDF + SVD。点=ページ、太点=重心、楕円=点群の広がり。本文は図に含めない。</text>',
        f'<line x1="{pad}" y1="{height/2:.1f}" x2="{width-pad}" y2="{height/2:.1f}" stroke="{axis}" stroke-width="1"/>',
        f'<line x1="{width/2:.1f}" y1="{pad}" x2="{width/2:.1f}" y2="{height-pad}" stroke="{axis}" stroke-width="1"/>',
    ]

    # Ellipses first.
    for author, indices in groups.items():
        pts = coords[indices]
        center = pts.mean(axis=0)
        ew, eh, angle = covariance_ellipse(pts, center)
        color = colors[author]
        rx = max(ew * (width - 2 * pad) / 2.16, 20.0)
        ry = max(eh * (height - 2 * pad) / 2.16, 20.0)
        lines.append(
            f'<ellipse cx="{sx(center[0]):.1f}" cy="{sy(center[1]):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'transform="rotate({-angle:.1f} {sx(center[0]):.1f} {sy(center[1]):.1f})" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-opacity="0.45" stroke-width="2"/>'
        )

    # Points.
    for chunk, (x, y) in zip(chunks, coords):
        color = colors[chunk.author]
        title = svg_escape(f"{chunk.author} {chunk.work} p.{chunk.page}")
        lines.append(
            f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4.2" fill="{color}" fill-opacity="0.54">'
            f'<title>{title}</title></circle>'
        )

    # Centroids and labels.
    for author, indices in groups.items():
        pts = coords[indices]
        center = pts.mean(axis=0)
        color = colors[author]
        lines.append(
            f'<circle cx="{sx(center[0]):.1f}" cy="{sy(center[1]):.1f}" r="11" fill="{color}" stroke="#ffffff" stroke-width="3">'
            f'<title>{svg_escape(author)} centroid</title></circle>'
        )
        lines.append(
            f'<text x="{sx(center[0]) + 15:.1f}" y="{sy(center[1]) - 12:.1f}" font-family="Hiragino Sans, Yu Gothic, sans-serif" '
            f'font-size="17" font-weight="700" fill="{color}">{svg_escape(author)} 重心</text>'
        )

    legend_x = width - 320
    legend_y = 106
    lines.append(f'<g font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="15" fill="{text}">')
    lines.append(f'<rect x="{legend_x}" y="{legend_y-26}" width="238" height="118" rx="6" fill="#ffffff" stroke="#ddd6ca"/>')
    for n, author in enumerate(["法然", "親鸞"]):
        y = legend_y + n * 36
        count = len(groups[author])
        lines.append(f'<circle cx="{legend_x + 22}" cy="{y}" r="6" fill="{colors[author]}" fill-opacity="0.62"/>')
        lines.append(f'<circle cx="{legend_x + 46}" cy="{y}" r="9" fill="{colors[author]}" stroke="#ffffff" stroke-width="2"/>')
        lines.append(f'<text x="{legend_x + 64}" y="{y + 5}">{author} pages: {count}</text>')
    lines.append(f'<text x="{legend_x + 18}" y="{legend_y + 83}" font-size="12" fill="#686158">この図は粗い下見。三層分析ではない。</text>')
    lines.append("</g>")

    lines.append("</svg>")
    return "\n".join(lines)


def render_svg_with_zoom(
    chunks: list[Chunk],
    coords: np.ndarray,
    title: str = "法然『選択集』と親鸞『教行信証』の単純2Dマップ",
    subtitle: str = "ページ単位。char n-gram TF-IDF + SVD。点=ページ、太点=重心、楕円=点群の広がり。右は局所拡大。",
) -> str:
    width, height = 1600, 1000
    bg = "#fbfaf7"
    axis = "#d8d2c5"
    text = "#25221d"
    colors = {"法然": "#1f78b4", "親鸞": "#d63f3f"}
    groups: dict[str, list[int]] = defaultdict(list)
    for i, chunk in enumerate(chunks):
        groups[chunk.author].append(i)

    def panel_mapper(px: float, py: float, pw: float, ph: float, center: np.ndarray, half_range: float):
        def sx(x: float) -> float:
            return px + pw / 2 + (x - center[0]) / (2 * half_range) * pw

        def sy(y: float) -> float:
            return py + ph / 2 - (y - center[1]) / (2 * half_range) * ph

        return sx, sy

    def draw_panel(
        lines: list[str],
        title: str,
        px: float,
        py: float,
        pw: float,
        ph: float,
        authors: list[str],
        center: np.ndarray,
        half_range: float,
        point_radius: float,
        show_other_faint: bool = False,
    ) -> None:
        sx, sy = panel_mapper(px, py, pw, ph, center, half_range)
        lines.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="8" fill="#ffffff" stroke="#ddd6ca"/>')
        lines.append(
            f'<text x="{px + 18}" y="{py + 34}" font-family="Hiragino Sans, Yu Gothic, sans-serif" '
            f'font-size="20" font-weight="700" fill="{text}">{svg_escape(title)}</text>'
        )
        lines.append(f'<line x1="{px + 24}" y1="{sy(center[1]):.1f}" x2="{px + pw - 24}" y2="{sy(center[1]):.1f}" stroke="{axis}" stroke-width="1"/>')
        lines.append(f'<line x1="{sx(center[0]):.1f}" y1="{py + 54}" x2="{sx(center[0]):.1f}" y2="{py + ph - 24}" stroke="{axis}" stroke-width="1"/>')

        visible_authors = list(colors.keys()) if show_other_faint else authors
        for author in visible_authors:
            if author not in groups:
                continue
            pts = coords[groups[author]]
            author_center = pts.mean(axis=0)
            ew, eh, angle = covariance_ellipse(pts, author_center)
            color = colors[author]
            rx = max(ew / (2 * half_range) * pw, 14.0)
            ry = max(eh / (2 * half_range) * ph, 14.0)
            opacity = "0.08" if author not in authors else "0.14"
            stroke_opacity = "0.24" if author not in authors else "0.55"
            lines.append(
                f'<ellipse cx="{sx(author_center[0]):.1f}" cy="{sy(author_center[1]):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
                f'transform="rotate({-angle:.1f} {sx(author_center[0]):.1f} {sy(author_center[1]):.1f})" '
                f'fill="{color}" fill-opacity="{opacity}" stroke="{color}" stroke-opacity="{stroke_opacity}" stroke-width="2"/>'
            )

        for i, chunk in enumerate(chunks):
            if chunk.author not in visible_authors:
                continue
            x, y = coords[i]
            if abs(x - center[0]) > half_range * 1.08 or abs(y - center[1]) > half_range * 1.08:
                continue
            color = colors[chunk.author]
            alpha = "0.18" if chunk.author not in authors else "0.72"
            r = point_radius * (0.72 if chunk.author not in authors else 1.0)
            lines.append(
                f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{r:.1f}" fill="{color}" fill-opacity="{alpha}">'
                f'<title>{svg_escape(chunk.author + " " + chunk.work + " p." + chunk.page)}</title></circle>'
            )

        for author in authors:
            pts = coords[groups[author]]
            author_center = pts.mean(axis=0)
            color = colors[author]
            lines.append(
                f'<circle cx="{sx(author_center[0]):.1f}" cy="{sy(author_center[1]):.1f}" r="{point_radius * 2.2:.1f}" '
                f'fill="{color}" stroke="#ffffff" stroke-width="3"/>'
            )
            label_x = min(max(sx(author_center[0]) + 14, px + 16), px + pw - 150)
            label_y = min(max(sy(author_center[1]) - 12, py + 66), py + ph - 18)
            lines.append(
                f'<text x="{label_x:.1f}" y="{label_y:.1f}" font-family="Hiragino Sans, Yu Gothic, sans-serif" '
                f'font-size="17" font-weight="700" fill="{color}">{author} 重心</text>'
            )

    all_center = coords.mean(axis=0)
    all_range = float(np.max(np.abs(coords - all_center))) * 1.08
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
        f'<text x="70" y="52" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="28" font-weight="700" fill="{text}">{svg_escape(title)}</text>',
        f'<text x="70" y="82" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="15" fill="#686158">{svg_escape(subtitle)}</text>',
    ]

    draw_panel(
        lines,
        "同一座標での全体図",
        70,
        120,
        1010,
        810,
        ["法然", "親鸞"],
        all_center,
        all_range,
        5.6,
        show_other_faint=True,
    )

    for author, y0 in [("法然", 120), ("親鸞", 535)]:
        pts = coords[groups[author]]
        center = pts.mean(axis=0)
        local_range = max(float(np.max(np.abs(pts - center))) * 1.22, 0.05)
        draw_panel(
            lines,
            f"{author} 点群の局所拡大",
            1120,
            y0,
            410,
            355,
            [author],
            center,
            local_range,
            5.2,
            show_other_faint=False,
        )

    legend_x = 1120
    legend_y = 62
    lines.append(f'<g font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="15" fill="{text}">')
    for n, author in enumerate(["法然", "親鸞"]):
        x = legend_x + n * 150
        lines.append(f'<circle cx="{x}" cy="{legend_y}" r="7" fill="{colors[author]}" fill-opacity="0.72"/>')
        lines.append(f'<circle cx="{x + 24}" cy="{legend_y}" r="11" fill="{colors[author]}" stroke="#ffffff" stroke-width="2"/>')
        lines.append(f'<text x="{x + 42}" y="{legend_y + 5}">{author} n={len(groups[author])}</text>')
    lines.append("</g>")

    lines.append("</svg>")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chunks = load_chunks()
    if not chunks:
        raise SystemExit("No chunks found. Download seiten HTML into data/raw/seiten first.")
    x = build_matrix(chunks)
    coords = project_2d(x)
    SVG_PATH.write_text(render_svg(chunks, coords), encoding="utf-8")
    ZOOM_SVG_PATH.write_text(render_svg_with_zoom(chunks, coords), encoding="utf-8")
    META_PATH.write_text(
        json.dumps(summarize(chunks, coords), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    counts = Counter(chunk.author for chunk in chunks)
    print(f"wrote {SVG_PATH}")
    print(f"wrote {ZOOM_SVG_PATH}")
    print(f"wrote {META_PATH}")
    print("chunks:", dict(counts))


if __name__ == "__main__":
    main()
