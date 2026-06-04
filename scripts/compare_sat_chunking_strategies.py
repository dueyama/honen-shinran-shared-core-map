#!/usr/bin/env python3
"""Compare unsafe token-slice chunks with Unicode-safe 700-token chunks.

Inputs are the prepared SAT kanbun-basis JSONL files under data/processed.
Raw/chunk text stays local-only and is not written to public metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import tiktoken


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from make_simple_2d_map import svg_escape  # noqa: E402


PROCESSED_DIR = ROOT / "data" / "processed" / "sat_kanbun"
CACHE_DIR = ROOT / "data" / "cache"
OUT_DIR = ROOT / "data" / "outputs"
MANIFEST_PATH = PROCESSED_DIR / "manifest.json"
MODEL = os.getenv("OKYOU2_EMBEDDING_MODEL", "text-embedding-3-large")
MAX_TOKENS = int(os.getenv("OKYOU2_MAX_TOKENS", "700"))
OVERLAP = int(os.getenv("OKYOU2_OVERLAP", "100"))
BATCH_SIZE = int(os.getenv("OKYOU2_EMBEDDING_BATCH_SIZE", "64"))
API_URL = os.getenv("OPENAI_EMBEDDINGS_URL", "https://api.openai.com/v1/embeddings")
CACHE_PATH = CACHE_DIR / f"sat_chunking_strategy_compare_{MODEL}_{MAX_TOKENS}_{OVERLAP}.json"
LEGACY_SAT_CACHE_PATH = CACHE_DIR / f"honen_shinran_sat_kanbun_embeddings_{MODEL}_{MAX_TOKENS}_{OVERLAP}.json"
META_PATH = OUT_DIR / f"sat_chunking_strategy_compare_{MODEL}_{MAX_TOKENS}_{OVERLAP}.json"
SVG_PATH = OUT_DIR / f"sat_chunking_strategy_compare_{MODEL}_{MAX_TOKENS}_{OVERLAP}.svg"


@dataclass
class TextLine:
    line_ref: str
    text: str
    char_start: int
    char_end: int
    token_start: int
    token_end: int


@dataclass
class WorkText:
    id: str
    author: str
    work: str
    sat_id: str
    source_url: str
    jsonl_path: Path
    lines: list[TextLine]
    body: str


@dataclass
class Chunk:
    strategy: str
    strategy_label: str
    chunk_id: str
    legacy_chunk_id: str | None
    author: str
    work: str
    sat_id: str
    source_url: str
    chunk_index: int
    text: str
    char_start: int | None
    char_end: int | None
    token_start: int | None
    token_end: int | None
    source_token_count: int
    actual_token_count: int
    line_start: str
    line_end: str


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    return float(np.quantile(np.array(values, dtype=float), q))


def rounded(value: float | None, digits: int = 6) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def line_for_char(lines: list[TextLine], char_pos: int | None) -> str:
    if char_pos is None:
        return ""
    if char_pos < 0:
        char_pos = 0
    if lines and char_pos >= lines[-1].char_end:
        return lines[-1].line_ref
    lo = 0
    hi = len(lines) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        line = lines[mid]
        if line.char_start <= char_pos < line.char_end:
            return line.line_ref
        if char_pos < line.char_start:
            hi = mid - 1
        else:
            lo = mid + 1
    return lines[max(0, min(lo, len(lines) - 1))].line_ref if lines else ""


def line_for_token(lines: list[TextLine], token_pos: int | None) -> str:
    if token_pos is None:
        return ""
    if token_pos < 0:
        token_pos = 0
    if lines and token_pos >= lines[-1].token_end:
        return lines[-1].line_ref
    lo = 0
    hi = len(lines) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        line = lines[mid]
        if line.token_start <= token_pos < line.token_end:
            return line.line_ref
        if token_pos < line.token_start:
            hi = mid - 1
        else:
            lo = mid + 1
    return lines[max(0, min(lo, len(lines) - 1))].line_ref if lines else ""


def load_works(encoder: tiktoken.Encoding) -> list[WorkText]:
    manifest = load_json(MANIFEST_PATH)
    works: list[WorkText] = []
    for item in manifest["works"]:
        rows = read_jsonl(ROOT / item["output"]["jsonl_path"])
        lines: list[TextLine] = []
        char_cursor = 0
        token_cursor = 0
        body_parts: list[str] = []
        for row in rows:
            text = row["text"]
            tokens = encoder.encode(text)
            line = TextLine(
                line_ref=row["line_ref"],
                text=text,
                char_start=char_cursor,
                char_end=char_cursor + len(text),
                token_start=token_cursor,
                token_end=token_cursor + len(tokens),
            )
            lines.append(line)
            body_parts.append(text)
            char_cursor = line.char_end
            token_cursor = line.token_end
        body = "".join(body_parts)
        if "\ufffd" in body:
            raise ValueError(f"{item['id']}: prepared body contains U+FFFD")
        works.append(
            WorkText(
                id=item["id"],
                author=item["author"],
                work=item["work"],
                sat_id=item["sat_id"],
                source_url=item["source_url"],
                jsonl_path=ROOT / item["output"]["jsonl_path"],
                lines=lines,
                body=body,
            )
        )
    return works


def make_unsafe_chunks(work: WorkText, encoder: tiktoken.Encoding) -> list[Chunk]:
    step = MAX_TOKENS - OVERLAP
    tokens = encoder.encode(work.body)
    chunks: list[Chunk] = []
    for chunk_index, start in enumerate(range(0, len(tokens), step)):
        end = min(start + MAX_TOKENS, len(tokens))
        if end - start < MAX_TOKENS // 4 and chunks:
            break
        text = encoder.decode(tokens[start:end]).strip()
        if not text:
            continue
        line_start = line_for_token(work.lines, start)
        line_end = line_for_token(work.lines, max(start, end - 1))
        legacy_chunk_id = f"{work.author}:{work.sat_id}:{work.work}:chunk_{chunk_index:04d}"
        chunks.append(
            Chunk(
                strategy="unsafe_token_decode",
                strategy_label="旧: token slice decode",
                chunk_id=f"unsafe_token_decode:{legacy_chunk_id}",
                legacy_chunk_id=legacy_chunk_id,
                author=work.author,
                work=work.work,
                sat_id=work.sat_id,
                source_url=work.source_url,
                chunk_index=chunk_index,
                text=text,
                char_start=None,
                char_end=None,
                token_start=start,
                token_end=end,
                source_token_count=end - start,
                actual_token_count=len(encoder.encode(text)),
                line_start=line_start,
                line_end=line_end,
            )
        )
    return chunks


def make_safe_chunks(work: WorkText, encoder: tiktoken.Encoding) -> list[Chunk]:
    step = MAX_TOKENS - OVERLAP
    tokens = encoder.encode(work.body)
    decoded, offsets = encoder.decode_with_offsets(tokens)
    if decoded != work.body:
        raise ValueError(f"{work.id}: decode_with_offsets did not round-trip prepared body")

    chunks: list[Chunk] = []
    body = work.body

    for chunk_index, token_start in enumerate(range(0, len(tokens), step)):
        token_end = min(token_start + MAX_TOKENS, len(tokens))
        char_start = offsets[token_start] if token_start < len(tokens) else len(body)
        char_end = offsets[token_end] if token_end < len(tokens) else len(body)
        while char_end <= char_start and token_end < len(tokens):
            token_end += 1
            char_end = offsets[token_end] if token_end < len(tokens) else len(body)
        text = body[char_start:char_end].strip()
        actual_token_count = len(encoder.encode(text))
        while actual_token_count > MAX_TOKENS and token_end > token_start:
            token_end -= 1
            char_end = offsets[token_end] if token_end < len(tokens) else len(body)
            text = body[char_start:char_end].strip()
            actual_token_count = len(encoder.encode(text))
        if actual_token_count < MAX_TOKENS // 4 and chunks:
            break
        if not text:
            continue
        if "\ufffd" in text:
            raise ValueError(f"{work.id} safe chunk {chunk_index} contains U+FFFD")
        line_start = line_for_char(work.lines, char_start)
        line_end = line_for_char(work.lines, max(char_start, char_end - 1))
        chunks.append(
            Chunk(
                strategy="safe_unicode_700",
                strategy_label="新: Unicode-safe 700",
                chunk_id=f"safe_unicode_700:{work.author}:{work.sat_id}:{work.work}:chunk_{chunk_index:04d}",
                legacy_chunk_id=None,
                author=work.author,
                work=work.work,
                sat_id=work.sat_id,
                source_url=work.source_url,
                chunk_index=chunk_index,
                text=text,
                char_start=char_start,
                char_end=char_end,
                token_start=token_start,
                token_end=token_end,
                source_token_count=token_end - token_start,
                actual_token_count=actual_token_count,
                line_start=line_start,
                line_end=line_end,
            )
        )
    return chunks


def chunk_stats(chunks: list[Chunk]) -> dict[str, Any]:
    source_tokens = [chunk.source_token_count for chunk in chunks]
    actual_tokens = [chunk.actual_token_count for chunk in chunks]
    chars = [len(chunk.text) for chunk in chunks]
    affected = [chunk for chunk in chunks if "\ufffd" in chunk.text]
    return {
        "chunk_count": len(chunks),
        "affected_chunks": len(affected),
        "replacement_chars": sum(chunk.text.count("\ufffd") for chunk in chunks),
        "source_token_count": distribution(source_tokens),
        "actual_token_count": distribution(actual_tokens),
        "char_count": distribution(chars),
    }


def distribution(values: list[int]) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    arr = np.array(values, dtype=float)
    return {
        "count": len(values),
        "min": int(arr.min()),
        "p10": rounded(percentile(values, 0.1), 3),
        "median": rounded(percentile(values, 0.5), 3),
        "mean": rounded(float(arr.mean()), 3),
        "p90": rounded(percentile(values, 0.9), 3),
        "max": int(arr.max()),
    }


def load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {"model": MODEL, "max_tokens": MAX_TOKENS, "overlap": OVERLAP, "embeddings": {}}
    data = load_json(CACHE_PATH)
    if data.get("model") != MODEL or data.get("max_tokens") != MAX_TOKENS or data.get("overlap") != OVERLAP:
        return {"model": MODEL, "max_tokens": MAX_TOKENS, "overlap": OVERLAP, "embeddings": {}}
    data.setdefault("embeddings", {})
    return data


def load_legacy_cache() -> dict[str, Any]:
    if not LEGACY_SAT_CACHE_PATH.exists():
        return {"embeddings": {}}
    data = load_json(LEGACY_SAT_CACHE_PATH)
    data.setdefault("embeddings", {})
    return data


def save_cache(cache: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    tmp.replace(CACHE_PATH)


def request_embeddings(inputs: list[str]) -> list[list[float]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    payload = json.dumps({"model": MODEL, "input": inputs}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI embeddings HTTP {exc.code}: {detail[:600]}") from exc
    data = json.loads(body)
    return [item["embedding"] for item in sorted(data["data"], key=lambda item: item["index"])]


def get_embeddings(chunks: list[Chunk]) -> np.ndarray:
    cache = load_cache()
    embeddings: dict[str, Any] = cache["embeddings"]
    legacy_embeddings: dict[str, Any] = load_legacy_cache().get("embeddings", {})

    copied_from_legacy = 0
    missing: list[Chunk] = []
    for chunk in chunks:
        text_hash = sha256_text(chunk.text)
        record = embeddings.get(chunk.chunk_id)
        if record and record.get("text_sha256") == text_hash:
            continue
        legacy_record = legacy_embeddings.get(chunk.legacy_chunk_id or "")
        if legacy_record and legacy_record.get("text_sha256") == text_hash:
            embeddings[chunk.chunk_id] = {
                "text_sha256": text_hash,
                "strategy": chunk.strategy,
                "author": chunk.author,
                "work": chunk.work,
                "sat_id": chunk.sat_id,
                "chunk_index": chunk.chunk_index,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "embedding": legacy_record["embedding"],
                "copied_from": str(LEGACY_SAT_CACHE_PATH.relative_to(ROOT)),
            }
            copied_from_legacy += 1
            continue
        missing.append(chunk)

    if copied_from_legacy:
        print(f"copied legacy embeddings: {copied_from_legacy}")
        save_cache(cache)
    if missing:
        print(f"embedding missing chunks: {len(missing)}")
    for start in range(0, len(missing), BATCH_SIZE):
        batch = missing[start : start + BATCH_SIZE]
        vectors = request_embeddings([chunk.text for chunk in batch])
        for chunk, vector in zip(batch, vectors):
            embeddings[chunk.chunk_id] = {
                "text_sha256": sha256_text(chunk.text),
                "strategy": chunk.strategy,
                "author": chunk.author,
                "work": chunk.work,
                "sat_id": chunk.sat_id,
                "chunk_index": chunk.chunk_index,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "source_token_count": chunk.source_token_count,
                "actual_token_count": chunk.actual_token_count,
                "embedding": vector,
            }
        save_cache(cache)
        done = min(start + len(batch), len(missing))
        print(f"embedded {done}/{len(missing)} missing chunks")
        if done < len(missing):
            time.sleep(0.3)

    return np.array([embeddings[chunk.chunk_id]["embedding"] for chunk in chunks], dtype=float)


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(matrix, axis=1, keepdims=True)
    denom[denom == 0] = 1.0
    return matrix / denom


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def pca_2d(matrix: np.ndarray) -> tuple[np.ndarray, list[float]]:
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :2] * s[:2]
    variances = s**2
    total = float(np.sum(variances)) or 1.0
    return coords, [float(variances[0] / total), float(variances[1] / total)]


def embedding_summary(chunks: list[Chunk], vectors: np.ndarray) -> dict[str, Any]:
    normalized = normalize_rows(vectors)
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, chunk in enumerate(chunks):
        groups[(chunk.strategy, chunk.author)].append(index)

    centroid_by_group: dict[tuple[str, str], np.ndarray] = {
        key: normalized[indices].mean(axis=0) for key, indices in groups.items()
    }
    summary: dict[str, Any] = {
        "group_centroid_cosine": {},
        "same_index_old_safe_cosine": {},
        "nearest_safe_for_old_cosine": {},
        "honen_shinran_centroid_cosine": {},
    }

    for author in sorted({chunk.author for chunk in chunks}):
        old_key = ("unsafe_token_decode", author)
        safe_key = ("safe_unicode_700", author)
        if old_key in centroid_by_group and safe_key in centroid_by_group:
            summary["group_centroid_cosine"][author] = rounded(
                cosine(centroid_by_group[old_key], centroid_by_group[safe_key])
            )

    for strategy in ["unsafe_token_decode", "safe_unicode_700"]:
        h_key = (strategy, "法然")
        s_key = (strategy, "親鸞")
        if h_key in centroid_by_group and s_key in centroid_by_group:
            c = cosine(centroid_by_group[h_key], centroid_by_group[s_key])
            summary["honen_shinran_centroid_cosine"][strategy] = {
                "cosine": rounded(c),
                "cosine_distance": rounded(1.0 - c),
            }

    by_work_strategy: dict[tuple[str, str, str], list[tuple[int, int]]] = defaultdict(list)
    for index, chunk in enumerate(chunks):
        by_work_strategy[(chunk.strategy, chunk.author, chunk.work)].append((chunk.chunk_index, index))

    for author, work in sorted({(chunk.author, chunk.work) for chunk in chunks}):
        old_pairs = sorted(by_work_strategy[("unsafe_token_decode", author, work)])
        safe_pairs = sorted(by_work_strategy[("safe_unicode_700", author, work)])
        n = min(len(old_pairs), len(safe_pairs))
        if n:
            values = [
                cosine(normalized[old_pairs[i][1]], normalized[safe_pairs[i][1]])
                for i in range(n)
            ]
            summary["same_index_old_safe_cosine"][f"{author}:{work}"] = {
                "paired_chunks": n,
                "old_chunks": len(old_pairs),
                "safe_chunks": len(safe_pairs),
                "min": rounded(min(values)),
                "p10": rounded(percentile(values, 0.1)),
                "median": rounded(percentile(values, 0.5)),
                "mean": rounded(float(np.mean(values))),
            }
        if old_pairs and safe_pairs:
            old_matrix = normalized[[index for _, index in old_pairs]]
            safe_matrix = normalized[[index for _, index in safe_pairs]]
            sims = old_matrix @ safe_matrix.T
            best = sims.max(axis=1)
            summary["nearest_safe_for_old_cosine"][f"{author}:{work}"] = {
                "old_chunks": len(old_pairs),
                "safe_chunks": len(safe_pairs),
                "min": rounded(float(best.min())),
                "p10": rounded(float(np.quantile(best, 0.1))),
                "median": rounded(float(np.median(best))),
                "mean": rounded(float(best.mean())),
            }
    return summary


def render_svg(chunks: list[Chunk], coords: np.ndarray, ratio: list[float]) -> str:
    width, height = 1540, 980
    pad_l, pad_r, pad_t, pad_b = 90, 300, 112, 90
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    xs = coords[:, 0]
    ys = coords[:, 1]
    x_min, x_max = float(xs.min()), float(xs.max())
    y_min, y_max = float(ys.min()), float(ys.max())
    x_pad = max((x_max - x_min) * 0.08, 0.03)
    y_pad = max((y_max - y_min) * 0.08, 0.03)
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad

    def sx(value: float) -> float:
        return pad_l + (value - x_min) / (x_max - x_min) * plot_w

    def sy(value: float) -> float:
        return pad_t + (y_max - value) / (y_max - y_min) * plot_h

    styles = {
        ("unsafe_token_decode", "法然"): ("#1f78b4", "旧 法然", "3.5", "0.38"),
        ("safe_unicode_700", "法然"): ("#0f9fb5", "新 法然", "5.0", "0.72"),
        ("unsafe_token_decode", "親鸞"): ("#d63f3f", "旧 親鸞", "3.5", "0.36"),
        ("safe_unicode_700", "親鸞"): ("#e58a22", "新 親鸞", "5.0", "0.72"),
    }
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for i, chunk in enumerate(chunks):
        groups[(chunk.strategy, chunk.author)].append(i)
    centers = {key: coords[indices].mean(axis=0) for key, indices in groups.items()}

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfaf7"/>',
        f'<text x="{pad_l}" y="48" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="30" font-weight="700" fill="#25221d">chunk方式比較: 旧 token decode と新 Unicode-safe 700</text>',
        f'<text x="{pad_l}" y="80" font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="15" fill="#686158">SAT T2608/T2646, model={svg_escape(MODEL)}, PC1+PC2={sum(ratio)*100:.1f}%。本文は図・メタデータに含めない。</text>',
        f'<rect x="{pad_l}" y="{pad_t}" width="{plot_w}" height="{plot_h}" rx="8" fill="#ffffff" stroke="#ddd6ca"/>',
    ]
    if x_min < 0 < x_max:
        lines.append(f'<line x1="{sx(0):.1f}" y1="{pad_t+20}" x2="{sx(0):.1f}" y2="{pad_t+plot_h-20}" stroke="#d8d2c5"/>')
    if y_min < 0 < y_max:
        lines.append(f'<line x1="{pad_l+20}" y1="{sy(0):.1f}" x2="{pad_l+plot_w-20}" y2="{sy(0):.1f}" stroke="#d8d2c5"/>')

    for author in ["法然", "親鸞"]:
        old_center = centers.get(("unsafe_token_decode", author))
        safe_center = centers.get(("safe_unicode_700", author))
        if old_center is not None and safe_center is not None:
            lines.append(
                f'<line x1="{sx(old_center[0]):.1f}" y1="{sy(old_center[1]):.1f}" '
                f'x2="{sx(safe_center[0]):.1f}" y2="{sy(safe_center[1]):.1f}" '
                'stroke="#4b5563" stroke-width="1.4" stroke-dasharray="5 5" opacity="0.62"/>'
            )

    for i, chunk in enumerate(chunks):
        color, _label, radius, opacity = styles[(chunk.strategy, chunk.author)]
        stroke = color if chunk.strategy == "unsafe_token_decode" else "#ffffff"
        fill = "none" if chunk.strategy == "unsafe_token_decode" else color
        stroke_width = "1.5" if chunk.strategy == "unsafe_token_decode" else "0.8"
        lines.append(
            f'<circle cx="{sx(coords[i, 0]):.1f}" cy="{sy(coords[i, 1]):.1f}" r="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" opacity="{opacity}">'
            f'<title>{svg_escape(chunk.strategy_label)} {svg_escape(chunk.author)} #{chunk.chunk_index}</title></circle>'
        )

    for key, center in centers.items():
        color, label, _radius, _opacity = styles[key]
        lines.append(
            f'<circle cx="{sx(center[0]):.1f}" cy="{sy(center[1]):.1f}" r="10" fill="{color}" stroke="#ffffff" stroke-width="3"/>'
        )
        lines.append(
            f'<text x="{sx(center[0])+12:.1f}" y="{sy(center[1])-10:.1f}" '
            f'font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="13" font-weight="700" fill="{color}">{svg_escape(label)}</text>'
        )

    lx = width - pad_r + 38
    ly = pad_t + 20
    lines.append(f'<g font-family="Hiragino Sans, Yu Gothic, sans-serif" font-size="14" fill="#25221d">')
    lines.append(f'<text x="{lx}" y="{ly}" font-size="18" font-weight="700">凡例</text>')
    y = ly + 34
    for key in [
        ("unsafe_token_decode", "法然"),
        ("safe_unicode_700", "法然"),
        ("unsafe_token_decode", "親鸞"),
        ("safe_unicode_700", "親鸞"),
    ]:
        color, label, radius, opacity = styles[key]
        fill = "none" if key[0] == "unsafe_token_decode" else color
        stroke = color if key[0] == "unsafe_token_decode" else "#ffffff"
        count = len(groups.get(key, []))
        lines.append(
            f'<circle cx="{lx+8}" cy="{y-5}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" opacity="{opacity}"/>'
        )
        lines.append(f'<text x="{lx+26}" y="{y}">{svg_escape(label)} n={count}</text>')
        y += 28
    lines.append(f'<text x="{lx}" y="{y+24}" font-size="13" fill="#686158">旧: token sliceをdecode</text>')
    lines.append(f'<text x="{lx}" y="{y+46}" font-size="13" fill="#686158">新: 文字境界で700 token近似</text>')
    lines.append(f'<text x="{lx}" y="{y+68}" font-size="13" fill="#686158">点線: 同一著者の重心移動</text>')
    lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines)


def build_summary(chunks: list[Chunk], works: list[WorkText], vectors: np.ndarray | None = None) -> dict[str, Any]:
    by_strategy = defaultdict(list)
    by_strategy_work = defaultdict(list)
    for chunk in chunks:
        by_strategy[chunk.strategy].append(chunk)
        by_strategy_work[(chunk.strategy, chunk.author, chunk.work)].append(chunk)

    summary: dict[str, Any] = {
        "title": "SAT kanbun chunking strategy comparison",
        "method": {
            "model": MODEL,
            "tokenizer": "tiktoken cl100k_base",
            "max_tokens": MAX_TOKENS,
            "overlap": OVERLAP,
            "unsafe_token_decode": "encode full text, slice token ids, decode each slice",
            "safe_unicode_700": "use the same 700-token grid, then round token boundaries to Python Unicode string offsets from tiktoken.decode_with_offsets",
            "raw_text_policy": "metadata excludes raw/chunk text; cache stores hashes and embeddings only",
        },
        "sources": [
            {
                "id": work.id,
                "author": work.author,
                "work": work.work,
                "sat_id": work.sat_id,
                "source_url": work.source_url,
                "jsonl_path": str(work.jsonl_path.relative_to(ROOT)),
                "line_count": len(work.lines),
                "char_count": len(work.body),
                "body_sha256": sha256_text(work.body),
            }
            for work in works
        ],
        "strategy_stats": {strategy: chunk_stats(items) for strategy, items in sorted(by_strategy.items())},
        "strategy_work_stats": {
            f"{strategy}:{author}:{work}": chunk_stats(items)
            for (strategy, author, work), items in sorted(by_strategy_work.items())
        },
        "chunk_records": [
            {
                "chunk_id": chunk.chunk_id,
                "strategy": chunk.strategy,
                "strategy_label": chunk.strategy_label,
                "author": chunk.author,
                "work": chunk.work,
                "sat_id": chunk.sat_id,
                "chunk_index": chunk.chunk_index,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "source_token_count": chunk.source_token_count,
                "actual_token_count": chunk.actual_token_count,
                "char_count": len(chunk.text),
                "replacement_chars": chunk.text.count("\ufffd"),
                "text_sha256": sha256_text(chunk.text),
            }
            for chunk in chunks
        ],
    }
    if vectors is not None:
        summary["embedding_comparison"] = embedding_summary(chunks, vectors)
        coords, ratio = pca_2d(normalize_rows(vectors))
        summary["projection"] = {
            "method": "PCA via centered NumPy SVD on L2-normalized embeddings for all old and safe chunks",
            "pca_explained_variance_ratio": [rounded(value) for value in ratio],
            "svg_path": str(SVG_PATH.relative_to(ROOT)),
        }
        for record, coord in zip(summary["chunk_records"], coords):
            record["x"] = rounded(float(coord[0]))
            record["y"] = rounded(float(coord[1]))
        SVG_PATH.write_text(render_svg(chunks, coords, ratio), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--embeddings", action="store_true", help="Run/use embedding cache and write comparison SVG.")
    args = parser.parse_args()

    if MAX_TOKENS <= OVERLAP:
        raise ValueError("MAX_TOKENS must be larger than OVERLAP.")
    encoder = tiktoken.get_encoding("cl100k_base")
    works = load_works(encoder)
    chunks: list[Chunk] = []
    for work in works:
        chunks.extend(make_unsafe_chunks(work, encoder))
        chunks.extend(make_safe_chunks(work, encoder))

    vectors = get_embeddings(chunks) if args.embeddings else None
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = build_summary(chunks, works, vectors)
    META_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {META_PATH.relative_to(ROOT)}")
    if args.embeddings:
        print(f"wrote {SVG_PATH.relative_to(ROOT)}")
    for strategy, items in sorted(defaultdict(list, {k: v for k, v in group_by_strategy(chunks).items()}).items()):
        stats = chunk_stats(items)
        print(
            f"{strategy}: chunks={stats['chunk_count']} affected={stats['affected_chunks']} "
            f"replacement_chars={stats['replacement_chars']} actual_tokens_median={stats['actual_token_count'].get('median')}"
        )


def group_by_strategy(chunks: list[Chunk]) -> dict[str, list[Chunk]]:
    grouped: dict[str, list[Chunk]] = defaultdict(list)
    for chunk in chunks:
        grouped[chunk.strategy].append(chunk)
    return dict(grouped)


if __name__ == "__main__":
    main()
