#!/usr/bin/env python3
"""Read-only audit for predecessor Okyou chunk text integrity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PREDECESSOR_ROOT = Path("/Users/daishin/Documents/Codex/Okyou")
OUTPUT_PATH = Path("data/outputs/predecessor_text_integrity_audit.json")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def token_chunks(text: str, max_tokens: int, overlap: int) -> list[str]:
    import tiktoken

    if max_tokens <= overlap:
        raise ValueError("max_tokens must be larger than overlap.")

    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    if not tokens:
        return []

    chunks: list[str] = []
    step = max_tokens - overlap
    for start in range(0, len(tokens), step):
        chunk_tokens = tokens[start : start + max_tokens]
        if len(chunk_tokens) < max_tokens // 4 and chunks:
            break
        chunks.append(encoder.decode(chunk_tokens))
    return chunks


def source_body_path(project_root: Path, item: dict[str, Any]) -> Path:
    body_path = item.get("body_path") or item.get("source_path")
    if not body_path:
        raise ValueError(f"No body/source path for {item.get('id')}")
    return project_root / body_path


def audit_processed_corpus(
    *,
    name: str,
    experiment_root: Path,
    corpus_index_path: Path,
    max_tokens: int,
    overlap: int,
) -> dict[str, Any]:
    project_root = PREDECESSOR_ROOT
    corpus = load_json(corpus_index_path)
    texts = corpus["texts"] if isinstance(corpus, dict) else corpus

    text_rows: list[dict[str, Any]] = []
    total_chunks = 0
    affected_chunks = 0
    total_replacement_chars = 0
    total_body_replacement_chars = 0

    for item in texts:
        path = source_body_path(project_root, item)
        body = path.read_text(encoding="utf-8").strip()
        chunks = token_chunks(body, max_tokens=max_tokens, overlap=overlap)
        bad_chunk_count = sum(1 for chunk in chunks if "\ufffd" in chunk)
        bad_char_count = sum(chunk.count("\ufffd") for chunk in chunks)
        body_bad_char_count = body.count("\ufffd")
        text_rows.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "body_path": str(path.relative_to(project_root)),
                "body_chars": len(body),
                "body_replacement_chars": body_bad_char_count,
                "chunk_count": len(chunks),
                "affected_chunks": bad_chunk_count,
                "chunk_replacement_chars": bad_char_count,
                "first_bad_chunk_index": next(
                    (index for index, chunk in enumerate(chunks) if "\ufffd" in chunk),
                    None,
                ),
            }
        )
        total_chunks += len(chunks)
        affected_chunks += bad_chunk_count
        total_replacement_chars += bad_char_count
        total_body_replacement_chars += body_bad_char_count

    return {
        "experiment": name,
        "root": str(experiment_root),
        "chunk_method": "cl100k_base token slices decoded with tiktoken.decode",
        "max_tokens": max_tokens,
        "overlap": overlap,
        "texts": len(text_rows),
        "chunks": total_chunks,
        "affected_chunks": affected_chunks,
        "chunk_replacement_chars": total_replacement_chars,
        "body_replacement_chars": total_body_replacement_chars,
        "affected_texts": [
            row for row in text_rows if row["affected_chunks"] or row["body_replacement_chars"]
        ],
        "all_texts": text_rows,
    }


def audit_output_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    data = load_json(path)
    chunks = data.get("chunks", [])
    previews = [chunk.get("preview", "") for chunk in chunks]
    return {
        "path": str(path),
        "exists": True,
        "chunks": len(chunks),
        "preview_affected_chunks": sum(1 for preview in previews if "\ufffd" in preview),
        "preview_replacement_chars": sum(preview.count("\ufffd") for preview in previews),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    audits = [
        audit_processed_corpus(
            name="sect_sutra_map",
            experiment_root=PREDECESSOR_ROOT / "experiments/sect_sutra_map",
            corpus_index_path=PREDECESSOR_ROOT
            / "experiments/sect_sutra_map/data/processed/corpus_index.json",
            max_tokens=700,
            overlap=100,
        ),
        audit_processed_corpus(
            name="multilingual_sutra_map",
            experiment_root=PREDECESSOR_ROOT / "experiments/multilingual_sutra_map",
            corpus_index_path=PREDECESSOR_ROOT
            / "experiments/multilingual_sutra_map/data/processed/corpus_index.json",
            max_tokens=700,
            overlap=100,
        ),
    ]

    output_checks = [
        audit_output_json(
            PREDECESSOR_ROOT / "experiments/sect_sutra_map/outputs/embeddings.json"
        ),
        audit_output_json(
            PREDECESSOR_ROOT / "experiments/multilingual_sutra_map/outputs/embeddings.json"
        ),
        audit_output_json(
            PREDECESSOR_ROOT / "experiments/sect_sutra_map/viewer/data.json"
        ),
        audit_output_json(
            PREDECESSOR_ROOT / "experiments/sect_sutra_map/viewer/public-data.json"
        ),
    ]

    result = {
        "predecessor_root": str(PREDECESSOR_ROOT),
        "audits": audits,
        "output_checks": output_checks,
    }

    if args.write:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {OUTPUT_PATH}")

    for audit in audits:
        print(
            f"{audit['experiment']}: {audit['affected_chunks']}/{audit['chunks']} chunks, "
            f"{audit['chunk_replacement_chars']} replacement chars; "
            f"source bodies {audit['body_replacement_chars']} replacement chars"
        )
        for row in audit["affected_texts"]:
            print(
                f"  {row['id']}: {row['affected_chunks']}/{row['chunk_count']} chunks, "
                f"{row['chunk_replacement_chars']} replacement chars, "
                f"first bad chunk {row['first_bad_chunk_index']}"
            )
    for check in output_checks:
        if check["exists"]:
            print(
                f"{check['path']}: preview {check['preview_affected_chunks']}/"
                f"{check['chunks']} chunks, {check['preview_replacement_chars']} replacement chars"
            )
        else:
            print(f"{check['path']}: missing")


if __name__ == "__main__":
    main()
