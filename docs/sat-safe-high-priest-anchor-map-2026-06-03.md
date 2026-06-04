# SAT Safe High-Priest Anchor Map 2026-06-03

## 目的

法然『選択本願念仏集』と親鸞『教行信証』の SAT 漢文系 safe chunk map に、浄土系高僧・典拠文献を重ねる。

基準は、先行 `Okyou` の固定長方針を保ったまま、文字列破損を避ける方式にする。

## 基準方式

- Text basis: SAT 漢文系 prepared text
- chunk size: 700 token
- overlap: 100 token
- boundary: Unicode-safe, `tiktoken.decode_with_offsets()` による文字境界丸め
- tokenizer: `cl100k_base`
- embedding: OpenAI `text-embedding-3-large`
- PCA fit: 法然・親鸞 chunks のみ
- anchors: 高僧文献 chunks を同じ PCA 面へ投影

## Focus Texts

- 法然『選択本願念仏集』
  - SAT `T2608`
  - `https://21dzk.l.u-tokyo.ac.jp/SAT/T2608.html`
- 親鸞『教行信証』
  - SAT `T2646`
  - `https://21dzk.l.u-tokyo.ac.jp/SAT/T2646_,83,0589a01:2646_,83,0643c29.html`

## Anchor Texts

- 龍樹『十住毘婆沙論』易行品
  - `https://21dzk.l.u-tokyo.ac.jp/SAT/T1521_,26,0038a25:1521_,26,0040a22.html`
- 天親『無量寿経優波提舎願生偈』
  - `https://21dzk.l.u-tokyo.ac.jp/SAT/T1524.html`
- 曇鸞『往生論註』
  - `https://21dzk.l.u-tokyo.ac.jp/SAT/T1819.html`
- 道綽『安楽集』
  - `https://21dzk.l.u-tokyo.ac.jp/SAT/T1958.html`
- 善導『観無量寿仏経疏』
  - `https://21dzk.l.u-tokyo.ac.jp/SAT/T1753.html`
- 源信『往生要集』
  - `https://21dzk.l.u-tokyo.ac.jp/SAT/T2682.html`

## Run Summary

PCA explained variance ratio on fit scope:

- PC1: `0.068562`
- PC2: `0.047405`
- PC1+PC2: about `11.6%`

Chunk counts:

| author | chunks |
| --- | ---: |
| 法然 | 69 |
| 親鸞 | 191 |
| 龍樹 | 6 |
| 天親 | 9 |
| 曇鸞 | 31 |
| 道綽 | 42 |
| 善導 | 23 |
| 源信 | 73 |

Centroid distances in the displayed PCA plane:

| author | distance to 法然 | distance to 親鸞 |
| --- | ---: | ---: |
| 龍樹 | 0.180264 | 0.109235 |
| 天親 | 0.115497 | 0.099764 |
| 曇鸞 | 0.213282 | 0.089145 |
| 道綽 | 0.146307 | 0.048035 |
| 善導 | 0.117257 | 0.076170 |
| 源信 | 0.227607 | 0.080767 |

## First Reading

この 2D 表示では、法然と親鸞の重心は PC1 方向に分かれる。高僧アンカーの重心は、多くが親鸞側へ寄る。

- 道綽は親鸞重心に最も近い。
- 善導も親鸞側に近いが、法然側との距離も比較的短い。
- 曇鸞と源信は親鸞側への距離が短く、親鸞の広がりと重なりやすい。
- 天親は法然・親鸞の中間寄り。
- 龍樹は親鸞側へ寄るが、PC2 方向では下方へ離れる。

これは意味 embedding の 2D map 上の初見であり、影響関係の結論ではない。今後、典拠マーカー層、文体語彙層、巻別・引用対応と照合する。

## 出力

- `scripts/make_sat_safe_high_priest_anchor_map.py`
- `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.svg`
- `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.svg.png`
- `data/outputs/sat_safe_honen_shinran_high_priest_anchor_map_text-embedding-3-large_700_100.json`
- `data/cache/sat_safe_high_priest_anchor_embeddings_text-embedding-3-large_700_100.json`

`data/` 以下はローカル専用。raw text, processed text, chunk text, embedding cache は publish / commit しない。

## 再実行

validation only:

```bash
/Users/daishin/.pyenv/shims/python scripts/make_sat_safe_high_priest_anchor_map.py --validate-only
```

embedding and map:

```bash
/Users/daishin/.pyenv/shims/python scripts/make_sat_safe_high_priest_anchor_map.py
```
