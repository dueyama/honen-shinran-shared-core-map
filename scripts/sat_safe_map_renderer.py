#!/usr/bin/env python3
"""Shared renderer for SAT-safe Honen/Shinran map figures.

Paper figures 1 and 2 must use the same coordinate transform and covariance
ellipse code. Keep rendering here instead of duplicating PIL/SVG logic.
"""

from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


MODEL = "text-embedding-3-large"
MAX_TOKENS = 700
OVERLAP = 100

COLORS: dict[str, tuple[int, int, int]] = {
    "法然": (31, 120, 180),
    "親鸞": (214, 63, 63),
    "龍樹": (139, 92, 246),
    "天親": (15, 159, 154),
    "曇鸞": (47, 143, 78),
    "道綽": (183, 121, 31),
    "善導": (109, 91, 208),
    "源信": (226, 109, 47),
}

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

FOCUS_AUTHORS = ("法然", "親鸞")
ANCHOR_AUTHORS = ("龍樹", "天親", "曇鸞", "道綽", "善導", "源信")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=0)
    return ImageFont.load_default()


def rounded(value: float) -> float:
    return round(float(value), 6)


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


def group_records(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        groups[row["author"]].append(row)
    return groups


def focus_extent(records: list[dict[str, Any]]) -> tuple[float, float, float, float]:
    focus_rows = [row for row in records if row["author"] in FOCUS_AUTHORS]
    if not focus_rows:
        raise ValueError("no Honen/Shinran rows for figure extent")
    xs = [row["x"] for row in focus_rows]
    ys = [row["y"] for row in focus_rows]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_pad = max((x_max - x_min) * 0.09, 0.03)
    y_pad = max((y_max - y_min) * 0.09, 0.03)
    return x_min - x_pad, x_max + x_pad, y_min - y_pad, y_max + y_pad


def author_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    for author, rows in group_records(records).items():
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        distances = np.linalg.norm(pts - center, axis=1)
        ell_w, ell_h, angle = covariance_ellipse(pts)
        stats[author] = {
            "chunk_count": len(rows),
            "centroid": [rounded(center[0]), rounded(center[1])],
            "rms_radius": rounded(float(np.sqrt(np.mean(distances**2)))),
            "p90_radius": rounded(float(np.quantile(distances, 0.9))),
            "ellipse_radius_scale": 1.5,
            "ellipse_width": rounded(ell_w),
            "ellipse_height": rounded(ell_h),
            "ellipse_angle_degrees": rounded(angle),
        }
    return stats


def render_sat_safe_map_png(
    records: list[dict[str, Any]],
    output_path: Path,
    *,
    title: str,
    subtitle: str,
    legend_order: list[str],
    show_anchor_note: bool,
) -> dict[str, Any]:
    width, height = 1620, 1060
    pad_l, pad_r, pad_t, pad_b = 100, 290, 126, 94
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    x_min, x_max, y_min, y_max = focus_extent(records)

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

    draw.text((pad_l, 44), title, fill=(37, 34, 29), font=title_font)
    draw.text((pad_l, 82), subtitle, fill=(104, 97, 88), font=sub_font)
    draw.rounded_rectangle(
        (pad_l, pad_t, pad_l + plot_w, pad_t + plot_h),
        radius=8,
        fill=(255, 255, 255),
        outline=(221, 214, 202),
        width=2,
    )

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

    groups = group_records(records)
    ellipse_order = [author for author in legend_order if author not in FOCUS_AUTHORS and author in groups]
    ellipse_order.extend([author for author in FOCUS_AUTHORS if author in groups])

    ellipse_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for author in ellipse_order:
        rows = groups[author]
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
        if author in FOCUS_AUTHORS:
            fill_alpha = 0.12
            stroke_alpha = 0.42
            stroke_width = 3
        else:
            fill_alpha = 0.07
            stroke_alpha = 0.32
            stroke_width = 2
        tdraw.ellipse(
            (6, 6, box_w - 6, box_h - 6),
            fill=blend(color, fill_alpha),
            outline=blend(color, stroke_alpha),
            width=stroke_width,
        )
        rotated = temp.rotate(-angle, expand=True, resample=Image.Resampling.BICUBIC)
        cx, cy = sx(center[0]), sy(center[1])
        ellipse_layer.alpha_composite(rotated, (int(cx - rotated.width / 2), int(cy - rotated.height / 2)))
    image = Image.alpha_composite(image.convert("RGBA"), ellipse_layer)
    draw = ImageDraw.Draw(image, "RGBA")

    for row in records:
        author = row["author"]
        color = COLORS[author]
        x, y = sx(row["x"]), sy(row["y"])
        radius = 5.8 if author in FOCUS_AUTHORS else 4.3
        alpha = 0.62 if author in FOCUS_AUTHORS else 0.42
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=blend(color, alpha),
            outline=blend((255, 255, 255), 0.8),
            width=1,
        )

    label_offsets = {
        "法然": (-56, -22),
        "親鸞": (15, -22),
        "龍樹": (12, 26),
        "天親": (12, -16),
        "曇鸞": (12, -16),
        "道綽": (12, 22),
        "善導": (12, -16),
        "源信": (12, 22),
    }
    for author in legend_order:
        if author not in groups:
            continue
        rows = groups[author]
        pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
        center = pts.mean(axis=0)
        color = COLORS[author]
        cx, cy = sx(center[0]), sy(center[1])
        radius = 13 if author in FOCUS_AUTHORS else 10
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            fill=(*color, 255),
            outline=(255, 255, 255, 255),
            width=4,
        )
        dx, dy = label_offsets.get(author, (12, -12))
        label = f"{author} 重心" if author in FOCUS_AUTHORS else author
        draw.text((cx + dx, cy + dy), label, fill=color, font=label_font)

    lx = width - pad_r + 38
    ly = pad_t + 10
    draw.text((lx, ly), "凡例", fill=(37, 34, 29), font=font(19, bold=True))
    y = ly + 42
    for author in legend_order:
        if author not in groups:
            continue
        rows = groups[author]
        color = COLORS[author]
        draw.ellipse((lx, y - 12, lx + 16, y + 4), fill=(*color, 190))
        draw.text((lx + 28, y - 14), f"{author} n={len(rows)}", fill=(37, 34, 29), font=legend_font)
        if author in FOCUS_AUTHORS:
            pts = np.array([[row["x"], row["y"]] for row in rows], dtype=float)
            center = pts.mean(axis=0)
            distances = np.linalg.norm(pts - center, axis=1)
            draw.text((lx + 28, y + 7), f"p90半径 {np.quantile(distances, 0.9):.3f}", fill=(104, 97, 88), font=small_font)
            y += 58
        else:
            y += 31
    draw.text((lx, y + 16), "点=Unicode-safe", fill=(104, 97, 88), font=small_font)
    draw.text((lx, y + 36), "700 token chunk", fill=(104, 97, 88), font=small_font)
    if show_anchor_note:
        draw.text((lx, y + 56), "祖師文献は同じPCA面へ投影", fill=(104, 97, 88), font=small_font)
    else:
        draw.text((lx, y + 56), "表示範囲は2者に合わせて調整", fill=(104, 97, 88), font=small_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, quality=95)

    stats = author_stats(records)
    stats["_figure"] = {
        "renderer": "scripts/sat_safe_map_renderer.py",
        "width": width,
        "height": height,
        "plot_padding": [pad_l, pad_r, pad_t, pad_b],
        "extent_basis": "Honen/Shinran records only",
        "extent": [rounded(x_min), rounded(x_max), rounded(y_min), rounded(y_max)],
        "ellipse_radius_scale": 1.5,
    }
    return stats
