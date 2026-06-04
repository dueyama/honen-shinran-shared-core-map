#!/usr/bin/env python3
"""Build a three-layer Shinran chunk-sequence heatmap.

Rows are semantic affinity, style/lexical groups, and source-marker groups.
Columns are Shinran safe chunks in reading order. This script reads local-only
chunk text to count features, but writes no raw or chunk text.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_readable_analysis_2026_06_04 import (  # noqa: E402
    SHINRAN_VOLUME_RANGES,
    STYLE_GROUPS,
    count_groups,
    load_embeddings,
    make_all_chunks,
    range_label,
    rounded,
    top_group,
)


MODEL = "text-embedding-3-large"
MAX_TOKENS = 700
OVERLAP = 100
OUT_JSON = ROOT / "data/outputs/shinran_three_layer_sequence_2026-06-04_text-embedding-3-large_700_100.json"
OUT_CSV = ROOT / "data/outputs/shinran_three_layer_sequence_2026-06-04.csv"
FIGURE_PATH = ROOT / "docs/figures/shinran-three-layer-sequence-heatmap.png"
DOC_PATH = ROOT / "docs/shinran-three-layer-sequence-2026-06-04.md"


SEMANTIC_ROWS = ["法然", "龍樹", "天親", "曇鸞", "道綽", "善導", "源信"]
STYLE_ROWS = list(STYLE_GROUPS.keys())
SOURCE_MARKER_ROWS = {
    "浄土三部経": ["大經", "大経", "無量壽經", "無量寿経", "觀經", "観経", "阿彌陀經", "阿弥陀経"],
    "涅槃経": ["涅槃經", "涅槃経"],
    "大集/日月蔵": ["大集經", "大集経", "日藏經", "日蔵経", "月藏經", "月蔵経"],
    "論/論註": ["往生論", "往生論註", "浄土論", "淨土論"],
    "安楽集": ["安樂集", "安楽集"],
    "観経疏/善導釈": ["觀經疏", "観経疏", "法事讃", "般舟讃", "往生禮讃", "往生礼讃"],
    "往生要集": ["往生要集"],
    "七高僧名": ["龍樹", "天親", "曇鸞", "道綽", "善導", "源信", "源空", "法然"],
    "引用導入": ["云", "曰", "言", "釋", "疏", "論曰", "經言", "問曰", "答曰", "私云"],
}

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

PANEL_COLORS = {
    "semantic": (47, 114, 178),
    "style": (54, 145, 92),
    "marker": (177, 114, 34),
}


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=0)
    return ImageFont.load_default()


def normalize(matrix: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(matrix, axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    return matrix / denom


def count_terms(text: str, terms: list[str]) -> int:
    return sum(text.count(term) for term in terms)


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


def make_layers() -> dict[str, Any]:
    chunks = make_all_chunks()
    embeddings = load_embeddings()
    matrix = normalize(np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float))
    indices_by_author: dict[str, list[int]] = defaultdict(list)
    for index, chunk in enumerate(chunks):
        indices_by_author[chunk.author].append(index)

    shinran_indices = indices_by_author["親鸞"]
    shinran_chunks = [chunks[index] for index in shinran_indices]
    shinran_vectors = matrix[np.array(shinran_indices, dtype=int)]

    semantic_scores = np.zeros((len(SEMANTIC_ROWS), len(shinran_chunks)), dtype=float)
    semantic_argmax: dict[str, list[int]] = {}
    for row_index, author in enumerate(SEMANTIC_ROWS):
        ref_indices = indices_by_author[author]
        ref_matrix = matrix[np.array(ref_indices, dtype=int)]
        sims = shinran_vectors @ ref_matrix.T
        semantic_scores[row_index, :] = sims.max(axis=1)
        semantic_argmax[author] = [chunks[ref_indices[int(local)]].chunk_index for local in sims.argmax(axis=1)]

    style_counts = np.zeros((len(STYLE_ROWS), len(shinran_chunks)), dtype=float)
    marker_counts = np.zeros((len(SOURCE_MARKER_ROWS), len(shinran_chunks)), dtype=float)
    chunk_rows = []
    marker_row_names = list(SOURCE_MARKER_ROWS.keys())

    for col, chunk in enumerate(shinran_chunks):
        style_hits = count_groups(chunk.text, STYLE_GROUPS)
        marker_hits = {label: count_terms(chunk.text, terms) for label, terms in SOURCE_MARKER_ROWS.items()}
        for row_index, label in enumerate(STYLE_ROWS):
            style_counts[row_index, col] = style_hits.get(label, 0)
        for row_index, label in enumerate(marker_row_names):
            marker_counts[row_index, col] = marker_hits.get(label, 0)
        best_semantic_idx = int(np.argmax(semantic_scores[:, col]))
        chunk_rows.append(
            {
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "volume_label": range_label(chunk.line_start, SHINRAN_VOLUME_RANGES, "未分類"),
                "text_sha256": embeddings[chunk.chunk_id]["text_sha256"],
                "replacement_chars": chunk.text.count("\ufffd"),
                "semantic_top_group": SEMANTIC_ROWS[best_semantic_idx],
                "semantic_top_score": rounded(float(semantic_scores[best_semantic_idx, col])),
                "style_top_group": top_group(style_hits),
                "style_hits": style_hits,
                "source_marker_top_group": top_group(marker_hits),
                "source_marker_hits": {k: v for k, v in marker_hits.items() if v},
            }
        )

    return {
        "shinran_chunks": shinran_chunks,
        "chunk_rows": chunk_rows,
        "semantic_scores": semantic_scores,
        "semantic_scaled": scale(semantic_scores),
        "style_counts": style_counts,
        "style_scaled": scale(np.log1p(style_counts)),
        "marker_counts": marker_counts,
        "marker_scaled": scale(np.log1p(marker_counts)),
        "marker_row_names": marker_row_names,
    }


def volume_boundaries(chunk_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    current = None
    start = 0
    for index, row in enumerate(chunk_rows):
        label = row["volume_label"]
        if current is None:
            current = label
            start = index
        elif label != current:
            out.append({"label": current, "start": start, "end": index - 1})
            current = label
            start = index
    if current is not None:
        out.append({"label": current, "start": start, "end": len(chunk_rows) - 1})
    return out


def draw_heatmap(layers: dict[str, Any]) -> None:
    chunk_rows = layers["chunk_rows"]
    marker_row_names = layers["marker_row_names"]
    cell_w = 7
    row_h = 17
    label_w = 208
    right_w = 180
    top_h = 104
    gap = 46
    panel_label_h = 42
    chart_w = cell_w * len(chunk_rows)
    panel1_h = panel_label_h + row_h * len(SEMANTIC_ROWS)
    panel2_h = panel_label_h + row_h * len(STYLE_ROWS)
    panel3_h = panel_label_h + row_h * len(marker_row_names)
    width = label_w + chart_w + right_w
    height = top_h + panel1_h + gap + panel2_h + gap + panel3_h + 64

    image = Image.new("RGB", (width, height), (251, 250, 247))
    draw = ImageDraw.Draw(image)
    title_font = font(28)
    small_font = font(13)
    label_font = font(14)
    panel_font = font(17)

    draw.text((34, 28), "親鸞『教行信証』三層chunk sequence", fill=(37, 34, 29), font=title_font)
    draw.text(
        (34, 64),
        "上=意味層(3072次元cosine) / 中=文体語彙層 / 下=典拠マーカー層。本文は含めない。",
        fill=(104, 97, 88),
        font=small_font,
    )

    chart_x = label_w
    y = top_h
    boundaries = volume_boundaries(chunk_rows)

    def draw_boundaries(panel_y: int, panel_h: int) -> None:
        for boundary in boundaries:
            x0 = chart_x + boundary["start"] * cell_w
            x1 = chart_x + (boundary["end"] + 1) * cell_w
            draw.rectangle((x0, panel_y - 18, x1, panel_y - 4), fill=(234, 229, 219), outline=(219, 212, 200))
            if x1 - x0 > 34:
                draw.text((x0 + 3, panel_y - 18), boundary["label"], fill=(82, 76, 68), font=small_font)
            draw.line((x0, panel_y - 2, x0, panel_y + panel_h), fill=(176, 167, 150), width=1)

    def draw_panel(
        panel_y: int,
        title: str,
        rows: list[str],
        scaled: np.ndarray,
        color: tuple[int, int, int],
    ) -> int:
        draw.text((34, panel_y), title, fill=(37, 34, 29), font=panel_font)
        heat_y = panel_y + panel_label_h
        panel_h = row_h * len(rows)
        draw.rectangle((chart_x, heat_y, chart_x + chart_w, heat_y + panel_h), fill=(255, 255, 255), outline=(221, 214, 202))
        draw_boundaries(heat_y, panel_h)
        for row_index, row_label in enumerate(rows):
            y0 = heat_y + row_index * row_h
            draw.text((34, y0 + 1), row_label, fill=(37, 34, 29), font=label_font)
            for col in range(len(chunk_rows)):
                x0 = chart_x + col * cell_w
                draw.rectangle(
                    (x0, y0, x0 + cell_w - 1, y0 + row_h - 1),
                    fill=color_for(float(scaled[row_index, col]), color),
                )
        for row_index in range(len(rows) + 1):
            yy = heat_y + row_index * row_h
            draw.line((chart_x, yy, chart_x + chart_w, yy), fill=(239, 235, 228), width=1)
        return heat_y + panel_h

    y = draw_panel(y, "意味層: 親鸞chunkから各文献群への最大cosine", SEMANTIC_ROWS, layers["semantic_scaled"], PANEL_COLORS["semantic"])
    y += gap
    y = draw_panel(y, "文体語彙層: 語群カウント", STYLE_ROWS, layers["style_scaled"], PANEL_COLORS["style"])
    y += gap
    y = draw_panel(y, "典拠マーカー層: 明示マーカー", marker_row_names, layers["marker_scaled"], PANEL_COLORS["marker"])

    legend_x = label_w + chart_w + 24
    legend_y = top_h
    draw.text((legend_x, legend_y), "濃度", fill=(37, 34, 29), font=panel_font)
    for i, (label, color) in enumerate([("意味", PANEL_COLORS["semantic"]), ("語彙", PANEL_COLORS["style"]), ("典拠", PANEL_COLORS["marker"])]):
        yy = legend_y + 34 + i * 48
        draw.text((legend_x, yy), label, fill=(37, 34, 29), font=label_font)
        for step in range(40):
            value = step / 39
            draw.rectangle((legend_x + 52 + step * 2, yy + 2, legend_x + 53 + step * 2, yy + 17), fill=color_for(value, color))
    draw.text((legend_x, legend_y + 202), "縦線=巻境界", fill=(104, 97, 88), font=small_font)
    draw.text((legend_x, legend_y + 224), "横軸=親鸞chunk順", fill=(104, 97, 88), font=small_font)

    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(FIGURE_PATH, quality=95)


def count_by(rows: list[dict[str, Any]], *keys: str) -> list[dict[str, Any]]:
    counter: Counter[tuple[Any, ...]] = Counter(tuple(row.get(key, "") for key in keys) for row in rows)
    out = []
    for values, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        record = {key: value for key, value in zip(keys, values)}
        record["chunk_count"] = count
        out.append(record)
    return out


def write_outputs(layers: dict[str, Any]) -> None:
    chunk_rows = layers["chunk_rows"]
    marker_row_names = layers["marker_row_names"]
    boundaries = volume_boundaries(chunk_rows)
    semantic_scores = layers["semantic_scores"]
    style_counts = layers["style_counts"]
    marker_counts = layers["marker_counts"]

    rows_out = []
    for col, row in enumerate(chunk_rows):
        for row_index, label in enumerate(SEMANTIC_ROWS):
            rows_out.append(
                {
                    "chunk_index": row["chunk_index"],
                    "volume_label": row["volume_label"],
                    "line_start": row["line_start"],
                    "line_end": row["line_end"],
                    "layer": "semantic",
                    "feature": label,
                    "value": rounded(float(semantic_scores[row_index, col])),
                    "text_sha256": row["text_sha256"],
                    "replacement_chars": row["replacement_chars"],
                }
            )
        for row_index, label in enumerate(STYLE_ROWS):
            rows_out.append(
                {
                    "chunk_index": row["chunk_index"],
                    "volume_label": row["volume_label"],
                    "line_start": row["line_start"],
                    "line_end": row["line_end"],
                    "layer": "style",
                    "feature": label,
                    "value": int(style_counts[row_index, col]),
                    "text_sha256": row["text_sha256"],
                    "replacement_chars": row["replacement_chars"],
                }
            )
        for row_index, label in enumerate(marker_row_names):
            rows_out.append(
                {
                    "chunk_index": row["chunk_index"],
                    "volume_label": row["volume_label"],
                    "line_start": row["line_start"],
                    "line_end": row["line_end"],
                    "layer": "source_marker",
                    "feature": label,
                    "value": int(marker_counts[row_index, col]),
                    "text_sha256": row["text_sha256"],
                    "replacement_chars": row["replacement_chars"],
                }
            )

    summary = {
        "title": "Shinran Kyogyoshinsho three-layer chunk sequence",
        "method": {
            "target": "Shinran T2646 chunks only, in chunk_index order",
            "embedding_model": MODEL,
            "embedding_dimension": 3072,
            "chunking": f"Unicode-safe {MAX_TOKENS}-token chunks, {OVERLAP}-token overlap",
            "semantic_layer": "max cosine from each Shinran chunk to chunks in each reference author group, computed in 3072D",
            "style_layer": "dictionary counts for style/lexical groups",
            "source_marker_layer": "dictionary counts for explicit source markers",
            "raw_text_policy": "no raw/chunk text is written",
        },
        "figure": str(FIGURE_PATH.relative_to(ROOT)),
        "volume_boundaries": boundaries,
        "chunk_count": len(chunk_rows),
        "row_counts": {
            "semantic": len(SEMANTIC_ROWS),
            "style": len(STYLE_ROWS),
            "source_marker": len(marker_row_names),
        },
        "summaries": {
            "semantic_top_by_volume": count_by(chunk_rows, "volume_label", "semantic_top_group"),
            "style_top_by_volume": count_by(chunk_rows, "volume_label", "style_top_group"),
            "source_marker_top_by_volume": count_by(chunk_rows, "volume_label", "source_marker_top_group"),
        },
        "chunks": [
            {
                "chunk_id": row["chunk_id"],
                "chunk_index": row["chunk_index"],
                "line_start": row["line_start"],
                "line_end": row["line_end"],
                "volume_label": row["volume_label"],
                "text_sha256": row["text_sha256"],
                "replacement_chars": row["replacement_chars"],
                "semantic_top_group": row["semantic_top_group"],
                "semantic_top_score": row["semantic_top_score"],
                "style_top_group": row["style_top_group"],
                "style_hits": row["style_hits"],
                "source_marker_top_group": row["source_marker_top_group"],
                "source_marker_hits": row["source_marker_hits"],
            }
            for row in chunk_rows
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        fields = ["chunk_index", "volume_label", "line_start", "line_end", "layer", "feature", "value", "text_sha256", "replacement_chars"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows_out)
    DOC_PATH.write_text(render_doc(summary), encoding="utf-8")


def md_table(rows: list[dict[str, Any]], fields: list[tuple[str, str]], limit: int = 12) -> list[str]:
    selected = rows[:limit]
    lines = [
        "| " + " | ".join(label for label, _ in fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in selected:
        lines.append("| " + " | ".join(str(row.get(key, "")).replace("|", "/") for _, key in fields) + " |")
    return lines


def render_doc(summary: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Shinran Three-Layer Sequence 2026-06-04",
        "",
        "親鸞『教行信証』SAT safe chunks を横軸にし、意味層・文体語彙層・典拠マーカー層を3段ヒートマップにした。",
        "",
        "## 読み方",
        "",
        "- 意味層は、各親鸞 chunk から法然・高僧各群への 3072 次元 cosine の最大値。",
        "- 文体語彙層は、辞書ベース語群のカウント。",
        "- 典拠マーカー層は、経名・論釈名・高僧名・引用導入句などの明示マーカー。",
        "- どの層も本文は出力しない。line range、hash、スコア、カウントだけを出す。",
        "",
        "## 出力図",
        "",
        f"![親鸞三層ヒートマップ](/Users/daishin/Documents/Codex/Okyou2/{summary['figure']})",
        "",
        "## 意味層: 巻別トップ近傍",
        "",
        *md_table(summary["summaries"]["semantic_top_by_volume"], [("巻", "volume_label"), ("top", "semantic_top_group"), ("chunks", "chunk_count")]),
        "",
        "## 文体語彙層: 巻別トップ語群",
        "",
        *md_table(summary["summaries"]["style_top_by_volume"], [("巻", "volume_label"), ("top", "style_top_group"), ("chunks", "chunk_count")]),
        "",
        "## 典拠マーカー層: 巻別トップマーカー",
        "",
        *md_table(summary["summaries"]["source_marker_top_by_volume"], [("巻", "volume_label"), ("top", "source_marker_top_group"), ("chunks", "chunk_count")]),
        "",
        "## 注意",
        "",
        "- 意味層の最大 cosine は典拠関係の証明ではない。",
        "- 文体語彙層と典拠マーカー層は辞書ベースの最小版であり、引用文の立場と親鸞自身の立場をまだ分けていない。",
        "- この図は、三層が一致する場所とズレる場所を探すための作業図である。",
        "",
        "## データ",
        "",
        f"- `{OUT_JSON.relative_to(ROOT)}`",
        f"- `{OUT_CSV.relative_to(ROOT)}`",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    layers = make_layers()
    draw_heatmap(layers)
    write_outputs(layers)
    print(f"wrote {FIGURE_PATH.relative_to(ROOT)}")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"wrote {DOC_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
