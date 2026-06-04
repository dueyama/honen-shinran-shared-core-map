#!/usr/bin/env python3
"""Render a focus-only Honen/Shinran figure from the SAT-safe map metadata.

The input metadata contains no raw text. This script keeps the same PCA
coordinates as the high-priest anchor map, but fits the visible plot extent to
Honen/Shinran chunks only so the two distributions are easier to read.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MODEL = "text-embedding-3-large"
MAX_TOKENS = 700
OVERLAP = 100
MAP_PATH = ROOT / "data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json"
FIGURE_PATH = ROOT / "docs/figures/sat-safe-honen-shinran-focus-map.png"
META_PATH = ROOT / "data/outputs/sat_safe_honen_shinran_focus_map_text-embedding-3-large_700_100.json"

COLORS = {
    "法然": (31, 120, 180),
    "親鸞": (214, 63, 63),
}

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=0)
    return ImageFont.load_default()


def rounded(value: float) -> float:
    return round(float(value), 6)


def load_focus_records() -> list[dict[str, Any]]:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    records = [row for row in data["chunks"] if row["author"] in {"法然", "親鸞"}]
    if not records:
        raise RuntimeError("no Honen/Shinran records found")
    return records


def covariance_ellipse(points: np.ndarray, radius: float = 1.5) -> tuple[float, float, float]:
    if len(points) < 3:
        return 0.04, 0.04, 0.0
    cov = np.cov(points.T)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    width = 2 * radius * math.sqrt(max(float(vals[0]), 1e-12))
    height = 2 * radius * math.sqrt(max(float(vals[1]), 1e-12))
    angle = math.degrees(math.atan2(float(vecs[1, 0]), float(vecs[0, 0])))
    return width, height, angle


def blend(color: tuple[int, int, int], alpha: float) -> tuple[int, int, int, int]:
    return (*color, int(max(0, min(255, alpha * 255))))


def render(records: list[dict[str, Any]]) -> None:
    width, height = 1620, 1060
    pad_l, pad_r, pad_t, pad_b = 100, 290, 126, 94
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    xs = [row["x"] for row in records]
    ys = [row["y"] for row in records]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_pad = max((x_max - x_min) * 0.09, 0.03)
    y_pad = max((y_max - y_min) * 0.09, 0.03)
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad

    def sx(value: float) -> float:
        return pad_l + (value - x_min) / (x_max - x_min) * plot_w

    def sy(value: float) -> float:
        return pad_t + (y_max - value) / (y_max - y_min) * plot_h

    image = Image.new("RGB", (width, height), (251, 250, 247))
    draw = ImageDraw.Draw(image, "RGBA")
    title_font = font(31, bold=True)
    sub_font = font(16)
    label_font = font(17, bold=True)
    small_font = font(14)
    legend_font = font(15)

    draw.text((pad_l, 44), "SAT漢文 safe chunk map: 法然・親鸞", fill=(37, 34, 29), font=title_font)
    draw.text(
        (pad_l, 82),
        f"PCA fit=法然/親鸞。model={MODEL}, {MAX_TOKENS} token / overlap {OVERLAP}。本文は図・メタに含めない。",
        fill=(104, 97, 88),
        font=sub_font,
    )
    draw.rounded_rectangle((pad_l, pad_t, pad_l + plot_w, pad_t + plot_h), radius=8, fill=(255, 255, 255), outline=(221, 214, 202), width=2)

    # Light reference grid.
    for step in range(1, 5):
        x = pad_l + plot_w * step / 5
        y = pad_t + plot_h * step / 5
        draw.line((x, pad_t + 22, x, pad_t + plot_h - 22), fill=(232, 227, 218, 170), width=1)
        draw.line((pad_l + 22, y, pad_l + plot_w - 22, y), fill=(232, 227, 218, 170), width=1)
    if x_min < 0 < x_max:
        x = sx(0)
        draw.line((x, pad_t + 22, x, pad_t + plot_h - 22), fill=(205, 198, 185, 230), width=2)
    if y_min < 0 < y_max:
        y = sy(0)
        draw.line((pad_l + 22, y, pad_l + plot_w - 22, y), fill=(205, 198, 185, 230), width=2)

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        groups[row["author"]].append(row)

    # Ellipses on a transparent layer so rotation works cleanly.
    ellipse_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        ell_w, ell_h, angle = covariance_ellipse(pts)
        rx = max(ell_w / (x_max - x_min) * plot_w / 2, 12.0)
        ry = max(ell_h / (y_max - y_min) * plot_h / 2, 12.0)
        color = COLORS[author]
        box_w = int(rx * 2 + 12)
        box_h = int(ry * 2 + 12)
        temp = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(temp, "RGBA")
        tdraw.ellipse((6, 6, box_w - 6, box_h - 6), fill=blend(color, 0.12), outline=blend(color, 0.42), width=3)
        rotated = temp.rotate(-angle, expand=True, resample=Image.Resampling.BICUBIC)
        cx, cy = sx(center[0]), sy(center[1])
        ellipse_layer.alpha_composite(rotated, (int(cx - rotated.width / 2), int(cy - rotated.height / 2)))
    image = Image.alpha_composite(image.convert("RGBA"), ellipse_layer)
    draw = ImageDraw.Draw(image, "RGBA")

    for row in records:
        color = COLORS[row["author"]]
        x, y = sx(row["x"]), sy(row["y"])
        draw.ellipse((x - 5.8, y - 5.8, x + 5.8, y + 5.8), fill=blend(color, 0.62), outline=blend((255, 255, 255), 0.8), width=1)

    label_offsets = {"法然": (-56, -22), "親鸞": (15, -22)}
    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        color = COLORS[author]
        cx, cy = sx(center[0]), sy(center[1])
        draw.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=(*color, 255), outline=(255, 255, 255, 255), width=4)
        dx, dy = label_offsets[author]
        draw.text((cx + dx, cy + dy), f"{author} 重心", fill=color, font=label_font)

    lx = width - pad_r + 38
    ly = pad_t + 10
    draw.text((lx, ly), "凡例", fill=(37, 34, 29), font=font(19, bold=True))
    y = ly + 42
    for author in ["法然", "親鸞"]:
        rows = groups[author]
        color = COLORS[author]
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        distances = np.linalg.norm(pts - center, axis=1)
        draw.ellipse((lx, y - 12, lx + 16, y + 4), fill=(*color, 190))
        draw.text((lx + 28, y - 14), f"{author} n={len(rows)}", fill=(37, 34, 29), font=legend_font)
        draw.text((lx + 28, y + 7), f"p90半径 {np.quantile(distances, 0.9):.3f}", fill=(104, 97, 88), font=small_font)
        y += 58
    draw.text((lx, y + 16), "点=Unicode-safe", fill=(104, 97, 88), font=small_font)
    draw.text((lx, y + 36), "700 token chunk", fill=(104, 97, 88), font=small_font)
    draw.text((lx, y + 56), "表示範囲は2者に合わせて調整", fill=(104, 97, 88), font=small_font)

    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(FIGURE_PATH, quality=95)


def write_meta(records: list[dict[str, Any]]) -> None:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        groups[row["author"]].append(row)
    stats = {}
    for author, rows in groups.items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        distances = np.linalg.norm(pts - center, axis=1)
        stats[author] = {
            "chunk_count": len(rows),
            "centroid": [rounded(center[0]), rounded(center[1])],
            "rms_radius": rounded(float(np.sqrt(np.mean(distances**2)))),
            "p90_radius": rounded(float(np.quantile(distances, 0.9))),
        }
    output = {
        "title": "SAT safe Honen/Shinran focus map",
        "input_map": str(MAP_PATH.relative_to(ROOT)),
        "figure": str(FIGURE_PATH.relative_to(ROOT)),
        "method": {
            "coordinate_basis": "same PCA coordinates as the SAT safe high-priest anchor map",
            "display_extent": "fitted to Honen/Shinran chunks only for readability",
            "raw_text_policy": "no raw/chunk text is read from the input metadata or written to this output",
        },
        "author_stats": stats,
        "chunks": [
            {
                "chunk_id": row["chunk_id"],
                "author": row["author"],
                "work": row["work"],
                "chunk_index": row["chunk_index"],
                "line_start": row["line_start"],
                "line_end": row["line_end"],
                "text_sha256": row["text_sha256"],
                "replacement_chars": row["replacement_chars"],
                "actual_token_count": row["actual_token_count"],
                "x": rounded(row["x"]),
                "y": rounded(row["y"]),
            }
            for row in records
        ],
    }
    META_PATH.parent.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    records = load_focus_records()
    render(records)
    write_meta(records)
    print(f"wrote {FIGURE_PATH.relative_to(ROOT)}")
    print(f"wrote {META_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
