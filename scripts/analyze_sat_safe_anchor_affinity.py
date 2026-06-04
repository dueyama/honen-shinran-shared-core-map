#!/usr/bin/env python3
"""Analyze high-dimensional affinity between focus texts and anchor texts."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FOCUS_CACHE = ROOT / "data/cache/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json"
ANCHOR_CACHE = ROOT / "data/cache/sat_safe_high_priest_anchor_embeddings_text-embedding-3-large_700_100.json"
OUT_PATH = ROOT / "data/outputs/sat_safe_anchor_affinity_text-embedding-3-large_700_100.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(matrix: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(matrix, axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    return matrix / denom


def rounded(value: float) -> float:
    return round(float(value), 6)


def distribution(values: np.ndarray) -> dict[str, float]:
    return {
        "min": rounded(float(values.min())),
        "p10": rounded(float(np.quantile(values, 0.1))),
        "median": rounded(float(np.median(values))),
        "mean": rounded(float(values.mean())),
        "p90": rounded(float(np.quantile(values, 0.9))),
        "max": rounded(float(values.max())),
    }


def load_focus_records() -> list[dict[str, Any]]:
    data = load_json(FOCUS_CACHE)["embeddings"]
    rows = []
    for chunk_id, record in data.items():
        if not chunk_id.startswith("safe_unicode_700:"):
            continue
        rows.append(
            {
                "chunk_id": chunk_id,
                "group": record["author"],
                "work": record["work"],
                "role": "focus",
                "chunk_index": record["chunk_index"],
                "embedding": record["embedding"],
            }
        )
    return sorted(rows, key=lambda row: (row["group"], row["chunk_index"]))


def load_anchor_records() -> list[dict[str, Any]]:
    data = load_json(ANCHOR_CACHE)["embeddings"]
    rows = []
    for chunk_id, record in data.items():
        rows.append(
            {
                "chunk_id": chunk_id,
                "group": record["author"],
                "work": record["work"],
                "role": "anchor",
                "chunk_index": record["chunk_index"],
                "embedding": record["embedding"],
            }
        )
    return sorted(rows, key=lambda row: (row["group"], row["work"], row["chunk_index"]))


def group_indices(records: list[dict[str, Any]]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        groups[record["group"]].append(index)
    return dict(groups)


def main() -> None:
    focus = load_focus_records()
    anchors = load_anchor_records()
    records = focus + anchors
    matrix = normalize(np.array([row["embedding"] for row in records], dtype=float))
    focus_matrix = matrix[: len(focus)]
    anchor_matrix = matrix[len(focus) :]
    focus_groups = group_indices(focus)
    anchor_groups = group_indices(anchors)
    all_groups = group_indices(records)

    centroid_cosine: dict[str, dict[str, float]] = {}
    centroids = {
        group: matrix[indices].mean(axis=0)
        for group, indices in all_groups.items()
    }
    for left, left_vec in centroids.items():
        centroid_cosine[left] = {}
        for right, right_vec in centroids.items():
            denom = np.linalg.norm(left_vec) * np.linalg.norm(right_vec)
            centroid_cosine[left][right] = rounded(float(np.dot(left_vec, right_vec) / denom))

    focus_to_anchor_mean_best: dict[str, dict[str, Any]] = {}
    focus_to_anchor_top1: dict[str, dict[str, Any]] = {}
    for focus_group, focus_indices in focus_groups.items():
        focus_local = np.array(focus_indices, dtype=int)
        focus_vectors = focus_matrix[focus_local]
        top1_counts: Counter[str] = Counter()
        top1_scores: list[float] = []
        per_anchor: dict[str, Any] = {}
        for anchor_group, anchor_indices in anchor_groups.items():
            anchor_vectors = anchor_matrix[np.array(anchor_indices, dtype=int)]
            sims = focus_vectors @ anchor_vectors.T
            best = sims.max(axis=1)
            per_anchor[anchor_group] = distribution(best)
        all_anchor_sims = focus_vectors @ anchor_matrix.T
        best_anchor_local = all_anchor_sims.argmax(axis=1)
        for row_index, score in zip(best_anchor_local, all_anchor_sims.max(axis=1)):
            top1_counts[anchors[int(row_index)]["group"]] += 1
            top1_scores.append(float(score))
        focus_to_anchor_mean_best[focus_group] = per_anchor
        total = sum(top1_counts.values()) or 1
        focus_to_anchor_top1[focus_group] = {
            "counts": dict(sorted(top1_counts.items(), key=lambda item: (-item[1], item[0]))),
            "shares": {
                key: rounded(value / total)
                for key, value in sorted(top1_counts.items(), key=lambda item: (-item[1], item[0]))
            },
            "score_distribution": distribution(np.array(top1_scores, dtype=float)),
        }

    nearest_nonself: dict[str, Any] = {}
    for focus_group, focus_indices in focus_groups.items():
        counts: Counter[str] = Counter()
        scores: list[float] = []
        target_indices = [
            index for index, record in enumerate(records) if record["group"] != focus_group
        ]
        target_matrix = matrix[np.array(target_indices, dtype=int)]
        sims = matrix[np.array(focus_indices, dtype=int)] @ target_matrix.T
        best_target_local = sims.argmax(axis=1)
        for target_local, score in zip(best_target_local, sims.max(axis=1)):
            counts[records[target_indices[int(target_local)]]["group"]] += 1
            scores.append(float(score))
        total = sum(counts.values()) or 1
        nearest_nonself[focus_group] = {
            "counts": dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))),
            "shares": {
                key: rounded(value / total)
                for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
            },
            "score_distribution": distribution(np.array(scores, dtype=float)),
        }

    output = {
        "title": "SAT safe high-dimensional anchor affinity",
        "method": {
            "embedding_model": "text-embedding-3-large",
            "vectors": "L2-normalized cached embeddings",
            "focus_cache": str(FOCUS_CACHE.relative_to(ROOT)),
            "anchor_cache": str(ANCHOR_CACHE.relative_to(ROOT)),
            "raw_text_policy": "no raw or chunk text is included",
        },
        "chunk_counts": dict(Counter(row["group"] for row in records)),
        "centroid_cosine": centroid_cosine,
        "focus_to_anchor_mean_best": focus_to_anchor_mean_best,
        "focus_to_anchor_top1": focus_to_anchor_top1,
        "nearest_nonself": nearest_nonself,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(ROOT)}")
    for group, value in nearest_nonself.items():
        print(group, "nearest_nonself", value["counts"])
    for group, value in focus_to_anchor_top1.items():
        print(group, "nearest_anchor", value["counts"])


if __name__ == "__main__":
    main()
