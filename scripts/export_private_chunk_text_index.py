#!/usr/bin/env python3
"""Export a private local chunk-to-text index.

This file intentionally writes raw chunk text under data/outputs/PRIVATE_*.
The data directory is ignored and must not be committed or published.
"""

from __future__ import annotations

import json
from pathlib import Path

from make_predecessor_style_embedding_map import MAX_TOKENS, MODEL, OVERLAP, make_token_chunks


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = (
    ROOT
    / "data"
    / "outputs"
    / f"PRIVATE_chunk_text_index_{MODEL}_{MAX_TOKENS}_{OVERLAP}.jsonl"
)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    chunks = make_token_chunks()
    with OUT_PATH.open("w", encoding="utf-8") as handle:
        for item in chunks:
            record = {
                "chunk_id": item.chunk.chunk_id,
                "author": item.chunk.author,
                "work": item.chunk.work,
                "page_start": item.page_start,
                "page_end": item.page_end,
                "source_urls": item.source_urls,
                "token_start": item.token_start,
                "token_end": item.token_end,
                "text_sha256": item.text_sha256,
                "text_char_count": len(item.chunk.text),
                "text": item.chunk.text,
                "private_policy": "local-only raw chunk text; do not commit or publish",
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_PATH}")
    print(f"chunks: {len(chunks)}")


if __name__ == "__main__":
    main()
