#!/usr/bin/env python3
"""Render English public paper figures from text-free analysis outputs.

This script does not read raw source text, processed source text, chunk
previews, or embedding vectors. It renders English-labeled PNGs from the
existing public-boundary CSV/JSON analysis outputs.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from sat_safe_map_renderer import (
    ANCHOR_AUTHORS,
    FOCUS_AUTHORS,
    MAX_TOKENS,
    MODEL,
    OVERLAP,
    render_sat_safe_map_png,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "figures" / "en"

FOCUS_MAP = ROOT / "data/outputs/sat_safe_honen_shinran_focus_map_text-embedding-3-large_700_100.json"
ANCHOR_MAP = ROOT / "data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json"
NEAREST_CSV = ROOT / "data/outputs/nearest_neighbor_subsampling_2026-06-04_text-embedding-3-large_700_100.csv"
HONEN_SEQUENCE_CSV = ROOT / "data/outputs/honen_three_layer_sequence_2026-06-04.csv"
SHINRAN_SEQUENCE_CSV = ROOT / "data/outputs/shinran_three_layer_sequence_2026-06-04.csv"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

PANEL_COLORS = {
    "semantic": (47, 114, 178),
    "style": (54, 145, 92),
    "marker": (177, 114, 34),
}

AUTHOR_EN = {
    "法然": "Honen",
    "親鸞": "Shinran",
    "龍樹": "Nagarjuna",
    "天親": "Vasubandhu",
    "曇鸞": "Tanluan",
    "道綽": "Daochuo",
    "善導": "Shandao",
    "源信": "Genshin",
}

STYLE_EN = {
    "念仏・称名": "Nembutsu / name",
    "選択・本願": "Selection / Primal Vow",
    "正雑・諸行": "Right / misc. practices",
    "廃立・取捨": "Abandon / establish",
    "信・三心": "Shinjin / three minds",
    "願・回向": "Vow / transfer",
    "名号・真実": "Name / true reality",
    "往生・浄土": "Birth / Pure Land",
    "方便・化身土": "Expedient / transformed land",
    "罪・救済": "Sin / salvation",
}

MARKER_EN = {
    "浄土三部経": "Pure Land sutras",
    "涅槃経": "Nirvana Sutra",
    "大集/日月蔵": "Mahasamghata / Sun-Moon",
    "論/論註": "Treatise / commentary",
    "安楽集": "Anleji",
    "観経疏/善導釈": "Guanjing shu / Shandao",
    "往生要集": "Ojo yoshu",
    "七高僧名": "Seven patriarch names",
    "引用導入": "Quotation markers",
}

HONEN_SECTION_EN = {
    "序": "Preface",
    "聖道門・浄土門": "Sacred/Pure Land gates",
    "正雑二行": "Right/misc. practices",
    "本願念仏": "Primal Vow nembutsu",
    "三輩・一向専念": "Three grades / single-minded",
    "三心・信心": "Three minds / shinjin",
    "付属・証誠・選択総結": "Entrust. / verification",
    "末尾・奥書系": "Ending / colophon",
    "未分類": "Unclassified",
}

SHINRAN_VOLUME_EN = {
    "序": "Preface",
    "教巻": "Teaching",
    "行巻": "Practice",
    "信巻": "Shinjin",
    "証巻": "Realization",
    "真仏土巻": "True Buddha Land",
    "化身土巻": "Transformed Land",
    "未分類": "Unclassified",
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=0)
    return ImageFont.load_default()


def font_size(text_font: ImageFont.ImageFont) -> int:
    return int(getattr(text_font, "size", 14))


def alpha(color: tuple[int, int, int], value: int) -> tuple[int, int, int, int]:
    return (*color, value)


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    text_font: ImageFont.ImageFont,
    max_width: int,
) -> str:
    if draw.textlength(text, font=text_font) <= max_width:
        return text
    suffix = "..."
    out = text
    while out and draw.textlength(out + suffix, font=text_font) > max_width:
        out = out[:-1]
    return out + suffix if out else suffix


def wrap_words(
    draw: ImageDraw.ImageDraw,
    text: str,
    text_font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split(" ")
        line = ""
        for word in words:
            candidate = word if not line else f"{line} {word}"
            if draw.textlength(candidate, font=text_font) <= max_width:
                line = candidate
                continue
            if line:
                lines.append(line)
                line = word
            while draw.textlength(line, font=text_font) > max_width and len(line) > 1:
                cut = 1
                while cut < len(line) and draw.textlength(line[: cut + 1], font=text_font) <= max_width:
                    cut += 1
                lines.append(line[:cut])
                line = line[cut:]
        if line:
            lines.append(line)
    return lines


def draw_text_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fill: tuple[int, int, int],
    text_font: ImageFont.ImageFont,
    line_gap: int = 6,
) -> None:
    x0, y0, x1, y1 = box
    y = y0
    line_height = font_size(text_font) + line_gap
    for line in wrap_words(draw, text, text_font, x1 - x0):
        if y + line_height > y1:
            clipped = fit_text(draw, line, text_font, x1 - x0)
            draw.text((x0, y), clipped, fill=fill, font=text_font)
            return
        draw.text((x0, y), line, fill=fill, font=text_font)
        y += line_height


def scale(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    upper = float(np.quantile(values, 0.97))
    lower = float(np.quantile(values, 0.03))
    if upper <= lower:
        upper = float(values.max()) or 1.0
        lower = 0.0
    return np.clip((values - lower) / (upper - lower), 0.0, 1.0)


def color_for(value: float, color: tuple[int, int, int]) -> tuple[int, int, int]:
    value = max(0.0, min(1.0, value))
    base = 248
    return tuple(int(base + (component - base) * value) for component in color)


def render_map_figures() -> None:
    focus_data = json.loads(FOCUS_MAP.read_text(encoding="utf-8"))
    render_sat_safe_map_png(
        focus_data["chunks"],
        OUT_DIR / "sat-safe-honen-shinran-focus-map.png",
        title="SAT Chinese Unicode-safe Chunk Map: Honen and Shinran",
        subtitle=f"PCA fit=Honen/Shinran. model={MODEL}, {MAX_TOKENS}-token chunks / {OVERLAP}-token overlap.",
        legend_order=list(FOCUS_AUTHORS),
        show_anchor_note=False,
        label_map=AUTHOR_EN,
        legend_title="Legend",
        p90_label="p90 radius",
        point_note="Dots=Unicode-safe",
        chunk_note="700-token chunks",
        focus_note="Extent fitted to Honen/Shinran",
        centroid_suffix=" centroid",
    )

    anchor_data = json.loads(ANCHOR_MAP.read_text(encoding="utf-8"))
    ratios = anchor_data.get("method", {}).get("pca_explained_variance_ratio_on_fit_scope", [])
    ratio_note = f", PC1+PC2={sum(ratios) * 100:.1f}%" if ratios else ""
    render_sat_safe_map_png(
        anchor_data["chunks"],
        OUT_DIR / "sat-safe-honen-shinran-high-priest-anchor-map.png",
        title="SAT Chinese Unicode-safe Chunk Map: Honen, Shinran, and Anchors",
        subtitle=f"PCA fit=Honen/Shinran; anchors projected to the same plane. model={MODEL}, {MAX_TOKENS}/{OVERLAP} tokens{ratio_note}.",
        legend_order=list(FOCUS_AUTHORS) + list(ANCHOR_AUTHORS),
        show_anchor_note=True,
        label_map=AUTHOR_EN,
        legend_title="Legend",
        p90_label="p90 radius",
        point_note="Dots=Unicode-safe",
        chunk_note="700-token chunks",
        anchor_note="Anchors projected to PCA plane",
        centroid_suffix=" centroid",
    )


def read_nearest_counts() -> dict[str, list[dict[str, float | int | str]]]:
    rows: dict[str, list[dict[str, float | int | str]]] = {"法然": [], "親鸞": []}
    with NEAREST_CSV.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            count = int(row["simple_count"])
            if count <= 0:
                continue
            target = row["target_author"]
            if target not in rows:
                continue
            rows[target].append(
                {
                    "group": row["nearest_group"],
                    "count": count,
                    "ratio": float(row["simple_ratio"]),
                }
            )
    for target in rows:
        rows[target].sort(key=lambda item: (-int(item["count"]), str(item["group"])))
    return rows


REGIONS_EN = [
    {
        "label": "Shared core",
        "sign": "Honen and Shinran chunks are mutually close\nDaochuo and Shandao also overlap",
        "terms": "nembutsu / name\nbirth / Pure Land\nshinjin / three minds",
        "reading": "Shared Pure Land problem field",
        "color": (89, 138, 132),
    },
    {
        "label": "Honen divergence",
        "sign": "Relatively distant from non-Honen points\nconcentrated in selection argument sections",
        "terms": "right / miscellaneous practices\nthree grades and single-minded nembutsu\nPrimal Vow nembutsu / entrustment",
        "reading": "Argument for selecting nembutsu from other practices",
        "color": (43, 110, 164),
    },
    {
        "label": "Shinran divergence",
        "sign": "Relatively distant from non-Shinran points\nconcentrated in Shin and Keshindo fascicles",
        "terms": "Shin fascicle / Keshindo fascicle\nsin / salvation\nexpedient / transformed land",
        "reading": "Source-based architecture of Primal Vow, shinjin, realization, and lands",
        "color": (176, 74, 70),
    },
]

GROUP_COLORS = {
    "親鸞": (183, 76, 72),
    "法然": (43, 110, 164),
    "道綽": (112, 137, 74),
    "源信": (131, 94, 151),
    "曇鸞": (194, 128, 49),
    "天親": (92, 137, 153),
    "善導": (91, 149, 96),
    "龍樹": (130, 130, 130),
}


def draw_region_flow(draw: ImageDraw.ImageDraw, x: int, y: int, width: int) -> int:
    title_font = font(32)
    small_font = font(19)
    label_font = font(23)
    body_font = font(18)

    draw.text((x, y), "Shared Core and Divergence Zones", fill=(39, 36, 31), font=title_font)
    draw.text((x, y + 42), "Widths are schematic; they do not encode quantity.", fill=(103, 96, 86), font=small_font)

    y += 88
    col_x = [x, x + 300, x + 780, x + 1210]
    col_w = [230, 390, 350, width - 1210]
    headers = ["Region", "Computational sign", "Main terms / fascicles or chapters", "Reading"]
    for i, header in enumerate(headers):
        draw.text((col_x[i], y), header, fill=(79, 73, 64), font=small_font)
    y += 34

    row_h = 144
    for idx, region in enumerate(REGIONS_EN):
        row_y = y + idx * (row_h + 20)
        color = region["color"]
        draw.rounded_rectangle((col_x[0], row_y, col_x[0] + col_w[0], row_y + row_h), radius=16, fill=alpha(color, 230))
        draw_text_box(draw, (col_x[0] + 20, row_y + 48, col_x[0] + col_w[0] - 18, row_y + row_h), region["label"], (255, 255, 255), label_font)

        for col_index, key in enumerate(["sign", "terms", "reading"], start=1):
            bx0 = col_x[col_index]
            bx1 = bx0 + col_w[col_index]
            draw.rounded_rectangle((bx0, row_y, bx1, row_y + row_h), radius=14, fill=(255, 255, 255), outline=alpha(color, 145), width=2)
            draw_text_box(draw, (bx0 + 18, row_y + 18, bx1 - 16, row_y + row_h - 12), str(region[key]), (44, 40, 35), body_font)

        for left, right in [(0, 1), (1, 2), (2, 3)]:
            cy = row_y + row_h // 2
            x0 = col_x[left] + col_w[left] + 12
            x1 = col_x[right] - 16
            draw.line((x0, cy, x1, cy), fill=alpha(color, 170), width=8)
            draw.polygon([(x1, cy), (x1 - 18, cy - 13), (x1 - 18, cy + 13)], fill=alpha(color, 190))

    return y + len(REGIONS_EN) * (row_h + 20) + 24


def draw_bars(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    title: str,
    rows: list[dict[str, float | int | str]],
    target_total: int,
    width: int,
) -> None:
    title_font = font(27)
    label_font = font(18)
    small_font = font(17)
    max_count = max(int(row["count"]) for row in rows)
    bar_x = x + 132
    bar_w = width - 250
    row_h = 44

    draw.text((x, y), title, fill=(39, 36, 31), font=title_font)
    draw.text((x, y + 36), "Simple nearest non-self chunk counts.", fill=(103, 96, 86), font=small_font)
    y += 78

    for index, row in enumerate(rows):
        yy = y + index * row_h
        group = str(row["group"])
        count = int(row["count"])
        ratio = float(row["ratio"])
        color = GROUP_COLORS.get(group, (100, 100, 100))
        draw.text((x, yy + 8), AUTHOR_EN.get(group, group), fill=(44, 40, 35), font=label_font)
        draw.rounded_rectangle((bar_x, yy + 8, bar_x + bar_w, yy + 30), radius=8, fill=(235, 231, 223))
        filled = int(bar_w * count / max_count)
        draw.rounded_rectangle((bar_x, yy + 8, bar_x + filled, yy + 30), radius=8, fill=color)
        draw.text((bar_x + filled + 12, yy + 3), f"{count} ({ratio * 100:.1f}%)", fill=(44, 40, 35), font=small_font)

    draw.text((bar_x, y + len(rows) * row_h + 10), f"Target chunks: {target_total}", fill=(103, 96, 86), font=small_font)


def render_shared_core_bars() -> None:
    counts = read_nearest_counts()
    width, height = 1900, 1260
    image = Image.new("RGB", (width, height), (251, 250, 247))
    draw = ImageDraw.Draw(image, "RGBA")

    flow_bottom = draw_region_flow(draw, 76, 54, width - 152)
    draw.line((76, flow_bottom + 4, width - 76, flow_bottom + 4), fill=(216, 208, 194), width=2)
    bar_y = flow_bottom + 50
    panel_w = 820
    draw_bars(draw, 100, bar_y, "Honen chunks: nearest non-self", counts["法然"], 69, panel_w)
    draw_bars(draw, 980, bar_y, "Shinran chunks: nearest non-self", counts["親鸞"], 191, panel_w)
    image.save(OUT_DIR / "shared-core-protrusion-nearest-bars.png", quality=95)


def read_sequence_csv(path: Path, boundary_field: str) -> dict[str, Any]:
    chunks: dict[int, dict[str, Any]] = {}
    feature_order: dict[str, list[str]] = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["replacement_chars"]) != 0:
                raise ValueError(f"{path}: replacement character in chunk {row['chunk_index']}")
            chunk_index = int(row["chunk_index"])
            layer = row["layer"]
            feature = row["feature"]
            chunks.setdefault(
                chunk_index,
                {
                    "chunk_index": chunk_index,
                    "boundary": row[boundary_field],
                    "features": defaultdict(dict),
                },
            )
            chunks[chunk_index]["features"][layer][feature] = float(row["value"])
            if feature not in feature_order[layer]:
                feature_order[layer].append(feature)
    ordered_chunks = [chunks[index] for index in sorted(chunks)]
    return {"chunks": ordered_chunks, "feature_order": feature_order}


def matrix_for(chunks: list[dict[str, Any]], layer: str, features: list[str]) -> np.ndarray:
    matrix = np.zeros((len(features), len(chunks)), dtype=float)
    for col, chunk in enumerate(chunks):
        values = chunk["features"].get(layer, {})
        for row, feature in enumerate(features):
            matrix[row, col] = values.get(feature, 0.0)
    return matrix


def boundary_runs(chunks: list[dict[str, Any]], label_map: dict[str, str]) -> list[dict[str, Any]]:
    out = []
    current = None
    start = 0
    for index, chunk in enumerate(chunks):
        label = label_map.get(chunk["boundary"], chunk["boundary"])
        if current is None:
            current = label
            start = index
        elif label != current:
            out.append({"label": current, "start": start, "end": index - 1})
            current = label
            start = index
    if current is not None:
        out.append({"label": current, "start": start, "end": len(chunks) - 1})
    return out


def render_sequence_heatmap(
    *,
    csv_path: Path,
    output_path: Path,
    boundary_field: str,
    boundary_label_map: dict[str, str],
    title: str,
    subject: str,
    cell_w: int,
    label_w: int,
    right_w: int,
    boundary_note: str,
) -> None:
    data = read_sequence_csv(csv_path, boundary_field)
    chunks = data["chunks"]
    feature_order = data["feature_order"]

    semantic_rows = feature_order["semantic"]
    style_rows = feature_order["style"]
    marker_rows = feature_order["source_marker"]
    semantic_labels = [AUTHOR_EN.get(row, row) for row in semantic_rows]
    style_labels = [STYLE_EN.get(row, row) for row in style_rows]
    marker_labels = [MARKER_EN.get(row, row) for row in marker_rows]

    semantic_scaled = scale(matrix_for(chunks, "semantic", semantic_rows))
    style_scaled = scale(np.log1p(matrix_for(chunks, "style", style_rows)))
    marker_scaled = scale(np.log1p(matrix_for(chunks, "source_marker", marker_rows)))

    row_h = 17
    top_h = 110
    gap = 48
    panel_label_h = 44
    chart_w = cell_w * len(chunks)
    panel1_h = panel_label_h + row_h * len(semantic_rows)
    panel2_h = panel_label_h + row_h * len(style_rows)
    panel3_h = panel_label_h + row_h * len(marker_rows)
    width = label_w + chart_w + right_w
    height = top_h + panel1_h + gap + panel2_h + gap + panel3_h + 68

    image = Image.new("RGB", (width, height), (251, 250, 247))
    draw = ImageDraw.Draw(image)
    title_font = font(28)
    small_font = font(13)
    label_font = font(13)
    panel_font = font(17)

    draw.text((34, 28), title, fill=(37, 34, 29), font=title_font)
    draw.text(
        (34, 66),
        "Top=semantic layer (3072D cosine) / middle=lexical-thematic counts / bottom=source-marker counts.",
        fill=(104, 97, 88),
        font=small_font,
    )

    chart_x = label_w
    y = top_h
    boundaries = boundary_runs(chunks, boundary_label_map)

    def draw_boundaries(panel_y: int, panel_h: int) -> None:
        for boundary in boundaries:
            x0 = chart_x + boundary["start"] * cell_w
            x1 = chart_x + (boundary["end"] + 1) * cell_w
            draw.rectangle((x0, panel_y - 18, x1, panel_y - 4), fill=(234, 229, 219), outline=(219, 212, 200))
            if x1 - x0 > 34:
                label = fit_text(draw, boundary["label"], small_font, max(18, x1 - x0 - 5))
                draw.text((x0 + 3, panel_y - 18), label, fill=(82, 76, 68), font=small_font)
            draw.line((x0, panel_y - 2, x0, panel_y + panel_h), fill=(176, 167, 150), width=1)

    def draw_panel(
        panel_y: int,
        panel_title: str,
        labels: list[str],
        scaled: np.ndarray,
        color: tuple[int, int, int],
    ) -> int:
        draw.text((34, panel_y), panel_title, fill=(37, 34, 29), font=panel_font)
        heat_y = panel_y + panel_label_h
        panel_h = row_h * len(labels)
        draw.rectangle((chart_x, heat_y, chart_x + chart_w, heat_y + panel_h), fill=(255, 255, 255), outline=(221, 214, 202))
        draw_boundaries(heat_y, panel_h)
        for row_index, row_label in enumerate(labels):
            y0 = heat_y + row_index * row_h
            draw.text((34, y0 + 1), fit_text(draw, row_label, label_font, label_w - 48), fill=(37, 34, 29), font=label_font)
            for col in range(len(chunks)):
                x0 = chart_x + col * cell_w
                draw.rectangle(
                    (x0, y0, x0 + cell_w - 1, y0 + row_h - 1),
                    fill=color_for(float(scaled[row_index, col]), color),
                )
        for row_index in range(len(labels) + 1):
            yy = heat_y + row_index * row_h
            draw.line((chart_x, yy, chart_x + chart_w, yy), fill=(239, 235, 228), width=1)
        return heat_y + panel_h

    y = draw_panel(y, f"Semantic layer: max cosine from each {subject} chunk", semantic_labels, semantic_scaled, PANEL_COLORS["semantic"])
    y += gap
    y = draw_panel(y, "Lexical-thematic layer: word-group counts", style_labels, style_scaled, PANEL_COLORS["style"])
    y += gap
    draw_panel(y, "Source-marker layer: explicit markers", marker_labels, marker_scaled, PANEL_COLORS["marker"])

    legend_x = label_w + chart_w + 24
    legend_y = top_h
    draw.text((legend_x, legend_y), "Intensity", fill=(37, 34, 29), font=panel_font)
    for i, (label, color) in enumerate([("Semantic", PANEL_COLORS["semantic"]), ("Lexical", PANEL_COLORS["style"]), ("Source", PANEL_COLORS["marker"])]):
        yy = legend_y + 34 + i * 48
        draw.text((legend_x, yy), label, fill=(37, 34, 29), font=label_font)
        for step in range(40):
            value = step / 39
            draw.rectangle((legend_x + 74 + step * 2, yy + 2, legend_x + 75 + step * 2, yy + 17), fill=color_for(value, color))
    draw_text_box(
        draw,
        (legend_x, legend_y + 202, width - 12, legend_y + 238),
        boundary_note,
        (104, 97, 88),
        small_font,
        line_gap=2,
    )
    draw_text_box(
        draw,
        (legend_x, legend_y + 242, width - 12, legend_y + 276),
        f"X-axis={subject} chunk order",
        (104, 97, 88),
        small_font,
        line_gap=2,
    )

    image.save(output_path, quality=95)


def render_sequence_heatmaps() -> None:
    render_sequence_heatmap(
        csv_path=HONEN_SEQUENCE_CSV,
        output_path=OUT_DIR / "honen-three-layer-sequence-heatmap.png",
        boundary_field="section_label",
        boundary_label_map=HONEN_SECTION_EN,
        title="Honen Senchakushu: Three-Layer Chunk Sequence",
        subject="Honen",
        cell_w=11,
        label_w=300,
        right_w=254,
        boundary_note="Vertical lines=chapter/position boundaries",
    )
    render_sequence_heatmap(
        csv_path=SHINRAN_SEQUENCE_CSV,
        output_path=OUT_DIR / "shinran-three-layer-sequence-heatmap.png",
        boundary_field="volume_label",
        boundary_label_map=SHINRAN_VOLUME_EN,
        title="Shinran Kyogyoshinsho: Three-Layer Chunk Sequence",
        subject="Shinran",
        cell_w=7,
        label_w=300,
        right_w=260,
        boundary_note="Vertical lines=fascicle boundaries",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    render_map_figures()
    render_shared_core_bars()
    render_sequence_heatmaps()
    for path in sorted(OUT_DIR.glob("*.png")):
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
