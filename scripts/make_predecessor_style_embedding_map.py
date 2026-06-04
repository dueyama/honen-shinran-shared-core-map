#!/usr/bin/env python3
"""Build a predecessor-style embedding map for Honen/Shinran.

This follows the Okyou v1 baseline choices as closely as possible for this
new corpus:

- text-embedding-3-large
- cl100k_base tokenization
- 700-token chunks with 100-token overlap
- PCA-style 2D coordinates from chunk embeddings
- no raw source text in public metadata or figures
"""

from __future__ import annotations

import hashlib
import json
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

from make_simple_2d_map import (  # noqa: E402
    Chunk,
    covariance_ellipse,
    load_chunks,
    render_svg_with_zoom,
)


OUT_DIR = ROOT / "data" / "outputs"
CACHE_DIR = ROOT / "data" / "cache"
MODEL = os.getenv("OKYOU2_EMBEDDING_MODEL", "text-embedding-3-large")
MAX_TOKENS = int(os.getenv("OKYOU2_MAX_TOKENS", "700"))
OVERLAP = int(os.getenv("OKYOU2_OVERLAP", "100"))
BATCH_SIZE = int(os.getenv("OKYOU2_EMBEDDING_BATCH_SIZE", "64"))
API_URL = os.getenv("OPENAI_EMBEDDINGS_URL", "https://api.openai.com/v1/embeddings")

EMBEDDING_CACHE_PATH = (
    CACHE_DIR
    / f"honen_shinran_predecessor_style_embeddings_{MODEL}_{MAX_TOKENS}_{OVERLAP}.json"
)
SVG_PATH = OUT_DIR / "honen_shinran_predecessor_style_embedding_map.svg"
META_PATH = OUT_DIR / "honen_shinran_predecessor_style_embedding_map_meta.json"


@dataclass
class TokenChunk:
    chunk: Chunk
    text_sha256: str
    token_start: int
    token_end: int
    page_start: str
    page_end: str
    source_urls: list[str]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def page_sort_key(page: str) -> tuple[int, int, str]:
    if page.startswith("z1-"):
        return (1, int(page.removeprefix("z1-")), page)
    if page.isdigit():
        return (0, int(page), page)
    return (2, 0, page)


def source_url(page: str) -> str:
    return f"https://seiten.icho.gr.jp/html/{page}.html"


def load_work_pages() -> dict[tuple[str, str], list[Chunk]]:
    pages: dict[tuple[str, str], list[Chunk]] = defaultdict(list)
    for page in load_chunks():
        pages[(page.author, page.work)].append(page)
    for key in pages:
        pages[key].sort(key=lambda chunk: page_sort_key(chunk.page))
    return dict(pages)


def make_token_chunks() -> list[TokenChunk]:
    if MAX_TOKENS <= OVERLAP:
        raise ValueError("MAX_TOKENS must be larger than OVERLAP.")

    encoder = tiktoken.get_encoding("cl100k_base")
    step = MAX_TOKENS - OVERLAP
    token_chunks: list[TokenChunk] = []

    for (author, work), pages in sorted(load_work_pages().items()):
        all_tokens: list[int] = []
        page_spans: list[tuple[str, int, int]] = []
        for page in pages:
            tokens = encoder.encode(page.text)
            if not tokens:
                continue
            start = len(all_tokens)
            all_tokens.extend(tokens)
            end = len(all_tokens)
            page_spans.append((page.page, start, end))

        chunk_index = 0
        for start in range(0, len(all_tokens), step):
            end = min(start + MAX_TOKENS, len(all_tokens))
            if end - start < MAX_TOKENS // 4 and chunk_index:
                break
            overlapping_pages = [
                page
                for page, page_start, page_end in page_spans
                if page_start < end and page_end > start
            ]
            if not overlapping_pages:
                continue
            text = encoder.decode(all_tokens[start:end]).strip()
            if not text:
                continue
            page_start = overlapping_pages[0]
            page_end = overlapping_pages[-1]
            page_range = page_start if page_start == page_end else f"{page_start}-{page_end}"
            chunk = Chunk(
                chunk_id=f"{author}:{work}:chunk_{chunk_index:04d}",
                author=author,
                work=work,
                page=page_range,
                text=text,
            )
            token_chunks.append(
                TokenChunk(
                    chunk=chunk,
                    text_sha256=sha256_text(text),
                    token_start=start,
                    token_end=end,
                    page_start=page_start,
                    page_end=page_end,
                    source_urls=sorted({source_url(page_start), source_url(page_end)}),
                )
            )
            chunk_index += 1

    return token_chunks


def load_cache() -> dict[str, Any]:
    if not EMBEDDING_CACHE_PATH.exists():
        return {"model": MODEL, "max_tokens": MAX_TOKENS, "overlap": OVERLAP, "embeddings": {}}
    data = json.loads(EMBEDDING_CACHE_PATH.read_text(encoding="utf-8"))
    if (
        data.get("model") != MODEL
        or data.get("max_tokens") != MAX_TOKENS
        or data.get("overlap") != OVERLAP
    ):
        return {"model": MODEL, "max_tokens": MAX_TOKENS, "overlap": OVERLAP, "embeddings": {}}
    data.setdefault("embeddings", {})
    return data


def save_cache(cache: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = EMBEDDING_CACHE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    tmp.replace(EMBEDDING_CACHE_PATH)


def request_embeddings(inputs: list[str]) -> list[list[float]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    payload = json.dumps({"model": MODEL, "input": inputs}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI embeddings HTTP {exc.code}: {detail[:600]}") from exc
    data = json.loads(body)
    ordered = sorted(data["data"], key=lambda item: item["index"])
    return [item["embedding"] for item in ordered]


def get_embeddings(token_chunks: list[TokenChunk]) -> np.ndarray:
    cache = load_cache()
    embeddings: dict[str, Any] = cache["embeddings"]

    missing: list[TokenChunk] = []
    for item in token_chunks:
        record = embeddings.get(item.chunk.chunk_id)
        if not record or record.get("text_sha256") != item.text_sha256:
            missing.append(item)

    if missing:
        print(f"embedding missing chunks: {len(missing)}")
    for start in range(0, len(missing), BATCH_SIZE):
        batch = missing[start : start + BATCH_SIZE]
        vectors = request_embeddings([item.chunk.text for item in batch])
        for item, vector in zip(batch, vectors):
            embeddings[item.chunk.chunk_id] = {
                "text_sha256": item.text_sha256,
                "author": item.chunk.author,
                "work": item.chunk.work,
                "page_start": item.page_start,
                "page_end": item.page_end,
                "token_start": item.token_start,
                "token_end": item.token_end,
                "embedding": vector,
            }
        save_cache(cache)
        done = min(start + len(batch), len(missing))
        print(f"embedded {done}/{len(missing)} missing chunks")
        if done < len(missing):
            time.sleep(0.3)

    return np.array([embeddings[item.chunk.chunk_id]["embedding"] for item in token_chunks], dtype=float)


def pca_2d(matrix: np.ndarray) -> tuple[np.ndarray, list[float]]:
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :2] * s[:2]
    variances = s**2
    total = float(np.sum(variances)) or 1.0
    ratio = [float(variances[0] / total), float(variances[1] / total)]
    return coords, ratio


def summarize(token_chunks: list[TokenChunk], coords: np.ndarray, vectors: np.ndarray, ratio: list[float]) -> dict[str, Any]:
    groups: dict[str, list[int]] = defaultdict(list)
    for i, item in enumerate(token_chunks):
        groups[item.chunk.author].append(i)

    author_stats: dict[str, Any] = {}
    centroids: dict[str, np.ndarray] = {}
    for author, indices in groups.items():
        pts = coords[indices]
        center = pts.mean(axis=0)
        centroids[author] = center
        distances = np.linalg.norm(pts - center, axis=1)
        ew, eh, angle = covariance_ellipse(pts, center)
        author_stats[author] = {
            "chunk_count": len(indices),
            "work": token_chunks[indices[0]].chunk.work,
            "centroid": [round(float(center[0]), 6), round(float(center[1]), 6)],
            "rms_radius": round(float(np.sqrt(np.mean(distances**2))), 6),
            "p90_radius": round(float(np.quantile(distances, 0.9)), 6),
            "ellipse_radius_scale": 1.55,
            "ellipse_width": round(float(ew), 6),
            "ellipse_height": round(float(eh), 6),
            "ellipse_angle_degrees": round(float(angle), 3),
        }

    centroid_distance = None
    if {"法然", "親鸞"}.issubset(centroids):
        centroid_distance = round(float(np.linalg.norm(centroids["法然"] - centroids["親鸞"])), 6)

    return {
        "title": "法然『選択集』と親鸞『教行信証』の predecessor-style embedding map",
        "created_from": "local downloaded seiten HTML; raw text and embeddings are not included here",
        "source_site": "聖教電子化研究会",
        "source_urls": [
            "https://seiten.icho.gr.jp/html/z1-[920-1005].html",
            "https://seiten.icho.gr.jp/html/[152-430].html",
        ],
        "method": {
            "baseline": "Okyou v1-style semantic chunk distribution",
            "text_basis": "Japanese reading text extracted from honbun/s_sage/l_nobegaki; r_kanbun excluded in this first run",
            "embedding_model": MODEL,
            "embedding_api_url": API_URL,
            "embedding_dimension": int(vectors.shape[1]),
            "tokenizer": "tiktoken cl100k_base",
            "max_tokens": MAX_TOKENS,
            "overlap": OVERLAP,
            "projection": "PCA via centered NumPy SVD on raw chunk embeddings",
            "pca_explained_variance_ratio": [round(float(value), 6) for value in ratio],
            "status": "predecessor-style semantic layer only; style/source-marker layers not yet overlaid",
        },
        "author_stats": author_stats,
        "centroid_distance": centroid_distance,
        "chunks": [
            {
                "chunk_id": item.chunk.chunk_id,
                "author": item.chunk.author,
                "work": item.chunk.work,
                "chunk_index": int(item.chunk.chunk_id.rsplit("_", 1)[-1]),
                "page_start": item.page_start,
                "page_end": item.page_end,
                "source_urls": item.source_urls,
                "token_start": item.token_start,
                "token_end": item.token_end,
                "text_sha256": item.text_sha256,
                "x": round(float(coords[i, 0]), 6),
                "y": round(float(coords[i, 1]), 6),
            }
            for i, item in enumerate(token_chunks)
        ],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    token_chunks = make_token_chunks()
    if not token_chunks:
        raise SystemExit("No token chunks found. Download seiten HTML first.")
    vectors = get_embeddings(token_chunks)
    coords, ratio = pca_2d(vectors)
    chunks_for_render = [item.chunk for item in token_chunks]
    SVG_PATH.write_text(
        render_svg_with_zoom(
            chunks_for_render,
            coords,
            title="法然『選択集』と親鸞『教行信証』の先行方式 embedding map",
            subtitle=(
                f"{MODEL}。cl100k_base {MAX_TOKENS} token / overlap {OVERLAP}。"
                f"PCA 第1+第2軸={sum(ratio) * 100:.1f}%。右は局所拡大。"
            ),
        ),
        encoding="utf-8",
    )
    META_PATH.write_text(
        json.dumps(summarize(token_chunks, coords, vectors, ratio), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    counts = Counter(item.chunk.author for item in token_chunks)
    print(f"wrote {SVG_PATH}")
    print(f"wrote {META_PATH}")
    print("chunks:", dict(counts))
    print(f"PCA ratio: {ratio[0]:.4f}, {ratio[1]:.4f}")


if __name__ == "__main__":
    main()
