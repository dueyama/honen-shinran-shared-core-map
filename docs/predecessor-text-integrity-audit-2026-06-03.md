# Predecessor Text Integrity Audit 2026-06-03

## 目的

先行 `Okyou` の主要な embedding map で、任意 token 境界の chunk decode による `U+FFFD` replacement character が混入していたかを確認する。

先行 `Okyou` はリリース済み・閉鎖済みの参照元なので、この監査では読み取りだけを行い、先行 repo には一切変更を加えない。

## 監査範囲

対象:

- `/Users/daishin/Documents/Codex/Okyou/experiments/sect_sutra_map`
- `/Users/daishin/Documents/Codex/Okyou/experiments/multilingual_sutra_map`

確認したこと:

- processed body text に `U+FFFD` が含まれるか。
- 先行 repo と同じ `cl100k_base`、700 token、100 token overlap の chunk 生成を再現したとき、chunk text に `U+FFFD` が含まれるか。
- 既存の `outputs/embeddings.json` の preview に `U+FFFD` が含まれるか。

確認していないこと:

- embedding を再計算した場合の PCA 図や近傍混合率の差。
- 論文本文の全記述の妥当性。
- 公開 HTML/PDF の記述修正。

## 結果

### sect_sutra_map

- processed body text: `U+FFFD` は 0。
- chunk text: 433 chunks 中 256 chunks に `U+FFFD`。
- chunk 内の `U+FFFD` 総数: 326。
- 既存 `outputs/embeddings.json` preview: 433 chunks 中 147 chunks に `U+FFFD`、総数 173。

影響が出た text:

| id | affected chunks | all chunks | replacement chars |
| --- | ---: | ---: | ---: |
| `t0360_larger_sukhavati` | 18 | 27 | 23 |
| `t0365_meditation_sutra` | 18 | 23 | 22 |
| `t0366_amida_sutra` | 4 | 7 | 6 |
| `t0367_praise_pure_land` | 9 | 12 | 11 |
| `kyogyoshinsho` | 108 | 197 | 138 |
| `t0262_lotus_sutra` | 9 | 13 | 10 |
| `t0262_kannon_chapter` | 4 | 6 | 4 |
| `t0848_maha_vairocana` | 16 | 28 | 25 |
| `t0865_vajrasekhara` | 12 | 22 | 15 |
| `t0243_rishu_kyo` | 5 | 9 | 5 |
| `t0251_heart_sutra` | 2 | 3 | 2 |
| `t0676_samdhinirmocana` | 11 | 18 | 12 |
| `t0235_diamond_sutra` | 7 | 15 | 10 |
| `t0475_vimalakirti` | 20 | 32 | 28 |
| `t0279_flower_garland` | 13 | 21 | 15 |

### multilingual_sutra_map

- processed body text: `U+FFFD` は 0。
- chunk text: 105 chunks 中 44 chunks に `U+FFFD`。
- chunk 内の `U+FFFD` 総数: 58。
- `outputs/embeddings.json` はこの checkout では存在しない。

影響が出た text:

| id | affected chunks | all chunks | replacement chars |
| --- | ---: | ---: | ---: |
| `t0676_samdhinirmocana_zh` | 11 | 18 | 12 |
| `t0235_diamond_zh` | 7 | 15 | 10 |
| `t0475_vimalakirti_zh` | 20 | 32 | 28 |
| `t0251_heart_zh` | 2 | 3 | 2 |
| `t0366_amida_zh` | 4 | 7 | 6 |

## 解釈

前レポの元本文そのものが壊れていたわけではない。問題は、`tiktoken` token list を固定長で切り、任意の境界から `encoder.decode()` したことで、chunk の先頭または末尾付近に replacement character が入ったこと。

したがって、前レポの図は「本文全体がゴミで壊れた」というより、「多くの chunk に 1 文字前後の境界由来ノイズを含んだ embedding map」と見るのが正確である。意味 embedding の大勢を完全に反転させる規模とは限らないが、方法論としては問題があり、厳密な再検証では使い回さない。

## Okyou2 での対応

Okyou2 では、本文を SAT 行単位で保持して provenance を失わない。ただし、基準 chunk は行単位ではなく、Unicode 文字境界で丸めた 700 token 近似 chunk とする。chunk text には品質検査を必須化し、少なくとも次を fail 条件にする。

- `U+FFFD`
- HTML tag / entity
- image placeholder / button label
- SAT line ref の本文混入
- control character
- empty chunk

## 再実行

```bash
/Users/daishin/.pyenv/shims/python scripts/audit_predecessor_text_integrity.py --write
```

出力:

- `data/outputs/predecessor_text_integrity_audit.json`

この監査 JSON はローカル用。本文は含まないが、先行 repo の絶対パスを含むため、公開前には扱いを確認する。
