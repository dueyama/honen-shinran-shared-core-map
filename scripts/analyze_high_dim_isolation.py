#!/usr/bin/env python3
"""Rank Honen/Shinran chunks by high-dimensional isolation.

The score is ``1 - nearest_nonself_cosine`` in the original embedding space, so
it is a PCA-independent companion check to the 2D protrusion score. This script
reads local-only chunk text for dictionary counts, but writes no raw text or
embedding vectors.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_readable_analysis_2026_06_04 import (  # noqa: E402
    HONEN_SECTION_RANGES,
    SHINRAN_VOLUME_RANGES,
    SOURCE_MARKERS,
    STYLE_GROUPS,
    count_groups,
    load_embeddings,
    make_all_chunks,
    range_label,
    rounded,
    top_group,
)


OUT_CSV = ROOT / "data/outputs/high_dim_isolation_ranking_2026-06-04.csv"
OUT_MD = ROOT / "docs/high-dim-isolation-2026-06-04.md"
HONEN_PROTRUSION_IN = ROOT / "data/outputs/honen_protrusion_table_2026-06-04.csv"
SHINRAN_PROTRUSION_IN = ROOT / "data/outputs/shinran_protrusion_table_2026-06-04.csv"

TOP_N = 24
TARGET_AUTHORS = ["法然", "親鸞"]


def normalize(matrix: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(matrix, axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    return matrix / denom


def read_protrusion_indices(path: Path) -> set[int]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {int(row["chunk_index"]) for row in csv.DictReader(handle)}


def target_label(author: str, line_start: str) -> str:
    if author == "法然":
        return range_label(line_start, HONEN_SECTION_RANGES, "未分類")
    if author == "親鸞":
        return range_label(line_start, SHINRAN_VOLUME_RANGES, "未分類")
    return ""


def zone_label(author: str, location: str, style_top: str, marker_hits: dict[str, int]) -> str:
    if author == "法然":
        return "doctrinal_argument_candidate"
    if author == "親鸞":
        if location == "信巻" and style_top in {"信・三心", "罪・救済", "願・回向"}:
            return "信巻: 信/三心・罪救済"
        if location == "化身土巻" and style_top in {"方便・化身土", "廃立・取捨", "正雑・諸行"}:
            return "化身土巻: 方便・真仮整理"
        if location == "化身土巻" and marker_hits.get("経名"):
            return "化身土巻: 経典・護法秩序候補"
        if marker_hits.get("祖師名"):
            return f"{location}: 祖師引用密度"
        if marker_hits.get("経名"):
            return f"{location}: 経典引用密度"
        return f"{location}: 高次元孤立候補"
    return ""


def make_rows() -> list[dict[str, Any]]:
    chunks = make_all_chunks()
    embeddings = load_embeddings()
    missing = [chunk.chunk_id for chunk in chunks if chunk.chunk_id not in embeddings]
    if missing:
        raise RuntimeError(f"missing embeddings for {len(missing)} chunks: {missing[:3]}")

    matrix = normalize(np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float))
    rows: list[dict[str, Any]] = []

    for index, chunk in enumerate(chunks):
        if chunk.author not in TARGET_AUTHORS:
            continue
        candidate_indices = [i for i, other in enumerate(chunks) if other.author != chunk.author]
        sims = matrix[np.array(candidate_indices, dtype=int)] @ matrix[index]
        local = int(np.argmax(sims))
        nearest_index = candidate_indices[local]
        nearest = chunks[nearest_index]
        nearest_cosine = float(sims[local])
        style_hits = count_groups(chunk.text, STYLE_GROUPS)
        marker_hits = count_groups(chunk.text, SOURCE_MARKERS)
        style_top = top_group(style_hits)
        location = target_label(chunk.author, chunk.line_start)
        rows.append(
            {
                "target_author": chunk.author,
                "chunk_index": chunk.chunk_index,
                "location_label": location,
                "zone_label": zone_label(chunk.author, location, style_top, marker_hits),
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "nearest_author": nearest.author,
                "nearest_work": nearest.work,
                "nearest_chunk_index": nearest.chunk_index,
                "nearest_cosine": rounded(nearest_cosine),
                "high_dim_isolation": rounded(1.0 - nearest_cosine),
                "style_top_group": style_top,
                "source_marker_top_group": top_group(marker_hits),
                "replacement_chars": chunk.text.count("\ufffd"),
            }
        )

    ranked: list[dict[str, Any]] = []
    for author in TARGET_AUTHORS:
        author_rows = [row for row in rows if row["target_author"] == author]
        author_rows.sort(key=lambda row: float(row["high_dim_isolation"]), reverse=True)
        for rank, row in enumerate(author_rows[:TOP_N], start=1):
            ranked.append({"rank": rank, **row})
    return ranked


def count_top(rows: list[dict[str, Any]], key: str) -> list[tuple[str, int]]:
    counter = Counter(str(row.get(key, "")) for row in rows)
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def overlap_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    protrusion_sets = {
        "法然": read_protrusion_indices(HONEN_PROTRUSION_IN),
        "親鸞": read_protrusion_indices(SHINRAN_PROTRUSION_IN),
    }
    summary: dict[str, dict[str, Any]] = {}
    for author in TARGET_AUTHORS:
        high_dim = {int(row["chunk_index"]) for row in rows if row["target_author"] == author}
        protrusion = protrusion_sets[author]
        intersection = high_dim & protrusion
        union = high_dim | protrusion
        summary[author] = {
            "protrusion_top_n": len(protrusion),
            "high_dim_top_n": len(high_dim),
            "overlap": len(intersection),
            "jaccard": rounded(len(intersection) / len(union)) if union else 0,
            "intersection": sorted(intersection),
        }
    return summary


def markdown_table(rows: list[tuple[str, int]], left: str) -> list[str]:
    lines = [f"| {left} | chunks |", "|---|---:|"]
    lines.extend(f"| {label} | {count} |" for label, count in rows)
    return lines


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "target_author",
        "rank",
        "chunk_index",
        "location_label",
        "zone_label",
        "line_start",
        "line_end",
        "nearest_author",
        "nearest_work",
        "nearest_chunk_index",
        "nearest_cosine",
        "high_dim_isolation",
        "style_top_group",
        "source_marker_top_group",
        "replacement_chars",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]]) -> None:
    honen_top = [row for row in rows if row["target_author"] == "法然"]
    shinran_top = [row for row in rows if row["target_author"] == "親鸞"]
    overlaps = overlap_summary(rows)
    lines = [
        "# High-Dimensional Isolation Check (2026-06-04)",
        "",
        "- 入力: 既存の SAT safe chunk と embedding cache。",
        "- 指標: `high_dim_isolation = 1 - nearest_nonself_cosine`。",
        "- 目的: 2D PCA 距離を含む protrusion score とは別に、高次元 cosine だけで孤立候補を見る。",
        "- 出力CSVにも本文、本文preview、embedding vectorは含めない。",
        "",
        "## Protrusion top 24 との重なり",
        "",
        "| 対象 | protrusion top | high-dim top | overlap | Jaccard |",
        "|---|---:|---:|---:|---:|",
        *[
            f"| {author} | {item['protrusion_top_n']} | {item['high_dim_top_n']} | {item['overlap']} | {item['jaccard']} |"
            for author, item in overlaps.items()
        ],
        "",
        "## 法然 top 24 の要約",
        "",
        *markdown_table(count_top(honen_top, "location_label"), "章/位置"),
        "",
        *markdown_table(count_top(honen_top, "style_top_group"), "語群"),
        "",
        "## 親鸞 top 24 の要約",
        "",
        *markdown_table(count_top(shinran_top, "location_label"), "巻"),
        "",
        *markdown_table(count_top(shinran_top, "zone_label"), "内容ゾーン"),
        "",
        "## Protrusion score との関係",
        "",
        "- 高次元孤立度だけで見ても、法然側は `付属・証誠・選択総結`、`正雑二行`、`本願念仏`、",
        "  `三輩・一向専念` が中心に残る。",
        "- 親鸞側は `信巻` と `化身土巻` が中心で、信/三心・罪救済、方便・真仮整理、",
        "  外教批判、護法秩序候補などに広がる。",
        "- したがって、共有核からのはみ出しを読む大枠は2D PCA距離だけに依存していない。",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = make_rows()
    write_csv(rows)
    write_markdown(rows)
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
