#!/usr/bin/env python3
"""Rank Honen/Shinran chunks by high-dimensional isolation.

This uses only existing text-free protrusion tables.  The score is
``1 - nearest_nonself_cosine`` in the original embedding space, so it is a
PCA-independent companion check to the 2D protrusion score.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HONEN_IN = ROOT / "data/outputs/honen_protrusion_table_2026-06-04.csv"
SHINRAN_IN = ROOT / "data/outputs/shinran_protrusion_table_2026-06-04.csv"
OUT_CSV = ROOT / "data/outputs/high_dim_isolation_ranking_2026-06-04.csv"
OUT_MD = ROOT / "docs/high-dim-isolation-2026-06-04.md"

TOP_N = 20


def read_rows(path: Path, target_author: str) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["target_author"] = target_author
        cosine = float(row["nearest_nonself_cosine"])
        row["high_dim_isolation"] = f"{1.0 - cosine:.6f}"
    return rows


def make_public_row(rank: int, row: dict[str, str]) -> dict[str, str | int]:
    return {
        "target_author": row["target_author"],
        "rank": rank,
        "chunk_index": row["chunk_index"],
        "location_label": row.get("section_label") or row.get("volume_label") or "",
        "zone_label": row.get("semantic_role") or row.get("protrusion_zone_label") or row.get("affinity_zone") or "",
        "line_start": row["line_start"],
        "line_end": row["line_end"],
        "nearest_author": row["nearest_nonself_author"],
        "nearest_work": row["nearest_nonself_work"],
        "nearest_chunk_index": row["nearest_nonself_chunk_index"],
        "nearest_cosine": row["nearest_nonself_cosine"],
        "high_dim_isolation": row["high_dim_isolation"],
        "protrusion_score": row["protrusion_score"],
        "style_top_group": row["style_top_group"],
        "source_marker_top_group": row["source_marker_top_group"],
        "replacement_chars": row["replacement_chars"],
    }


def rank_rows(rows: list[dict[str, str]]) -> list[dict[str, str | int]]:
    ranked = sorted(rows, key=lambda row: float(row["high_dim_isolation"]), reverse=True)
    return [make_public_row(index + 1, row) for index, row in enumerate(ranked[:TOP_N])]


def count_top(rows: list[dict[str, str | int]], key: str) -> list[tuple[str, int]]:
    counter = Counter(str(row.get(key, "")) for row in rows)
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def write_csv(rows: list[dict[str, str | int]]) -> None:
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
        "protrusion_score",
        "style_top_group",
        "source_marker_top_group",
        "replacement_chars",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[tuple[str, int]], left: str) -> list[str]:
    lines = [f"| {left} | chunks |", "|---|---:|"]
    lines.extend(f"| {label} | {count} |" for label, count in rows)
    return lines


def write_markdown(honen_top: list[dict[str, str | int]], shinran_top: list[dict[str, str | int]]) -> None:
    lines = [
        "# High-Dimensional Isolation Check (2026-06-04)",
        "",
        "- 入力: 既存の本文なし protrusion CSV。",
        "- 指標: `high_dim_isolation = 1 - nearest_nonself_cosine`。",
        "- 目的: 2D PCA 距離を含む protrusion score とは別に、高次元 cosine だけで孤立候補を見る。",
        "- 出力CSVにも本文、本文preview、embedding vectorは含めない。",
        "",
        "## 法然 top 20 の要約",
        "",
        *markdown_table(count_top(honen_top, "location_label"), "章/位置"),
        "",
        *markdown_table(count_top(honen_top, "style_top_group"), "語群"),
        "",
        "## 親鸞 top 20 の要約",
        "",
        *markdown_table(count_top(shinran_top, "location_label"), "巻"),
        "",
        *markdown_table(count_top(shinran_top, "zone_label"), "内容ゾーン"),
        "",
        "## Protrusion score との関係",
        "",
        "- 法然側は、2D protrusion と同じく `付属・証誠・選択総結` と `三輩・一向専念` が目立つが、",
        "  高次元だけでは `三心・信心` も上位に入りやすい。",
        "- 親鸞側は、2D protrusion と同じく `信巻` と `化身土巻` が中心で、信/三心・罪救済、",
        "  方便・真仮整理、外教批判などに広がる。",
        "- したがって、共有核からのはみ出しを読む大枠は変わらない。ただし、2D PCA上の距離を含む",
        "  protrusion score は図上の孤立も拾うため、個別順位は高次元孤立度ランキングと一致しない。",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    honen_top = rank_rows(read_rows(HONEN_IN, "法然"))
    shinran_top = rank_rows(read_rows(SHINRAN_IN, "親鸞"))
    write_csv([*honen_top, *shinran_top])
    write_markdown(honen_top, shinran_top)
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
