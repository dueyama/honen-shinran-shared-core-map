#!/usr/bin/env python3
"""Summarize Shinran-only zones in the Honen/Shinran anchor map.

This reads local-only chunk text but writes only labels, coordinates, source
page ranges, keyword flags, and interpretive summaries. It does not write raw
source text.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from make_predecessor_style_embedding_map import make_token_chunks
from make_simple_2d_map import SeitenParser


ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "data" / "outputs" / "honen_shinran_high_priest_anchor_map_meta.json"
OUT_MD = ROOT / "docs" / "shinran-isolated-zones-2026-06-03.md"
OUT_JSON = ROOT / "data" / "outputs" / "shinran_isolated_zones_meta.json"
RAW_SEITEN = ROOT / "data" / "raw" / "seiten"
THRESHOLD = 0.10

KEYWORDS = [
    "名号",
    "本願",
    "往生",
    "無量寿",
    "阿弥陀",
    "不退",
    "信心",
    "疑",
    "涅槃",
    "阿闍世",
    "提婆",
    "五逆",
    "慙愧",
    "慚愧",
    "耆婆",
    "地獄",
    "餓鬼",
    "邪見",
    "六師",
    "老子",
    "孔子",
    "史記",
    "周書",
    "論語",
    "道士",
    "大集",
    "梵王",
    "四天王",
    "鬼神",
    "星宿",
    "暦",
    "正法",
    "末法",
    "魔",
    "化身",
    "方便",
    "胎生",
    "雑行",
    "専修",
    "回向",
]


ZONE_SUMMARIES = {
    "A": {
        "label": "A: 行巻・真仏土の上方島",
        "summary": "諸仏称讃、名号、本願力、無量寿・阿弥陀の光明/寿命、不退をめぐる展開。法然・高僧アンカーの共有核に近い念仏論ではあるが、複数経典を連結して名号と仏徳を押し出す親鸞側の構成が強く出ている。",
    },
    "B": {
        "label": "B: 信巻右下の阿闍世・涅槃経島",
        "summary": "『涅槃経』系の阿闍世物語、父殺し、五逆、提婆達多、耆婆、慙愧、地獄、六師/邪見をめぐる長い引用群。親鸞の信の問題が、単なる安心論ではなく、極悪・悔過・救済可能性の場面へ広がる領域として見える。",
    },
    "C": {
        "label": "C: 化身土末の護法・鬼神・宇宙秩序島",
        "summary": "『大集経』などに見える梵王、四天王、鬼神、星宿、暦、護持の語彙が集まる領域。浄土教の中心語彙から外れ、末法・護法・世俗世界の秩序へ視野が広がる。",
    },
    "D": {
        "label": "D: 化身土末の外教批判島",
        "summary": "老子、孔子、『史記』『周書』『論語』、道士など、仏教外の典拠や外教批判が前面に出る領域。図上でも親鸞側右下に孤立しやすく、浄土教内部の祖師アンカーでは説明しにくい。",
    },
    "E": {
        "label": "E: 化身土本の方便・雑行島",
        "summary": "方便、雑行、専修、回向、疑、胎生など、真実/方便の区別や化身土の構造に関わる領域。法然の専修念仏論と接続するが、親鸞側では辺地・胎宮・方便真門の整理として再配置される。",
    },
}


def normalize(value: str) -> str:
    return re.sub(r"\s+", "", value)


def page_title(page: str) -> str:
    path = RAW_SEITEN / f"{page}.html"
    raw = path.read_text(encoding="utf-8", errors="ignore")
    parser = SeitenParser({"honbun", "s_sage", "l_nobegaki"})
    parser.feed(raw)
    title = re.sub(r"<[^>]+>", "", parser.title)
    return title.split("/")[-1].strip()


def zone_for(page_start: str, x: float, y: float, keywords: list[str]) -> str:
    page = int(page_start) if page_start.isdigit() else -1
    if 152 <= page <= 180 and y > 0.25:
        return "A"
    if 300 <= page <= 305 and y > 0.25:
        return "A"
    if 252 <= page <= 270 and x > 0.25 and y < 0.0:
        return "B"
    if 369 <= page <= 382 and x > 0.25:
        return "C"
    if 389 <= page <= 392 and x > 0.15 and y < 0.0:
        return "D"
    if 335 <= page <= 350:
        return "E"
    if {"老子", "孔子", "史記", "道士"}.intersection(keywords):
        return "D"
    if {"鬼神", "星宿", "四天王", "大集"}.intersection(keywords):
        return "C"
    if {"阿闍世", "提婆", "五逆", "耆婆", "慙愧", "慚愧"}.intersection(keywords):
        return "B"
    return "other"


def nearest_non_shinran(records: list[dict[str, Any]], record: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    others = [row for row in records if row["author"] != "親鸞"]
    nearest = min(
        others,
        key=lambda row: math.dist([record["x"], record["y"]], [row["x"], row["y"]]),
    )
    distance = math.dist([record["x"], record["y"]], [nearest["x"], nearest["y"]])
    return distance, nearest


def build_summary() -> dict[str, Any]:
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    records = meta["chunks"]
    token_chunks = {item.chunk.chunk_id: item for item in make_token_chunks()}
    selected = []

    for record in records:
        if record["author"] != "親鸞":
            continue
        distance, nearest = nearest_non_shinran(records, record)
        if distance < THRESHOLD:
            continue
        item = token_chunks[record["chunk_id"]]
        text = normalize(item.chunk.text)
        keywords = [word for word in KEYWORDS if word in text]
        zone = zone_for(item.page_start, float(record["x"]), float(record["y"]), keywords)
        selected.append(
            {
                "chunk_id": record["chunk_id"],
                "page_start": item.page_start,
                "page_end": item.page_end,
                "title": page_title(item.page_start),
                "x": round(float(record["x"]), 6),
                "y": round(float(record["y"]), 6),
                "nearest_non_shinran_author": nearest["author"],
                "nearest_non_shinran_chunk": nearest["chunk_id"],
                "nearest_non_shinran_distance": round(distance, 6),
                "keywords": keywords,
                "zone": zone,
            }
        )

    selected.sort(key=lambda row: row["nearest_non_shinran_distance"], reverse=True)
    zones: dict[str, Any] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        grouped[row["zone"]].append(row)
    for zone_id, rows in grouped.items():
        keyword_counts = Counter(word for row in rows for word in row["keywords"])
        zones[zone_id] = {
            "label": ZONE_SUMMARIES.get(zone_id, {"label": zone_id})["label"],
            "summary": ZONE_SUMMARIES.get(zone_id, {"summary": ""})["summary"],
            "chunk_count": len(rows),
            "page_ranges": [f"{row['page_start']}-{row['page_end']}" for row in rows],
            "top_keywords": keyword_counts.most_common(12),
            "chunks": rows,
        }

    return {
        "title": "Shinran-only zones in the Honen/Shinran high-priest anchor map",
        "threshold": THRESHOLD,
        "method": {
            "selection": "Shinran chunks whose nearest non-Shinran point in the fixed PCA plane is at least threshold.",
            "non_shinran_points": "Honen chunks plus high-priest/source anchor chunks.",
            "raw_text_policy": "Local text was read to flag keywords, but raw text is not written to this output.",
        },
        "selected_chunk_count": len(selected),
        "zones": zones,
        "chunks": selected,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Shinran-Only Zones 2026-06-03",
        "",
        "## 目的",
        "",
        "法然・親鸞 map に高僧文献アンカーを投影した図で、親鸞点だけが入り込んでいるように見える領域を拾い、その内容を本文非公開のまま要約する。",
        "",
        "## 判定方法",
        "",
        f"- 対象: 親鸞『教行信証』 chunks。",
        f"- 非親鸞点: 法然『選択本願念仏集』 chunks と高僧文献アンカー chunks。",
        f"- 孤立判定: 固定 PCA 面で最寄り非親鸞点までの距離が `{summary['threshold']}` 以上。",
        f"- 該当: {summary['selected_chunk_count']} chunks。",
        "- raw text は出力しない。本文はローカルで keyword flag のためだけに読む。",
        "",
        "## 主要ゾーン",
        "",
    ]
    zone_order = ["A", "B", "C", "D", "E", "other"]
    for zone_id in zone_order:
        zone = summary["zones"].get(zone_id)
        if not zone:
            continue
        lines.extend(
            [
                f"### {zone['label']}",
                "",
                zone["summary"] or "未分類の孤立点。",
                "",
                f"- chunks: {zone['chunk_count']}",
                f"- page ranges: {', '.join(zone['page_ranges'])}",
                "- top keywords: "
                + ", ".join(f"{word}({count})" for word, count in zone["top_keywords"]),
                "",
                "| chunk | pages | x | y | nearest non-Shinran | distance | keywords |",
                "| --- | --- | ---: | ---: | --- | ---: | --- |",
            ]
        )
        for row in zone["chunks"]:
            keywords = ", ".join(row["keywords"])
            lines.append(
                "| {chunk_id} | {page_start}-{page_end} | {x:.3f} | {y:.3f} | {near} | {dist:.3f} | {keywords} |".format(
                    chunk_id=row["chunk_id"],
                    page_start=row["page_start"],
                    page_end=row["page_end"],
                    x=row["x"],
                    y=row["y"],
                    near=row["nearest_non_shinran_author"],
                    dist=row["nearest_non_shinran_distance"],
                    keywords=keywords,
                )
            )
        lines.append("")

    lines.extend(
        [
            "## 読み筋",
            "",
            "現時点では、親鸞だけが深く入り込む領域は一枚岩ではない。少なくとも、名号・本願力を押し出す行巻/真仏土の島、阿闍世・五逆・慙愧をめぐる信巻の島、化身土末の護法/鬼神/星宿の島、老子・孔子・史記などを含む外教批判の島、化身土本の方便・雑行の島に分かれる。",
            "",
            "この結果は、親鸞の右方向の広がりを単に「法然から離れた」と読むより、共有された専修念仏の中心から、罪・救済、末法/護法、外教批判、方便真門の整理へ分岐していると読む方がよいことを示す。",
            "",
            "## 注意",
            "",
            "- これは semantic layer の孤立領域抽出であり、歴史的影響の証明ではない。",
            "- PCA 2D 上の距離で拾っているため、高次元 embedding 空間での近傍確認が次に必要。",
            "- seiten の日本語読み本文と SAT 漢文アンカーが混在しているため、style/script effect を別レイヤーで確認する必要がある。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = build_summary()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_markdown(summary), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"selected chunks: {summary['selected_chunk_count']}")


if __name__ == "__main__":
    main()
