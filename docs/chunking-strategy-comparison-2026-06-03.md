# Chunking Strategy Comparison 2026-06-03

## 目的

SAT 漢文系本文について、旧方式の `token slice -> decode` と、新方式の `Unicode-safe 700 token 近似` を同じ本文・同じ embedding model で比較する。

ここでの新方式は行単位 chunk ではない。700 token / 100 overlap の固定長方針を保ちつつ、`tiktoken.decode_with_offsets()` の文字 offset を使って、chunk 境界を Python の Unicode 文字列境界へ丸める。

## 対象

- 法然『選択本願念仏集』
  - SAT `T2608`
  - source: `https://21dzk.l.u-tokyo.ac.jp/SAT/T2608.html`
- 親鸞『教行信証』
  - SAT `T2646`
  - source: `https://21dzk.l.u-tokyo.ac.jp/SAT/T2646_,83,0589a01:2646_,83,0643c29.html`

入力本文:

- `data/processed/sat_kanbun/honen_t2608_senchakushu.lines.jsonl`
- `data/processed/sat_kanbun/shinran_t2646_kyogyoshinsho.lines.jsonl`

入力本文はローカル専用で、commit / publish しない。

## 比較した方式

旧方式:

- 本文全体を `cl100k_base` で token 化。
- token id list を 700 token / 100 overlap で機械的に切る。
- 各 token slice を `encoder.decode()` で文字列に戻す。

新方式:

- 本文全体を `cl100k_base` で token 化。
- 700 token / 100 overlap の token grid は保つ。
- `decode_with_offsets()` で token index から文字 offset を得る。
- 境界が文字の途中にある場合は、文字列境界へ丸めて chunk 文字列を作る。
- `U+FFFD` が出たら fail。

## 文字列品質

| strategy | chunks | affected chunks | replacement chars | median actual tokens | mean actual tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| 旧 `unsafe_token_decode` | 260 | 148 | 181 | 700.0 | 698.5 |
| 新 `safe_unicode_700` | 260 | 0 | 0 | 700.0 | 698.165 |

新方式でも chunk 数は同じ 260。token 長分布もほぼ同じで、旧方式にあった `U+FFFD` だけが消える。

## Embedding 比較

Model:

- `text-embedding-3-large`

同じ index の旧 chunk と新 chunk の cosine similarity:

| work | paired chunks | min | p10 | median | mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| 法然『選択本願念仏集』 | 69 | 0.952533 | 0.972654 | 0.997852 | 0.990319 |
| 親鸞『教行信証』 | 191 | 0.954691 | 0.972646 | 0.998012 | 0.990932 |

著者別 centroid の旧・新 cosine:

| author | old vs safe centroid cosine |
| --- | ---: |
| 法然 | 0.999352 |
| 親鸞 | 0.999443 |

法然・親鸞 centroid 間 cosine distance:

| strategy | cosine | cosine distance |
| --- | ---: | ---: |
| 旧 `unsafe_token_decode` | 0.944168 | 0.055832 |
| 新 `safe_unicode_700` | 0.944594 | 0.055406 |

## 読み

旧方式の `U+FFFD` は文字列品質としては避けるべきだが、700 token chunk の embedding 幾何全体を大きく動かすほどではない。今回の比較では、旧・新の同index chunk は平均 cosine 約 0.99、著者別重心も 0.999 以上で一致した。

したがって、前稿や旧試行の大局的な意味マップは参考として残せる。一方で、今後の基準方式としては、本文品質、再現性、line range との対応を優先し、Unicode-safe 方式を採用する。新方式は token 長・chunk 数・overlap 方針をほぼ維持しながら、文字列破損を避けられる。

## 出力

- `scripts/compare_sat_chunking_strategies.py`
- `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json`
- `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.svg`
- `data/outputs/sat_chunking_strategy_compare_text-embedding-3-large_700_100.svg.png`
- `data/cache/sat_chunking_strategy_compare_text-embedding-3-large_700_100.json`

`data/` 以下はローカル専用。公開前には、本文・ローカルパス・cache の扱いを確認する。

## 再実行

文字列品質のみ:

```bash
python3 scripts/compare_sat_chunking_strategies.py
```

embedding 比較込み:

```bash
python3 scripts/compare_sat_chunking_strategies.py --embeddings
```
