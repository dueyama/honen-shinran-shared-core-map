#!/usr/bin/env python3
"""Build an embedding-based 2D map for Honen/Shinran page chunks.

Raw source text is read only from ignored local data/raw/. Embeddings are
cached under ignored data/cache/. Public-facing outputs contain coordinates,
source URLs, hashes, and summary statistics, but no source text.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from make_simple_2d_map import (  # noqa: E402
    Chunk,
    chunk_source_url,
    covariance_ellipse,
    load_chunks,
    render_svg_with_zoom,
)


OUT_DIR = ROOT / "data" / "outputs"
CACHE_DIR = ROOT / "data" / "cache"
MODEL = os.getenv("OKYOU2_EMBEDDING_MODEL", "text-embedding-3-large")
EMBEDDING_CACHE_PATH = CACHE_DIR / f"honen_shinran_page_embeddings_{MODEL}.json"
SVG_PATH = OUT_DIR / "honen_shinran_embedding_2d_with_zoom.svg"
META_PATH = OUT_DIR / "honen_shinran_embedding_2d_meta.json"
API_URL = os.getenv("OPENAI_EMBEDDINGS_URL", "https://api.openai.com/v1/embeddings")
BATCH_SIZE = int(os.getenv("OKYOU2_EMBEDDING_BATCH_SIZE", "64"))
MAX_CHARS = int(os.getenv("OKYOU2_EMBEDDING_MAX_CHARS", "6000"))


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def public_chunk_hash(chunk: Chunk) -> str:
    return text_hash(f"{chunk.chunk_id}\n{chunk.text}")


def load_cache() -> dict[str, Any]:
    if not EMBEDDING_CACHE_PATH.exists():
        return {"model": MODEL, "embeddings": {}}
    data = json.loads(EMBEDDING_CACHE_PATH.read_text(encoding="utf-8"))
    if data.get("model") != MODEL:
        return {"model": MODEL, "embeddings": {}}
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


def get_embeddings(chunks: list[Chunk]) -> np.ndarray:
    cache = load_cache()
    embeddings: dict[str, Any] = cache["embeddings"]

    missing: list[Chunk] = []
    for chunk in chunks:
        item = embeddings.get(chunk.chunk_id)
        if not item or item.get("text_sha256") != public_chunk_hash(chunk):
            missing.append(chunk)

    if missing:
        print(f"embedding missing chunks: {len(missing)}")
    for start in range(0, len(missing), BATCH_SIZE):
        batch = missing[start : start + BATCH_SIZE]
        inputs = [chunk.text[:MAX_CHARS] for chunk in batch]
        vectors = request_embeddings(inputs)
        for chunk, vector in zip(batch, vectors):
            embeddings[chunk.chunk_id] = {
                "text_sha256": public_chunk_hash(chunk),
                "source_url": chunk_source_url(chunk),
                "author": chunk.author,
                "work": chunk.work,
                "page": chunk.page,
                "embedding": vector,
            }
        save_cache(cache)
        done = min(start + len(batch), len(missing))
        print(f"embedded {done}/{len(missing)} missing chunks")
        if done < len(missing):
            time.sleep(0.3)

    vectors = [embeddings[chunk.chunk_id]["embedding"] for chunk in chunks]
    return np.array(vectors, dtype=float)


def project_2d(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    x = vectors / norms
    centered = x - x.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :2] * s[:2]
    coords -= coords.mean(axis=0, keepdims=True)
    scale = np.max(np.abs(coords)) or 1.0
    return coords / scale


def summarize(chunks: list[Chunk], coords: np.ndarray, vectors: np.ndarray) -> dict[str, Any]:
    groups: dict[str, list[int]] = defaultdict(list)
    for i, chunk in enumerate(chunks):
        groups[chunk.author].append(i)

    author_stats: dict[str, Any] = {}
    centroids: dict[str, np.ndarray] = {}
    for author, indices in groups.items():
        pts = coords[indices]
        center = pts.mean(axis=0)
        centroids[author] = center
        distances = np.linalg.norm(pts - center, axis=1)
        ew, eh, angle = covariance_ellipse(pts, center)
        pages = [chunks[i].page for i in indices]
        author_stats[author] = {
            "chunk_count": len(indices),
            "work": chunks[indices[0]].work,
            "centroid": [round(float(center[0]), 6), round(float(center[1]), 6)],
            "rms_radius": round(float(np.sqrt(np.mean(distances**2))), 6),
            "p90_radius": round(float(np.quantile(distances, 0.9)), 6),
            "ellipse_radius_scale": 1.55,
            "ellipse_width": round(float(ew), 6),
            "ellipse_height": round(float(eh), 6),
            "ellipse_angle_degrees": round(float(angle), 3),
            "page_min": min(pages),
            "page_max": max(pages),
        }

    centroid_distance = None
    if {"法然", "親鸞"}.issubset(centroids):
        centroid_distance = round(float(np.linalg.norm(centroids["法然"] - centroids["親鸞"])), 6)

    return {
        "title": "法然『選択集』と親鸞『教行信証』の embedding 2Dマップ",
        "created_from": "local downloaded seiten HTML; raw text and embeddings are not included here",
        "source_site": "聖教電子化研究会",
        "source_urls": [
            "https://seiten.icho.gr.jp/html/z1-[920-1005].html",
            "https://seiten.icho.gr.jp/html/[152-430].html",
        ],
        "method": {
            "chunk_unit": "seiten page",
            "text_basis": "Japanese reading text extracted from honbun/s_sage/l_nobegaki; r_kanbun excluded in this first page-level run",
            "embedding_model": MODEL,
            "embedding_api_url": API_URL,
            "embedding_dimension": int(vectors.shape[1]),
            "projection": "L2-normalized embeddings, centered SVD, first two components, scaled by max absolute coordinate",
            "status": "rough exploratory embedding map; not yet separated into semantic/style/source-marker layers",
        },
        "author_stats": author_stats,
        "centroid_distance": centroid_distance,
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "author": chunk.author,
                "work": chunk.work,
                "page": chunk.page,
                "source_url": chunk_source_url(chunk),
                "text_sha256": public_chunk_hash(chunk),
                "x": round(float(coords[i, 0]), 6),
                "y": round(float(coords[i, 1]), 6),
            }
            for i, chunk in enumerate(chunks)
        ],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chunks = load_chunks()
    if not chunks:
        raise SystemExit("No chunks found. Download seiten HTML into data/raw/seiten first.")
    vectors = get_embeddings(chunks)
    coords = project_2d(vectors)
    SVG_PATH.write_text(
        render_svg_with_zoom(
            chunks,
            coords,
            title="法然『選択集』と親鸞『教行信証』の embedding 2Dマップ",
            subtitle=f"ページ単位。{MODEL} + SVD。点=ページ、太点=重心、楕円=点群の広がり。右は局所拡大。",
        ),
        encoding="utf-8",
    )
    META_PATH.write_text(
        json.dumps(summarize(chunks, coords, vectors), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    counts = Counter(chunk.author for chunk in chunks)
    print(f"wrote {SVG_PATH}")
    print(f"wrote {META_PATH}")
    print("chunks:", dict(counts))


if __name__ == "__main__":
    main()
