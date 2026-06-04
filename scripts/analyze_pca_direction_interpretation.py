#!/usr/bin/env python3
"""Summarize rough semantic directions in the SAT-safe 2D PCA map.

PCA axes do not have intrinsic doctrinal labels. This script labels directions
post hoc by aggregating chunks near each edge of the displayed Honen/Shinran
focus map. It reads local-only chunk text to count features, but writes no raw
or chunk text.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_honen_distinctive_zones import top_cjk_terms  # noqa: E402
from build_readable_analysis_2026_06_04 import (  # noqa: E402
    HONEN_SECTION_RANGES,
    MAP_PATH,
    SHINRAN_VOLUME_RANGES,
    SOURCE_MARKERS,
    STYLE_GROUPS,
    count_groups,
    make_all_chunks,
    range_label,
    rounded,
    top_group,
)


OUT_JSON = ROOT / "data/outputs/pca_direction_interpretation_2026-06-04_text-embedding-3-large_700_100.json"
OUT_CSV = ROOT / "data/outputs/pca_direction_representative_chunks_2026-06-04.csv"
DOC_PATH = ROOT / "docs/pca-direction-interpretation-2026-06-04.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def chunk_label(row: dict[str, Any]) -> str:
    author = row["author"]
    line_start = row.get("line_start", "")
    if author == "法然":
        return range_label(line_start, HONEN_SECTION_RANGES, "未分類")
    if author == "親鸞":
        return range_label(line_start, SHINRAN_VOLUME_RANGES, "未分類")
    return f"高僧:{author}"


def feature_record(map_row: dict[str, Any], chunk: Any) -> dict[str, Any]:
    style_hits = count_groups(chunk.text, STYLE_GROUPS)
    marker_hits = count_groups(chunk.text, SOURCE_MARKERS)
    return {
        "chunk_id": chunk.chunk_id,
        "author": chunk.author,
        "work": chunk.work,
        "role": map_row.get("role", ""),
        "chunk_index": chunk.chunk_index,
        "line_start": chunk.line_start,
        "line_end": chunk.line_end,
        "label": chunk_label(map_row),
        "x": float(map_row["x"]),
        "y": float(map_row["y"]),
        "text_sha256": map_row.get("text_sha256"),
        "replacement_chars": chunk.text.count("\ufffd"),
        "style_top_group": top_group(style_hits),
        "style_hits": style_hits,
        "source_marker_top_group": top_group(marker_hits),
        "source_marker_hits": marker_hits,
        "top_terms": top_cjk_terms(chunk.text, limit=8),
    }


def count_values(rows: list[dict[str, Any]], key: str, limit: int = 12) -> list[dict[str, Any]]:
    counts = Counter(row.get(key, "") for row in rows)
    return [
        {key: value, "chunk_count": count}
        for value, count in counts.most_common(limit)
        if value != ""
    ]


def aggregate_terms(rows: list[dict[str, Any]], limit: int = 16) -> list[list[Any]]:
    counts: Counter[str] = Counter()
    for row in rows:
        for term, count in row["top_terms"]:
            counts[term] += count
    return [[term, count] for term, count in counts.most_common(limit)]


def summarize_direction(
    name: str,
    axis_label: str,
    rows: list[dict[str, Any]],
    sort_key: str,
    reverse: bool,
    threshold: float,
) -> dict[str, Any]:
    selected = [row for row in rows if row[sort_key] >= threshold] if reverse else [row for row in rows if row[sort_key] <= threshold]
    selected = sorted(selected, key=lambda row: row[sort_key], reverse=reverse)
    representatives = [
        {
            "chunk_id": row["chunk_id"],
            "author": row["author"],
            "work": row["work"],
            "chunk_index": row["chunk_index"],
            "label": row["label"],
            "line_start": row["line_start"],
            "line_end": row["line_end"],
            "x": rounded(row["x"]),
            "y": rounded(row["y"]),
            "style_top_group": row["style_top_group"],
            "source_marker_top_group": row["source_marker_top_group"],
            "top_terms": row["top_terms"],
            "text_sha256": row["text_sha256"],
            "replacement_chars": row["replacement_chars"],
        }
        for row in selected[:10]
    ]
    return {
        "name": name,
        "axis_label": axis_label,
        "selection": f"{sort_key} {'>=' if reverse else '<='} {rounded(threshold)}",
        "chunk_count": len(selected),
        "author_counts": count_values(selected, "author"),
        "label_counts": count_values(selected, "label"),
        "style_counts": count_values(selected, "style_top_group"),
        "source_marker_counts": count_values(selected, "source_marker_top_group"),
        "top_terms": aggregate_terms(selected),
        "representative_chunks": representatives,
    }


def write_csv(path: Path, summaries: list[dict[str, Any]]) -> None:
    fields = [
        "direction",
        "axis_label",
        "chunk_id",
        "chunk_index",
        "author",
        "work",
        "label",
        "line_start",
        "line_end",
        "x",
        "y",
        "style_top_group",
        "source_marker_top_group",
        "top_terms",
        "text_sha256",
        "replacement_chars",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for summary in summaries:
            for row in summary["representative_chunks"]:
                record = {
                    "direction": summary["name"],
                    "axis_label": summary["axis_label"],
                    **row,
                }
                record["top_terms"] = json.dumps(record["top_terms"], ensure_ascii=False, separators=(",", ":"))
                writer.writerow(record)


def md_table(rows: list[dict[str, Any]], fields: list[tuple[str, str]], limit: int | None = None) -> list[str]:
    selected = rows[:limit] if limit else rows
    lines = [
        "| " + " | ".join(label for label, _ in fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in selected:
        values = []
        for _, key in fields:
            value = row.get(key, "")
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            values.append(str(value).replace("|", "/"))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def render_doc(output: dict[str, Any]) -> str:
    lines: list[str] = [
        "# PCA Direction Interpretation 2026-06-04",
        "",
        "SAT 漢文・Unicode-safe 700 token chunk・`text-embedding-3-large` の法然/親鸞 2D PCA 図について、端にある chunk 群を本文なしで集計した。",
        "",
        "## 読み方",
        "",
        "- PCA 軸には自動的な教義ラベルはない。軸の符号も再計算で反転しうる。",
        "- ここでの方向名は、この PCA fit における相対的な後付けラベルである。",
        "- 各方向は、法然/親鸞 focus chunks の座標について、15%/85% 分位の外側を集計した。",
        "- 本文は出力していない。line range、hash、語群、典拠マーカー、上位語のみを使う。",
        "",
        "## 概要",
        "",
        "- 右方向（PC1+）は親鸞のみで、信巻・化身土巻を中心に、罪救済、廃立/取捨、護持・天王・涅槃などが出やすい。",
        "- 左方向（PC1-）は法然が相対的に多く、正雑二行、一向専念、三心、往生、選択、雑行などの共有核・選択論証が目立つ。",
        "- 上方向（PC2+）は親鸞の行巻・真仏土巻が多く、阿弥陀、光明、名号、願/回向、往生/浄土の方向として読める。",
        "- 下方向（PC2-）は親鸞の信巻・化身土巻が多く、信/三心、罪救済、正雑、方便/化身土、外教批判側の広がりが出る。",
        "",
    ]
    for summary in output["direction_summaries"]:
        lines.extend(
            [
                f"## {summary['name']}",
                "",
                f"- selection: `{summary['selection']}`",
                f"- chunks: `{summary['chunk_count']}`",
                "",
                "author:",
                "",
                *md_table(summary["author_counts"], [("author", "author"), ("chunks", "chunk_count")]),
                "",
                "label:",
                "",
                *md_table(summary["label_counts"], [("label", "label"), ("chunks", "chunk_count")], limit=8),
                "",
                "style:",
                "",
                *md_table(summary["style_counts"], [("style", "style_top_group"), ("chunks", "chunk_count")], limit=8),
                "",
                "top terms:",
                "",
                json.dumps(summary["top_terms"][:12], ensure_ascii=False),
                "",
                "representatives:",
                "",
                *md_table(
                    summary["representative_chunks"],
                    [
                        ("idx", "chunk_index"),
                        ("author", "author"),
                        ("label", "label"),
                        ("line", "line_start"),
                        ("style", "style_top_group"),
                        ("terms", "top_terms"),
                    ],
                    limit=6,
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## 出力",
            "",
            f"- `{OUT_JSON.relative_to(ROOT)}`",
            f"- `{OUT_CSV.relative_to(ROOT)}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    chunks = {chunk.chunk_id: chunk for chunk in make_all_chunks()}
    map_rows = load_json(MAP_PATH)["chunks"]
    records = [feature_record(row, chunks[row["chunk_id"]]) for row in map_rows if row["author"] in {"法然", "親鸞"}]
    xs = np.array([row["x"] for row in records], dtype=float)
    ys = np.array([row["y"] for row in records], dtype=float)
    summaries = [
        summarize_direction("右方向 / PC1+", "x high", records, "x", True, float(np.quantile(xs, 0.85))),
        summarize_direction("左方向 / PC1-", "x low", records, "x", False, float(np.quantile(xs, 0.15))),
        summarize_direction("上方向 / PC2+", "y high", records, "y", True, float(np.quantile(ys, 0.85))),
        summarize_direction("下方向 / PC2-", "y low", records, "y", False, float(np.quantile(ys, 0.15))),
    ]
    output = {
        "title": "PCA direction interpretation for SAT safe Honen/Shinran focus map",
        "method": {
            "basis": "SAT kanbun, Unicode-safe 700-token chunks, 100-token overlap, text-embedding-3-large",
            "input_map": str(MAP_PATH.relative_to(ROOT)),
            "selection_policy": "focus chunks only; summarize records outside 15th/85th coordinate percentiles",
            "interpretation_policy": "post-hoc descriptive labels only; PCA axes have no intrinsic doctrinal labels",
            "raw_text_policy": "no raw/chunk text is written",
        },
        "direction_summaries": summaries,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(OUT_CSV, summaries)
    DOC_PATH.write_text(render_doc(output), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"wrote {DOC_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
