#!/usr/bin/env python3
"""Check nearest-neighbor counts under capped reference-group sampling.

This uses existing local embedding caches only. It writes summary statistics,
not raw text or embedding vectors.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_readable_analysis_2026_06_04 import load_embeddings, make_all_chunks, rounded  # noqa: E402


MODEL = "text-embedding-3-large"
MAX_TOKENS = 700
OVERLAP = 100
ITERATIONS = 1000
SAMPLE_CAP = 20
SEED = 20260604

OUT_JSON = ROOT / "data/outputs/nearest_neighbor_subsampling_2026-06-04_text-embedding-3-large_700_100.json"
OUT_CSV = ROOT / "data/outputs/nearest_neighbor_subsampling_2026-06-04_text-embedding-3-large_700_100.csv"
OUT_MD = ROOT / "docs/nearest-neighbor-subsampling-2026-06-04.md"


TARGET_AUTHORS = ["法然", "親鸞"]


def normalize(matrix: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(matrix, axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    return matrix / denom


def nearest_group_counts(
    target_indices: list[int],
    candidate_indices_by_author: dict[str, list[int]],
    matrix: np.ndarray,
) -> Counter[str]:
    counts: Counter[str] = Counter()
    target_matrix = matrix[np.array(target_indices, dtype=int)]
    candidate_authors = list(candidate_indices_by_author.keys())
    candidate_matrices = {
        author: matrix[np.array(indices, dtype=int)]
        for author, indices in candidate_indices_by_author.items()
        if indices
    }
    for vector in target_matrix:
        best_author = ""
        best_score = -2.0
        for author in candidate_authors:
            candidates = candidate_matrices.get(author)
            if candidates is None or candidates.size == 0:
                continue
            score = float((candidates @ vector).max())
            if score > best_score:
                best_author = author
                best_score = score
        counts[best_author] += 1
    return counts


def summarize_ratios(ratios: list[float], target_count: int) -> dict[str, float]:
    arr = np.array(ratios, dtype=float)
    return {
        "mean_ratio": rounded(float(arr.mean())),
        "ci95_low_ratio": rounded(float(np.quantile(arr, 0.025))),
        "ci95_high_ratio": rounded(float(np.quantile(arr, 0.975))),
        "mean_count": rounded(float(arr.mean() * target_count)),
        "ci95_low_count": rounded(float(np.quantile(arr, 0.025) * target_count)),
        "ci95_high_count": rounded(float(np.quantile(arr, 0.975) * target_count)),
    }


def run() -> dict[str, Any]:
    chunks = make_all_chunks()
    embeddings = load_embeddings()
    missing = [chunk.chunk_id for chunk in chunks if chunk.chunk_id not in embeddings]
    if missing:
        raise RuntimeError(f"missing embeddings for {len(missing)} chunks: {missing[:3]}")

    matrix = normalize(np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float))
    indices_by_author: dict[str, list[int]] = defaultdict(list)
    for index, chunk in enumerate(chunks):
        indices_by_author[chunk.author].append(index)

    rng = np.random.default_rng(SEED)
    target_results: dict[str, Any] = {}

    for target_author in TARGET_AUTHORS:
        target_indices = indices_by_author[target_author]
        candidate_full = {
            author: indices
            for author, indices in indices_by_author.items()
            if author != target_author
        }
        simple_counts = nearest_group_counts(target_indices, candidate_full, matrix)
        simple_rows = []
        for author in sorted(candidate_full):
            count = simple_counts.get(author, 0)
            simple_rows.append(
                {
                    "nearest_group": author,
                    "count": count,
                    "ratio": rounded(count / len(target_indices)),
                }
            )

        ratios_by_author: dict[str, list[float]] = {author: [] for author in candidate_full}
        for _ in range(ITERATIONS):
            sampled: dict[str, list[int]] = {}
            for author, indices in candidate_full.items():
                sample_size = min(SAMPLE_CAP, len(indices))
                if sample_size >= len(indices):
                    sampled[author] = list(indices)
                else:
                    sampled[author] = rng.choice(indices, size=sample_size, replace=False).tolist()
            counts = nearest_group_counts(target_indices, sampled, matrix)
            for author in candidate_full:
                ratios_by_author[author].append(counts.get(author, 0) / len(target_indices))

        sampled_rows = []
        for author in sorted(candidate_full):
            row = {
                "nearest_group": author,
                "full_group_size": len(candidate_full[author]),
                "sampled_group_size": min(SAMPLE_CAP, len(candidate_full[author])),
                **summarize_ratios(ratios_by_author[author], len(target_indices)),
            }
            sampled_rows.append(row)

        target_results[target_author] = {
            "target_chunk_count": len(target_indices),
            "candidate_groups": {
                author: {
                    "full_group_size": len(indices),
                    "sampled_group_size": min(SAMPLE_CAP, len(indices)),
                }
                for author, indices in sorted(candidate_full.items())
            },
            "simple_nearest": simple_rows,
            "sampled_nearest": sampled_rows,
        }

    return {
        "title": "Nearest-neighbor subsampling check 2026-06-04",
        "method": {
            "embedding_model": MODEL,
            "embedding_dimension": 3072,
            "chunking": f"Unicode-safe {MAX_TOKENS}-token chunks, {OVERLAP}-token overlap",
            "iterations": ITERATIONS,
            "sample_cap": SAMPLE_CAP,
            "seed": SEED,
            "sampling_policy": "For each iteration, each non-target author group contributes min(20, group_size) reference chunks; groups below 20 use all chunks.",
            "nearest_policy": "For every target chunk, choose the reference author group with the maximum cosine similarity in 3072D among that iteration's sampled candidate chunks.",
            "raw_text_policy": "No raw/chunk text or embedding vector is written.",
        },
        "target_authors": target_results,
    }


def write_outputs(summary: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = []
    for target_author, result in summary["target_authors"].items():
        simple_lookup = {row["nearest_group"]: row for row in result["simple_nearest"]}
        for row in result["sampled_nearest"]:
            simple = simple_lookup.get(row["nearest_group"], {})
            rows.append(
                {
                    "target_author": target_author,
                    "target_chunk_count": result["target_chunk_count"],
                    "nearest_group": row["nearest_group"],
                    "full_group_size": row["full_group_size"],
                    "sampled_group_size": row["sampled_group_size"],
                    "simple_count": simple.get("count", 0),
                    "simple_ratio": simple.get("ratio", 0),
                    "sampled_mean_count": row["mean_count"],
                    "sampled_ci95_low_count": row["ci95_low_count"],
                    "sampled_ci95_high_count": row["ci95_high_count"],
                    "sampled_mean_ratio": row["mean_ratio"],
                    "sampled_ci95_low_ratio": row["ci95_low_ratio"],
                    "sampled_ci95_high_ratio": row["ci95_high_ratio"],
                }
            )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "target_author",
            "target_chunk_count",
            "nearest_group",
            "full_group_size",
            "sampled_group_size",
            "simple_count",
            "simple_ratio",
            "sampled_mean_count",
            "sampled_ci95_low_count",
            "sampled_ci95_high_count",
            "sampled_mean_ratio",
            "sampled_ci95_low_ratio",
            "sampled_ci95_high_ratio",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    OUT_MD.write_text(render_doc(summary, rows), encoding="utf-8")


def md_table(rows: list[dict[str, Any]], fields: list[tuple[str, str]]) -> list[str]:
    lines = [
        "| " + " | ".join(label for label, _ in fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(key, "")) for _, key in fields) + " |")
    return lines


def render_doc(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Nearest-Neighbor Subsampling 2026-06-04",
        "",
        "単純最近傍集計が参照群の chunk 数に影響されうるため、既存 embedding cache だけを使って、参照群ごとの候補数を上限20件に揃える補助確認を行った。",
        "",
        "## 方法",
        "",
        f"- 反復数: `{summary['method']['iterations']}`",
        f"- sample cap: `{summary['method']['sample_cap']}`",
        f"- seed: `{summary['method']['seed']}`",
        "- 各反復で、対象著者以外の各著者群から `min(20, group_size)` chunk を抽出する。",
        "- 各対象 chunk について、抽出された候補群の中で3072次元 cosine 最大の著者群を最近傍とする。",
        "- 本文・chunk text・embedding vector は出力しない。",
        "",
    ]
    for target_author in TARGET_AUTHORS:
        target_rows = [row for row in rows if row["target_author"] == target_author]
        lines.extend(
            [
                f"## {target_author} chunks",
                "",
                *md_table(
                    target_rows,
                    [
                        ("nearest", "nearest_group"),
                        ("full n", "full_group_size"),
                        ("sample n", "sampled_group_size"),
                        ("simple count", "simple_count"),
                        ("simple ratio", "simple_ratio"),
                        ("sample mean", "sampled_mean_ratio"),
                        ("95% low", "sampled_ci95_low_ratio"),
                        ("95% high", "sampled_ci95_high_ratio"),
                    ],
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## 注意",
            "",
            "- この補正は、参照群の候補数上限をそろえた場合にも大きな傾向が残るかを見る補助分析である。",
            "- 龍樹・天親など20 chunk未満の群は全件使用するため、完全な同数サンプリングではない。",
            "- 最近傍比率は影響史の向きを証明しない。",
            "",
            "## データ",
            "",
            f"- `{OUT_JSON.relative_to(ROOT)}`",
            f"- `{OUT_CSV.relative_to(ROOT)}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    summary = run()
    write_outputs(summary)
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
