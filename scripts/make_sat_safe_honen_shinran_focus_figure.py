#!/usr/bin/env python3
"""Render the focus-only Honen/Shinran SAT-safe map figure."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from sat_safe_map_renderer import (
    FOCUS_AUTHORS,
    MAX_TOKENS,
    MODEL,
    OVERLAP,
    render_sat_safe_map_png,
    rounded,
)


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json"
FIGURE_PATH = ROOT / "docs/figures/sat-safe-honen-shinran-focus-map.png"
META_PATH = ROOT / "data/outputs/sat_safe_honen_shinran_focus_map_text-embedding-3-large_700_100.json"


def load_focus_records() -> list[dict[str, Any]]:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    records = [row for row in data["chunks"] if row["author"] in set(FOCUS_AUTHORS)]
    if not records:
        raise RuntimeError("no Honen/Shinran records found")
    return records


def write_meta(records: list[dict[str, Any]], render_stats: dict[str, Any]) -> None:
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
        if author in render_stats:
            stats[author]["rendered_ellipse"] = render_stats[author]
    output = {
        "title": "SAT safe Honen/Shinran focus map",
        "input_map": str(MAP_PATH.relative_to(ROOT)),
        "figure": str(FIGURE_PATH.relative_to(ROOT)),
        "method": {
            "coordinate_basis": "same PCA coordinates as the SAT safe high-priest anchor map",
            "display_extent": "fitted to Honen/Shinran chunks; identical renderer to the high-priest anchor paper figure",
            "renderer": "scripts/sat_safe_map_renderer.py",
            "raw_text_policy": "no raw/chunk text is read from the input metadata or written to this output",
        },
        "figure_rendering": render_stats.get("_figure", {}),
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
    render_stats = render_sat_safe_map_png(
        records,
        FIGURE_PATH,
        title="SAT漢文 Unicode-safeチャンク地図: 法然・親鸞",
        subtitle=f"PCA fit=法然/親鸞。model={MODEL}, {MAX_TOKENS} token / overlap {OVERLAP}。",
        legend_order=list(FOCUS_AUTHORS),
        show_anchor_note=False,
    )
    write_meta(records, render_stats)
    print(f"wrote {FIGURE_PATH.relative_to(ROOT)}")
    print(f"wrote {META_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
