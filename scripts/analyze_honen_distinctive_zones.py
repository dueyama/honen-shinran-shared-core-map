#!/usr/bin/env python3
"""Summarize Honen chunks that protrude from Shinran/anchor neighborhoods."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import tiktoken


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compare_sat_chunking_strategies import load_works, make_safe_chunks, normalize_rows, rounded  # noqa: E402
from make_sat_safe_high_priest_anchor_map import ANCHORS, load_anchor_text, make_anchor_chunks  # noqa: E402


FOCUS_CACHE = ROOT / "data/cache/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json"
ANCHOR_CACHE = ROOT / "data/cache/sat_safe_high_priest_anchor_embeddings_text-embedding-3-large_700_100.json"
MAP_META = ROOT / "data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json"
OUT_PATH = ROOT / "data/outputs/honen_distinctive_zones_text-embedding-3-large_700_100.json"
DOC_PATH = ROOT / "docs/honen-distinctive-zones-2026-06-03.md"


KEYWORDS = {
    "念仏・称名": ["念佛", "念仏", "稱名", "称名", "名號", "名号"],
    "選択・本願": ["選擇", "選択", "本願", "第十八願"],
    "正雑二行": ["正行", "雜行", "雑行", "正雜", "助業", "正定業", "五種正行"],
    "廃立・取捨": ["廢", "廃", "立", "捨", "閣", "傍", "抛", "選取"],
    "三心": ["三心", "至誠心", "深心", "迴向發願心", "回向發願心"],
    "往生・浄土": ["往生", "極樂", "極楽", "淨土", "浄土", "安樂"],
    "観経・善導": ["觀經", "観経", "善導", "觀經疏", "散善義"],
    "諸行・万行": ["諸行", "萬行", "万行", "修諸", "諸善"],
    "聖道・末法": ["聖道", "末法", "像法", "末代"],
    "経論引用": ["云", "曰", "經", "論", "釋", "疏"],
}


def sha256_text(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_embeddings() -> dict[str, dict[str, Any]]:
    data = load_json(FOCUS_CACHE)["embeddings"]
    data.update(load_json(ANCHOR_CACHE)["embeddings"])
    return data


def make_all_chunks() -> list[Any]:
    encoder = tiktoken.get_encoding("cl100k_base")
    chunks = []
    for work in load_works(encoder):
        chunks.extend(make_safe_chunks(work, encoder))
    for anchor in [load_anchor_text(item) for item in ANCHORS]:
        chunks.extend(make_anchor_chunks(anchor, encoder))
    return chunks


def keyword_hits(text: str) -> dict[str, int]:
    hits = {}
    for label, terms in KEYWORDS.items():
        count = sum(text.count(term) for term in terms)
        if count:
            hits[label] = count
    return hits


def top_cjk_terms(text: str, limit: int = 12) -> list[tuple[str, int]]:
    terms: Counter[str] = Counter()
    stop = {
        "如是", "爾者", "云何", "若有", "一切", "衆生", "眾生", "是故", "應知",
        "故知", "若不", "不能", "不可", "已上", "乃至", "何以", "所以",
    }
    for width in (2, 3, 4):
        for i in range(0, max(0, len(text) - width + 1)):
            term = text[i : i + width]
            if not re.fullmatch(r"[\u3400-\u9fffぁ-んァ-ン]+", term):
                continue
            if term in stop:
                continue
            if any(ch in term for ch in "之也而者於以其所無有不為佛法人"):
                continue
            terms[term] += 1
    return terms.most_common(limit)


def normalize(matrix: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(matrix, axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    return matrix / denom


def summarize_zone(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    keyword_totals: Counter[str] = Counter()
    term_totals: Counter[str] = Counter()
    for row in rows:
        keyword_totals.update(row["keyword_hits"])
        term_totals.update(dict(row["top_terms"]))
    return {
        "label": label,
        "chunk_count": len(rows),
        "chunk_indices": [row["chunk_index"] for row in rows],
        "line_ranges": [f"{row['line_start']}-{row['line_end']}" for row in rows],
        "keyword_totals": dict(keyword_totals.most_common()),
        "top_terms": term_totals.most_common(15),
        "chunks": rows,
    }


def main() -> None:
    chunks = make_all_chunks()
    embeddings = load_embeddings()
    meta = load_json(MAP_META)
    coords = {record["chunk_id"]: np.array([record["x"], record["y"]], dtype=float) for record in meta["chunks"]}

    matrix = normalize(np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float))
    honen_indices = [index for index, chunk in enumerate(chunks) if chunk.author == "法然"]
    non_honen_indices = [index for index, chunk in enumerate(chunks) if chunk.author != "法然"]
    shinran_indices = [index for index, chunk in enumerate(chunks) if chunk.author == "親鸞"]
    anchor_indices = [index for index, chunk in enumerate(chunks) if chunk.author not in {"法然", "親鸞"}]

    non_honen_matrix = matrix[non_honen_indices]
    shinran_matrix = matrix[shinran_indices]
    anchor_matrix = matrix[anchor_indices]

    non_honen_2d = np.array([coords[chunks[index].chunk_id] for index in non_honen_indices], dtype=float)
    rows: list[dict[str, Any]] = []
    for index in honen_indices:
        chunk = chunks[index]
        vector = matrix[index]
        non_honen_sims = non_honen_matrix @ vector
        shinran_sims = shinran_matrix @ vector
        anchor_sims = anchor_matrix @ vector
        nearest_non_honen = chunks[non_honen_indices[int(np.argmax(non_honen_sims))]]
        nearest_anchor = chunks[anchor_indices[int(np.argmax(anchor_sims))]]
        point = coords[chunk.chunk_id]
        distances_2d = np.linalg.norm(non_honen_2d - point, axis=1)
        nearest_2d = chunks[non_honen_indices[int(np.argmin(distances_2d))]]
        text = chunk.text
        rows.append(
            {
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "x": rounded(float(point[0])),
                "y": rounded(float(point[1])),
                "nearest_non_honen_author": nearest_non_honen.author,
                "nearest_non_honen_work": nearest_non_honen.work,
                "nearest_non_honen_cosine": rounded(float(non_honen_sims.max())),
                "nearest_shinran_cosine": rounded(float(shinran_sims.max())),
                "nearest_anchor_author": nearest_anchor.author,
                "nearest_anchor_work": nearest_anchor.work,
                "nearest_anchor_cosine": rounded(float(anchor_sims.max())),
                "nearest_non_honen_2d_author": nearest_2d.author,
                "nearest_non_honen_2d_distance": rounded(float(distances_2d.min())),
                "keyword_hits": keyword_hits(text),
                "top_terms": top_cjk_terms(text),
                "text_sha256": sha256_text(text),
                "text_char_count": len(text),
                "actual_token_count": chunk.actual_token_count,
            }
        )

    # Map protrusions: far from non-Honen in 2D. Semantic protrusions: low high-dimensional nearest.
    by_2d = sorted(rows, key=lambda row: row["nearest_non_honen_2d_distance"], reverse=True)
    by_semantic = sorted(rows, key=lambda row: row["nearest_non_honen_cosine"])
    left_side = sorted(
        [row for row in rows if row["x"] < -0.19],
        key=lambda row: row["nearest_non_honen_2d_distance"],
        reverse=True,
    )
    lower_side = sorted(
        [row for row in rows if row["y"] < -0.14],
        key=lambda row: row["nearest_non_honen_2d_distance"],
        reverse=True,
    )

    zones = [
        summarize_zone("2D map protrusion: farthest from non-Honen points", by_2d[:12]),
        summarize_zone("High-dimensional protrusion: weakest nearest non-Honen cosine", by_semantic[:12]),
        summarize_zone("Left-side Honen region", left_side[:16]),
        summarize_zone("Lower-side Honen region", lower_side[:12]),
    ]

    output = {
        "title": "Honen distinctive zones on SAT safe map",
        "method": {
            "selection": "Honen chunks ranked by 2D distance to nearest non-Honen point and by high-dimensional nearest non-Honen cosine",
            "raw_text_policy": "no raw chunk text is written; only keywords, line refs, hashes, and metrics",
        },
        "honen_chunk_count": len(rows),
        "zones": zones,
        "all_honen_chunks": rows,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    doc = [
        "# Honen Distinctive Zones 2026-06-03",
        "",
        "SAT 漢文系 safe chunk map で、法然 chunks のうち親鸞・高僧アンカーから相対的に離れる部分を調べた。",
        "",
        "本文はここに貼らない。line range、指標、キーワードだけを記録する。",
        "",
        "## 初見",
        "",
        "- 法然の左側・下側に出る chunks は、全体として念仏そのものの単純な称揚というより、`選択`、`正雑二行`、`諸行との取捨`、`三心`、`善導/観経` を使った教判的整理が目立つ。",
        "- 高次元では、法然の多くは親鸞に近く、完全な孤立ではない。ただし 2D 上の左側は親鸞・高僧アンカーの重心群から離れて見える。",
        "- したがって、仮説としては「法然独自の念仏理解」よりも、「念仏を諸行から選び出す論証・分類の圧縮」が左側の出方を作っている可能性が高い。",
        "",
    ]
    for zone in zones:
        doc.extend(
            [
                f"## {zone['label']}",
                "",
                f"- chunks: {zone['chunk_count']}",
                f"- chunk indices: `{zone['chunk_indices']}`",
                f"- line ranges: `{zone['line_ranges']}`",
                f"- keyword totals: `{zone['keyword_totals']}`",
                f"- top terms: `{zone['top_terms']}`",
                "",
            ]
        )
    doc.extend(
        [
            "## 出力",
            "",
            "- `data/outputs/honen_distinctive_zones_text-embedding-3-large_700_100.json`",
            "",
            "この JSON も本文は含まないが、line refs と chunk hashes を含むためローカル分析用として扱う。",
            "",
        ]
    )
    DOC_PATH.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"wrote {DOC_PATH.relative_to(ROOT)}")
    for zone in zones:
        print(zone["label"], zone["chunk_indices"], zone["keyword_totals"])


if __name__ == "__main__":
    main()
