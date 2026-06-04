#!/usr/bin/env python3
"""Render a text-free visual summary for shared-core/protrusion tables.

The figure visualizes the qualitative region summary and nearest-neighbor
counts used in the paper.  It reads only existing text-free CSV output and
does not expose chunk text or embeddings.
"""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data/outputs/nearest_neighbor_subsampling_2026-06-04_text-embedding-3-large_700_100.csv"
FIGURE_PATH = ROOT / "docs/figures/shared-core-protrusion-nearest-bars.png"

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

REGIONS = [
    {
        "label": "共有核",
        "sign": "法然・親鸞が相互近接\n道綽・善導も重なる",
        "terms": "念仏・称名\n往生・浄土\n信・三心",
        "reading": "専修念仏・浄土教的\n共通問題圏",
        "color": (89, 138, 132),
    },
    {
        "label": "法然はみ出し",
        "sign": "非法然点から相対的に離れる\n選択論証部に集中",
        "terms": "正雑二行\n三輩・一向専念\n本願念仏 / 付属・証誠",
        "reading": "念仏を諸行から\n選び出す論証",
        "color": (43, 110, 164),
    },
    {
        "label": "親鸞はみ出し",
        "sign": "非親鸞点から相対的に離れる\n信巻・化身土巻に集中",
        "terms": "信巻 / 化身土巻\n罪・救済\n方便・化身土",
        "reading": "本願・信・証・真仏土/化身土の\n典拠的体系",
        "color": (176, 74, 70),
    },
]

GROUP_COLORS = {
    "親鸞": (183, 76, 72),
    "法然": (43, 110, 164),
    "道綽": (112, 137, 74),
    "源信": (131, 94, 151),
    "曇鸞": (194, 128, 49),
    "天親": (92, 137, 153),
    "善導": (91, 149, 96),
    "龍樹": (130, 130, 130),
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=0)
    return ImageFont.load_default()


def alpha(color: tuple[int, int, int], value: int) -> tuple[int, int, int, int]:
    return (*color, value)


def draw_text_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fill: tuple[int, int, int],
    text_font: ImageFont.ImageFont,
    line_gap: int = 7,
) -> None:
    x0, y0, x1, _ = box
    y = y0
    max_width = x1 - x0
    for raw_line in text.splitlines():
        line = ""
        for char in raw_line:
            candidate = line + char
            if draw.textlength(candidate, font=text_font) <= max_width:
                line = candidate
            else:
                draw.text((x0, y), line, fill=fill, font=text_font)
                y += text_font.size + line_gap
                line = char
        if line:
            draw.text((x0, y), line, fill=fill, font=text_font)
            y += text_font.size + line_gap


def read_counts() -> dict[str, list[dict[str, float | int | str]]]:
    rows: dict[str, list[dict[str, float | int | str]]] = {"法然": [], "親鸞": []}
    with INPUT_CSV.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            count = int(row["simple_count"])
            if count <= 0:
                continue
            target = row["target_author"]
            if target not in rows:
                continue
            rows[target].append(
                {
                    "group": row["nearest_group"],
                    "count": count,
                    "ratio": float(row["simple_ratio"]),
                }
            )
    for target in rows:
        rows[target].sort(key=lambda item: (-int(item["count"]), str(item["group"])))
    return rows


def draw_region_flow(draw: ImageDraw.ImageDraw, x: int, y: int, width: int) -> int:
    title_font = font(32)
    small_font = font(20)
    label_font = font(23)
    body_font = font(20)

    draw.text((x, y), "共有核とはみ出し領域", fill=(39, 36, 31), font=title_font)
    draw.text((x, y + 42), "幅は量を表さない。計算サイン・語群・解釈の対応を示す模式図。", fill=(103, 96, 86), font=small_font)

    y += 88
    col_x = [x, x + 334, x + 765, x + 1188]
    col_w = [250, 330, 315, width - 1188]
    headers = ["領域", "計算上のサイン", "主な語群・巻/章", "解釈"]
    for i, header in enumerate(headers):
        draw.text((col_x[i], y), header, fill=(79, 73, 64), font=small_font)
    y += 34

    row_h = 134
    for idx, region in enumerate(REGIONS):
        row_y = y + idx * (row_h + 20)
        color = region["color"]
        draw.rounded_rectangle((col_x[0], row_y, col_x[0] + col_w[0], row_y + row_h), radius=16, fill=alpha(color, 230))
        draw_text_box(draw, (col_x[0] + 22, row_y + 45, col_x[0] + col_w[0] - 18, row_y + row_h), region["label"], (255, 255, 255), label_font)

        for col_index, key in enumerate(["sign", "terms", "reading"], start=1):
            bx0 = col_x[col_index]
            bx1 = bx0 + col_w[col_index]
            draw.rounded_rectangle((bx0, row_y, bx1, row_y + row_h), radius=14, fill=(255, 255, 255), outline=alpha(color, 145), width=2)
            draw_text_box(draw, (bx0 + 20, row_y + 23, bx1 - 16, row_y + row_h), str(region[key]), (44, 40, 35), body_font)

        for left, right in [(0, 1), (1, 2), (2, 3)]:
            cy = row_y + row_h // 2
            x0 = col_x[left] + col_w[left] + 12
            x1 = col_x[right] - 16
            draw.line((x0, cy, x1, cy), fill=alpha(color, 170), width=8)
            draw.polygon([(x1, cy), (x1 - 18, cy - 13), (x1 - 18, cy + 13)], fill=alpha(color, 190))

    return y + len(REGIONS) * (row_h + 20) + 24


def draw_bars(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    title: str,
    rows: list[dict[str, float | int | str]],
    target_total: int,
    width: int,
) -> None:
    title_font = font(27)
    label_font = font(20)
    small_font = font(18)
    max_count = max(int(row["count"]) for row in rows)
    bar_x = x + 116
    bar_w = width - 240
    row_h = 44

    draw.text((x, y), title, fill=(39, 36, 31), font=title_font)
    draw.text((x, y + 36), "単純最近傍非自己のchunk数。候補数補正とは別に読む。", fill=(103, 96, 86), font=small_font)
    y += 78

    for index, row in enumerate(rows):
        yy = y + index * row_h
        group = str(row["group"])
        count = int(row["count"])
        ratio = float(row["ratio"])
        color = GROUP_COLORS.get(group, (100, 100, 100))
        draw.text((x, yy + 8), group, fill=(44, 40, 35), font=label_font)
        draw.rounded_rectangle((bar_x, yy + 8, bar_x + bar_w, yy + 30), radius=8, fill=(235, 231, 223))
        filled = int(bar_w * count / max_count)
        draw.rounded_rectangle((bar_x, yy + 8, bar_x + filled, yy + 30), radius=8, fill=color)
        draw.text((bar_x + filled + 12, yy + 3), f"{count} ({ratio * 100:.1f}%)", fill=(44, 40, 35), font=small_font)

    draw.text((bar_x, y + len(rows) * row_h + 10), f"対象chunk数: {target_total}", fill=(103, 96, 86), font=small_font)


def render() -> None:
    counts = read_counts()
    width, height = 1700, 1220
    image = Image.new("RGB", (width, height), (251, 250, 247))
    draw = ImageDraw.Draw(image, "RGBA")

    flow_bottom = draw_region_flow(draw, 76, 54, width - 152)

    draw.line((76, flow_bottom + 4, width - 76, flow_bottom + 4), fill=(216, 208, 194), width=2)
    bar_y = flow_bottom + 50
    panel_w = 730
    draw_bars(draw, 100, bar_y, "法然チャンクの最近傍", counts["法然"], 69, panel_w)
    draw_bars(draw, 890, bar_y, "親鸞チャンクの最近傍", counts["親鸞"], 191, panel_w)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(FIGURE_PATH)
    print(f"Wrote {FIGURE_PATH}")


if __name__ == "__main__":
    render()
