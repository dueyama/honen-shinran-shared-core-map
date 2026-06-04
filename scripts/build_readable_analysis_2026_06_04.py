#!/usr/bin/env python3
"""Build reader-facing, text-free analysis tables for the SAT safe map.

This script reads local-only prepared text to count features, but it never
writes raw chunk text. Outputs are intended as the data basis for a later
viewer/report.
"""

from __future__ import annotations

import csv
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

from analyze_honen_distinctive_zones import top_cjk_terms  # noqa: E402
from compare_sat_chunking_strategies import load_works, make_safe_chunks, rounded  # noqa: E402
from make_sat_safe_high_priest_anchor_map import ANCHORS, load_anchor_text, make_anchor_chunks  # noqa: E402


FOCUS_CACHE = ROOT / "data/cache/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json"
ANCHOR_CACHE = ROOT / "data/cache/sat_safe_high_priest_anchor_embeddings_text-embedding-3-large_700_100.json"
MAP_PATH = ROOT / "data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json"
OUT_JSON = ROOT / "data/outputs/readable_map_analysis_2026-06-04_text-embedding-3-large_700_100.json"
HONEN_CSV = ROOT / "data/outputs/honen_protrusion_table_2026-06-04.csv"
SHINRAN_CSV = ROOT / "data/outputs/shinran_volume_affinity_table_2026-06-04.csv"
SHINRAN_PROTRUSION_CSV = ROOT / "data/outputs/shinran_protrusion_table_2026-06-04.csv"
DOC_PATH = ROOT / "docs/readable-map-analysis-2026-06-04.md"


STYLE_GROUPS = {
    "念仏・称名": ["念佛", "念仏", "稱名", "称名", "專念", "専念", "念佛三昧"],
    "選択・本願": ["選擇", "選択", "撰擇", "本願", "弘誓", "誓願", "第十八願"],
    "正雑・諸行": ["正行", "雜行", "雑行", "二行", "諸行", "萬行", "万行", "餘行", "正定業"],
    "廃立・取捨": ["廢", "廃", "立", "捨", "閣", "抛", "傍", "取", "選取"],
    "信・三心": ["信", "信樂", "信楽", "三心", "至誠心", "深心", "眞實心", "一心"],
    "願・回向": ["願", "回向", "廻向", "往相", "還相", "利他", "欲生"],
    "名号・真実": ["名號", "名号", "眞實", "真実", "金剛", "大利", "無上"],
    "往生・浄土": ["往生", "淨土", "浄土", "安樂", "安楽", "極樂", "極楽", "報土", "佛土"],
    "方便・化身土": ["方便", "化身土", "眞門", "真門", "假", "仮", "邪", "外道"],
    "罪・救済": ["五逆", "謗法", "闡提", "阿闍世", "提婆", "慚愧", "地獄", "煩惱"],
}

SOURCE_MARKERS = {
    "経名": [
        "大經", "大経", "觀經", "観経", "阿彌陀經", "阿弥陀経", "無量壽經", "無量寿経",
        "大無量壽經", "平等覺經", "涅槃經", "華嚴經", "大集經", "日藏經", "月藏經",
    ],
    "論釈名": ["往生論", "往生論註", "安樂集", "觀經疏", "法事讃", "般舟讃", "往生要集"],
    "祖師名": ["龍樹", "天親", "曇鸞", "道綽", "善導", "源信", "源空", "法然", "光明寺"],
    "引用導入": ["云", "曰", "言", "釋", "疏", "論曰", "經言", "問曰", "答曰", "私云"],
}


SHINRAN_VOLUME_RANGES = [
    ("序", "T2646_.83.0589a04", "T2646_.83.0589b02"),
    ("教巻", "T2646_.83.0589b03", "T2646_.83.0590a07"),
    ("行巻", "T2646_.83.0590a08", "T2646_.83.0600c13"),
    ("信巻", "T2646_.83.0600c14", "T2646_.83.0616a21"),
    ("証巻", "T2646_.83.0616a22", "T2646_.83.0620c09"),
    ("真仏土巻", "T2646_.83.0620c10", "T2646_.83.0626c08"),
    ("化身土巻", "T2646_.83.0626c09", "T2646_.83.0643a23"),
]

HONEN_SECTION_RANGES = [
    ("序", "T2608_.83.0001a04", "T2608_.83.0001a27"),
    ("聖道門・浄土門", "T2608_.83.0001b03", "T2608_.83.0002c13"),
    ("正雑二行", "T2608_.83.0002c14", "T2608_.83.0004b23"),
    ("本願念仏", "T2608_.83.0004b24", "T2608_.83.0006c09"),
    ("三輩・一向専念", "T2608_.83.0006c10", "T2608_.83.0008a99"),
    ("三心・信心", "T2608_.83.0008b01", "T2608_.83.0012c99"),
    ("付属・証誠・選択総結", "T2608_.83.0013a01", "T2608_.83.0019a99"),
    ("末尾・奥書系", "T2608_.83.0019b01", "T2608_.83.0020b99"),
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def line_key(line_ref: str) -> tuple[int, int, int, int]:
    match = re.search(r"\.(\d{4})([abc])(\d{2})", line_ref)
    if not match:
        return (0, 0, 0, 0)
    page = int(match.group(1))
    col = {"a": 0, "b": 1, "c": 2}[match.group(2)]
    line = int(match.group(3))
    return (page, col, line, 0)


def in_range(line_ref: str, start: str, end: str) -> bool:
    key = line_key(line_ref)
    return line_key(start) <= key <= line_key(end)


def range_label(line_ref: str, ranges: list[tuple[str, str, str]], fallback: str) -> str:
    for label, start, end in ranges:
        if in_range(line_ref, start, end):
            return label
    return fallback


def count_groups(text: str, groups: dict[str, list[str]]) -> dict[str, int]:
    hits: dict[str, int] = {}
    for label, terms in groups.items():
        count = sum(text.count(term) for term in terms)
        if count:
            hits[label] = count
    return hits


def normalize(matrix: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(matrix, axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    return matrix / denom


def make_all_chunks() -> list[Any]:
    encoder = tiktoken.get_encoding("cl100k_base")
    chunks = []
    for work in load_works(encoder):
        chunks.extend(make_safe_chunks(work, encoder))
    for anchor in [load_anchor_text(item) for item in ANCHORS]:
        chunks.extend(make_anchor_chunks(anchor, encoder))
    return chunks


def load_embeddings() -> dict[str, dict[str, Any]]:
    embeddings = {}
    for chunk_id, record in load_json(FOCUS_CACHE)["embeddings"].items():
        if chunk_id.startswith("safe_unicode_700:"):
            embeddings[chunk_id] = record
    embeddings.update(load_json(ANCHOR_CACHE)["embeddings"])
    return embeddings


def nearest_record(
    vector: np.ndarray,
    matrix: np.ndarray,
    chunks: list[Any],
    indices: list[int],
) -> tuple[Any, float]:
    sims = matrix[np.array(indices, dtype=int)] @ vector
    local = int(np.argmax(sims))
    return chunks[indices[local]], float(sims[local])


def top_group(hits: dict[str, int]) -> str:
    if not hits:
        return ""
    return sorted(hits.items(), key=lambda item: (-item[1], item[0]))[0][0]


def public_chunk_row(
    chunk: Any,
    coord: dict[str, float],
    text: str,
    extra: dict[str, Any],
) -> dict[str, Any]:
    style_hits = count_groups(text, STYLE_GROUPS)
    marker_hits = count_groups(text, SOURCE_MARKERS)
    return {
        "chunk_id": chunk.chunk_id,
        "author": chunk.author,
        "work": chunk.work,
        "chunk_index": chunk.chunk_index,
        "line_start": chunk.line_start,
        "line_end": chunk.line_end,
        "source_url": chunk.source_url,
        "text_sha256": extra.get("text_sha256"),
        "text_char_count": len(text),
        "actual_token_count": chunk.actual_token_count,
        "replacement_chars": text.count("\ufffd"),
        "x": coord["x"],
        "y": coord["y"],
        "style_hits": style_hits,
        "style_top_group": top_group(style_hits),
        "source_marker_hits": marker_hits,
        "source_marker_top_group": top_group(marker_hits),
        "top_terms": top_cjk_terms(text, limit=10),
        **extra,
    }


def shinran_protrusion_zone(row: dict[str, Any], text: str) -> str:
    volume = row.get("volume_label", "")
    style = row.get("style_top_group", "")
    marker_hits = row.get("source_marker_hits", {})

    if volume == "信巻" and (
        style in {"信・三心", "罪・救済", "願・回向"}
        or any(term in text for term in ["阿闍世", "提婆", "五逆", "慚愧", "地獄", "涅槃經"])
    ):
        return "信巻: 信/三心・罪救済"
    if volume == "化身土巻" and any(term in text for term in ["大集", "日藏", "月藏", "鬼神", "星宿"]):
        return "化身土巻: 護法・鬼神・宇宙秩序"
    if volume == "化身土巻" and any(term in text for term in ["老子", "孔子", "史記", "論語", "外道", "道士"]):
        return "化身土巻: 外教批判"
    if volume == "化身土巻" and style in {"方便・化身土", "廃立・取捨", "正雑・諸行"}:
        return "化身土巻: 方便・真仮整理"
    if volume in {"行巻", "真仏土巻"} and style in {"名号・真実", "選択・本願", "願・回向", "念仏・称名"}:
        return f"{volume}: 名号・本願・真実"
    if marker_hits.get("祖師名"):
        return f"{volume}: 祖師引用密度"
    if marker_hits.get("経名"):
        return f"{volume}: 経典引用密度"
    return f"{volume}: その他親鸞独自候補"


def count_by(rows: list[dict[str, Any]], *keys: str) -> list[dict[str, Any]]:
    counter: Counter[tuple[Any, ...]] = Counter(tuple(row.get(key, "") for key in keys) for row in rows)
    out = []
    for values, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        record = {key: value for key, value in zip(keys, values)}
        record["chunk_count"] = count
        out.append(record)
    return out


def distribution(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "median": None, "mean": None, "max": None}
    arr = np.array(values, dtype=float)
    return {
        "min": rounded(float(arr.min())),
        "median": rounded(float(np.median(arr))),
        "mean": rounded(float(arr.mean())),
        "max": rounded(float(arr.max())),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            flat = dict(row)
            for key, value in list(flat.items()):
                if isinstance(value, (dict, list, tuple)):
                    flat[key] = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            writer.writerow(flat)


def main() -> None:
    chunks = make_all_chunks()
    embeddings = load_embeddings()
    map_data = load_json(MAP_PATH)
    coords = {row["chunk_id"]: {"x": row["x"], "y": row["y"]} for row in map_data["chunks"]}

    missing = [chunk.chunk_id for chunk in chunks if chunk.chunk_id not in embeddings or chunk.chunk_id not in coords]
    if missing:
        raise RuntimeError(f"missing embeddings/coords for {len(missing)} chunks: {missing[:3]}")

    matrix = normalize(np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float))
    indices_by_author: dict[str, list[int]] = defaultdict(list)
    for index, chunk in enumerate(chunks):
        indices_by_author[chunk.author].append(index)

    anchor_authors = [author for author in indices_by_author if author not in {"法然", "親鸞"}]
    anchor_indices = [index for author in anchor_authors for index in indices_by_author[author]]
    honen_indices = indices_by_author["法然"]
    shinran_indices = indices_by_author["親鸞"]

    author_centroids = {
        author: matrix[np.array(indices, dtype=int)].mean(axis=0)
        for author, indices in indices_by_author.items()
    }

    all_rows: list[dict[str, Any]] = []
    honen_rows: list[dict[str, Any]] = []
    shinran_rows: list[dict[str, Any]] = []

    for index, chunk in enumerate(chunks):
        vector = matrix[index]
        nonself_indices = [i for i, other in enumerate(chunks) if other.author != chunk.author]
        nearest_nonself, nonself_cos = nearest_record(vector, matrix, chunks, nonself_indices)
        nearest_anchor, anchor_cos = nearest_record(vector, matrix, chunks, anchor_indices)
        extra = {
            "text_sha256": embeddings[chunk.chunk_id]["text_sha256"],
            "nearest_nonself_author": nearest_nonself.author,
            "nearest_nonself_work": nearest_nonself.work,
            "nearest_nonself_chunk_index": nearest_nonself.chunk_index,
            "nearest_nonself_line_start": nearest_nonself.line_start,
            "nearest_nonself_line_end": nearest_nonself.line_end,
            "nearest_nonself_cosine": rounded(nonself_cos),
            "nearest_anchor_author": nearest_anchor.author,
            "nearest_anchor_work": nearest_anchor.work,
            "nearest_anchor_chunk_index": nearest_anchor.chunk_index,
            "nearest_anchor_cosine": rounded(anchor_cos),
            "cosine_to_honen_centroid": rounded(float(np.dot(vector, author_centroids["法然"]) / (np.linalg.norm(author_centroids["法然"]) or 1.0))),
            "cosine_to_shinran_centroid": rounded(float(np.dot(vector, author_centroids["親鸞"]) / (np.linalg.norm(author_centroids["親鸞"]) or 1.0))),
        }
        if chunk.author == "法然":
            extra["section_label"] = range_label(chunk.line_start, HONEN_SECTION_RANGES, "未分類")
            extra["semantic_role"] = (
                "paratext_or_terminal_candidate"
                if range_label(chunk.line_start, HONEN_SECTION_RANGES, "未分類") in {"序", "末尾・奥書系"}
                else "doctrinal_argument_candidate"
            )
            extra["nearest_shinran_cosine"] = rounded(nearest_record(vector, matrix, chunks, shinran_indices)[1])
            row = public_chunk_row(chunk, coords[chunk.chunk_id], chunk.text, extra)
            honen_rows.append(row)
        elif chunk.author == "親鸞":
            extra["volume_label"] = range_label(chunk.line_start, SHINRAN_VOLUME_RANGES, "未分類")
            extra["nearest_honen_cosine"] = rounded(nearest_record(vector, matrix, chunks, honen_indices)[1])
            row = public_chunk_row(chunk, coords[chunk.chunk_id], chunk.text, extra)
            shinran_rows.append(row)
        else:
            row = public_chunk_row(chunk, coords[chunk.chunk_id], chunk.text, extra)
        all_rows.append(row)

    # Protrusion: combine 2D distance to non-Honen with lower nearest non-Honen cosine.
    non_honen_points = np.array([[coords[chunks[i].chunk_id]["x"], coords[chunks[i].chunk_id]["y"]] for i in range(len(chunks)) if chunks[i].author != "法然"])
    for row in honen_rows:
        point = np.array([row["x"], row["y"]], dtype=float)
        row["nearest_non_honen_2d_distance"] = rounded(float(np.linalg.norm(non_honen_points - point, axis=1).min()))
        row["protrusion_score"] = rounded(row["nearest_non_honen_2d_distance"] * (1.0 - row["nearest_nonself_cosine"]))
    honen_table = sorted(
        honen_rows,
        key=lambda row: (row["semantic_role"] != "doctrinal_argument_candidate", -row["protrusion_score"]),
    )[:24]

    non_shinran_points = np.array([[coords[chunks[i].chunk_id]["x"], coords[chunks[i].chunk_id]["y"]] for i in range(len(chunks)) if chunks[i].author != "親鸞"])
    for row in shinran_rows:
        point = np.array([row["x"], row["y"]], dtype=float)
        row["nearest_non_shinran_2d_distance"] = rounded(float(np.linalg.norm(non_shinran_points - point, axis=1).min()))
        row["protrusion_score"] = rounded(row["nearest_non_shinran_2d_distance"] * (1.0 - row["nearest_nonself_cosine"]))
        if row["nearest_nonself_author"] == "法然":
            row["affinity_zone"] = "法然近接"
        elif row["nearest_nonself_author"] in {"源信", "道綽", "曇鸞", "善導", "天親", "龍樹"}:
            row["affinity_zone"] = f"{row['nearest_nonself_author']}近接"
        else:
            row["affinity_zone"] = "その他"
    iso_threshold = float(np.quantile([row["nearest_non_shinran_2d_distance"] for row in shinran_rows], 0.9))
    for row in shinran_rows:
        if row["nearest_non_shinran_2d_distance"] >= iso_threshold:
            row["affinity_zone"] = "親鸞独自候補"
        chunk = next(item for item in chunks if item.chunk_id == row["chunk_id"])
        row["protrusion_zone_label"] = shinran_protrusion_zone(row, chunk.text)
    shinran_table = sorted(
        shinran_rows,
        key=lambda row: (row["volume_label"], row["affinity_zone"], -row["nearest_non_shinran_2d_distance"]),
    )
    shinran_protrusion_table = sorted(
        shinran_rows,
        key=lambda row: (row["affinity_zone"] != "親鸞独自候補", -row["protrusion_score"]),
    )[:24]

    volume_summary = count_by(shinran_rows, "volume_label", "affinity_zone")
    volume_nearest_summary = count_by(shinran_rows, "volume_label", "nearest_nonself_author")
    honen_section_summary = count_by(honen_rows, "section_label", "style_top_group", "nearest_nonself_author")
    honen_protrusion_summary = {
        "by_section": count_by(honen_table, "section_label"),
        "by_style": count_by(honen_table, "style_top_group"),
        "by_nearest": count_by(honen_table, "nearest_nonself_author"),
    }
    shinran_protrusion_summary = {
        "by_volume": count_by(shinran_protrusion_table, "volume_label"),
        "by_zone": count_by(shinran_protrusion_table, "protrusion_zone_label"),
        "by_style": count_by(shinran_protrusion_table, "style_top_group"),
        "by_nearest": count_by(shinran_protrusion_table, "nearest_nonself_author"),
    }
    layer_summary = {
        "semantic_layer": {
            "honen_nearest_nonself": count_by(honen_rows, "nearest_nonself_author"),
            "shinran_nearest_nonself": count_by(shinran_rows, "nearest_nonself_author"),
            "shinran_volume_affinity": volume_summary,
            "honen_protrusion_score_distribution": distribution([row["protrusion_score"] for row in honen_rows]),
            "shinran_protrusion_score_distribution": distribution([row["protrusion_score"] for row in shinran_rows]),
            "shinran_isolation_2d_p90_threshold": rounded(iso_threshold),
            "protrusion_comparison": {
                "honen": honen_protrusion_summary,
                "shinran": shinran_protrusion_summary,
            },
        },
        "style_layer": {
            "honen": count_by(honen_rows, "style_top_group"),
            "shinran": count_by(shinran_rows, "volume_label", "style_top_group"),
        },
        "source_marker_layer": {
            "honen": count_by(honen_rows, "source_marker_top_group"),
            "shinran": count_by(shinran_rows, "volume_label", "source_marker_top_group"),
        },
    }

    output = {
        "title": "Readable SAT safe map analysis 2026-06-04",
        "method": {
            "basis": "SAT kanbun, Unicode-safe 700-token chunks, 100-token overlap",
            "embedding_model": "text-embedding-3-large",
            "raw_text_policy": "no raw/chunk text is written; features, line refs, hashes, and metrics only",
            "volume_label_policy": "Shinran volume labels are assigned from SAT line ranges and should be treated as approximate where chunks overlap boundaries",
        },
        "input_paths": {
            "focus_cache": str(FOCUS_CACHE.relative_to(ROOT)),
            "anchor_cache": str(ANCHOR_CACHE.relative_to(ROOT)),
            "map": str(MAP_PATH.relative_to(ROOT)),
        },
        "chunk_counts": dict(Counter(row["author"] for row in all_rows)),
        "layer_summary": layer_summary,
        "honen_protrusion_table": honen_table,
        "shinran_protrusion_table": shinran_protrusion_table,
        "shinran_volume_affinity_table": shinran_table,
        "shinran_volume_nearest_summary": volume_nearest_summary,
        "honen_section_summary": honen_section_summary,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_csv(
        HONEN_CSV,
        honen_table,
        [
            "chunk_index", "section_label", "semantic_role", "line_start", "line_end",
            "nearest_nonself_author", "nearest_nonself_work", "nearest_nonself_chunk_index",
            "nearest_nonself_cosine", "nearest_anchor_author", "nearest_anchor_work",
            "nearest_anchor_cosine", "nearest_non_honen_2d_distance", "protrusion_score",
            "style_top_group", "style_hits", "source_marker_top_group", "source_marker_hits",
            "top_terms", "text_sha256", "text_char_count", "replacement_chars",
        ],
    )
    write_csv(
        SHINRAN_CSV,
        shinran_table,
        [
            "chunk_index", "volume_label", "affinity_zone", "line_start", "line_end",
            "nearest_nonself_author", "nearest_nonself_work", "nearest_nonself_chunk_index",
            "nearest_nonself_cosine", "nearest_honen_cosine", "nearest_anchor_author",
            "nearest_anchor_work", "nearest_anchor_cosine", "nearest_non_shinran_2d_distance",
            "style_top_group", "style_hits", "source_marker_top_group", "source_marker_hits",
            "top_terms", "text_sha256", "text_char_count", "replacement_chars",
        ],
    )
    write_csv(
        SHINRAN_PROTRUSION_CSV,
        shinran_protrusion_table,
        [
            "chunk_index", "volume_label", "affinity_zone", "protrusion_zone_label",
            "line_start", "line_end", "nearest_nonself_author", "nearest_nonself_work",
            "nearest_nonself_chunk_index", "nearest_nonself_cosine", "nearest_honen_cosine",
            "nearest_anchor_author", "nearest_anchor_work", "nearest_anchor_cosine",
            "nearest_non_shinran_2d_distance", "protrusion_score", "style_top_group",
            "style_hits", "source_marker_top_group", "source_marker_hits", "top_terms",
            "text_sha256", "text_char_count", "replacement_chars",
        ],
    )

    doc = render_doc(output)
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {HONEN_CSV.relative_to(ROOT)}")
    print(f"wrote {SHINRAN_CSV.relative_to(ROOT)}")
    print(f"wrote {SHINRAN_PROTRUSION_CSV.relative_to(ROOT)}")
    print(f"wrote {DOC_PATH.relative_to(ROOT)}")


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
            if isinstance(value, float):
                value = rounded(value)
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            values.append(str(value).replace("|", "/"))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def render_doc(output: dict[str, Any]) -> str:
    semantic = output["layer_summary"]["semantic_layer"]
    comparison = semantic["protrusion_comparison"]
    lines: list[str] = [
        "# Readable Map Analysis 2026-06-04",
        "",
        "SAT 漢文・Unicode-safe 700 token chunk・`text-embedding-3-large` の既存 map を、本文非公開のまま読める分析表へ変換した。",
        "",
        "## 結論メモ",
        "",
        "- 法然『選択集』のはみ出しは、念仏の意味そのものの差というより、`正雑二行`、`諸行との取捨`、`本願`、`付属/証誠` などを使って念仏を選び出す論証のまとまりとして見える。",
        "- 親鸞『教行信証』のはみ出しは、法然と同じ念仏選択論ではなく、`信/三心・罪救済`、`化身土の方便/真仮整理`、`護法・鬼神・宇宙秩序`、`外教批判` などへ分岐する。",
        "- したがって現段階では、「法然は念仏選択の論証、親鸞は本願・信・証の典拠的体系化」という作業仮説は map と語群集計で支えられる。ただし、歴史的影響の証明には典拠マーカー層の精査が必要である。",
        "",
        "## 意味層",
        "",
        "法然 chunks の最近傍非自己:",
        "",
        *md_table(semantic["honen_nearest_nonself"], [("最近傍", "nearest_nonself_author"), ("chunks", "chunk_count")]),
        "",
        "親鸞 chunks の最近傍非自己:",
        "",
        *md_table(semantic["shinran_nearest_nonself"], [("最近傍", "nearest_nonself_author"), ("chunks", "chunk_count")]),
        "",
        "親鸞の巻別・近接ゾーン:",
        "",
        *md_table(semantic["shinran_volume_affinity"], [("巻", "volume_label"), ("zone", "affinity_zone"), ("chunks", "chunk_count")]),
        "",
        "## 法然はみ出し表 上位",
        "",
        *md_table(
            output["honen_protrusion_table"],
            [
                ("idx", "chunk_index"),
                ("位置", "section_label"),
                ("line", "line_start"),
                ("近傍", "nearest_nonself_author"),
                ("anchor", "nearest_anchor_author"),
                ("style", "style_top_group"),
                ("score", "protrusion_score"),
            ],
            limit=12,
        ),
        "",
        "## 親鸞はみ出し表 上位",
        "",
        *md_table(
            output["shinran_protrusion_table"],
            [
                ("idx", "chunk_index"),
                ("巻", "volume_label"),
                ("zone", "protrusion_zone_label"),
                ("line", "line_start"),
                ("近傍", "nearest_nonself_author"),
                ("anchor", "nearest_anchor_author"),
                ("style", "style_top_group"),
                ("score", "protrusion_score"),
            ],
            limit=12,
        ),
        "",
        "## 法然/親鸞はみ出し比較",
        "",
        "法然はみ出し上位の位置:",
        "",
        *md_table(comparison["honen"]["by_section"], [("位置", "section_label"), ("chunks", "chunk_count")]),
        "",
        "親鸞はみ出し上位の巻:",
        "",
        *md_table(comparison["shinran"]["by_volume"], [("巻", "volume_label"), ("chunks", "chunk_count")]),
        "",
        "親鸞はみ出し上位の内容ゾーン:",
        "",
        *md_table(comparison["shinran"]["by_zone"], [("zone", "protrusion_zone_label"), ("chunks", "chunk_count")]),
        "",
        "## 三層分析の最小版",
        "",
        "- 意味層: cached embedding の高次元 cosine と、既存 2D map の距離を併用した。",
        "- 文体語彙層: `選択・本願`、`正雑・諸行`、`廃立・取捨`、`信・三心`、`願・回向`、`名号・真実` などの語群を数えた。",
        "- 典拠マーカー層: 経名、論釈名、祖師名、引用導入句を数えた。",
        "",
        "## 限界",
        "",
        "- chunk は 100 token overlap を持つため、巻境界・章境界をまたぐ chunk がある。巻別ラベルは line_start 基準の近似である。",
        "- 2D map は PCA の低次元表示であり、高次元 cosine と併読する必要がある。",
        "- 語群集計は辞書ベースの最小版であり、語の文脈や否定・引用者の区別はまだ見ていない。",
        "- 本文は出力していない。CSV/JSON は line refs、hash、語群カウント、近傍指標だけを含む。",
        "",
        "## 出力",
        "",
        f"- `{OUT_JSON.relative_to(ROOT)}`",
        f"- `{HONEN_CSV.relative_to(ROOT)}`",
        f"- `{SHINRAN_CSV.relative_to(ROOT)}`",
        f"- `{SHINRAN_PROTRUSION_CSV.relative_to(ROOT)}`",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
