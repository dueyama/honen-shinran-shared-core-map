#!/usr/bin/env python3
"""Compare reading-order semantic flow for Honen and Shinran.

Uses existing text-embedding-3-large cache only. No API calls and no raw text
output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "data" / "outputs" / "honen_shinran_predecessor_style_embedding_map_meta.json"
CACHE_PATH = (
    ROOT
    / "data"
    / "cache"
    / "honen_shinran_predecessor_style_embeddings_text-embedding-3-large_700_100.json"
)
OUT_JSON = ROOT / "data" / "outputs" / "honen_shinran_semantic_flow_meta.json"
OUT_MD = ROOT / "docs" / "honen-shinran-semantic-flow-2026-06-03.md"
BIN_COUNT = 12


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def spearman_like(x: np.ndarray, y: np.ndarray) -> float:
    x = x.astype(float)
    y = y.astype(float)
    x_std = float(x.std()) or 1.0
    y_std = float(y.std()) or 1.0
    x = (x - float(x.mean())) / x_std
    y = (y - float(y.mean())) / y_std
    return float(np.mean(x * y))


def load_ordered() -> dict[str, list[tuple[dict[str, Any], np.ndarray]]]:
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))["embeddings"]
    works: dict[str, list[tuple[dict[str, Any], np.ndarray]]] = {"法然": [], "親鸞": []}
    for chunk in meta["chunks"]:
        vector = np.array(cache[chunk["chunk_id"]]["embedding"], dtype=float)
        vector = vector / (np.linalg.norm(vector) or 1.0)
        works[chunk["author"]].append((chunk, vector))
    for author in works:
        works[author].sort(key=lambda item: item[0]["chunk_index"])
    return works


def bin_centroids(items: list[tuple[dict[str, Any], np.ndarray]], bins: int) -> tuple[np.ndarray, list[dict[str, Any]]]:
    vectors = np.stack([vector for _, vector in items])
    n = len(items)
    centroids = []
    ranges = []
    for index in range(bins):
        start = round(index * n / bins)
        end = round((index + 1) * n / bins)
        if end <= start:
            end = start + 1
        mean = vectors[start:end].mean(axis=0)
        mean = mean / (np.linalg.norm(mean) or 1.0)
        centroids.append(mean)
        first = items[start][0]
        last = items[end - 1][0]
        ranges.append(
            {
                "bin": index + 1,
                "chunk_start": start,
                "chunk_end": end - 1,
                "page_start": first["page_start"],
                "page_end": last["page_end"],
            }
        )
    return np.stack(centroids), ranges


def summarize() -> dict[str, Any]:
    works = load_ordered()
    honen = np.stack([vector for _, vector in works["法然"]])
    shinran = np.stack([vector for _, vector in works["親鸞"]])
    sim = honen @ shinran.T
    h_to_s = sim.argmax(axis=1)
    s_to_h = sim.argmax(axis=0)

    honen_bins, honen_ranges = bin_centroids(works["法然"], BIN_COUNT)
    shinran_bins, shinran_ranges = bin_centroids(works["親鸞"], BIN_COUNT)
    bin_sim = honen_bins @ shinran_bins.T

    honen_best_bins = []
    for h_index in range(BIN_COUNT):
        s_index = int(np.argmax(bin_sim[h_index]))
        honen_best_bins.append(
            {
                "honen_bin": honen_ranges[h_index],
                "best_shinran_bin": shinran_ranges[s_index],
                "best_similarity": round(float(bin_sim[h_index, s_index]), 6),
                "same_relative_bin_similarity": round(float(bin_sim[h_index, h_index]), 6),
            }
        )

    shinran_best_bins = []
    for s_index in range(BIN_COUNT):
        h_index = int(np.argmax(bin_sim[:, s_index]))
        shinran_best_bins.append(
            {
                "shinran_bin": shinran_ranges[s_index],
                "best_honen_bin": honen_ranges[h_index],
                "best_similarity": round(float(bin_sim[h_index, s_index]), 6),
                "same_relative_bin_similarity": round(float(bin_sim[s_index, s_index]), 6),
            }
        )

    return {
        "title": "Honen/Shinran reading-order semantic flow comparison",
        "method": {
            "embedding_model": "text-embedding-3-large",
            "chunks": "700-token chunks, 100-token overlap",
            "similarity": "cosine similarity on normalized cached embeddings",
            "bin_count": BIN_COUNT,
            "raw_text_policy": "No raw source text is written.",
        },
        "chunk_counts": {"法然": len(honen), "親鸞": len(shinran)},
        "metrics": {
            "mean_best_similarity_honen_to_shinran": round(float(sim.max(axis=1).mean()), 6),
            "mean_best_similarity_shinran_to_honen": round(float(sim.max(axis=0).mean()), 6),
            "nearest_index_correlation_honen_to_shinran": round(
                spearman_like(np.arange(len(h_to_s)), h_to_s), 6
            ),
            "nearest_index_correlation_shinran_to_honen": round(
                spearman_like(np.arange(len(s_to_h)), s_to_h), 6
            ),
            "same_relative_bin_similarity_mean": round(float(np.diag(bin_sim).mean()), 6),
            "same_relative_bin_similarity_min": round(float(np.diag(bin_sim).min()), 6),
            "same_relative_bin_similarity_max": round(float(np.diag(bin_sim).max()), 6),
            "consecutive_similarity_mean_honen": round(float(np.sum(honen[:-1] * honen[1:], axis=1).mean()), 6),
            "consecutive_similarity_mean_shinran": round(
                float(np.sum(shinran[:-1] * shinran[1:], axis=1).mean()), 6
            ),
        },
        "honen_bin_best_matches": honen_best_bins,
        "shinran_bin_best_matches": shinran_best_bins,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    lines = [
        "# Honen/Shinran Semantic Flow 2026-06-03",
        "",
        "## 問い",
        "",
        "法然『選択本願念仏集』と親鸞『教行信証』を、それぞれ前から順に読んだ場合、意味的な流れが似ているかを見る。",
        "",
        "## 方法",
        "",
        "- 既存の `text-embedding-3-large` cache を使用し、API は呼ばない。",
        "- 700-token chunks、100-token overlap。",
        "- chunk 順序は各本文の出現順。",
        "- cosine similarity で法然 chunk と親鸞 chunk の対応を見る。",
        "- 12分割 bin で、相対位置ごとの対応も見る。",
        "- raw text は出力しない。",
        "",
        "## 結果",
        "",
        f"- 法然 chunks: {summary['chunk_counts']['法然']}",
        f"- 親鸞 chunks: {summary['chunk_counts']['親鸞']}",
        f"- 法然 chunk から見た最良親鸞 chunk との平均類似度: `{metrics['mean_best_similarity_honen_to_shinran']}`",
        f"- 親鸞 chunk から見た最良法然 chunk との平均類似度: `{metrics['mean_best_similarity_shinran_to_honen']}`",
        f"- 法然順序と最寄り親鸞位置の相関: `{metrics['nearest_index_correlation_honen_to_shinran']}`",
        f"- 親鸞順序と最寄り法然位置の相関: `{metrics['nearest_index_correlation_shinran_to_honen']}`",
        f"- 同じ相対位置 bin 同士の平均類似度: `{metrics['same_relative_bin_similarity_mean']}`",
        f"- 連続 chunk 類似度平均 法然/親鸞: `{metrics['consecutive_similarity_mean_honen']}` / `{metrics['consecutive_similarity_mean_shinran']}`",
        "",
        "## 解釈",
        "",
        "両書は語彙・主題の部品としてはよく重なる。法然 chunk から親鸞本文内の近い chunk を探すと平均類似度は高い。ただし、順序の対応は弱い。最寄り位置の相関はほぼ 0 に近く、法然の前半・中盤・後半が親鸞の同じ相対位置へ素直に対応するわけではない。",
        "",
        "したがって、前から読んだ意味的流れとしては、全体はあまり似ていない。似ているのは材料・主題であり、配列ではない。法然は専修念仏を論証する方向へ比較的集約して進むが、親鸞は教・行・信・証・真仏土・化身土の構成の中で、同じ浄土教コアを別の場所に再配置し、阿闍世、方便、真仮、化身土、外教批判などへ大きく分岐する。",
        "",
        "## 法然 bin から見た親鸞側の最良対応",
        "",
        "| 法然 bin/pages | 最良親鸞 bin/pages | best sim | same-position sim |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in summary["honen_bin_best_matches"]:
        h = row["honen_bin"]
        s = row["best_shinran_bin"]
        lines.append(
            f"| {h['bin']} / {h['page_start']}-{h['page_end']} | {s['bin']} / {s['page_start']}-{s['page_end']} | {row['best_similarity']:.3f} | {row['same_relative_bin_similarity']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## 注意",
            "",
            "- 類似度が高いことは、同じ主題部品があることを示すが、引用関係や歴史的影響を直接証明しない。",
            "- 順序相関が低いことは、両書が同じ主題を異なる構成で配列していることを示す。",
            "- 次は巻別・章別の自然単位で同じ分析を行う方がよい。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = summarize()
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_markdown(summary), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(json.dumps(summary["metrics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
